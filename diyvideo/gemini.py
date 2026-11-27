"""Real Gemini adapters (generateContent / batchGenerateContent). Never used by tests or CI.

Auth: if GEMINI_API_KEY is set it is sent as x-goog-api-key (GitHub Actions); otherwise the request relies on a
network proxy that injects the header (cloud development session). Responses are untrusted data."""
import base64, json, os, re, ssl, time, urllib.error, urllib.request
from .providers import Result

BASE = "https://generativelanguage.googleapis.com/v1beta"


class PendingBatch(RuntimeError):
    """A batch job is still running; the caller should stop this guide and resume on the next run."""


class ApiError(RuntimeError):
    pass


def _ctx():
    return ssl.create_default_context(cafile=os.environ.get("SSL_CERT_FILE") or None)


def _call(method, path, body=None, timeout=300):
    headers = {"Content-Type": "application/json"}
    if os.environ.get("GEMINI_API_KEY"):
        headers["x-goog-api-key"] = os.environ["GEMINI_API_KEY"]
    req = urllib.request.Request(f"{BASE}/{path}", method=method, headers=headers,
                                 data=json.dumps(body).encode() if body is not None else None)
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=_ctx()) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")[:300]
        raise ApiError(f"HTTP {e.code}: {re.sub(r'AIza[0-9A-Za-z_-]{20,}', '[redacted]', detail)}") from None


def _usage(resp):
    u = resp.get("usageMetadata", {})
    img = sum(d.get("tokenCount", 0) for d in u.get("candidatesTokensDetails", []) if d.get("modality") == "IMAGE")
    out = u.get("candidatesTokenCount", 0) - img + u.get("thoughtsTokenCount", 0)
    return {"in": u.get("promptTokenCount", 0), "text_out": max(out, 0), "image_out": img}


def _parts(resp):
    c = (resp.get("candidates") or [{}])[0]
    return (c.get("content") or {}).get("parts") or [], c.get("finishReason")


def _image_request(prompt, refs):
    parts = [{"text": prompt}] + [{"inlineData": {"mimeType": "image/jpeg", "data": base64.b64encode(r).decode()}}
                                  for r in refs]
    return {"contents": [{"role": "user", "parts": parts}],
            "generationConfig": {"responseModalities": ["IMAGE"],
                                 "imageConfig": {"aspectRatio": "9:16", "imageSize": "1K"}}}


def _image_from(resp, label):
    parts, finish = _parts(resp)
    for p in parts:
        d = p.get("inlineData") or p.get("inline_data")
        if d and d.get("data"):
            return base64.b64decode(d["data"])
    raise ApiError(f"{label}: no image returned (finishReason={finish})")


class GeminiText:
    def __init__(self, model):
        self.model = model

    def generate_json(self, prompt):
        resp = _call("POST", f"models/{self.model}:generateContent", {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"responseMimeType": "application/json", "thinkingConfig": {"thinkingLevel": "LOW"}}})
        parts, finish = _parts(resp)
        text = "".join(p.get("text", "") for p in parts if not p.get("thought"))
        try:
            value = json.loads(re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.M).strip())
        except ValueError:
            value = {"_unparsed": text[:500], "_finish": finish}
        return Result(value=value, model=self.model, usage=_usage(resp))


class GeminiVerifier:
    def __init__(self, model, template):
        self.text = GeminiText(model); self.model = model; self.template = template

    def check(self, prev, cur, step_text, required, label):
        parts = [{"text": self.template.replace("{step}", step_text).replace("{required}", ", ".join(required) or "none")}]
        if prev:
            parts += [{"text": "PREVIOUS image:"}, {"inlineData": {"mimeType": "image/jpeg", "data": base64.b64encode(prev).decode()}}]
        parts += [{"text": "CURRENT image:"}, {"inlineData": {"mimeType": "image/jpeg", "data": base64.b64encode(cur).decode()}}]
        resp = _call("POST", f"models/{self.model}:generateContent", {
            "contents": [{"role": "user", "parts": parts}],
            "generationConfig": {"responseMimeType": "application/json", "thinkingConfig": {"thinkingLevel": "LOW"}}})
        ps, _ = _parts(resp)
        try:
            v = json.loads("".join(p.get("text", "") for p in ps if not p.get("thought")))
        except ValueError:
            v = {"issues": "unparsed verifier output"}  # verdict_pass() treats missing fields as failure
        return Result(value=v, model=self.model, usage=_usage(resp))


class GeminiImage:
    """tier="standard": synchronous. tier="batch": one single-request batch job per frame, persisted in the
    ledger so an unfinished job resumes on the next run (raises PendingBatch after `wait_s`)."""

    def __init__(self, model, ledger=None, tier="batch", wait_s=600, poll_s=15):
        self.model, self.ledger, self.tier, self.wait_s, self.poll_s = model, ledger, tier, wait_s, poll_s

    def generate(self, prompt, refs, label, job_key=None):
        body = _image_request(prompt, refs)
        if self.tier == "standard":
            resp = _call("POST", f"models/{self.model}:generateContent", body)
            return Result(value=_image_from(resp, label), model=self.model, usage=_usage(resp), tier="standard")
        key = job_key or label
        job = self.ledger.batch_job(key)
        if not job:
            op = _call("POST", f"models/{self.model}:batchGenerateContent", {"batch": {
                "display_name": f"diy-{key}"[:120],
                "input_config": {"requests": {"requests": [{"request": body, "metadata": {"key": key}}]}}}})
            job = op.get("name") or (op.get("metadata") or {}).get("name")
            if not job:
                raise ApiError(f"{label}: batch create returned no job name")
            self.ledger.set_batch_job(key, job)
        deadline = time.time() + self.wait_s
        while True:
            st = _call("GET", job)
            state = (st.get("metadata") or {}).get("state", "")
            if st.get("done") or state.endswith(("SUCCEEDED", "FAILED", "CANCELLED", "EXPIRED")):
                break
            if time.time() > deadline:
                raise PendingBatch(f"{label}: {job} still {state or 'running'}")
            time.sleep(self.poll_s)
        self.ledger.set_batch_job(key, None)
        if not state.endswith("SUCCEEDED"):
            raise ApiError(f"{label}: batch {state}: {json.dumps(st.get('error'))[:200]}")
        inl = (st.get("response") or {}).get("inlinedResponses")
        items = inl.get("inlinedResponses") if isinstance(inl, dict) else inl
        if not items:
            raise ApiError(f"{label}: batch succeeded without inline responses")
        item = items[0]
        if item.get("error"):
            raise ApiError(f"{label}: {json.dumps(item['error'])[:200]}")
        resp = item.get("response") or {}
        return Result(value=_image_from(resp, label), model=self.model, usage=_usage(resp), tier="batch")
