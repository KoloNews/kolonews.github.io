#!/usr/bin/env python3
"""Автоперевірка якості «Коло Новин»: шукає типові проблеми в готових даних сайту.

Запуск:
  python3 collector/qa.py            — перевіряє локальні data/ (після збирача)
  python3 collector/qa.py --live     — завантажує дані з https://kolonews.github.io і перевіряє їх
Збирач викликає check() наприкінці кожного оновлення й пише підсумок у журнал.
"""
from __future__ import annotations

import concurrent.futures as cf
import io
import json
import re
import sys
import urllib.request
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
SITE = "https://kolonews.github.io"
LANGS = ["uk", "en", "zh", "ru"]
TOPICS = ["tech", "economy", "crime", "sport", "science", "games", "crypto"]
REGIONS = ["world", "eurasia", "us", "cn", "ua"]
WORLD_ONLY = {"science", "games", "crypto"}
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15"

SMALL_IMG = 500          # ширше за стільки — фото виглядає нормально на всю ширину
SHORT_TEXT = 400         # символів у тексті ШІ — менше вже «дуже коротко»
JUNK = re.compile(
    r"читати далі|читать далее|read more|continue reading|阅读全文|editorial process|full profile|"
    r"subscribe to|підпишіться|подпишитесь|enable javascript|увімкніть javascript|включите javascript|"
    r"&amp;|&quot;|&#\d+;|<[a-z/][^>]*>|\[…\]|\[\.\.\.\]",
    re.I)
CJK = re.compile(r"[぀-ヿ㐀-鿿]")
CYR = re.compile(r"[а-яіїєґё]", re.I)
LAT = re.compile(r"[a-z]", re.I)


def _get(url: str, timeout: int = 20) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def load(live: bool) -> tuple[dict, dict]:
    """Повертає ({мова: список історій}, {мова: {id: деталі}})."""
    lists, details = {}, {}
    for L in LANGS:
        if live:
            lists[L] = json.loads(_get(f"{SITE}/data/{L}.json"))["stories"]
        else:
            lists[L] = json.loads((DATA / f"{L}.json").read_text("utf-8"))["stories"]
    ids = [s["id"] for s in lists["uk"]]

    def det(args):
        L, sid = args
        try:
            if live:
                return L, sid, json.loads(_get(f"{SITE}/data/{L}/{sid}.json"))
            return L, sid, json.loads((DATA / L / f"{sid}.json").read_text("utf-8"))
        except Exception:
            return L, sid, None
    jobs = [(L, sid) for L in LANGS for sid in ids]
    with cf.ThreadPoolExecutor(24) as ex:
        for L, sid, d in ex.map(det, jobs):
            details.setdefault(L, {})[sid] = d
    return lists, details


def image_sizes(urls: list[str], cache: dict | None) -> dict[str, tuple[int, int]]:
    """Ширина й висота фото: з кешу збирача (img_cache) або завантаживши (лише заголовок файлу)."""
    out: dict[str, tuple[int, int]] = {}
    need = []
    for u in urls:
        c = (cache or {}).get(u)
        if c:  # уже перевірене збирачем (0 — не вдалося завантажити)
            out[u] = (c[0], c[1])
        else:
            need.append(u)
    try:
        from PIL import Image
    except ImportError:
        return out

    def size(u):
        try:
            return u, Image.open(io.BytesIO(_get(u, 12)[:600_000])).size
        except Exception:
            return u, (0, 0)
    with cf.ThreadPoolExecutor(16) as ex:
        for u, wh in ex.map(size, need):
            out[u] = wh
    return out


def check(lists: dict, details: dict, img_cache: dict | None = None, now: datetime | None = None) -> dict[str, list[str]]:
    now = now or datetime.now(timezone.utc)
    P: dict[str, list[str]] = {}

    def add(kind: str, msg: str) -> None:
        P.setdefault(kind, []).append(msg)

    uk = lists["uk"]
    by_id = {s["id"]: s for s in uk}
    t = lambda s: s["title"][:60]

    # 1. фото: розмір, однакові фото в різних новинах, фото з текстом
    urls = [s["image"] for s in uk if s.get("image")]
    for s in uk:
        d = details["uk"].get(s["id"]) or {}
        urls += [im["u"] for im in d.get("images", [])]
    sizes = image_sizes(list(dict.fromkeys(urls)), img_cache)
    for s in uk:
        d = details["uk"].get(s["id"]) or {}
        if not s.get("image"):
            add("без фото", t(s))
        else:
            w, h = sizes.get(s["image"], (0, 0))
            if not w:
                add("фото не відкривається", f"{t(s)} — {s['image'][:90]}")
            elif w < SMALL_IMG and not s.get("imageSmall"):
                add("маленьке фото розтягнуто", f"{w}×{h} {t(s)} — {s['image'][:90]}")
        for im in d.get("images", [])[1:]:
            w, h = sizes.get(im["u"], (0, 0))
            if w and w < SMALL_IMG and not im.get("sm"):
                add("маленьке фото в галереї", f"{w}×{h} {t(s)}")
        if s.get("imageText") and len(d.get("images", [])) > 1:
            add("фото з текстом, хоча є інші", t(s))
    for u, n in Counter(s["image"] for s in uk if s.get("image")).items():
        if n > 1:
            add("одне фото в кількох новинах", f"{n}× {u[:90]}")

    # 2. тексти: наявність, довжина, мова, сміття
    for L in LANGS:
        for s in lists[L]:
            d = details[L].get(s["id"])
            if d is None:
                add("немає файлу новини", f"[{L}] {s['id']}")
                continue
            ai = d.get("ai") or {}
            body = " ".join([ai.get("lead", "")] + ai.get("body", []) + ai.get("points", []))
            if not ai:
                add("без тексту ШІ", f"[{L}] {t(s)}")
            elif len(body) < (SHORT_TEXT // 2.5 if L == "zh" else SHORT_TEXT):  # 1 ієрогліф ≈ 2–3 літери
                add("дуже короткий текст", f"[{L}] {len(body)} симв. {t(s)}")
            whole = f"{s['title']} {s.get('summary', '')} {body}"
            if JUNK.search(whole):
                add("сміття в тексті", f"[{L}] «{JUNK.search(whole).group(0)}» {t(s)}")
            letters = len(CYR.findall(whole)) + len(LAT.findall(whole)) + len(CJK.findall(whole)) or 1
            if L == "uk" and (CJK.search(whole) or len(CYR.findall(whole)) / letters < 0.6):
                add("не українською", f"{t(s)}")
            if L == "en" and len(CYR.findall(whole)) / letters > 0.1:
                add("не перекладено (en)", t(s))
            if L == "zh" and len(CJK.findall(whole)) / letters < 0.3:
                add("не перекладено (zh)", t(s))
            # окремі назви («Дія», «Київ») — нормально; кілька українських слів — переклад не вдався
            if L == "ru" and len(re.findall(r"\w*[іїєґ]\w*", whole, re.I)) >= 3:
                add("українські літери в російському", t(s))

    # 3. дублі: дуже схожі заголовки
    def toks(x: str) -> set[str]:
        return {w for w in re.findall(r"\w{4,}", x.lower())}
    seen = [(s, toks(s["title"])) for s in lists["en"]]
    for i, (a, ta) in enumerate(seen):
        for b, tb in seen[i + 1:]:
            if ta and tb and len(ta & tb) / min(len(ta), len(tb)) >= 0.7:
                add("схожі заголовки (можливий дубль)", f"{a['title'][:55]} ‖ {b['title'][:55]}")

    # 4. час, розділи
    for s in uk:
        age = now - datetime.fromisoformat(s["time"])
        if age > timedelta(hours=24, minutes=30):
            add("старше 24 годин", t(s))
        if len(s.get("topics") or []) > 1:
            add("новина в кількох розділах", t(s))
    for tp in TOPICS:
        for r in (["world"] if tp in WORLD_ONLY else REGIONS):
            n = sum(1 for s in uk if r in s["cats"] and tp in (s.get("topics") or []))
            if n < 5:
                add("мало новин у розділі", f"{tp}/{r}: {n}")
    for r in REGIONS:
        n = sum(1 for s in uk if r in (s.get("pop") or s["cats"]))
        if n < 10:
            add("мало новин у «Популярному»", f"{r}: {n}")

    # 5. джерела
    for s in uk:
        d = details["uk"].get(s["id"]) or {}
        if not [x for x in d.get("sources", []) if x.get("url", "#") != "#"]:
            add("без посилань на джерела", t(s))
    return P


def report(P: dict[str, list[str]], log=print, limit: int = 6) -> int:
    total = sum(len(v) for v in P.values())
    log(f"Перевірка якості: проблем {total}" + ("" if total else " — усе гаразд"))
    for kind, items in sorted(P.items(), key=lambda kv: -len(kv[1])):
        log(f"  • {kind}: {len(items)}")
        for m in items[:limit]:
            log(f"      {m}")
    return total


if __name__ == "__main__":
    live = "--live" in sys.argv
    lists, details = load(live)
    cache = None
    if not live:
        try:
            cache = json.loads((DATA / "img_cache.json").read_text("utf-8"))
        except (OSError, ValueError):
            cache = None
    report(check(lists, details, cache), limit=40 if "--all" in sys.argv else 6)
