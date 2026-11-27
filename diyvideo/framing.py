"""Free framing gate: similarity transform between consecutive frames from static features (research R10)."""
import math
import cv2, numpy as np

MAX_SCALE_DEV, MAX_ROT_DEG, MAX_SHIFT_PX, MIN_INLIER_RATIO = 0.02, 1.0, 20.0, 0.30
_sift = cv2.SIFT_create(4000)
_bf = cv2.BFMatcher()


def decode(b):
    return cv2.imdecode(np.frombuffer(b, np.uint8), cv2.IMREAD_COLOR)


def measure(prev_bytes, cur_bytes):
    a = cv2.cvtColor(decode(prev_bytes), cv2.COLOR_BGR2GRAY); b = cv2.cvtColor(decode(cur_bytes), cv2.COLOR_BGR2GRAY)
    k1, d1 = _sift.detectAndCompute(a, None); k2, d2 = _sift.detectAndCompute(b, None)
    if d1 is None or d2 is None or len(k1) < 2 or len(k2) < 2:
        return {"pass": False, "reason": "no_features"}
    good = [m for m, n in (p for p in _bf.knnMatch(d2, d1, k=2) if len(p) == 2) if m.distance < .75 * n.distance]
    if len(good) < 12:
        return {"pass": False, "reason": "few_matches", "matches": len(good)}
    A, inl = cv2.estimateAffinePartial2D(np.float32([k2[m.queryIdx].pt for m in good]),
                                         np.float32([k1[m.trainIdx].pt for m in good]),
                                         method=cv2.RANSAC, ransacReprojThreshold=4)
    if A is None:
        return {"pass": False, "reason": "no_transform"}
    s = math.hypot(A[0, 0], A[1, 0]); r = math.degrees(math.atan2(A[1, 0], A[0, 0])); sh = math.hypot(A[0, 2], A[1, 2])
    ratio = int(inl.sum()) / len(good)
    ok = ratio >= MIN_INLIER_RATIO and abs(s - 1) < MAX_SCALE_DEV and abs(r) < MAX_ROT_DEG and sh < MAX_SHIFT_PX
    return {"pass": ok, "reason": "ok" if ok else "drift", "scale": round(s, 4), "rot_deg": round(r, 3),
            "shift_px": round(sh, 2), "inlier_ratio": round(ratio, 3), "matrix": A.tolist()}


def correct(cur_bytes, m):
    """Warp a frame that passed the gate with small non-zero drift back onto the previous framing."""
    if not m.get("pass") or m["shift_px"] < 0.75:
        return cur_bytes
    img = decode(cur_bytes); h, w = img.shape[:2]
    out = cv2.warpAffine(img, np.array(m["matrix"]), (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
    return cv2.imencode(".jpg", out, [cv2.IMWRITE_JPEG_QUALITY, 94])[1].tobytes()
