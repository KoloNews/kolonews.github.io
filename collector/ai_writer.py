"""ШІ для «Коло Новин» — безкоштовний Google Gemini (тариф Free).

Дві задачі:
1. classify — розкладає історії по розділах і регіонах (40 заголовків за один запит).
2. run — пише ВЛАСНИЙ текст новини українською на основі матеріалів кількох видань
   (без копіювання речень); Google Translate потім перекладає його на інші мови сайту.

Ключ (безкоштовний, з Google AI Studio):
- на GitHub — секрет GEMINI_API_KEY;
- на Mac — файл ~/.config/kolo-novyn/gemini_key (або змінна GEMINI_API_KEY).
Без ключа сайт працює як раніше: розділи за ключовими словами, без тексту від ШІ.

Безкоштовний тариф має ліміти (орієнтовно 15 запитів/хв і ~1000/день),
тому рахуємо запити й зупиняємось заздалегідь.
"""

from __future__ import annotations

import base64
import json
import os
import re
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
# Черга моделей: денний ліміт у Google рахується окремо для кожної моделі.
# Коли в моделі закінчився денний ліміт (або вона недоступна) — переходимо до наступної.
MODELS = [m.strip() for m in os.environ.get(
    "GEMINI_MODELS", "gemini-flash-lite-latest,gemini-3.1-flash-lite,gemini-flash-latest,gemini-3.5-flash,gemma-4-26b-a4b-it").split(",") if m.strip()]
MODEL = MODELS[0]
_dead: set[str] = set()      # моделі, недоступні сьогодні (зберігаються в кеші, щоб не смикати їх щоразу)
_state: dict = {}
PER_RUN = int(os.environ.get("AI_PER_RUN", "12"))        # текстів за один запуск
CLS_PER_RUN = int(os.environ.get("AI_CLS_PER_RUN", "3"))   # запитів на розкладання за запуск (по 40 історій)
# Безкоштовних запитів на добу всього ~900 (усі моделі разом). Допоміжні задачі (розділи, злиття,
# перевірка розділів і фото) отримують не більше AUX_DAILY, решта — на тексти новин.
AUX_DAILY = int(os.environ.get("AI_AUX_DAILY", "350"))
DAILY_LIMIT = int(os.environ.get("AI_DAILY_LIMIT", "2500"))  # наш запобіжник на всі моделі разом
PAUSE = 4.5                                               # секунд між запитами (≤ 15 за хвилину)
TOPICS = ["tech", "economy", "crime", "sport", "science", "games", "crypto"]
REGIONS = ["eurasia", "us", "cn", "ua"]
CLS_BATCH = 40

SYSTEM = """Ти — редактор новинного сайту «Коло Новин». Тобі дають матеріали кількох видань про одну подію.
Напиши власний інформаційний текст українською мовою.

Правила:
- Лише факти з наданих матеріалів. Нічого не вигадуй і не додавай від себе. Якщо дані у виданнях різняться — так і напиши, назвавши видання.
- Пиши своїми словами, не копіюй речення з матеріалів.
- Нейтральний тон, без оцінок, емоцій і закликів.
- Увесь текст — ЛИШЕ українською. Імена, прізвища, назви компаній і місць пиши українськими літерами в усталеній формі
  (黄仁勋 → Дженсен Хуанг, 习近平 → Сі Цзіньпін, 台湾 → Тайвань). Жодних ієрогліфів чи інших писемностей у тексті.
  Латиницею можна лише назви брендів і продуктів (Nvidia, iPhone, PlayStation).
- title: короткий точний заголовок.
- lead: 1–2 речення — головне про подію.
- body: від 3 до 6 абзаців: що сталося, подробиці, контекст, реакції, що буде далі — тільки те, що є в матеріалах. Якщо матеріалів мало, пиши коротше, але нічого не вигадуй.
- points: 3–5 ключових фактів коротко."""

SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "title": {"type": "STRING"},
        "lead": {"type": "STRING"},
        "body": {"type": "ARRAY", "items": {"type": "STRING"}},
        "points": {"type": "ARRAY", "items": {"type": "STRING"}},
    },
    "required": ["title", "lead", "body", "points"],
}

CLS_SYSTEM = """Ти розкладаєш новини по розділах і регіонах новинного сайту. Для кожної новини (номер, заголовок, уривок) визнач:

topics — розділи, до яких новина СПРАВДІ належить (0, 1 або 2; якщо жоден не підходить — порожній список):
- tech — технології: ШІ, гаджети, смартфони, комп'ютери, софт, інтернет, соцмережі, кібербезпека, техкомпанії, космічні технології та запуски.
- economy — економіка: ринки, ціни, інфляція, бюджет, податки, торгівля й мита, банки, компанії та їхні прибутки, енергетичні ринки, робочі місця.
- crime — кримінал: злочини, вбивства, стрілянини, теракти, шахрайство, корупція, арешти, суди й вироки. НЕ війна і НЕ бойові дії, НЕ обстріли армією.
- sport — спорт: змагання, спортсмени, клуби, трансфери, спортивні організації. Політична подія за участі спортивної особи — не спорт.
- science — наука: наукові дослідження й відкриття, космос і астрономія, медицина як наука, клімат як наука, природа, археологія.
- games — відеоігри, ігрові консолі, кіберспорт (не настільні ігри і не Олімпійські ігри).
- crypto — криптовалюти, біткоїн, блокчейн, криптобіржі, NFT, регулювання криптоактивів.
Війна, політика, дипломатія, вибори, катастрофи, погода, культура, шоу-бізнес — це не розділи вище, для них topics порожній (вони й так є в «Популярному»).

regions — кого новина ПРЯМО стосується (може бути порожнім, якщо це глобальна тема або інші частини світу):
- ua — Україна (зокрема війна Росії проти України, українські міста, політики, компанії).
- us — США.
- cn — Китай (включно з Гонконгом).
- eurasia — інші країни Європи та Азії, ЄС, Близький Схід (окрім України, Росії й Китаю).
Новини лише про Росію не позначай жодним регіоном."""

CLS_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "items": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "i": {"type": "INTEGER"},
                    "topics": {"type": "ARRAY", "items": {"type": "STRING", "enum": TOPICS}},
                    "regions": {"type": "ARRAY", "items": {"type": "STRING", "enum": REGIONS}},
                },
                "required": ["i", "topics", "regions"],
            },
        }
    },
    "required": ["items"],
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


def call(system: str, text: str, schema: dict, key: str, max_tokens: int = 3000, parts: list | None = None) -> dict | None:
    """Запит до Gemini. Перебирає моделі з черги MODELS, поки якась не відповість."""
    body = {
        "systemInstruction": {"parts": [{"text": system}]},
        "contents": [{"role": "user", "parts": (parts or []) + [{"text": text}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": schema,
            "temperature": 0.2,
            "maxOutputTokens": max_tokens,
        },
    }
    payload = json.dumps(body).encode()
    # Gemma не підтримує systemInstruction і JSON-схему — просимо JSON прямо в тексті
    gemma_body = {
        "contents": [{"role": "user", "parts": (parts or []) + [{"text":
            f"{system}\n\nВідповідай ЛИШЕ одним JSON-об'єктом за цією схемою (без пояснень і без ```):\n"
            f"{json.dumps(schema, ensure_ascii=False)}\n\n{text}"}]}],
        "generationConfig": {"temperature": 0.2, "maxOutputTokens": max(max_tokens, 4096)},
    }
    gemma_payload = json.dumps(gemma_body).encode()
    for model in MODELS:
        if model in _dead:
            continue
        is_gemma = model.startswith("gemma")
        req = urllib.request.Request(
            ENDPOINT.format(model=model), data=gemma_payload if is_gemma else payload,
            headers={"Content-Type": "application/json", "x-goog-api-key": key},
        )
        data, switch = None, False
        for attempt in range(3):
            try:
                with urllib.request.urlopen(req, timeout=90) as r:
                    data = json.loads(r.read().decode("utf-8"))
                break
            except urllib.error.HTTPError as e:
                raw = e.read().decode("utf-8", "ignore")
                try:
                    err = json.loads(raw).get("error", {})
                except ValueError:
                    err = {}
                if e.code == 429:
                    ids = [v.get("quotaId") or "" for d in err.get("details", []) for v in d.get("violations", [])]
                    wait = 0.0
                    for d in err.get("details", []):
                        if d.get("retryDelay"):
                            wait = float(str(d["retryDelay"]).rstrip("s") or 0)
                    if any("PerDay" in q for q in ids) or wait > 60 or attempt == 2:
                        print(f"ШІ: у моделі {model} закінчився ліміт ({', '.join(ids) or 'без деталей'}) — переходжу до наступної", flush=True)
                        switch = True
                        break
                    time.sleep(max(wait, 20) + 2)  # тимчасове обмеження «за хвилину»
                    continue
                if e.code in (400, 403, 404):  # модель недоступна для цього ключа
                    print(f"ШІ: модель {model} недоступна ({e.code}) — переходжу до наступної", flush=True)
                    switch = True
                    break
                if e.code in (500, 502, 503, 504) and attempt < 2:
                    time.sleep(8 * (attempt + 1))  # модель тимчасово перевантажена
                    continue
                print(f"ШІ: помилка {e.code} ({model}): {raw[:200]}", flush=True)
                return None
            except Exception as e:
                if attempt < 2:
                    time.sleep(5)
                    continue
                print(f"ШІ: помилка з'єднання ({model}): {e}", flush=True)
                return None
        if switch:
            _dead.add(model)
            if _state is not None:
                _state.setdefault("dead", [])
                if model not in _state["dead"]:
                    _state["dead"].append(model)
            continue
        if data is None:
            return None
        try:
            txt = data["candidates"][0]["content"]["parts"][-1]["text"]
            if is_gemma:  # беремо JSON між першою «{» і останньою «}»
                txt = txt[txt.index("{"):txt.rindex("}") + 1]
            return json.loads(txt)
        except (KeyError, IndexError, ValueError):
            return None
    raise QuotaExceeded()


def _aux_ok(state: dict) -> bool:
    """Чи лишився денний бюджет на допоміжні задачі (щоб основне — тексти — не залишились без ліміту)."""
    return state.get("aux", 0) < AUX_DAILY and state["count"] < DAILY_LIMIT


def _aux_used(state: dict) -> None:
    state["count"] += 1
    state["aux"] = state.get("aux", 0) + 1


FOREIGN = re.compile(r"[\u3040-\u30ff\u3400-\u9fff\uac00-\ud7af\uf900-\ufaff]")  # ієрогліфи, кана, хангиль
CYR = re.compile(r"[а-яіїєґ]", re.I)


def is_ukrainian(res: dict) -> bool:
    """Текст ШІ придатний: без ієрогліфів і переважно кирилицею."""
    blob = " ".join([res["title"], res["lead"], *res["body"], *res["points"]])
    letters = [c for c in blob if c.isalpha()]
    return not FOREIGN.search(blob) and len(CYR.findall(blob)) >= 0.6 * max(1, len(letters))


def generate(material: str, key: str) -> dict | None:
    out = call(SYSTEM, material, SCHEMA, key)
    if not out:
        return None
    body_ = [p.strip() for p in out.get("body", []) if isinstance(p, str) and p.strip()]
    if not out.get("title") or not out.get("lead") or not body_:
        return None
    return {
        "title": out["title"].strip(),
        "lead": out["lead"].strip(),
        "body": body_[:8],
        "points": [p.strip() for p in out.get("points", []) if isinstance(p, str) and p.strip()][:6],
    }


def material_for(items: list[dict], lang_names: dict[str, str]) -> str:
    """Матеріали для ШІ: до 6 різних видань, спершу ті, де є текст статті (до ~12 000 символів)."""
    chosen, seen = [], set()
    for i in sorted(items, key=lambda i: (not i.get("article"), -len(i.get("article") or i.get("text") or ""))):
        if i["source"] in seen:
            continue
        seen.add(i["source"])
        chosen.append(i)
        if len(chosen) >= 6:
            break
    parts, total = [], 0
    for n, i in enumerate(chosen, 1):
        text = (i.get("article") or i.get("text") or i.get("summary") or "")[:3000]
        block = f"Видання {n}: {i['source']} (мова: {lang_names.get(i['lang'], i['lang'])})\nЗаголовок: {i['title']}\n{text}"
        if total + len(block) > 12000 and parts:
            break
        parts.append(block)
        total += len(block)
    return "\n\n---\n\n".join(parts)


def _budget(cache: dict) -> dict:
    global _state
    # день рахуємо за тихоокеанським часом (UTC−8) — тоді Google скидає безкоштовні ліміти
    today = (datetime.now(timezone.utc) - timedelta(hours=8)).strftime("%Y-%m-%d")
    state = cache.setdefault("_state", {})
    if state.get("day") != today:
        state.update(day=today, count=0, aux=0, dead=[])
    _dead.update(state.get("dead", []))
    _state = state
    return state


def classify(bases: list[dict], cache: dict, log) -> None:
    """Розкладає історії без розділів по topics/regions. Результат — cache["cls"][id]."""
    key = api_key()
    cls = cache.setdefault("cls", {})
    if not key:
        return
    state = _budget(cache)
    todo = [b for b in bases if b["id"] not in cls]  # bases уже відсортовані за рейтингом
    done = 0
    for start in range(0, len(todo), CLS_BATCH):
        if done >= CLS_PER_RUN or not _aux_ok(state):
            break
        batch = todo[start:start + CLS_BATCH]
        lines = []
        for n, b in enumerate(batch):
            lead = b["_lead"]
            titles = list(dict.fromkeys([lead["en_title"]] + [i["en_title"] for i in b["_items"][:2]]))
            snippet = (lead.get("summary") or "")[:220].replace("\n", " ")
            lines.append(f"{n}. {' / '.join(titles)} — {snippet}")
        try:
            out = call(CLS_SYSTEM, "\n".join(lines), CLS_SCHEMA, key, max_tokens=6000)
        except QuotaExceeded:
            log("ШІ: досягнуто ліміту безкоштовного тарифу — розкладання продовжимо згодом")
            break
        _aux_used(state)
        done += 1
        for it in (out or {}).get("items", []):
            n = it.get("i")
            if isinstance(n, int) and 0 <= n < len(batch):
                cls[batch[n]["id"]] = {
                    "t": [t for t in it.get("topics", []) if t in TOPICS],
                    "r": [r for r in it.get("regions", []) if r in REGIONS],
                }
        time.sleep(PAUSE)
    left = sum(1 for b in bases if b["id"] not in cls)
    log(f"ШІ: розкладено по розділах за запуск: {done} запитів; без розділів лишилось: {left}")


def run(bases: list[dict], cache: dict, log) -> None:
    """Пише тексти для найважливіших історій без тексту. cache — data/ai_cache.json."""
    key = api_key()
    if not key:
        log("ШІ: ключ Gemini не знайдено — тексти від ШІ пропущено")
        return
    state = _budget(cache)
    stories = cache.setdefault("stories", {})
    names = {"uk": "українська", "en": "англійська", "ru": "російська", "zh": "китайська", "zh-TW": "китайська"}

    # тексти з ієрогліфами чи не українською (старі, до перевірки) — переписуємо
    for sid in [k for k, v in stories.items() if not is_ukrainian(v["a"])]:
        del stories[sid]

    def need(b) -> int:
        old = stories.get(b["id"])
        if not old:
            return 2
        return 1 if b["sourceCount"] >= old.get("n", 0) + 3 else 0  # з'явилось багато нових джерел

    def own_text(b) -> int:  # скільки тексту є без ШІ — найкоротші отримують текст першими
        return max((len(i.get("text") or "") for i in b["_items"]), default=0)

    todo = sorted((b for b in bases if need(b)), key=lambda b: (-need(b), own_text(b) >= 150, -b["score"]))
    done = 0
    for b in todo:
        if done >= PER_RUN or state["count"] >= DAILY_LIMIT:
            break
        material = material_for(b["_items"], names)
        if len(material) < 200:
            continue
        try:
            res = generate(material, key)
            state["count"] += 1
            if res and not is_ukrainian(res):  # ієрогліфи чи інша мова — ще одна спроба зі суворішою вимогою
                res = generate(material + "\n\n---\nВАЖЛИВО: попередня відповідь містила ієрогліфи або була не українською. "
                               "Напиши ВЕСЬ текст українською, усі імена й назви — українськими літерами.", key)
                state["count"] += 1
                if res and not is_ukrainian(res):
                    res = None
        except QuotaExceeded:
            log("ШІ: досягнуто ліміту безкоштовного тарифу — продовжимо в наступному запуску")
            break
        done += 1
        if res:
            stories[b["id"]] = {"n": b["sourceCount"], "d": state["day"], "a": res}
        time.sleep(PAUSE)
    log(f"ШІ: написано текстів у цьому запуску: {done}, запитів сьогодні всього: {state['count']}/{DAILY_LIMIT}")


SAME_SYSTEM = """Тобі дають пари новин (номер пари, новина A, новина B). Для кожної пари визнач,
чи це ОДНА Й ТА САМА конкретна подія (той самий інцидент, рішення, заява, матч, вибори тощо),
можливо з різними подробицями чи на різних етапах розвитку.
same=true — якщо це та сама подія або пряме продовження/реакція саме на неї (наприклад: стрілянина → траур через неї → розслідування цієї стрілянини).
same=false — якщо події лише схожі за темою, місцем чи типом (два різні обстріли, два різні матчі, різні рішення однієї установи, різні ігри)."""

SAME_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "pairs": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {"i": {"type": "INTEGER"}, "same": {"type": "BOOLEAN"}},
                "required": ["i", "same"],
            },
        }
    },
    "required": ["pairs"],
}


def same_event(pairs: list[tuple[str, str, str]], cache: dict, log) -> dict[str, bool]:
    """pairs: (ключ пари, текст A, текст B). Повертає {ключ: так/ні} — з кешу або від ШІ."""
    key = api_key()
    known = cache.setdefault("same", {})
    out = {k: known[k] for k, _, _ in pairs if k in known}
    if not key:
        return out
    state = _budget(cache)
    todo = [p for p in pairs if p[0] not in known]
    asked = 0
    for start in range(0, len(todo), 40):
        if asked >= 2 or not _aux_ok(state):
            break
        batch = todo[start:start + 40]
        text = "\n".join(f"{n}. A: {a}\n   B: {b}" for n, (_, a, b) in enumerate(batch))
        try:
            res = call(SAME_SYSTEM, text, SAME_SCHEMA, key, max_tokens=3000)
        except QuotaExceeded:
            break
        _aux_used(state)
        asked += 1
        for it in (res or {}).get("pairs", []):
            n = it.get("i")
            if isinstance(n, int) and 0 <= n < len(batch):
                known[batch[n][0]] = bool(it.get("same"))
                out[batch[n][0]] = known[batch[n][0]]
        time.sleep(PAUSE)
    if asked:
        log(f"ШІ: перевірено пар «та сама подія?»: {asked} запитів")
    return out


TEXT_SYSTEM = """Тобі дають кілька зображень до новин (по порядку: зображення 0, 1, 2…).
Для кожного визнач text=true, якщо на зображенні є ПОМІТНИЙ надрукований текст, доданий поверх або як частина
графіки: заголовок, напис-плашка («Термінова новина»), цитата, інфографіка, скриншот тексту, обкладинка з написами,
картка соцмережі, великий логотип видання з текстом.
text=false — звичайне фото, де текст випадковий і дрібний (вивіски, номери машин, написи на одязі, табло на тлі)."""

TEXT_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "images": {
            "type": "ARRAY",
            "items": {"type": "OBJECT", "properties": {"i": {"type": "INTEGER"}, "text": {"type": "BOOLEAN"}}, "required": ["i", "text"]},
        }
    },
    "required": ["images"],
}


def image_text_flags(thumbs: dict[str, bytes], cache: dict, log, max_requests: int = 2) -> None:
    """Записує в cache["txt"][адреса] = True, якщо на фото надрукований текст."""
    key = api_key()
    known = cache.setdefault("txt", {})
    todo = [(u, b) for u, b in thumbs.items() if u not in known]
    if not key or not todo:
        return
    state = _budget(cache)
    asked = 0
    for start in range(0, len(todo), 8):
        if asked >= max_requests or not _aux_ok(state):
            break
        batch = todo[start:start + 8]
        parts = []
        for n, (_, data) in enumerate(batch):
            parts.append({"text": f"Зображення {n}:"})
            parts.append({"inline_data": {"mime_type": "image/jpeg", "data": base64.b64encode(data).decode()}})
        try:
            res = call(TEXT_SYSTEM, "Відповідай для кожного зображення.", TEXT_SCHEMA, key, max_tokens=800, parts=parts)
        except QuotaExceeded:
            break
        _aux_used(state)
        asked += 1
        for it in (res or {}).get("images", []):
            n = it.get("i")
            if isinstance(n, int) and 0 <= n < len(batch):
                known[batch[n][0]] = bool(it.get("text"))
        time.sleep(PAUSE)
    if asked:
        log(f"ШІ: перевірено фото на текст: {asked} запитів ({sum(1 for u, _ in todo if known.get(u))} з текстом)")


TOPIC_NAMES = {
    "tech": "Технології (ШІ, гаджети, софт, інтернет, кібербезпека, техкомпанії, космічні технології)",
    "economy": "Економіка (ринки, ціни, бюджет, податки, торгівля, банки, бізнес і компанії, енергетичні ринки, робота)",
    "crime": "Кримінал (злочини, вбивства, стрілянини, теракти, шахрайство, корупція, арешти, суди; НЕ війна)",
    "sport": "Спорт (змагання, спортсмени, клуби; НЕ кіберспорт і НЕ політика за участі спортсменів)",
    "science": "Наука (дослідження й відкриття, космос, медицина як наука, природа, археологія)",
    "games": "Відеоігри (ігри, консолі, ігрові студії, кіберспорт)",
    "crypto": "Криптовалюта (біткоїн, криптовалюти, блокчейн, криптобіржі, регулювання криптоактивів)",
}

VERIFY_SYSTEM = """Ти — уважний редактор. Для кожного рядка є новина і розділ сайту.
ok=true лише якщо тема розділу — ГОЛОВНА тема новини, і читач, відкривши цей розділ, очікує побачити саме таку новину.
ok=false, якщо розділ лише побічно згадується або новина насправді про війну, політику, дипломатію, вибори,
допомогу іншим країнам, катастрофи чи погоду. Будь суворим: у сумнівних випадках — false."""

VERIFY_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "items": {
            "type": "ARRAY",
            "items": {"type": "OBJECT", "properties": {"i": {"type": "INTEGER"}, "ok": {"type": "BOOLEAN"}}, "required": ["i", "ok"]},
        }
    },
    "required": ["items"],
}


def verify_topics(checks: list[tuple[str, str, str]], cache: dict, log, max_requests: int = 3) -> dict[str, bool]:
    """checks: (ключ, тема, текст новини). Повертає {ключ: чи справді тема головна}."""
    key = api_key()
    known = cache.setdefault("ver", {})
    out = {k: known[k] for k, _, _ in checks if k in known}
    if not key:
        return out
    state = _budget(cache)
    todo = [c for c in checks if c[0] not in known]
    asked = 0
    for start in range(0, len(todo), 40):
        if asked >= max_requests or not _aux_ok(state):
            break
        batch = todo[start:start + 40]
        text = "\n".join(f"{n}. Розділ: {TOPIC_NAMES[t]}\n   Новина: {txt}" for n, (_, t, txt) in enumerate(batch))
        try:
            res = call(VERIFY_SYSTEM, text, VERIFY_SCHEMA, key, max_tokens=3000)
        except QuotaExceeded:
            break
        _aux_used(state)
        asked += 1
        for it in (res or {}).get("items", []):
            n = it.get("i")
            if isinstance(n, int) and 0 <= n < len(batch):
                known[batch[n][0]] = bool(it.get("ok"))
                out[batch[n][0]] = known[batch[n][0]]
        time.sleep(PAUSE)
    if asked:
        rejected = sum(1 for k, _, _ in todo if known.get(k) is False)
        log(f"ШІ: друга перевірка розділів: {asked} запитів, відхилено: {rejected}")
    return out


def prune(cache: dict, keep_ids: set[str]) -> None:
    for part in ("stories", "cls"):
        st = cache.get(part, {})
        for sid in list(st):
            if sid not in keep_ids:
                del st[sid]
    ver = cache.get("ver", {})
    for k in list(ver):  # ключ «id:тема»
        if k.split(":")[0] not in keep_ids:
            del ver[k]
    txt = cache.get("txt", {})
    if len(txt) > 4000:
        cache["txt"] = dict(list(txt.items())[-4000:])
    same = cache.get("same", {})
    if len(same) > 4000:  # відповіді «та сама подія?» — лишаємо найновіші
        cache["same"] = dict(list(same.items())[-4000:])
