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
from keywords import COUNTRIES, EURASIA, STOPWORDS, TOPICS  # noqa: E402
import ai_writer  # noqa: E402
import images  # noqa: E402
from translator import Translator  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
META_CACHE_FILE = DATA / "meta_cache.json"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15"
WINDOW = timedelta(hours=24)
PER_SECTION = 15           # не більше стількох історій у кожному поєднанні «розділ × регіон»
META_LOOKUPS = 900         # скільки нових сторінок статей максимум відкрити за запуск (опис і фото)
MAX_IMAGES = 8             # скільки фото в галереї історії
TEXT_LIMIT = 700           # скільки символів опису брати від кожного джерела

TOPIC_RE = {t: re.compile(p, re.I) for t, p in TOPICS.items()}
TOPIC_IDS = ["popular", *TOPICS]   # «Популярне» — усі новини за рейтингом
REGION_IDS = ["world", "eurasia", "us", "cn", "ua"]  # Росію прибрано з регіонів (рішення користувача)
AI_CACHE_FILE = DATA / "ai_cache.json"
IMG_CACHE_FILE = DATA / "img_cache.json"
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
            full=shorten(summary, TEXT_LIMIT),
            time=published,
            image=better_image(max(images)[1]) if images else "",
        )
        items.append(it)
    return items


def fetch_one(lang: str, feed: tuple) -> tuple[str, list[dict], str | None]:
    source, url, hints = feed
    err = None
    for attempt in range(3):  # повторюємо, якщо мережа «моргнула»
        try:
            return lang, parse_feed(http_get(url, timeout=25), source, hints), None
        except Exception as e:  # стрічка може тимчасово не працювати — не страшно
            err = e
            time.sleep(2 * (attempt + 1))
    return lang, [], f"{source} ({url}): {err}"


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


def topics_of(group: list[dict]) -> list[str]:
    """Теми: тематична стрічка (підказка t:...) або ключові слова в англійському заголовку."""
    found = {h[2:] for i in group for h in i["hints"] if h.startswith("t:")}
    text = " ".join(i["en_title"] for i in group)
    text += " " + " ".join(i["summary"] for i in group if i["lang"] == "en")
    for t, rx in TOPIC_RE.items():
        if len(rx.findall(text)) >= (1 if t in ("sport", "games", "science") else 2) or rx.search(" ".join(i["en_title"] for i in group[:1])):
            found.add(t)
    return [t for t in TOPICS if t in found]


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
    # стабільний id: за найпершою публікацією — не змінюється, коли додаються нові джерела
    first = min(group, key=lambda i: (i["time"], i["url"]))
    sid = hashlib.md5(first["url"].encode()).hexdigest()[:10]
    return {
        "id": sid,
        "image": image,
        "time": latest.isoformat(),
        "cats": categorize(group),
        "topics": topics_of(group),
        "sourceCount": n_src,
        "color": PALETTE[int(sid, 16) % len(PALETTE)],
        "score": round(n_src * 3 + n_lang * 2 + len(items) * 0.5 + max(0, 24 - hours) / 4, 2),
        "_lead": lead,
        "_items": items,
    }


def build_gallery(b: dict) -> None:
    lead = b["_lead"]
    gallery, seen_img = [], set()
    for i in [lead] + sorted(b["_items"], key=lead_key):
        for u in i.get("images", []):
            k = image_key(u)
            if k not in seen_img and len(gallery) < MAX_IMAGES + 4:
                seen_img.add(k)
                gallery.append({"u": u, "s": i["source"]})
    b["_gallery"] = gallery
    if not b["image"] and gallery:
        b["image"] = gallery[0]["u"]


def select_shown(bases: list[dict]) -> list[dict]:
    """Залишаємо лише те, що буде на сайті: топ-15 за рейтингом у кожному «розділ × регіон»."""
    keep: set[str] = set()
    for t in TOPIC_IDS:
        for r in REGION_IDS:
            n = 0
            for b in bases:  # bases уже відсортовані за рейтингом
                if r in b["cats"] and (t == "popular" or t in b["topics"]):
                    keep.add(b["id"])
                    n += 1
                    if n >= PER_SECTION:
                        break
    return [b for b in bases if b["id"] in keep]


def ui_lang(code: str) -> str:
    return {"zh-TW": "zh-Hant"}.get(code, code)


def render_language(bases: list[dict], L: str, tr: Translator, ai: dict) -> tuple[list[dict], list[dict]]:
    """Готує історії для мови L.
    Текст: від ШІ (написаний українською, перекладений Google), а якщо його ще немає —
    короткий опис видання (оригінал цією мовою або переклад).
    Джерела — лише назва, заголовок і посилання."""
    plan = []
    need: dict[str, list[str]] = {}
    for b in bases:
        native = [i for i in b["_items"] if i["lang"] == L]
        lead = min(native, key=lead_key) if native else b["_lead"]
        srcs = b["_items"][:MAX_SOURCES]
        longest = max(native or b["_items"], key=lambda i: len(i["text"]))
        a = ai.get(b["id"], {}).get("a")
        plan.append((b, lead, bool(native), srcs, longest, a))
        if a:
            if L != "uk":
                need.setdefault("uk", []).extend([a["title"], a["lead"], *a["body"], *a["points"]])
        else:
            if not native:
                need.setdefault(lead["lang"], []).extend([lead["title"], lead["summary"]])
            if longest["lang"] != L:
                need.setdefault(longest["lang"], []).append(longest["text"])
        for i in srcs:
            if i["lang"] != L:
                need.setdefault(i["lang"], []).append(i["title"])
    done: dict[str, dict[str, str | None]] = {sl: tr.translate(texts, sl, L) for sl, texts in need.items()}

    def t(i_lang: str, text: str) -> str | None:
        if not text:
            return ""
        return text if i_lang == L else done.get(i_lang, {}).get(text)

    stories, details = [], []
    for b, lead, native, srcs, longest, a in plan:
        story = {k: v for k, v in b.items() if not k.startswith("_")}
        detail_extra: dict = {}
        ai_ok = False
        if a:
            parts = [t("uk", a["title"]), t("uk", a["lead"])] + [t("uk", p) for p in a["body"]] + [t("uk", p) for p in a["points"]]
            if all(parts):
                ai_ok = True
                nb = len(a["body"])
                story.update(title=parts[0], summary=parts[1], ai=True)
                detail_extra = {"ai": {"lead": parts[1], "body": parts[2:2 + nb], "points": parts[2 + nb:]}}
                if L != "uk":
                    story["aiTr"] = True  # перекладено з української
        if not ai_ok:
            long_text = t(longest["lang"], longest["text"]) or (lead["text"] if lead["lang"] == L else "") or ""
            if native:
                story.update(title=lead["title"], summary=lead["summary"])
            else:
                title, summary = t(lead["lang"], lead["title"]), t(lead["lang"], lead["summary"])
                ok = bool(title) and summary is not None
                story.update(
                    title=title if ok else lead["title"],
                    summary=summary if ok else lead["summary"],
                    orig={"lang": ui_lang(lead["lang"]), "title": lead["title"], "summary": lead["summary"], "text": longest["text"]},
                    tr=ok,
                )
                if not ok:
                    long_text = longest["text"]
            detail_extra = {"text": long_text}
        story["names"] = list(dict.fromkeys(i["source"] for i in srcs))
        stories.append(story)

        sources = [{
            "name": i["source"], "url": i["url"], "time": i["time"].isoformat(), "lang": ui_lang(i["lang"]),
            "title": (t(i["lang"], i["title"]) or i["title"]) if i["lang"] != L else i["title"],
        } for i in srcs]
        detail = {k: v for k, v in story.items() if k != "names"}
        detail.update(detail_extra, images=b["_gallery"][:MAX_IMAGES], sources=sources)
        details.append(detail)
    return stories, details


# ---------------------------------------------------------------- опис і фото зі сторінки статті
# Беремо лише те, що видання самі публікують для поширення (og:image, og:description),
# а не весь текст статті — він захищений авторським правом.

def meta_tag(page: str, names: tuple[str, ...]) -> str:
    for n in names:
        n = re.escape(n)
        for rx in (
            rf"<meta[^>]+(?:property|name)=[\"']{n}[\"'][^>]*?content=\"([^\"]*)\"",
            rf"<meta[^>]+(?:property|name)=[\"']{n}[\"'][^>]*?content='([^']*)'",
            rf"<meta[^>]+content=\"([^\"]*)\"[^>]*?(?:property|name)=[\"']{n}[\"']",
            rf"<meta[^>]+content='([^']*)'[^>]*?(?:property|name)=[\"']{n}[\"']",
        ):
            m = re.search(rx, page, re.I)
            if m and m.group(1).strip():
                return html.unescape(m.group(1)).strip()
    return ""


P_RE = re.compile(r"<p\b[^>]*>(.*?)</p>", re.S | re.I)
JUNK_RE = re.compile(r"cookie|subscribe|newsletter|©|all rights reserved|javascript|підпиш|підписат|реклам|подпис|реклам|订阅|版权", re.I)


def article_text(page: str) -> str:
    """Текст статті — лише як матеріал для ШІ (на сайті не показується)."""
    m = re.search(r"<article\b.*?</article>", page, re.S | re.I)
    scope = m.group(0) if m and len(m.group(0)) > 1500 else page
    scope = re.sub(r"<(script|style|noscript|figure|figcaption|aside|nav|footer|form|header)\b.*?</\1>", " ", scope, flags=re.S | re.I)
    paras, total = [], 0
    for p in P_RE.findall(scope):
        t = clean(p)
        if len(t) < 60 or JUNK_RE.search(t):
            continue
        paras.append(t)
        total += len(t)
        if total > 4000:
            break
    return "\n".join(paras)[:4000]


def page_meta(url: str) -> dict:
    try:
        page = http_get(url, timeout=10, limit=800_000).decode("utf-8", "ignore")
    except Exception:
        return {"i": "", "d": "", "t": "", "err": 1}
    return {
        "i": meta_tag(page, ("og:image", "twitter:image", "twitter:image:src")),
        "d": clean(meta_tag(page, ("og:description", "description", "twitter:description"))),
        "t": article_text(page),
    }


def enrich(items: list[dict], cache: dict) -> None:
    """Для кожної новини: фото й опис зі сторінки статті (з кешем)."""
    need = [i["url"] for i in items if i["url"] not in cache or cache[i["url"]].get("err") or "t" not in cache[i["url"]]][:META_LOOKUPS]
    if need:
        with cf.ThreadPoolExecutor(16) as ex:
            for url, meta in zip(need, ex.map(page_meta, need)):
                cache[url] = meta
    for i in items:
        meta = cache.get(i["url"], {})
        og_img = better_image(meta.get("i") or "")
        i["images"] = [u for u in dict.fromkeys([i["image"], og_img]) if u]
        if not i["image"] and og_img:
            i["image"] = og_img
        desc = meta.get("d") or ""
        # беремо довший з двох описів (RSS чи сторінка), якщо він не повторює заголовок
        text = desc if len(desc) > len(i["full"]) and desc.lower() != i["title"].lower() else i["full"]
        i["text"] = shorten(text, TEXT_LIMIT)
        i["article"] = meta.get("t") or ""
        if not i["summary"] and i["text"]:
            i["summary"] = shorten(i["text"])


def image_key(url: str) -> str:
    # одне й те саме фото в різних розмірах має однакову назву файлу
    name = urllib.parse.urlparse(url).path.rsplit("/", 1)[-1].lower()
    return re.sub(r"^\d+x\d+[-_]|[-_]\d+x\d+(?=\.)", "", name) or url


# ---------------------------------------------------------------- головне

def main() -> int:
    started = time.time()
    now = datetime.now(timezone.utc)
    DATA.mkdir(exist_ok=True)
    try:
        meta_cache = json.loads(META_CACHE_FILE.read_text("utf-8"))
    except (OSError, ValueError):
        meta_cache = {}
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

    # 3. групуємо, рахуємо категорії, теми й рейтинг
    try:
        ai_cache = json.loads(AI_CACHE_FILE.read_text("utf-8"))
    except (OSError, ValueError):
        ai_cache = {}
    bases = [build_base(g, now) for g in cluster(items)]
    for b in bases:  # тема, яку визначив ШІ раніше, теж враховуємо
        at = ai_cache.get("stories", {}).get(b["id"], {}).get("a", {}).get("topic")
        if at in TOPICS and at not in b["topics"]:
            b["topics"].append(at)
    bases.sort(key=lambda s: s["score"], reverse=True)
    shown = select_shown(bases)
    log(f"Історій усього: {len(bases)}, на сайті (топ-{PER_SECTION} у кожному розділі): {len(shown)}")

    # 4. опис, фото й текст статей — лише для історій, що на сайті
    shown_items = [i for b in shown for i in b["_items"]]
    enrich(shown_items, meta_cache)
    try:
        img_cache = json.loads(IMG_CACHE_FILE.read_text("utf-8"))
    except (OSError, ValueError):
        img_cache = {}
    for b in shown:
        build_gallery(b)
    images.dedupe_galleries([b["_gallery"] for b in shown], img_cache)
    for b in shown:
        if b["_gallery"]:
            b["image"] = b["_gallery"][0]["u"]

    # 5. текст від ШІ (безкоштовний Gemini)
    ai_writer.run(shown, ai_cache, log)
    ai_stories = ai_cache.get("stories", {})
    for b in shown:
        # якщо ШІ визначив тему — вона точніша за ключові слова (тематичні стрічки лишаються)
        at = ai_stories.get(b["id"], {}).get("a", {}).get("topic")
        if at:
            hinted = {h[2:] for i in b["_items"] for h in i["hints"] if h.startswith("t:")}
            b["topics"] = [t for t in TOPICS if t in hinted or t == at]

    # 6. для кожної мови сайту
    names = sorted({n for feeds in FEEDS.values() for n, _, _ in feeds})
    for L in SITE_LANGS:
        stories, details = render_language(shown, L, tr, ai_stories)
        out = {"lang": L, "generated": now.isoformat(), "sources": names, "perSection": PER_SECTION, "stories": stories}
        # окремий файл на кожну історію: data/<мова>/<id>.json (відкривається на сторінці новини)
        ddir = DATA / L
        ddir.mkdir(exist_ok=True)
        keep = set()
        for d in details:
            f = ddir / f"{d['id']}.json"
            keep.add(f.name)
            f.write_text(json.dumps(d, ensure_ascii=False, separators=(",", ":")), "utf-8")
        for old in ddir.glob("*.json"):
            if old.name not in keep:
                old.unlink()
        tmp = DATA / f"{L}.json.tmp"
        tmp.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), "utf-8")
        tmp.replace(DATA / f"{L}.json")
        n_ai = sum(1 for s in stories if s.get("ai"))
        log(f"[{L}] історій: {len(stories)}, з текстом ШІ: {n_ai}")

    all_ids = {b['id'] for b in bases}  # історії ще в межах 24 годин
    bases = shown
    counts = {t: sum(1 for s in shown if t == "popular" or t in s["topics"]) for t in TOPIC_IDS}
    log(f"На сайті за розділами: {counts}")
    log(f"Запитів до перекладача: {tr.requests}, невдалих: {tr.failed}")
    tr.save()
    urls = {i["url"] for i in items}
    meta_cache = {u: m for u, m in meta_cache.items() if u in urls}  # лише для поточних новин
    ai_writer.prune(ai_cache, all_ids)  # тексти ШІ тримаємо, поки історія свіжа
    AI_CACHE_FILE.write_text(json.dumps(ai_cache, ensure_ascii=False, separators=(",", ":")), "utf-8")
    gallery_urls = {im["u"] for b in shown for im in b.get("_gallery", [])}
    img_cache = {u: v for u, v in img_cache.items() if u in gallery_urls or u in urls}
    IMG_CACHE_FILE.write_text(json.dumps(img_cache, separators=(",", ":")), "utf-8")
    META_CACHE_FILE.write_text(json.dumps(meta_cache, ensure_ascii=False, separators=(",", ":")), "utf-8")
    old_og = DATA / "og_cache.json"
    if old_og.exists():
        old_og.unlink()
    for e in errors:
        log("Не вдалося завантажити:", e)
    log(f"Готово за {time.time() - started:.1f} с")
    return 0


if __name__ == "__main__":
    sys.exit(main())
