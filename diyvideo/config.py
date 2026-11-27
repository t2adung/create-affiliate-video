"""Prices, caps and limits. Prices: official Gemini pricing page read 2026-11-26 (docs/research.md R1)."""
PRICING_VERSION = "gemini-2026-11-26"
VND_PER_USD = 26000
CAP_GUIDE_VND = 15000
CAP_MONTH_VND = 900000
MAX_NEW_GUIDES_PER_RUN = 2
# USD per 1M tokens (standard tier); batch halves every rate.
PRICES = {
    "gemini-3.5-flash-lite": {"in": 0.30, "out": 2.50, "image_out": 0.0},
    "gemini-3.5-flash": {"in": 1.50, "out": 9.00, "image_out": 0.0},
    "gemini-nano-banana-2.1": {"in": 1.50, "out": 7.50, "image_out": 30.0},
    "mock": {"in": 0.0, "out": 0.0, "image_out": 0.0},
}
EST_FRAME_USD = {"standard": 0.050, "batch": 0.025}
EST_TEXT_USD = 0.02
SCRIPT_MODEL = "gemini-3.5-flash-lite"
IMAGE_MODEL = "gemini-nano-banana-2.1"
VERIFY_MODEL = "gemini-3.5-flash"
PROMPT_VERSIONS = {"script": "script_v1", "image": "image_v2", "verify": "verify_v2"}
FETCH_MAX_BYTES = 2 * 1024 * 1024
FETCH_TIMEOUT_S = 20
SOURCE_MAX_CHARS = 20000
TOPICS = ("noel", "don-dep", "meo-don-dep", "tet", "cam-hoa", "khac")
AI_CAPTION_LINE = "Nội dung có sử dụng hình ảnh AI"


def usd_from_usage(model, usage, tier="standard"):
    """usage: dict with in, text_out (incl. thinking), image_out token counts."""
    p = PRICES[model]
    usd = (usage.get("in", 0) * p["in"] + usage.get("text_out", 0) * p["out"]
           + usage.get("image_out", 0) * p["image_out"]) / 1e6
    return usd / 2 if tier == "batch" else usd
