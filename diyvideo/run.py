"""Orchestrator: Sheet A rows → Sheet B guides → frames → video package. Publishing is a separate command."""
import hashlib, json, traceback
from pathlib import Path
from . import config, images, ingest, package, render, script as scriptmod, sheets, styles
from .ledger import CostCapExceeded


class Providers:
    def __init__(self, text, image, verifier, tier):
        self.text, self.image, self.verifier, self.tier = text, image, verifier, tier


def guide_id_for(source_id):
    return "g-" + source_id[2:]


def _parse_steps(cell, old):
    steps = []
    for line, o in zip([l for l in cell.splitlines() if l.strip()], old):
        n, on_screen, detail = (part.strip() for part in (line.split("|", 2) + ["", ""])[:3])
        steps.append({**o, "on_screen": on_screen[:60] or o["on_screen"], "detail": detail[:220] or o["detail"]})
    return steps


def process_new(store, ledger, prov, out_root, work_root):
    done = 0
    prev_style = next((r.get("style_id") for r in reversed(store.rows_b()) if r.get("style_id")), None)
    for i, row in enumerate(store.rows_a()):
        if done >= config.MAX_NEW_GUIDES_PER_RUN:
            break
        if (row.get("status") or "new") != "new":
            continue
        try:
            src = ingest.ingest(row)
        except ingest.SourceError as e:
            store.update_a(i, status=f"error: {e.code}", id=ingest.source_id(row)); continue
        gid = guide_id_for(src["source_id"])
        store.update_a(i, id=src["source_id"], status="scripted")
        try:
            ledger.preflight(gid, frames=16, tier=prov.tier)
            sc = ledger.get(f"script:{gid}") or scriptmod.make_script(src["text"], row.get("notes"), prov.text, ledger, gid)
            ledger.put(f"script:{gid}", sc)
        except (scriptmod.ScriptError, CostCapExceeded) as e:
            store.update_a(i, status=f"error: {'cost_cap' if isinstance(e, CostCapExceeded) else 'script_failed'}")
            continue
        style = styles.pick(row["topic"], prev_style); prev_style = style["id"]
        store.upsert_b(gid, source_id=src["source_id"], source_url=src["url"], mode="ai", style_id=style["id"],
                       status="script_ready", **sheets.steps_to_cells(sc), title=sc["title"], summary=sc["summary"],
                       caption=sc["caption"])
        build(store, ledger, prov, gid, sc, style, src, out_root, work_root)
        done += 1
    return done


def build(store, ledger, prov, gid, sc, style, src, out_root, work_root):
    store.upsert_b(gid, status="rendering", error="")
    frames_dir = Path(work_root) / gid / "frames"
    try:
        fr = images.generate_frames(sc, style, gid, frames_dir, prov.image, prov.verifier, ledger, tier=prov.tier)
        if fr["flagged"]:
            # IDEA MVP-4: a flagged image never goes into the video unreviewed. Render with the last accepted
            # frame in its place; the flagged attempts stay in frames/attempts for the user's review.
            frames_dir = substitute_flagged(frames_dir, fr["flagged"], Path(work_root) / gid / "frames-render")
        script_hash = hashlib.sha256(json.dumps(sc, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:16]
        mp4 = Path(work_root) / gid / f"video-{script_hash}.mp4"
        probe = render.render(sc, frames_dir, mp4, workdir=Path(work_root) / gid / "render")
        out, report = package.build(gid, sc, style, frames_dir, mp4, probe, fr, ledger.spent_vnd(guide=gid),
                                    {"url": src.get("url"), "truncated": src.get("truncated")}, out_root)
        store.upsert_b(gid, status="needs_review", video_url=str(out / "video.mp4"), cost_vnd=report["cost_vnd"],
                       script_hash=script_hash,
                       error=(f"image_flagged: {', '.join(fr['flagged'])} (previous frame shown)" if fr["flagged"] else ""))
        return report
    except CostCapExceeded as e:
        store.upsert_b(gid, status="failed", error=f"cost_cap: {e}"[:200])
    except Exception as e:  # keep other guides running; details go to the error cell, not secrets
        if e.__class__.__name__ == "PendingBatch":
            store.upsert_b(gid, status="rendering", error="waiting: image batch still running")
        else:
            store.upsert_b(gid, status="failed", error=f"{e.__class__.__name__}: {e}"[:200])
    return None


def substitute_flagged(frames_dir, flagged, dest):
    import shutil
    dest = Path(dest); dest.mkdir(parents=True, exist_ok=True)
    names = sorted(p.name for p in Path(frames_dir).glob("*.jpg"))
    ok = [n for n in names if n not in flagged]
    if not ok:
        raise RuntimeError("all frames flagged; nothing safe to render")
    for n in names:
        if n in flagged:
            before = [o for o in ok if o < n]
            src = before[-1] if before else ok[0]  # never copy a flagged image into the render set
        else:
            src = n
        shutil.copy(Path(frames_dir) / src, dest / n)
    return dest


def process_regenerate(store, ledger, prov, out_root, work_root):
    for row in store.rows_b():
        if row.get("status") != "regenerate":
            continue
        gid = row["guide_id"]; sc = ledger.get(f"script:{gid}")
        if not sc:
            store.upsert_b(gid, status="failed", error="no stored script"); continue
        sc = {**sc, "title": row.get("title", sc["title"])[:70], "caption": row.get("caption", sc["caption"]),
              "steps": _parse_steps(row.get("steps", ""), sc["steps"])}
        ledger.put(f"script:{gid}", sc)
        style = next(s for s in styles.STYLES if s["id"] == row["style_id"])
        build(store, ledger, prov, gid, sc, style, {"url": row.get("source_url")}, out_root, work_root)


def process_pending(store, ledger, prov, out_root, work_root):
    """Resume guides whose image batch was still running on a previous run (submit-and-exit design)."""
    resumed = 0
    for row in store.rows_b():
        if row.get("status") != "rendering" or not str(row.get("error", "")).startswith("waiting"):
            continue
        gid = row["guide_id"]; sc = ledger.get(f"script:{gid}")
        style = next((s for s in styles.STYLES if s["id"] == row.get("style_id")), None)
        if not sc or not style:
            store.upsert_b(gid, status="failed", error="cannot resume: missing script or style"); continue
        build(store, ledger, prov, gid, sc, style, {"url": row.get("source_url")}, out_root, work_root)
        resumed += 1
    return resumed


def run(store, ledger, prov, out_root, work_root):
    process_pending(store, ledger, prov, out_root, work_root)
    process_regenerate(store, ledger, prov, out_root, work_root)
    return process_new(store, ledger, prov, out_root, work_root)
