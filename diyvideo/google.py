"""Google adapters (OAuth user refresh token): Sheets store, Drive package upload, YouTube upload.

Secrets come from environment variables (GitHub Secrets): GOOGLE_OAUTH_CLIENT_ID, GOOGLE_OAUTH_CLIENT_SECRET,
GOOGLE_OAUTH_REFRESH_TOKEN. Scopes: spreadsheets, drive.file, youtube.upload. A transport function can be injected
for tests: transport(method, url, headers, body) -> (status, headers, bytes)."""
import json, mimetypes, os, ssl, time, urllib.error, urllib.parse, urllib.request
from pathlib import Path

TOKEN_URL = "https://oauth2.googleapis.com/token"
SHEETS = "https://sheets.googleapis.com/v4/spreadsheets"
DRIVE = "https://www.googleapis.com/drive/v3/files"
DRIVE_UP = "https://www.googleapis.com/upload/drive/v3/files"
YT_UP = "https://www.googleapis.com/upload/youtube/v3/videos"
A_COLS = ["id", "source_url", "source_text", "topic", "notes", "status"]
B_COLS = ["guide_id", "source_id", "mode", "style_id", "title", "summary", "materials", "steps", "safety_notes",
          "caption", "hashtags", "status", "video_url", "post_urls", "cost_vnd", "error", "script_hash", "source_url"]


class GoogleError(RuntimeError):
    pass


def urllib_transport(method, url, headers, body):
    ctx = ssl.create_default_context(cafile=os.environ.get("SSL_CERT_FILE") or None)
    req = urllib.request.Request(url, data=body, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=300, context=ctx) as r:
            return r.status, dict(r.headers), r.read()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers or {}), e.read()


class Session:
    def __init__(self, transport=urllib_transport, env=os.environ):
        self.t = transport; self.env = env; self.token = None; self.exp = 0

    def access_token(self):
        if self.token and time.time() < self.exp - 60:
            return self.token
        missing = [k for k in ("GOOGLE_OAUTH_CLIENT_ID", "GOOGLE_OAUTH_CLIENT_SECRET", "GOOGLE_OAUTH_REFRESH_TOKEN")
                   if not self.env.get(k)]
        if missing:
            raise GoogleError(f"missing secrets: {', '.join(missing)}")
        body = urllib.parse.urlencode({"grant_type": "refresh_token", "client_id": self.env["GOOGLE_OAUTH_CLIENT_ID"],
                                       "client_secret": self.env["GOOGLE_OAUTH_CLIENT_SECRET"],
                                       "refresh_token": self.env["GOOGLE_OAUTH_REFRESH_TOKEN"]}).encode()
        st, _, data = self.t("POST", TOKEN_URL, {"Content-Type": "application/x-www-form-urlencoded"}, body)
        if st != 200:
            raise GoogleError(f"token refresh failed: HTTP {st}")  # never echo the response (may contain secrets)
        j = json.loads(data); self.token = j["access_token"]; self.exp = time.time() + int(j.get("expires_in", 3600))
        return self.token

    def call(self, method, url, body=None, content_type="application/json", extra=None, raw=False):
        headers = {"Authorization": f"Bearer {self.access_token()}", **(extra or {})}
        data = body
        if body is not None and not isinstance(body, (bytes, bytearray)):
            data = json.dumps(body).encode()
        if data is not None:
            headers["Content-Type"] = content_type
        for attempt in range(3):
            st, h, out = self.t(method, url, headers, data)
            if st in (429, 500, 502, 503) and attempt < 2:
                time.sleep(2 ** attempt); continue
            break
        if st >= 300 and not (raw and st == 308):
            raise GoogleError(f"{method} {url.split('?')[0]} -> HTTP {st}: {out[:200].decode(errors='replace')}")
        return (st, h, out) if raw else (json.loads(out) if out else {})


def _col(n):
    s = ""
    while n:
        n, r = divmod(n - 1, 26); s = chr(65 + r) + s
    return s


class GoogleSheetStore:
    """Same interface as LocalSheetStore over a spreadsheet with tabs 'A' and 'B' (header row = column names)."""

    def __init__(self, sheet_id, session):
        self.id, self.s = sheet_id, session

    def _rows(self, tab, cols):
        v = self.s.call("GET", f"{SHEETS}/{self.id}/values/{tab}!A1:{_col(len(cols))}").get("values", [])
        if not v:
            self.s.call("PUT", f"{SHEETS}/{self.id}/values/{tab}!A1?valueInputOption=RAW", {"values": [cols]})
            return [], cols
        header = v[0]
        return [dict(zip(header, r + [""] * (len(header) - len(r)))) for r in v[1:]], header

    def rows_a(self):
        return [{k: v for k, v in r.items() if v != ""} for r in self._rows("A", A_COLS)[0]]

    def update_a(self, index, **fields):
        _, header = self._rows("A", A_COLS)
        for k, v in fields.items():
            c = header.index(k) + 1
            self.s.call("PUT", f"{SHEETS}/{self.id}/values/A!{_col(c)}{index + 2}?valueInputOption=RAW",
                        {"values": [[str(v)]]})

    def rows_b(self):
        return [{k: v for k, v in r.items() if v != ""} for r in self._rows("B", B_COLS)[0]]

    def upsert_b(self, guide_id, **fields):
        rows, header = self._rows("B", B_COLS)
        idx = next((i for i, r in enumerate(rows) if r.get("guide_id") == guide_id), None)
        row = rows[idx] if idx is not None else {c: "" for c in header}
        row.update({"guide_id": guide_id, **{k: ("" if v is None else str(v)) for k, v in fields.items()}})
        values = [[row.get(c, "") for c in header]]
        if idx is None:
            self.s.call("POST", f"{SHEETS}/{self.id}/values/B!A1:append?valueInputOption=RAW&insertDataOption=INSERT_ROWS",
                        {"values": values})
        else:
            self.s.call("PUT", f"{SHEETS}/{self.id}/values/B!A{idx + 2}?valueInputOption=RAW", {"values": values})
        return row


class Drive:
    def __init__(self, session):
        self.s = session

    def folder(self, name, parent=None):
        q = f"name = '{name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        if parent:
            q += f" and '{parent}' in parents"
        found = self.s.call("GET", f"{DRIVE}?q={urllib.parse.quote(q)}&fields=files(id,name)").get("files", [])
        if found:
            return found[0]["id"]
        meta = {"name": name, "mimeType": "application/vnd.google-apps.folder", **({"parents": [parent]} if parent else {})}
        return self.s.call("POST", f"{DRIVE}?fields=id", meta)["id"]

    def upload(self, path, parent):
        path = Path(path); boundary = "diyvideo-boundary"
        meta = json.dumps({"name": path.name, "parents": [parent]}).encode()
        ctype = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        body = (f"--{boundary}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n".encode() + meta +
                f"\r\n--{boundary}\r\nContent-Type: {ctype}\r\n\r\n".encode() + path.read_bytes() +
                f"\r\n--{boundary}--".encode())
        r = self.s.call("POST", f"{DRIVE_UP}?uploadType=multipart&fields=id,webViewLink", body,
                        content_type=f"multipart/related; boundary={boundary}")
        return r

    def upload_package(self, pkg_dir, root_name="diy-output"):
        root = self.folder(root_name); sub = self.folder(Path(pkg_dir).name, root)
        links = {}
        for f in sorted(Path(pkg_dir).rglob("*")):
            if f.is_file():
                parent = sub if f.parent == Path(pkg_dir) else self.folder(f.parent.name, sub)
                links[str(f.relative_to(pkg_dir))] = self.upload(f, parent).get("webViewLink")
        return links


def youtube_upload(session, video, title, description, tags, privacy="private"):
    """Resumable upload with the synthetic-media disclosure (research R4). Returns the video id."""
    meta = {"snippet": {"title": title[:100], "description": description[:5000], "tags": tags[:30], "categoryId": "26"},
            "status": {"privacyStatus": privacy, "containsSyntheticMedia": True, "selfDeclaredMadeForKids": False}}
    size = Path(video).stat().st_size
    _, h, _ = session.call("POST", f"{YT_UP}?uploadType=resumable&part=snippet,status", meta,
                           content_type="application/json; charset=UTF-8",
                           extra={"X-Upload-Content-Type": "video/mp4", "X-Upload-Content-Length": str(size)}, raw=True)
    loc = h.get("Location") or h.get("location")
    if not loc:
        raise GoogleError("YouTube resumable session URL missing")
    r = session.call("PUT", loc, Path(video).read_bytes(), content_type="video/mp4")
    return r["id"]
