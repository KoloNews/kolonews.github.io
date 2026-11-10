"""Прибирає однакові фото з галереї історії.

Одне й те саме фото різні видання публікують з різними адресами й розмірами,
тож порівнюємо самі зображення: зменшуємо до 9×8 сірих пікселів і рахуємо
«відбиток» (dHash). Дуже схожі відбитки = те саме фото.
Також відкидаємо дрібні картинки (логотипи, іконки).
Потрібна бібліотека Pillow; без неї галерея лишається як є.
"""

from __future__ import annotations

import concurrent.futures as cf
import io
import time
import urllib.error
import urllib.parse
import urllib.request

try:
    from PIL import Image, ImageFile
    ImageFile.LOAD_TRUNCATED_IMAGES = True  # великі фото читаємо не повністю (MAX_BYTES) — це нормально
except ImportError:  # без Pillow просто не порівнюємо
    Image = None

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15"
MAX_BYTES = 3_000_000
MIN_WIDTH = 360          # менші картинки — найчастіше логотипи чи іконки (якщо є інші фото)
TINY = 200               # менші — прибираємо завжди: розтягнуте таке фото виглядає як мило
SMALL = 500              # менші — не розтягуємо на всю ширину (сайт показує їх у справжньому розмірі)
SAME_DISTANCE = 10       # з 64 біт; менше — те саме фото
MAX_DOWNLOADS = 700      # за один запуск
RETRY_FAIL = 6 * 3600    # фото, яке не вдалося завантажити, пробуємо знову через 6 годин


def fingerprint(url: str) -> list:
    """[ширина, висота, відбиток-hex] або [0, 0, ""], якщо не вдалося (биті фото, помилка сервера)."""
    try:
        req = urllib.request.Request(urllib.parse.quote(url, safe=":/?&=%#+,;@~"), headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=12) as r:
            data = r.read(MAX_BYTES)
        im = Image.open(io.BytesIO(data))
        w, h = im.size  # розмір — із заголовка файлу, навіть якщо сам файл завеликий
        try:
            im.draft("L", (64, 64))  # швидке декодування JPEG у зменшеному розмірі
            g = im.convert("L").resize((9, 8))
        except Exception:
            return [w, h, ""]
        px = list(g.getdata())
        bits = 0
        for row in range(8):
            for col in range(8):
                bits = (bits << 1) | (px[row * 9 + col] > px[row * 9 + col + 1])
        return [w, h, f"{bits:016x}"]
    except urllib.error.HTTPError as e:
        # 404/410/5xx — фото справді бите; 403 тощо — сервер просто не пускає нас, у браузері може відкритись
        return [0, 0, "x" if e.code in (404, 410) or e.code >= 500 else ""]
    except Exception:
        return [0, 0, ""]


def distance(a: str, b: str) -> int:
    return bin(int(a, 16) ^ int(b, 16)).count("1")


def dedupe_galleries(galleries: list[list[dict]], cache: dict) -> None:
    """Змінює галереї на місці. galleries — списки {"u": адреса, "s": джерело}.
    Для кожного фото дізнаємось розмір (кеш), і:
    - биті (не відкриваються) і крихітні (< TINY) — прибираємо завжди;
    - дрібні (< MIN_WIDTH) — прибираємо, якщо є інші;
    - те саме фото в різних розмірах — лишаємо більше;
    - обкладинкою (першим) стає перше фото, ширше за SMALL, якщо таке є;
    - фото, вужчі за SMALL, позначаємо sm=1 — сайт не розтягує їх.
    Невдалі завантаження запам'ятовуємо на RETRY_FAIL секунд — щоб не пробувати щоразу (це довго)."""
    if Image is None:
        return
    now = time.time()

    def known(u: str) -> bool:
        c = cache.get(u)
        return bool(c) and (c[0] > 0 or (len(c) > 3 and now - c[3] < RETRY_FAIL))
    need = list(dict.fromkeys(im["u"] for g in galleries for im in g if not known(im["u"])))[:MAX_DOWNLOADS]
    if need:
        with cf.ThreadPoolExecutor(16) as ex:
            for url, fp in zip(need, ex.map(fingerprint, need)):
                cache[url] = fp if fp[0] else fp[:3] + [int(now)]
    for g in galleries:
        kept: list[dict] = []
        for im in g:
            w, h, fp = (cache.get(im["u"]) or [0, 0, ""])[:3]
            if (not w and fp == "x") or (w and w < TINY):
                continue  # бите або крихітне
            im["_w"], im["_fp"] = w, fp
            dup = next((k for k in kept if fp and k["_fp"] and distance(fp, k["_fp"]) <= SAME_DISTANCE), None)
            if dup is not None:
                if w > dup["_w"]:  # те саме фото, але більше — беремо його
                    dup.update(u=im["u"], s=im["s"], _w=w, _fp=fp)
                continue
            kept.append(im)
        if any(k["_w"] >= MIN_WIDTH for k in kept):  # невідомий розмір (0) — не відкидаємо
            kept = [k for k in kept if k["_w"] >= MIN_WIDTH or not k["_w"]]
        big = next((k for k in kept if k["_w"] >= SMALL), None)
        if big is not None and kept[0] is not big:
            kept.remove(big)
            kept.insert(0, big)
        for k in kept:
            if k["_w"] and k["_w"] < SMALL:
                k["sm"] = 1
            k.pop("_w", None)
            k.pop("_fp", None)
        g[:] = kept


def thumbnail(url: str, size: int = 384) -> bytes | None:
    """Зменшена копія фото (JPEG) — щоб ШІ подивився, чи є на ньому надрукований текст."""
    if Image is None:
        return None
    try:
        req = urllib.request.Request(urllib.parse.quote(url, safe=":/?&=%#+,;@~"), headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=12) as r:
            data = r.read(MAX_BYTES)
        im = Image.open(io.BytesIO(data))
        im.draft("RGB", (size, size))
        im = im.convert("RGB")
        im.thumbnail((size, size))
        out = io.BytesIO()
        im.save(out, "JPEG", quality=70)
        return out.getvalue()
    except Exception:
        return None


def thumbnails(urls: list[str]) -> dict[str, bytes]:
    res = {}
    with cf.ThreadPoolExecutor(12) as ex:
        for u, b in zip(urls, ex.map(thumbnail, urls)):
            if b:
                res[u] = b
    return res
