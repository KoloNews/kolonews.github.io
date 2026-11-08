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
import urllib.parse
import urllib.request

try:
    from PIL import Image
except ImportError:  # без Pillow просто не порівнюємо
    Image = None

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15"
MAX_BYTES = 3_000_000
MIN_WIDTH = 360          # менші картинки — найчастіше логотипи чи іконки
SAME_DISTANCE = 10       # з 64 біт; менше — те саме фото
MAX_DOWNLOADS = 700      # за один запуск


def fingerprint(url: str) -> list:
    """[ширина, висота, відбиток-hex] або [0, 0, ""], якщо не вдалося."""
    try:
        req = urllib.request.Request(urllib.parse.quote(url, safe=":/?&=%#+,;@~"), headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=12) as r:
            data = r.read(MAX_BYTES)
        im = Image.open(io.BytesIO(data))
        w, h = im.size
        im.draft("L", (64, 64))  # швидке декодування JPEG у зменшеному розмірі
        g = im.convert("L").resize((9, 8))
        px = list(g.getdata())
        bits = 0
        for row in range(8):
            for col in range(8):
                bits = (bits << 1) | (px[row * 9 + col] > px[row * 9 + col + 1])
        return [w, h, f"{bits:016x}"]
    except Exception:
        return [0, 0, ""]


def distance(a: str, b: str) -> int:
    return bin(int(a, 16) ^ int(b, 16)).count("1")


def dedupe_galleries(galleries: list[list[dict]], cache: dict) -> None:
    """Змінює галереї на місці. galleries — списки {"u": адреса, "s": джерело}."""
    if Image is None:
        return
    need = []
    for g in galleries:
        if len(g) < 2:
            continue
        need += [im["u"] for im in g if im["u"] not in cache]
    need = list(dict.fromkeys(need))[:MAX_DOWNLOADS]
    if need:
        with cf.ThreadPoolExecutor(16) as ex:
            for url, fp in zip(need, ex.map(fingerprint, need)):
                cache[url] = fp
    for g in galleries:
        if len(g) < 2:
            continue
        kept: list[dict] = []
        for im in g:
            w, h, fp = cache.get(im["u"], [0, 0, ""])
            if fp and w and w < MIN_WIDTH:
                continue  # іконка/логотип
            if fp and any(k.get("_fp") and distance(fp, k["_fp"]) <= SAME_DISTANCE for k in kept):
                continue  # те саме фото вже є
            im["_fp"] = fp
            kept.append(im)
        for im in kept:
            im.pop("_fp", None)
        g[:] = kept
