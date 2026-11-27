"""Sheet A row → untrusted source text, with URL rules, an SSRF guard and size limits (MVP-1)."""
import hashlib, ipaddress, re, socket, ssl, os, urllib.error, urllib.parse, urllib.request
from html.parser import HTMLParser
from . import config

VIDEO_HOSTS = ("youtube.com", "youtu.be", "tiktok.com", "facebook.com", "fb.watch", "instagram.com", "vimeo.com")


class SourceError(ValueError):
    def __init__(self, code, message=""):
        super().__init__(f"{code}: {message}" if message else code)
        self.code = code


def source_id(row):
    basis = (row.get("source_url") or "").strip() or (row.get("source_text") or "").strip()
    return "a-" + hashlib.sha256(basis.encode()).hexdigest()[:10]


class _Text(HTMLParser):
    SKIP = {"script", "style", "noscript", "nav", "footer", "header", "aside", "form", "svg"}
    BLOCK = {"p", "li", "h1", "h2", "h3", "h4", "br", "div", "tr", "section", "article"}

    def __init__(self):
        super().__init__(); self.out = []; self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP: self.skip += 1
        if tag in self.BLOCK: self.out.append("\n")
        if tag == "li": self.out.append("- ")

    def handle_endtag(self, tag):
        if tag in self.SKIP and self.skip: self.skip -= 1

    def handle_data(self, data):
        if not self.skip: self.out.append(data)


def html_to_text(html):
    p = _Text(); p.feed(html)
    text = re.sub(r"[ \t\r\f\v]+", " ", "".join(p.out))
    return re.sub(r"\n\s*\n+", "\n", text).strip()


def truncate(text):
    if len(text) <= config.SOURCE_MAX_CHARS:
        return text, False
    cut = text.rfind("\n", 0, config.SOURCE_MAX_CHARS)
    return text[: cut if cut > 0 else config.SOURCE_MAX_CHARS].rstrip(), True


def check_url(url, resolve=socket.getaddrinfo):
    if not url or len(url) > 2048:
        raise SourceError("invalid_url", "empty or longer than 2048 chars")
    u = urllib.parse.urlsplit(url)
    if u.scheme not in ("http", "https") or not u.hostname:
        raise SourceError("invalid_url", "only http(s) URLs with a host")
    host = u.hostname.lower()
    if any(host == h or host.endswith("." + h) for h in VIDEO_HOSTS) or u.path.lower().endswith(".pdf"):
        raise SourceError("unsupported_source", "video or PDF sources are not supported; paste the text instead")
    try:
        addrs = {ai[4][0] for ai in resolve(host, None)}
    except OSError as e:
        raise SourceError("fetch_failed", f"cannot resolve host ({e.__class__.__name__})")
    for a in addrs:
        ip = ipaddress.ip_address(a.split("%")[0])
        if not ip.is_global:
            raise SourceError("blocked_host", "host resolves to a non-public address")
    return u


class _NoRedirectToPrivate(urllib.request.HTTPRedirectHandler):
    max_redirections = 3

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        check_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch(url, opener=None):
    check_url(url)
    ctx = ssl.create_default_context(cafile=os.environ.get("SSL_CERT_FILE"))
    opener = opener or urllib.request.build_opener(_NoRedirectToPrivate, urllib.request.HTTPSHandler(context=ctx))
    req = urllib.request.Request(url, headers={"User-Agent": "diyvideo/1.0 (+guide summarizer)"})
    try:
        with opener.open(req, timeout=config.FETCH_TIMEOUT_S) as r:
            ctype = (r.headers.get("Content-Type") or "").lower()
            if not (ctype.startswith("text/html") or ctype.startswith("text/plain")):
                raise SourceError("unsupported_source", f"content type {ctype.split(';')[0] or 'unknown'}")
            body = r.read(config.FETCH_MAX_BYTES + 1)
    except urllib.error.URLError as e:
        raise SourceError("fetch_failed", e.__class__.__name__)
    if len(body) > config.FETCH_MAX_BYTES:
        raise SourceError("too_large", "page over 2 MB")
    charset = "utf-8"
    m = re.search(r"charset=([\w-]+)", ctype)
    if m: charset = m.group(1)
    html = body.decode(charset, errors="replace")
    return html_to_text(html) if ctype.startswith("text/html") else html


def ingest(row, fetcher=fetch):
    """Return {"source_id", "text", "truncated", "url"} or raise SourceError."""
    topic = (row.get("topic") or "").strip()
    if topic not in config.TOPICS:
        raise SourceError("invalid_topic", f"topic must be one of {', '.join(config.TOPICS)}")
    text = (row.get("source_text") or "").strip()
    url = (row.get("source_url") or "").strip()
    if not text and not url:
        raise SourceError("missing_source", "add source_url or source_text")
    if text:
        if len(text) > config.SOURCE_MAX_CHARS:
            raise SourceError("too_large", "source_text over 20,000 chars")
    else:
        text = fetcher(url)
    if len(text.strip()) < 80:
        raise SourceError("empty_text", "too little readable text")
    text, truncated = truncate(text)
    return {"source_id": source_id(row), "text": text, "truncated": truncated, "url": url or None}
