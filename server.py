#!/usr/bin/env python3
"""Локальний сервер «Коло Новин».

- Роздає сайт на порту 8000 (на Mac і на телефоні в тій самій Wi-Fi мережі).
- Кожні 20 хвилин сам оновлює новини й переклади (collector/fetch_news.py).

Запуск: python3 server.py   (зупинити: Ctrl+C)
"""

import gzip
import socket
import sys
import threading
import time
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "collector"))
import fetch_news  # noqa: E402

PORT = 8000
REFRESH_MIN = 20
ALLOWED = ("/", "/index.html", "/manifest.webmanifest", "/assets/", "/data/uk.json", "/data/en.json", "/data/zh.json", "/data/ru.json",
           "/data/uk/", "/data/en/", "/data/zh/", "/data/ru/")


class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        path = self.path.split("?", 1)[0]
        # віддаємо лише файли сайту, а не код збирача чи інші файли
        if not any(path == a or (a.endswith("/") and a != "/" and path.startswith(a)) for a in ALLOWED) or ".." in path:
            self.send_error(404)
            return
        # дані новин віддаємо стиснутими — на телефоні завантажується в ~5 разів менше
        if path.startswith("/data/") and "gzip" in self.headers.get("Accept-Encoding", ""):
            try:
                body = gzip.compress((ROOT / path.lstrip("/")).read_bytes(), 6)
            except OSError:
                self.send_error(404)
                return
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Encoding", "gzip")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()

    def end_headers(self):
        if self.path.startswith("/data/"):
            self.send_header("Cache-Control", "no-store")
        else:
            self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    def log_message(self, *args):  # не засмічуємо термінал кожним запитом
        pass


def local_ip() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))  # пакет не надсилається, так лише дізнаємось свою адресу в мережі
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


def refresher():
    while True:
        try:
            fetch_news.main()
        except Exception as e:  # збій однієї спроби не зупиняє сервер
            print("Помилка оновлення новин:", e, flush=True)
        time.sleep(REFRESH_MIN * 60)


def main():
    # сайт відкривається одразу (з останніми збереженими новинами), а свіжі збираються у фоні
    print("Збираю свіжі новини у фоні (перший раз — до 2 хвилин)…", flush=True)
    threading.Thread(target=refresher, daemon=True).start()

    server = ThreadingHTTPServer(("0.0.0.0", PORT), partial(Handler, directory=str(ROOT)))
    ip = local_ip()
    print("\n  Коло Новин працює!")
    print(f"  На цьому Mac:     http://localhost:{PORT}")
    print(f"  На iPhone (та сама Wi-Fi): http://{ip}:{PORT}")
    print(f"  Новини оновлюються кожні {REFRESH_MIN} хв. Зупинити: Ctrl+C\n", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nСервер зупинено.")


if __name__ == "__main__":
    main()
