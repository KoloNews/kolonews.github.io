"""Машинний переклад через безкоштовний сервіс Google Translate (без ключа).

- Тексти надсилаються пакетами (до 40 штук / ~4500 символів за запит).
- Готові переклади зберігаються в кеші, тож кожен текст перекладається один раз.
- Якщо сервіс недоступний, повертається None — сайт тоді покаже оригінал.
"""

from __future__ import annotations

import concurrent.futures as cf
import hashlib
import json
import threading
import time
import urllib.parse
import urllib.request
from pathlib import Path

ENDPOINT = "https://translate.googleapis.com/translate_a/t?client=gtx&sl={sl}&tl={tl}"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15"
GOOGLE_CODE = {"uk": "uk", "en": "en", "ru": "ru", "zh": "zh-CN", "zh-TW": "zh-TW"}
MAX_ITEMS, MAX_CHARS = 40, 4500


class Translator:
    def __init__(self, cache_file: Path):
        self.cache_file = cache_file
        try:
            self.cache: dict[str, str] = json.loads(cache_file.read_text("utf-8"))
        except (OSError, ValueError):
            self.cache = {}
        self.used: set[str] = set()
        self.lock = threading.Lock()
        self.failed = 0
        self.requests = 0
        self.disabled = False  # якщо Google почав відмовляти — більше не смикаємо його в цьому запуску

    @staticmethod
    def key(sl: str, tl: str, text: str) -> str:
        return hashlib.sha1(f"{sl}>{tl}|{text}".encode()).hexdigest()[:20]

    def _request(self, texts: list[str], sl: str, tl: str) -> list[str] | None:
        if self.disabled:
            return None
        body = urllib.parse.urlencode([("q", t) for t in texts]).encode()
        url = ENDPOINT.format(sl=GOOGLE_CODE[sl], tl=GOOGLE_CODE[tl])
        for attempt in range(3):
            try:
                req = urllib.request.Request(url, data=body, headers={
                    "User-Agent": UA, "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"})
                with urllib.request.urlopen(req, timeout=30) as r:
                    data = json.loads(r.read().decode("utf-8"))
                with self.lock:
                    self.requests += 1
                # відповідь: ["текст", ...] або [["текст", "мова"], ...]
                out = [d[0] if isinstance(d, list) else d for d in data] if isinstance(data, list) else [data]
                if len(texts) == 1 and isinstance(data, str):
                    out = [data]
                if len(out) != len(texts):
                    return None
                return [str(x) for x in out]
            except Exception:
                time.sleep(1.5 * (attempt + 1))
        with self.lock:
            self.failed += 1
            if self.failed >= 5:
                self.disabled = True
        return None

    def translate(self, texts: list[str], sl: str, tl: str) -> dict[str, str | None]:
        """Повертає {оригінал: переклад або None}."""
        result: dict[str, str | None] = {}
        todo: list[str] = []
        for t in dict.fromkeys(x for x in texts if x):
            if sl == tl:
                result[t] = t
                continue
            k = self.key(sl, tl, t)
            if k in self.cache:
                self.used.add(k)
                result[t] = self.cache[k]
            else:
                todo.append(t)
        batches, cur, size = [], [], 0
        for t in todo:
            if cur and (len(cur) >= MAX_ITEMS or size + len(t) > MAX_CHARS):
                batches.append(cur)
                cur, size = [], 0
            cur.append(t)
            size += len(t)
        if cur:
            batches.append(cur)
        with cf.ThreadPoolExecutor(4) as ex:
            for batch, out in zip(batches, ex.map(lambda b: self._request(b, sl, tl), batches)):
                for src, dst in zip(batch, out or [None] * len(batch)):
                    result[src] = dst
                    if dst:
                        k = self.key(sl, tl, src)
                        with self.lock:
                            self.cache[k] = dst
                            self.used.add(k)
        return result

    def save(self) -> None:
        # зберігаємо лише переклади, потрібні для поточних новин — кеш не розростається
        keep = {k: v for k, v in self.cache.items() if k in self.used}
        tmp = self.cache_file.with_suffix(".tmp")
        tmp.write_text(json.dumps(keep, ensure_ascii=False, separators=(",", ":")), "utf-8")
        tmp.replace(self.cache_file)
