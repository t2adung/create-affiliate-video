"""Source text → validated Sheet B script (MVP-2)."""
import hashlib, json, re
from . import config, prompts


class ScriptError(ValueError):
    pass


def _words(text):
    return re.findall(r"\w+", text.lower())


def copied_span(source, generated, n=12):
    """True if `generated` shares any run of n consecutive words with `source`."""
    src = _words(source)
    grams = {tuple(src[i:i + n]) for i in range(len(src) - n + 1)}
    gen = _words(generated)
    return any(tuple(gen[i:i + n]) in grams for i in range(len(gen) - n + 1))


def normalize(j):
    """Deterministic fixes that never change meaning: in looks without key steps, drop key flags."""
    if isinstance(j, dict) and isinstance(j.get("steps"), list) and config.look()["keys"][1] == 0:
        for s in j["steps"]:
            if isinstance(s, dict):
                s["key"] = False
    return j


def overlap_spans(source, generated, n=12):
    src = _words(source); grams = {tuple(src[i:i + n]) for i in range(len(src) - n + 1)}
    gen = _words(generated)
    return sorted({" ".join(gen[i:i + n]) for i in range(len(gen) - n + 1) if tuple(gen[i:i + n]) in grams})


def validate(j, source):
    errs = []
    for k, t in (("title", str), ("summary", str), ("materials", list), ("safety_notes", list), ("scene", str),
                 ("steps", list), ("caption", str), ("hashtags", list)):
        if not isinstance(j.get(k), t):
            errs.append(f"missing or invalid {k}")
    if errs:
        raise ScriptError("; ".join(errs))
    steps = j["steps"]; lk = config.look(); lo, hi = lk["steps"]
    if not lo <= len(steps) <= hi: errs.append(f"{len(steps)} steps (need {lo}-{hi})")
    if lk["materials_frame"] and not str(j.get("materials_scene") or "").strip(): errs.append("missing materials_scene")
    if len(j["title"]) > 70: errs.append("title > 70 chars")
    if len(j["summary"]) > 400: errs.append("summary > 400 chars")
    if not 1 <= len(j["materials"]) <= 15: errs.append("materials count")
    if len(j["caption"]) > 2200: errs.append("caption > 2200 chars")
    if config.AI_CAPTION_LINE not in j["caption"]: errs.append("caption lacks AI line")
    for i, s in enumerate(steps, 1):
        if s.get("n") != i: errs.append(f"step numbering at {i}")
        if not isinstance(s.get("on_screen"), str) or not 1 <= len(s["on_screen"]) <= lk["on_screen_max"]:
            errs.append(f"step {i} on_screen")
        if not isinstance(s.get("detail"), str) or len(s["detail"]) > 220: errs.append(f"step {i} detail")
        if not isinstance(s.get("image_prompt"), str) or not s["image_prompt"].strip(): errs.append(f"step {i} image_prompt")
        if not isinstance(s.get("required_objects"), list): errs.append(f"step {i} required_objects")
    keys = [s["n"] for s in steps if s.get("key")]
    klo, khi = lk["keys"]
    if not klo <= len(keys) <= khi or 1 in keys: errs.append(f"key steps {keys} (need {klo}-{khi}, not step 1)")
    visible = " ".join([j["title"], j["summary"], j["caption"]] + [s["on_screen"] + " " + s["detail"] for s in steps])
    if copied_span(source, visible): errs.append("copies >=12 consecutive words from the source")
    if re.search(r"https?://|www\.|\b[\w-]+\.(com|net|vn|org|io|ly)\b", visible + " " + " ".join(j["hashtags"]), re.I):
        errs.append("contains a URL or domain (links are never generated)")
    if errs:
        raise ScriptError("; ".join(errs))
    return j


def make_script(source_text, notes, text_model, ledger, guide_id, attempts=3):
    tpl = prompts.load(config.look()["script"])
    safe = re.sub(r"<<<\s*SOURCE|SOURCE\s*>>>", "[delimiter removed]", source_text, flags=re.I)
    safe_notes = re.sub(r"<<<\s*SOURCE|SOURCE\s*>>>", "", (notes or "")[:300], flags=re.I)
    prompt = prompts.fill(tpl, ai_line=config.AI_CAPTION_LINE, notes=safe_notes, source=safe)
    last, feedback = None, ""
    for a in range(attempts):
        ledger.guard(guide_id, config.EST_TEXT_USD)
        r = text_model.generate_json(prompt + feedback)
        ledger.record(guide_id, f"script:{a}", r.model, config.usd_from_usage(r.model, r.usage, r.tier))
        try:
            return validate(normalize(r.value), source_text)
        except ScriptError as e:
            last = e
            ledger.put(f"scripterr:{guide_id}:{a}", {"error": str(e)})
            copied = overlap_spans(source_text, json.dumps(r.value, ensure_ascii=False)) if isinstance(r.value, dict) else []
            feedback = ("\n\nYOUR PREVIOUS ANSWER WAS REJECTED: " + str(e) +
                        (". Rewrite these parts in clearly different words: " + " | ".join(copied[:5]) if copied else "") +
                        ". Return the full corrected JSON.")
    raise ScriptError(f"script failed validation {attempts}x: {last}")


def frame_plan(script):
    """Ordered frames: key steps get in-betweens k=1,2 then the step frame k=3; others a single k=1 frame."""
    plan = []
    for s in script["steps"]:
        ks = (1, 2, 3) if s.get("key") else (1,)
        for k in ks:
            plan.append({"step": s["n"], "k": k, "last": k == ks[-1], "key": bool(s.get("key"))})
    return plan
