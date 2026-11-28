"""Frames + script → final MP4 (MVP-5): key-step interpolation clips, Remotion render, exact encode, probes."""
import json, os, shutil, subprocess, tempfile
from pathlib import Path
from . import audio, config

REMOTION = Path(__file__).parent / "remotion"
FPS = 30
HOLD_S = 0.6


class RenderError(RuntimeError):
    pass


def timing(n):
    """Frames per segment for the active look (Remotion receives these as props)."""
    if config.LOOK == "crossfade":
        step = round(max(1.2, min(1.6, (24 - 1.5 - 1.5 - 2.5) / n)) * FPS)
        return {"hook": 45, "mats": 45, "step": step, "end": 75, "xfade": 9, "zoom": 0.035}
    return {"hook": 60, "mats": 0, "step": round(min(3.0, 25 / n) * FPS), "end": 90, "xfade": 8, "zoom": 0.08}


def step_seconds(n):
    return timing(n)["step"] / FPS


def total_seconds(n):
    t = timing(n)
    return (t["hook"] + t["mats"] + n * t["step"] + t["end"]) / FPS


def _run(cmd, **kw):
    p = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if p.returncode:
        lines = p.stderr.strip().splitlines()
        key = [l for l in lines if any(w in l for w in ("Error", "error:", "Cannot", "failed", "not found", "ENOENT"))
               and not l.lstrip().startswith("at ")]
        raise RenderError(f"{Path(cmd[0]).name} failed: " + " | ".join((key[:6] or lines[-8:]))[:1500])
    return p.stdout


def key_clip(frames, out, seconds):
    """Interpolate a short sequence of locked frames into smooth motion lasting `seconds` (research R10)."""
    with tempfile.TemporaryDirectory() as d:
        for i, f in enumerate(frames, 1):
            shutil.copy(f, Path(d) / f"{i}.jpg")
        shutil.copy(frames[-1], Path(d) / f"{len(frames) + 1}.jpg")  # pad so the last interval completes
        rate = (len(frames) - 1) / seconds
        _run(["ffmpeg", "-v", "error", "-y", "-framerate", f"{rate:.6f}", "-i", str(Path(d) / "%d.jpg"),
              "-vf", f"scale=1080:1920:flags=lanczos,minterpolate=fps={FPS}:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,format=yuv420p",
              "-t", f"{seconds:.3f}", "-an", "-c:v", "libx264", "-crf", "16", str(out)])
    return out


def build_public(script, frames_dir, frame_plan, stage):
    """Copy frames, make key clips and audio into the Remotion public dir; return Remotion props."""
    stage = Path(stage); g = stage / "g"; g.mkdir(parents=True, exist_ok=True)
    audio.write_assets(stage / "audio")
    n = len(script["steps"]); slot = step_seconds(n)
    steps = []
    for s in script["steps"]:
        name = f"{s['n']:02d}.jpg"; shutil.copy(Path(frames_dir) / name, g / name)
        entry = {"n": s["n"], "on_screen": s["on_screen"], "image": f"g/{name}"}
        if s.get("key"):
            prev = Path(frames_dir) / f"{s['n'] - 1:02d}.jpg"
            seq = [prev] + [Path(frames_dir) / f"{s['n']:02d}-k{k}.jpg" for k in (1, 2)] + [Path(frames_dir) / name]
            seq = [p for p in seq if p.exists()]
            if len(seq) >= 3:
                key_clip(seq, g / f"{s['n']:02d}-clip.mp4", slot - HOLD_S)
                entry["clip"] = f"g/{s['n']:02d}-clip.mp4"
        steps.append(entry)
    has_links = any((m.get("link") or "").startswith("https://") for m in script["materials"])
    mats = None
    if (Path(frames_dir) / "00.jpg").exists():
        shutil.copy(Path(frames_dir) / "00.jpg", g / "00.jpg"); mats = "g/00.jpg"
    return {"guide": {"title": script["title"], "hook": f"g/{n:02d}.jpg", "steps": steps, "mats": mats,
                      "timing": timing(n), "compact": config.LOOK == "crossfade",
                      "materials": [{"name": m["name"], "qty": m.get("qty", "")} for m in script["materials"]],
                      "hasLinks": has_links}}


def encode_final(raw, out, seconds):
    _run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-t", f"{seconds:.3f}", "-c:v", "libx264", "-profile:v", "high",
          "-crf", "20", "-preset", "medium", "-pix_fmt", "yuv420p", "-r", str(FPS), "-g", "60", "-keyint_min", "60",
          "-sc_threshold", "0", "-flags", "+cgop", "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-ac", "2",
          "-af", "alimiter=limit=0.89", "-movflags", "+faststart", str(out)])
    return out


def probe(path):
    info = json.loads(_run(["ffprobe", "-v", "error", "-show_entries",
                            "stream=codec_type,codec_name,profile,width,height,avg_frame_rate,sample_rate,channels,pix_fmt"
                            ":format=duration,size", "-of", "json", str(path)]))
    _run(["ffmpeg", "-v", "error", "-xerror", "-i", str(path), "-f", "null", "-"])
    vol = subprocess.run(["ffmpeg", "-i", str(path), "-af", "volumedetect", "-vn", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    peak = float(vol.split("max_volume:")[1].split("dB")[0]) if "max_volume:" in vol else None
    v = next(s for s in info["streams"] if s["codec_type"] == "video")
    a = next((s for s in info["streams"] if s["codec_type"] == "audio"), {})
    return {"width": v["width"], "height": v["height"], "vcodec": v["codec_name"], "pix_fmt": v.get("pix_fmt"),
            "fps": v["avg_frame_rate"], "acodec": a.get("codec_name"), "sample_rate": a.get("sample_rate"),
            "channels": a.get("channels"), "duration_s": round(float(info["format"]["duration"]), 3),
            "size_mb": round(int(info["format"]["size"]) / 1e6, 2), "peak_dbfs": peak, "decode_ok": True}


def check(p, n):
    errs = []
    if (p["width"], p["height"]) != (1080, 1920): errs.append("dimensions")
    if p["vcodec"] != "h264" or p["acodec"] != "aac": errs.append("codecs")
    if p["fps"] != "30/1": errs.append("fps")
    if not 20.0 <= p["duration_s"] <= 30.05: errs.append(f"duration {p['duration_s']}")
    if p["size_mb"] > 50: errs.append("size")
    if p["peak_dbfs"] is None or p["peak_dbfs"] > -1.0: errs.append(f"peak {p['peak_dbfs']}")
    if step_seconds(n) < (1.2 if config.LOOK == "crossfade" else 2.5): errs.append("step too short")
    if errs:
        raise RenderError("video checks failed: " + ", ".join(errs))
    return True


def render(script, frames_dir, out_mp4, workdir=None):
    work = Path(workdir or tempfile.mkdtemp(prefix="diy-render-")); work.mkdir(parents=True, exist_ok=True)
    props = build_public(script, frames_dir, None, work / "public")
    (work / "props.json").write_text(json.dumps(props, ensure_ascii=False))
    if not (REMOTION / "node_modules").exists():
        raise RenderError("run `npm ci --prefix diyvideo/remotion` first")
    _run(["node", str(REMOTION / "render.mjs"), str(work / "public"), str(work / "props.json"), str(work / "raw.mp4")],
         env={**os.environ})
    n = len(script["steps"])
    encode_final(work / "raw.mp4", out_mp4, total_seconds(n))
    p = probe(out_mp4); check(p, n)
    return p
