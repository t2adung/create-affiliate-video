"""Chained frame generation with camera lock, framing gate, independent verifier and bounded retries (MVP-3/4)."""
import hashlib, json
from pathlib import Path
from . import config, framing, prompts, styles
from .providers import verdict_pass

PHASES = {1: "the hands begin this step's action; the result is about one third done",
          2: "the hands are mid-action; the result is about two thirds done"}


def sha(*parts):
    h = hashlib.sha256()
    for p in parts:
        h.update(p if isinstance(p, bytes) else str(p).encode()); h.update(b"\x00")
    return h.hexdigest()[:16]


def frame_prompt(script, style, f, attempt, progress):
    s = script["steps"][f["step"] - 1]
    if f["last"]:
        instr = f"Step {s['n']} of {len(script['steps'])} completed: {s['image_prompt']}"
    else:
        instr = (f"Step {s['n']} in progress ({PHASES[f['k']]}). Final state of this step will be: {s['image_prompt']}. "
                 "Only the hands and the items they handle move a little compared with the previous photo.")
    body = prompts.fill(prompts.load("image_v1"), style=styles.describe(style), scene=script["scene"],
                        frame_instruction=instr, required=", ".join(s.get("required_objects") or []) or "none")
    if f["step"] > 1 or f["k"] > 1:
        body = prompts.load("edit_lock_v1") + "\n" + body
    if attempt:
        body += "\nPREVIOUS ATTEMPT FAILED REVIEW (camera moved or content wrong). Keep the framing identical."
    return body + f"\n[progress={progress}]"


def generate_frames(script, style, guide_id, out_dir, image_model, verifier, ledger, max_retries=2, tier="batch"):
    """Frames chain from the last frame that passed the framing gate; flagged frames are kept for review."""
    out_dir = Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True)
    from .script import frame_plan
    plan = frame_plan(script)
    frames, flags, first, prev = [], [], None, None
    for idx, f in enumerate(plan, 1):
        name = f"{f['step']:02d}.jpg" if f["last"] else f"{f['step']:02d}-k{f['k']}.jpg"
        s = script["steps"][f["step"] - 1]
        base_key = sha(guide_id, name, json.dumps(s, sort_keys=True, ensure_ascii=False), style["id"],
                       config.IMAGE_MODEL, config.PROMPT_VERSIONS["image"], sha(prev or b""))
        cached = ledger.get(f"img:{base_key}")
        if cached and (out_dir / name).exists():
            img = (out_dir / name).read_bytes(); rec = cached
        else:
            rec = None
            for attempt in range(max_retries + 1):
                ledger.guard(guide_id, config.EST_FRAME_USD[tier] + 0.003)
                refs = [] if prev is None else ([prev] if first is prev else [first, prev])
                r = image_model.generate(frame_prompt(script, style, f, attempt, idx), refs, f"{name}:{attempt}")
                ledger.record(guide_id, f"img:{name}:{attempt}", r.model, config.usd_from_usage(r.model, r.usage, tier))
                img = r.value
                gate = framing.measure(prev, img) if prev is not None else {"pass": True, "reason": "first"}
                if not gate["pass"]:
                    rec = {"frame": name, "gate": _slim(gate), "verify": None, "attempts": attempt + 1, "pass": False}
                    continue
                img = framing.correct(img, gate) if prev is not None else img
                v = verifier.check(prev, img, f"{s['on_screen']} - {s['detail']}", s.get("required_objects") or [],
                                   f"{name}:{attempt}")
                ledger.record(guide_id, f"verify:{name}:{attempt}", v.model, config.usd_from_usage(v.model, v.usage))
                ok = verdict_pass(v.value)
                rec = {"frame": name, "gate": _slim(gate), "verify": v.value, "attempts": attempt + 1, "pass": ok}
                if ok:
                    break
            (out_dir / name).write_bytes(img)
            if rec["pass"]:
                ledger.put(f"img:{base_key}", rec)
        frames.append({**f, "file": name, "qa": rec})
        if not rec["pass"]:
            flags.append(name)
            if rec.get("verify") is None:  # failed the framing gate: never chain from a drifted frame
                continue
        first = first or img
        prev = img
    return {"frames": frames, "flagged": flags}


def _slim(g):
    return {k: v for k, v in g.items() if k != "matrix"}
