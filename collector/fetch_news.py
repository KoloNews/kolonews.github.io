#!/usr/bin/env python3
"""Збирач новин для сайту «Коло Новин».

Що робить:
1. Завантажує всі RSS-стрічки з feeds.py (видання 4 мовами) в одну спільну стрічку.
2. Залишає тільки новини за останні 24 години.
3. Об'єднує однакові події з різних джерел і мов в одну «історію».
4. Розкладає історії по категоріях: світ, Європа і Азія, США, Китай, Україна, Росія.
5. Для кожної мови сайту бере оригінал (якщо видання пише цією мовою) або машинний
   переклад Google; якщо переклад не вдався — залишає оригінал.
6. Записує результат у data/<мова>.json — однаковий набір історій для всіх мов.

Запуск: python3 collector/fetch_news.py
Потрібен лише Python 3, сторонні бібліотеки не потрібні.
"""

from __future__ import annotations

import concurrent.futures as cf
import hashlib
import html
import json
import math
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from feeds import FEEDS  # noqa: E402
from keywords import COUNTRIES, EURASIA, STOPWORDS  # noqa: E402
from translator import Translator  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OG_CACHE_FILE = DATA / "og_cache.json"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15"
WINDOW = timedelta(hours=24)
MAX_STORIES = 600          # скільки історій на мову зберігати
OG_LOOKUPS = 150           # скільки сторінок максимум відкрити, щоб знайти фото

COUNTRY_RE = {lang: {c: re.compile(p, re.I) for c, p in d.items()} for lang, d in COUNTRIES.items()}
EURASIA_RE = {lang: re.compile(p, re.I) for lang, p in EURASIA.items()}


def log(*a):
    print(*a, flush=True)


# ---------------------------------------------------------------- завантаження

def http_get(url: str, timeout: int = 20, limit: int | None = None) -> bytes:
    url = urllib.parse.quote(url, safe=":/?&=%#+,;@~")  # кирилиця/ієрогліфи в адресі
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read(limit) if limit else r.read()


def local(tag: str) -> str:
    """'{namespace}title' -> 'title'"""
    return tag.rsplit("}", 1)[-1].lower() if isinstance(tag, str) else ""


TAG_RE = re.compile(r"<[^>]+>")
WS_RE = re.compile(r"\s+")


def clean(text: str | None) -> str:
    if not text:
        return ""
    text = html.unescape(text)
    text = TAG_RE.sub(" ", text)
    text = html.unescape(text)
    text = text.replace("Continue reading...", "").replace("Читать далее", "")
    return WS_RE.sub(" ", text).strip()


def shorten(text: str, limit: int = 300) -> str:
    if len(text) <= limit:
        return text
    cut = text[:limit]
    # обрізаємо по кінцю речення, якщо можна
    for mark in (". ", "。", "! ", "? ", "！", "？"):
        i = cut.rfind(mark)
        if i > limit * 0.5:
            return cut[: i + 1].strip()
    i = cut.rfind(" ")
    return (cut[:i] if i > limit * 0.6 else cut).rstrip(",;:—- ") + "…"


def parse_date(s: str | None) -> datetime | None:
    if not s:
        return None
    s = s.strip()
    try:
        d = parsedate_to_datetime(s)
    except (TypeError, ValueError, IndexError):
        d = None
    if d is None:
        try:
            d = datetime.fromisoformat(s.replace("Z", "+00:00"))
        except ValueError:
            return None
    if d.tzinfo is None:
        d = d.replace(tzinfo=timezone.utc)
    return d.astimezone(timezone.utc)


IMG_IN_HTML = re.compile(r"<img[^>]+src=[\"']([^\"']+)[\"']", re.I)


PLACEHOLDER_IMG = re.compile(r"/default\.(jpe?g|png|webp)|placeholder|no[-_]?image|/logo", re.I)


def better_image(url: str) -> str:
    if PLACEHOLDER_IMG.search(url):  # заглушки з логотипом видання — не фото
        return ""
    # BBC віддає в RSS маленькі картинки 240px — беремо 800px
    url = re.sub(r"(ichef\.bbci\.co\.uk/[^ ]*?/)(\d{2,3})(/)", lambda m: m.group(1) + "800" + m.group(3), url, count=1)
    return url.replace("&amp;", "&")


def parse_feed(raw: bytes, source: str, hints: list[str]) -> list[dict]:
    root = ET.fromstring(raw)
    items = []
    for node in root.iter():
        if local(node.tag) not in ("item", "entry"):
            continue
        it = {"source": source, "hints": hints}
        title = link = desc = content = date = ""
        images: list[tuple[int, str]] = []  # (ширина, адреса)
        for ch in node.iter():
            if ch is node:
                continue
            name = local(ch.tag)
            text = (ch.text or "").strip()
            if name == "title" and not title:
                title = text
            elif name == "link" and not link:
                link = text or ch.get("href", "")
            elif name in ("description", "summary") and not desc:
                desc = text
            elif name == "encoded" and not content:
                content = text
            elif name in ("pubdate", "date", "published", "updated") and not date:
                date = text
            elif name in ("thumbnail", "content", "enclosure"):
                url = ch.get("url") or ""
                typ = (ch.get("type") or "") + (ch.get("medium") or "")
                if url and (name == "thumbnail" or "image" in typ or (not typ and re.search(r"\.(jpe?g|png|webp)", url, re.I))):
                    try:
                        w = int(ch.get("width") or 0)
                    except ValueError:
                        w = 0
                    images.append((w, url))
        if not title or not link:
            continue
        if not images:
            m = IMG_IN_HTML.search(content or desc or "")
            if m:
                images.append((0, m.group(1)))
        published = parse_date(date)
        if not published:
            continue
        summary = clean(desc) or clean(content)
        t = clean(title)
        if summary.startswith(t):
            summary = summary[len(t):].lstrip(" .:—-")
        it.update(
            title=t,
            url=link.strip(),
            summary=shorten(summary),
            time=published,
            image=better_image(max(images)[1]) if images else "",
        )
        items.append(it)
    return items


def fetch_one(lang: str, feed: tuple) -> tuple[str, list[dict], str | None]:
    source, url, hints = feed
    try:
        return lang, parse_feed(http_get(url), source, hints), None
    except Exception as e:  # стрічка може тимчасово не працювати — не страшно
        return lang, [], f"{source} ({url}): {e}"


# ---------------------------------------------------------------- групування

WORD_RE = re.compile(r"[\w'’]+", re.U)
HAN_RE = re.compile(r"[一-鿿]+")


def tokens(text: str, lang: str) -> set[str]:
    text = text.lower()
    out: set[str] = set()
    if lang == "zh":
        for run in HAN_RE.findall(text):
            out.update(run[i : i + 2] for i in range(len(run) - 1))
        text = HAN_RE.sub(" ", text)
    stop = STOPWORDS.get(lang, set())
    for w in WORD_RE.findall(text):
        if w.isdigit():
            if len(w) >= 2:
                out.add(w)
            continue
        if len(w) < 4 or w in stop:
            continue
        out.add(w[:6] if lang in ("uk", "ru", "en") else w)
    return out


def same_story(a: set[str], b: set[str], lang: str, idf: dict[str, float]) -> bool:
    """Дві новини про одне, якщо в заголовках багато спільних слів.
    Рідкісні слова (назви, імена) важать більше, ніж часті («атака», «світло»)."""
    if not a or not b:
        return False
    shared = a & b
    if len(shared) < (4 if lang == "zh" else 3):
        return False
    w = lambda s: sum(idf.get(t, 1.0) for t in s)  # noqa: E731
    return w(shared) / min(w(a), w(b)) >= 0.55


def cluster(items: list[dict]) -> list[list[dict]]:
    """Групуємо за англійськими заголовками (оригінал або переклад),
    тому одна подія з видань різними мовами стає однією історією."""
    items = sorted(items, key=lambda x: x["time"], reverse=True)
    for it in items:
        it["_tk"] = tokens(it["en_title"], "en")
    df: dict[str, int] = {}
    for it in items:
        for t in it["_tk"]:
            df[t] = df.get(t, 0) + 1
    n = max(len(items), 1)
    idf = {t: math.log((n + 1) / (c + 0.5)) for t, c in df.items()}
    groups: list[list[dict]] = []
    for it in items:
        for g in groups:
            if any(same_story(it["_tk"], other["_tk"], "en", idf) for other in g[:6]):
                g.append(it)
                break
        else:
            groups.append([it])
    return groups


# ---------------------------------------------------------------- категорії

def categorize(group: list[dict]) -> list[str]:
    """Перевіряємо і англійський заголовок, і оригінальний текст його мовою."""
    title_hit: set[str] = set()
    text_count: dict[str, int] = {}
    eur_title, eur_count = False, 0
    for i in group:
        checks = [("en", i["en_title"], i["en_title"])]
        if i["lang"] in COUNTRY_RE:  # для традиційних ієрогліфів — лише переклад
            checks.append((i["lang"], i["title"], f"{i['title']} {i['summary']}"))
        for lang, title, text in checks:
            for c, rx in COUNTRY_RE[lang].items():
                if rx.search(title):
                    title_hit.add(c)
                text_count[c] = text_count.get(c, 0) + len(rx.findall(text))
            if EURASIA_RE[lang].search(title):
                eur_title = True
            eur_count += len(EURASIA_RE[lang].findall(text))
    # країна має бути в заголовку або згадана в тексті щонайменше двічі
    found = [c for c in ("us", "cn", "ua", "ru") if c in title_hit or text_count.get(c, 0) >= 2]
    hints = {h for i in group for h in i["hints"]}
    if "us" in hints and "us" not in found:
        found.append("us")
    cats = ["world"]
    if eur_title or eur_count >= 2 or ("eurasia" in hints and not found):
        cats.append("eurasia")
    return cats + found


PALETTE = ["#2f5d8a", "#7a3b5c", "#2e6b5a", "#8a5a2b", "#4b3f8a", "#7a2f2f", "#3f6b2e", "#2b6c7a", "#6b5a2e", "#5c3f7a"]
SITE_LANGS = ("uk", "en", "zh", "ru")
MAX_SOURCES = 10


def lead_key(i: dict):
    # з описом і фото — краще; далі — вище у списку feeds.py; далі — новіше
    return (not i["summary"], not i["image"], i["prio"], -i["time"].timestamp())


def build_base(group: list[dict], now: datetime) -> dict:
    lead = min(group, key=lead_key)
    image = lead["image"] or next((i["image"] for i in group if i["image"]), "")
    latest = max(i["time"] for i in group)
    seen, items = set(), []
    for i in sorted(group, key=lambda i: i["time"], reverse=True):
        if i["url"] not in seen:
            seen.add(i["url"])
            items.append(i)
    n_src = len({i["source"] for i in items})
    n_lang = len({i["lang"].split("-")[0] for i in items})
    hours = (now - latest).total_seconds() / 3600
    sid = hashlib.md5(lead["url"].encode()).hexdigest()[:10]
    return {
        "id": sid,
        "image": image,
        "time": latest.isoformat(),
        "cats": categorize(group),
        "sourceCount": n_src,
        "color": PALETTE[int(sid, 16) % len(PALETTE)],
        "score": round(n_src * 3 + n_lang * 2 + len(items) * 0.5 + max(0, 24 - hours) / 4, 2),
        "_lead": lead,
        "_items": items,
    }


def ui_lang(code: str) -> str:
    return {"zh-TW": "zh-Hant"}.get(code, code)


def render_language(bases: list[dict], L: str, tr: Translator) -> list[dict]:
    """Готує історії для мови L: оригінал, якщо видання пише цією мовою, інакше — переклад."""
    plan = []
    need: dict[str, list[str]] = {}
    for b in bases:
        native = [i for i in b["_items"] if i["lang"] == L]
        lead = min(native, key=lead_key) if native else b["_lead"]
        srcs = b["_items"][:MAX_SOURCES]
        plan.append((b, lead, bool(native), srcs))
        if not native:
            need.setdefault(lead["lang"], []).extend([lead["title"], lead["summary"]])
        for i in srcs:
            if i["lang"] != L:
                need.setdefault(i["lang"], []).append(i["title"])
    done: dict[str, dict[str, str | None]] = {sl: tr.translate(texts, sl, L) for sl, texts in need.items()}

    def t(i_lang: str, text: str) -> str | None:
        if not text:
            return ""
        return text if i_lang == L else done.get(i_lang, {}).get(text)

    out = []
    for b, lead, native, srcs in plan:
        story = {k: v for k, v in b.items() if not k.startswith("_")}
        if native:
            story.update(title=lead["title"], summary=lead["summary"])
        else:
            title, summary = t(lead["lang"], lead["title"]), t(lead["lang"], lead["summary"])
            ok = bool(title) and (summary is not None)
            story.update(
                title=title if ok else lead["title"],
                summary=summary if ok else lead["summary"],
                orig={"lang": ui_lang(lead["lang"]), "title": lead["title"], "summary": lead["summary"]},
                tr=ok,  # False — переклад не вдався, показано оригінал
            )
        story["sources"] = [{
            "name": i["source"],
            "title": t(i["lang"], i["title"]) or i["title"],
            "url": i["url"],
            "time": i["time"].isoformat(),
            "lang": ui_lang(i["lang"]),
        } for i in srcs]
        out.append(story)
    return out


# ---------------------------------------------------------------- фото зі сторінки

OG_RE = re.compile(r"<meta[^>]+(?:property|name)=[\"'](?:og:image|twitter:image)[\"'][^>]+content=[\"']([^\"']+)", re.I)
OG_RE2 = re.compile(r"<meta[^>]+content=[\"']([^\"']+)[\"'][^>]+(?:property|name)=[\"'](?:og:image|twitter:image)", re.I)


def og_image(url: str) -> str:
    try:
        page = http_get(url, timeout=10, limit=400_000).decode("utf-8", "ignore")
    except Exception:
        return ""
    m = OG_RE.search(page) or OG_RE2.search(page)
    return html.unescape(m.group(1)).strip() if m else ""


def fill_images(stories: list[dict], cache: dict) -> None:
    todo = [s for s in stories if not s["image"]][:OG_LOOKUPS]
    need = [s["_items"][0]["url"] for s in todo if s["_items"][0]["url"] not in cache]
    if need:
        with cf.ThreadPoolExecutor(12) as ex:
            for url, img in zip(need, ex.map(og_image, need)):
                cache[url] = img
    for s in todo:
        for i in s["_items"]:
            if cache.get(i["url"]):
                s["image"] = better_image(cache[i["url"]])
                break


# ---------------------------------------------------------------- головне

def main() -> int:
    started = time.time()
    now = datetime.now(timezone.utc)
    DATA.mkdir(exist_ok=True)
    try:
        og_cache = json.loads(OG_CACHE_FILE.read_text("utf-8"))
    except (OSError, ValueError):
        og_cache = {}
    tr = Translator(DATA / "translations.json")

    # 1. завантажуємо всі стрічки всіх мов
    jobs = [(lang, f) for lang, feeds in FEEDS.items() for f in feeds]
    prio = {}
    for lang, feeds in FEEDS.items():
        for idx, (name, _, _) in enumerate(feeds):
            prio.setdefault(name, idx)
    items, errors, seen = [], [], set()
    with cf.ThreadPoolExecutor(16) as ex:
        for lang, got, err in ex.map(lambda j: fetch_one(*j), jobs):
            if err:
                errors.append(err)
            for it in got:
                if now - it["time"] > WINDOW or it["time"] - now > timedelta(hours=2) or it["url"] in seen:
                    continue
                seen.add(it["url"])
                it["lang"] = "zh-TW" if "trad" in it["hints"] else lang
                it["prio"] = prio.get(it["source"], 99)
                items.append(it)
    log(f"Новин за 24 год з усіх джерел: {len(items)}")

    # 2. англійські заголовки — щоб знайти однакові події різними мовами
    by_lang: dict[str, list[dict]] = {}
    for it in items:
        by_lang.setdefault(it["lang"], []).append(it)
    for sl, group in by_lang.items():
        res = tr.translate([i["title"] for i in group], sl, "en")
        for i in group:
            i["en_title"] = res.get(i["title"]) or i["title"]

    # 3. групуємо, рахуємо категорії й важливість
    bases = [build_base(g, now) for g in cluster(items)]
    bases.sort(key=lambda s: s["score"], reverse=True)
    bases = bases[:MAX_STORIES]
    fill_images(bases, og_cache)

    # 4. для кожної мови сайту — оригінал або переклад
    names = sorted({n for feeds in FEEDS.values() for n, _, _ in feeds})
    for L in SITE_LANGS:
        stories = render_language(bases, L, tr)
        out = {"lang": L, "generated": now.isoformat(), "sources": names, "stories": stories}
        tmp = DATA / f"{L}.json.tmp"
        tmp.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), "utf-8")
        tmp.replace(DATA / f"{L}.json")
        native = sum(1 for s in stories if "orig" not in s)
        failed = sum(1 for s in stories if s.get("tr") is False)
        log(f"[{L}] історій: {len(stories)} (оригінал: {native}, переклад: {len(stories) - native - failed}, без перекладу: {failed})")

    counts = {c: sum(c in s["cats"] for s in bases) for c in ["world", "eurasia", "us", "cn", "ua", "ru"]}
    log(f"По категоріях: {counts}")
    log(f"Запитів до перекладача: {tr.requests}, невдалих: {tr.failed}")
    tr.save()
    if len(og_cache) > 3000:
        og_cache = dict(list(og_cache.items())[-3000:])
    OG_CACHE_FILE.write_text(json.dumps(og_cache, ensure_ascii=False), "utf-8")
    for e in errors:
        log("Не вдалося завантажити:", e)
    log(f"Готово за {time.time() - started:.1f} с")
    return 0


if __name__ == "__main__":
    sys.exit(main())
