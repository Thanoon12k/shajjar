#!/usr/bin/env python3
"""Deploy Shajjar to PythonAnywhere using the official API.

    export PA_API_TOKEN=...            # Account → API token
    python scripts/deploy_pythonanywhere.py --user SHAJJAR [--setup]

Steps: upload backend/ + scripts/, create the web app (once), static/media mappings,
WSGI file, reload. With --setup it schedules scripts/pa_setup.sh to run in ~2 minutes
(pip install, migrate, collectstatic, seed) because free accounts cannot drive consoles
through the API. Secrets are generated on the server and never uploaded.
"""
import argparse
import datetime as dt
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {"__pycache__", "media", "staticfiles", ".venv", "node_modules"}
SKIP_FILES = {".env", "db.sqlite3"}


class PA:
    def __init__(self, user, token, host):
        self.user, self.token, self.base = user, token, f"https://{host}/api/v0/user/{user}"

    def req(self, method, path, data=None, files=None, ok=(200, 201, 204)):
        url = self.base + path
        headers = {"Authorization": f"Token {self.token}"}
        body = None
        if files is not None:
            boundary = uuid.uuid4().hex
            name, content = files
            body = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"content\"; filename=\"{name}\"\r\n"
                    "Content-Type: application/octet-stream\r\n\r\n").encode() + content + f"\r\n--{boundary}--\r\n".encode()
            headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"
        elif data is not None:
            body = urllib.parse.urlencode(data).encode()
            headers["Content-Type"] = "application/x-www-form-urlencoded"
        r = urllib.request.Request(url, data=body, headers=headers, method=method)
        for attempt in range(4):
            try:
                with urllib.request.urlopen(r, timeout=60) as resp:
                    raw = resp.read()
                    return resp.status, (json.loads(raw) if raw and raw[:1] in b"[{" else raw)
            except urllib.error.HTTPError as e:
                raw = e.read()
                if e.code in ok:
                    return e.code, raw
                if e.code >= 500 and attempt < 3:
                    time.sleep(2 ** attempt)
                    continue
                return e.code, raw
            except urllib.error.URLError:
                if attempt == 3:
                    raise
                time.sleep(2 ** attempt)

    def upload(self, remote, content):
        code, body = self.req("POST", f"/files/path{remote}", files=(Path(remote).name, content))
        if code not in (200, 201):
            raise SystemExit(f"upload failed {remote}: {code} {body!r}")


def iter_files():
    for base in ("backend", "scripts"):
        for p in sorted((ROOT / base).rglob("*")):
            if p.is_dir() or any(part in SKIP_DIRS for part in p.parts) or p.name in SKIP_FILES or p.suffix == ".pyc":
                continue
            yield p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--user", default=os.environ.get("PA_USER", "SHAJJAR"))
    ap.add_argument("--host", default="www.pythonanywhere.com", help="eu.pythonanywhere.com for EU accounts")
    ap.add_argument("--python", default="python311")
    ap.add_argument("--setup", action="store_true", help="schedule pa_setup.sh on the server")
    ap.add_argument("--skip-upload", action="store_true")
    a = ap.parse_args()
    token = os.environ.get("PA_API_TOKEN")
    if not token:
        sys.exit("PA_API_TOKEN is not set")
    pa = PA(a.user, token, a.host)
    home = f"/home/{a.user}/shajjar"
    domain = f"{a.user.lower()}.pythonanywhere.com"
    wsgi_path = f"/var/www/{domain.replace('.', '_')}_wsgi.py"

    if not a.skip_upload:
        files = list(iter_files())
        for i, p in enumerate(files, 1):
            pa.upload(f"{home}/{p.relative_to(ROOT).as_posix()}", p.read_bytes())
            if i % 20 == 0 or i == len(files):
                print(f"uploaded {i}/{len(files)}")

    code, apps = pa.req("GET", "/webapps/")
    if not any(w.get("domain_name") == domain for w in (apps or [])):
        code, body = pa.req("POST", "/webapps/", {"domain_name": domain, "python_version": a.python})
        print("create webapp:", code, body if code >= 300 else "ok")
    pa.req("PATCH", f"/webapps/{domain}/", {"source_directory": f"{home}/backend", "force_https": "true"})

    code, statics = pa.req("GET", f"/webapps/{domain}/static_files/")
    have = {s["url"] for s in (statics or [])}
    for url, path in (("/static/", f"{home}/backend/staticfiles"), ("/media/", f"{home}/backend/media")):
        if url not in have:
            print("static", url, pa.req("POST", f"/webapps/{domain}/static_files/", {"url": url, "path": path})[0])

    wsgi = f'''import os
import sys

path = "{home}/backend"
if path not in sys.path:
    sys.path.insert(0, path)
os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings"

from django.core.wsgi import get_wsgi_application  # noqa: E402

application = get_wsgi_application()
'''
    pa.upload(wsgi_path, wsgi.encode())
    print("wsgi written")

    if a.setup:
        now = dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=2)
        cmd = f"PA_PYTHON=python{a.python[6]}.{a.python[7:]} bash {home}/scripts/pa_setup.sh > /home/{a.user}/shajjar_setup.log 2>&1"
        code, body = pa.req("POST", "/schedule/", {"command": cmd, "enabled": "true", "interval": "daily", "hour": now.hour, "minute": now.minute})
        print("scheduled setup at", now.strftime("%H:%M UTC"), code, body if code >= 300 else "")
    code, body = pa.req("POST", f"/webapps/{domain}/reload/")
    print("reload:", code)
    print(f"→ https://{domain}/")


if __name__ == "__main__":
    main()
