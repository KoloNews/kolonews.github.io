"""Текст новини від ШІ — безкоштовний Google Gemini (тариф Free).

ШІ читає матеріали кількох видань і пише ВЛАСНИЙ текст українською
(без копіювання речень), потім Google Translate перекладає його на інші мови сайту.

Ключ (безкоштовний, з Google AI Studio):
- на GitHub — секрет GEMINI_API_KEY;
- на Mac — файл ~/.config/kolo-novyn/gemini_key (або змінна GEMINI_API_KEY).
Без ключа сайт працює як раніше, просто без тексту від ШІ.

Безкоштовний тариф має ліміти (орієнтовно 15 запитів/хв і ~1000/день),
тому рахуємо запити й зупиняємось заздалегідь.
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
MODEL = os.environ.get("GEMINI_MODEL", "gemini-flash-lite-latest")
PER_RUN = int(os.environ.get("AI_PER_RUN", "12"))       # 72 запуски на день × 12 = до 864
DAILY_LIMIT = int(os.environ.get("AI_DAILY_LIMIT", "900"))
PAUSE = 4.5                                              # секунд між запитами (≤ 15 за хвилину)
TOPICS = ["science", "tech", "crime", "sport", "economy", "games", "other"]

SYSTEM = """Ти — редактор новинного сайту «Коло Новин». Тобі дають матеріали кількох видань про одну подію.
Напиши власний інформаційний текст українською мовою.

Правила:
- Лише факти з наданих матеріалів. Нічого не вигадуй і не додавай від себе. Якщо дані у виданнях різняться — так і напиши, назвавши видання.
- Пиши своїми словами, не копіюй речення з матеріалів.
- Нейтральний тон, без оцінок, емоцій і закликів.
- title: короткий точний заголовок.
- lead: 1–2 речення — головне про подію.
- body: від 3 до 6 абзаців: що сталося, подробиці, контекст, реакції, що буде далі — тільки те, що є в матеріалах. Якщо матеріалів мало, пиши коротше, але нічого не вигадуй.
- points: 3–5 ключових фактів коротко.
- topic: одна тема з переліку (science — наука, tech — технології, crime — кримінал, sport — спорт, economy — економіка, games — відеоігри, other — інше)."""

SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "title": {"type": "STRING"},
        "lead": {"type": "STRING"},
        "body": {"type": "ARRAY", "items": {"type": "STRING"}},
        "points": {"type": "ARRAY", "items": {"type": "STRING"}},
        "topic": {"type": "STRING", "enum": TOPICS},
    },
    "required": ["title", "lead", "body", "points", "topic"],
}


def api_key() -> str:
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not key:
        f = Path.home() / ".config" / "kolo-novyn" / "gemini_key"
        if f.exists():
            key = f.read_text("utf-8").strip()
    return key


class QuotaExceeded(Exception):
    pass


def generate(material: str, key: str) -> dict | None:
    body = {
        "systemInstruction": {"parts": [{"text": SYSTEM}]},
        "contents": [{"role": "user", "parts": [{"text": material}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": SCHEMA,
            "temperature": 0.3,
            "maxOutputTokens": 3000,
        },
    }
    req = urllib.request.Request(
        ENDPOINT.format(model=MODEL),
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "x-goog-api-key": key},
    )
    data = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                data = json.loads(r.read().decode("utf-8"))
            break
        except urllib.error.HTTPError as e:
            if e.code == 429:
                raise QuotaExceeded() from e
            if e.code in (500, 502, 503, 504) and attempt < 2:
                time.sleep(8 * (attempt + 1))  # модель тимчасово перевантажена — чекаємо й пробуємо ще
                continue
            detail = e.read()[:200].decode("utf-8", "ignore")
            print(f"ШІ: помилка {e.code}: {detail}", flush=True)
            return None
        except Exception as e:
            print(f"ШІ: помилка з'єднання: {e}", flush=True)
            return None
    if data is None:
        return None
    try:
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        out = json.loads(text)
    except (KeyError, IndexError, ValueError):
        return None
    body_ = [p.strip() for p in out.get("body", []) if isinstance(p, str) and p.strip()]
    if not out.get("title") or not out.get("lead") or not body_:
        return None
    return {
        "title": out["title"].strip(),
        "lead": out["lead"].strip(),
        "body": body_[:8],
        "points": [p.strip() for p in out.get("points", []) if isinstance(p, str) and p.strip()][:6],
        "topic": out.get("topic") if out.get("topic") in TOPICS else "other",
    }


def material_for(items: list[dict], lang_names: dict[str, str]) -> str:
    """Матеріали для ШІ: заголовок, опис і текст статті кожного видання (до ~12 000 символів)."""
    parts, total = [], 0
    for n, i in enumerate(items[:6], 1):
        text = i.get("article") or i.get("text") or i.get("summary") or ""
        text = text[:3000]
        block = f"Видання {n}: {i['source']} (мова: {lang_names.get(i['lang'], i['lang'])})\nЗаголовок: {i['title']}\n{text}"
        if total + len(block) > 12000 and parts:
            break
        parts.append(block)
        total += len(block)
    return "\n\n---\n\n".join(parts)


def run(bases: list[dict], cache: dict, log) -> None:
    """Пише тексти для найважливіших історій без тексту. cache — data/ai_cache.json."""
    key = api_key()
    if not key:
        log("ШІ: ключ Gemini не знайдено — тексти від ШІ пропущено")
        return
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    state = cache.setdefault("_state", {})
    if state.get("day") != today:
        state.update(day=today, count=0)
    stories = cache.setdefault("stories", {})
    names = {"uk": "українська", "en": "англійська", "ru": "російська", "zh": "китайська", "zh-TW": "китайська"}

    def need(b) -> int:
        old = stories.get(b["id"])
        if not old:
            return 2
        return 1 if b["sourceCount"] >= old.get("n", 0) + 2 else 0  # з'явилось багато нових джерел

    todo = sorted((b for b in bases if need(b)), key=lambda b: (-need(b), -b["score"]))
    done = 0
    for b in todo:
        if done >= PER_RUN or state["count"] >= DAILY_LIMIT:
            break
        material = material_for(b["_items"], names)
        if len(material) < 200:
            continue
        try:
            res = generate(material, key)
        except QuotaExceeded:
            log("ШІ: досягнуто ліміту безкоштовного тарифу — продовжимо в наступному запуску")
            break
        state["count"] += 1
        done += 1
        if res:
            stories[b["id"]] = {"n": b["sourceCount"], "d": today, "a": res}
        time.sleep(PAUSE)
    log(f"ШІ: написано текстів у цьому запуску: {done}, сьогодні всього: {state['count']}/{DAILY_LIMIT}")


def prune(cache: dict, keep_ids: set[str]) -> None:
    st = cache.get("stories", {})
    for sid in list(st):
        if sid not in keep_ids:
            del st[sid]
