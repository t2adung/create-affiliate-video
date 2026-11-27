"""Provider interfaces and deterministic mocks used by tests and CI (no network, zero cost)."""
import hashlib, json, re
import cv2, numpy as np


class Result:
    """value + model id + usage token counts {"in", "text_out", "image_out"}."""

    def __init__(self, value, model, usage, tier="standard"):
        self.value, self.model, self.usage, self.tier = value, model, usage, tier


class MockText:
    model = "mock"

    def __init__(self, override=None):
        self.override = override
        self.calls = 0

    def generate_json(self, prompt):
        self.calls += 1
        if self.override is not None:
            value = self.override(prompt, self.calls) if callable(self.override) else self.override
            return Result(value=value, model=self.model, usage={"in": len(prompt) // 4, "text_out": 400})
        src = prompt.rsplit("<<<SOURCE", 1)[1].rsplit("SOURCE>>>", 1)[0]
        lines = [l.strip("- ").strip() for l in src.splitlines() if l.strip().startswith("- ")]
        steps_src = [l for l in lines if len(l) > 25][:10] or lines[:6]
        while len(steps_src) < 6:
            steps_src.append(f"Kiểm tra lại và hoàn thiện phần {len(steps_src) + 1}")
        n = len(steps_src)
        keys = {2, 4, 6} if n >= 6 else {2, 3, 4}
        steps = [{"n": i + 1, "on_screen": f"Bước {i + 1}: " + " ".join(s.split()[:6])[:48],
                  "detail": f"Thực hiện thao tác số {i + 1} thật cẩn thận rồi kiểm tra lại.",
                  "image_prompt": f"overhead scene after step {i + 1}", "required_objects": ["object"],
                  "key": (i + 1) in keys} for i, s in enumerate(steps_src)]
        title = next((l.strip() for l in src.splitlines() if l.strip()), "Hướng dẫn DIY")[:60]
        value = {"title": title, "summary": "Tóm tắt hướng dẫn DIY từng bước.",
                 "materials": [{"name": "Vật liệu chính", "qty": "1"}], "safety_notes": [],
                 "scene": "objects centred on the surface", "steps": steps,
                 "caption": "Làm theo từng bước nhé!\nNội dung có sử dụng hình ảnh AI", "hashtags": ["#diy", "#meovat"]}
        return Result(value=value, model=self.model, usage={"in": len(prompt) // 4, "text_out": 900})


class MockImage:
    """Draws a deterministic 9:16 scene: textured static background + progress-dependent shapes.
    `drift` maps frame label -> (dx, dy, scale) to simulate a camera move."""
    model = "mock"

    def __init__(self, drift=None, w=432, h=768):
        self.drift = drift or {}
        self.w, self.h = w, h
        self.calls = []

    def background(self):
        rng = np.random.default_rng(7)
        bg = (rng.random((self.h, self.w, 3)) * 60 + 120).astype(np.uint8)
        bg = cv2.GaussianBlur(bg, (0, 0), 1.2)
        for i in range(40):  # wood-grain-like static features for the framing gate
            y = int(rng.integers(0, self.h)); x = int(rng.integers(0, self.w))
            cv2.circle(bg, (x, y), int(rng.integers(3, 9)), (60, 80, 110), -1)
        return bg

    def generate(self, prompt, refs, label, job_key=None):
        self.calls.append(label)
        m = re.search(r"progress=(\d+)", prompt)
        progress = int(m.group(1)) if m else len(self.calls)
        img = self.background()
        for i in range(progress):  # objects accumulate with progress
            cx = self.w // 2 + int(60 * np.sin(i)); cy = self.h // 3 + 25 * i % (self.h // 2)
            cv2.rectangle(img, (cx - 18, cy - 10), (cx + 18, cy + 10), (40, 160 - 10 * i % 120, 200), -1)
        hy = self.h - 160 + (progress % 4) * 12  # "hands" from the bottom edge
        cv2.ellipse(img, (self.w // 2 - 60, hy), (40, 70), 0, 0, 360, (170, 190, 230), -1)
        cv2.ellipse(img, (self.w // 2 + 60, hy), (40, 70), 0, 0, 360, (170, 190, 230), -1)
        if label in self.drift:
            dx, dy, s = self.drift[label]
            M = cv2.getRotationMatrix2D((self.w / 2, self.h / 2), 0, s); M[0, 2] += dx; M[1, 2] += dy
            img = cv2.warpAffine(img, M, (self.w, self.h), borderMode=cv2.BORDER_REFLECT)
        ok, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 92])
        return Result(value=buf.tobytes(), model=self.model, usage={"in": 50, "text_out": 0, "image_out": 1120})


class MockVerifier:
    model = "mock"

    def __init__(self, script=None):
        self.script = script or {}  # label -> dict overrides
        self.calls = []

    def check(self, prev, cur, step_text, required, label):
        self.calls.append(label)
        v = {"face_visible": False, "head_or_shoulders_visible": False, "hands_ok": True, "matches_step": True,
             "continuity_ok": True, "required_objects_present": True, "text_or_logo": False, "issues": ""}
        v.update(self.script.get(label, {}))
        return Result(value=v, model=self.model, usage={"in": 600, "text_out": 80})


def verdict_pass(v):
    return bool(v.get("hands_ok") and v.get("matches_step") and v.get("continuity_ok")
                and v.get("required_objects_present") and not v.get("face_visible")
                and not v.get("head_or_shoulders_visible") and not v.get("text_or_logo")
                and "face_visible" in v and "hands_ok" in v)
