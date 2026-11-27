"""Output package (MVP-6): video, cover, caption, step frames and report.json in output/<guide_id>/."""
import json, shutil, subprocess
from datetime import datetime, timezone
from pathlib import Path
from . import config


def build(guide_id, script, style, frames_dir, video, probe, frames_report, cost_vnd, source, out_root):
    out = Path(out_root) / guide_id; (out / "steps").mkdir(parents=True, exist_ok=True)
    shutil.copy(video, out / "video.mp4")
    last = Path(frames_dir) / f"{len(script['steps']):02d}.jpg"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(last), "-vf", "scale=1080:1920:flags=lanczos",
                    "-q:v", "3", str(out / "cover.jpg")], check=True)
    for f in sorted(Path(frames_dir).glob("*.jpg")):
        shutil.copy(f, out / "steps" / f.name)
    caption = script["caption"].rstrip() + "\n\n" + " ".join(script["hashtags"])
    if config.AI_CAPTION_LINE not in caption:
        caption += "\n" + config.AI_CAPTION_LINE
    (out / "caption.txt").write_text(caption, encoding="utf-8")
    frames = frames_report["frames"]
    report = {
        "guide_id": guide_id, "style_id": style["id"], "steps": len(script["steps"]),
        "keyframe_steps": [s["n"] for s in script["steps"] if s.get("key")], "duration_s": probe["duration_s"],
        "images": {"generated": sum(f["qa"]["attempts"] for f in frames),
                   "retried": sum(f["qa"]["attempts"] - 1 for f in frames), "flagged": len(frames_report["flagged"])},
        "framing": {"max_shift_px": max([f["qa"]["gate"].get("shift_px", 0) or 0 for f in frames] or [0])},
        "video": probe, "cost_vnd": round(cost_vnd), "ai_label": "0-3s",
        "prompts": config.PROMPT_VERSIONS, "pricing_version": config.PRICING_VERSION,
        "source": source, "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    (out / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    return out, report
