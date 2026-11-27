"""Style library: per-video looks so consecutive videos differ (IDEA revision 4)."""
STYLES = [
    # bright, warm looks first (user reference video, 2026-11-27); darker looks remain as fallbacks
    {"id": "noel-bright-cosy", "topics": ["noel"], "surface": "warm honey-wood table",
     "sleeve": "no sleeves visible", "light": "bright warm daylight with glowing fairy-light bokeh, lanterns and gift boxes",
     "palette": "cream white, Christmas red, pine green, gold"},
    {"id": "flower-bright-linen", "topics": ["cam-hoa", "tet"], "surface": "light oak table with a white linen runner",
     "sleeve": "no sleeves visible", "light": "soft bright morning window light, airy and fresh, blurred plants behind",
     "palette": "white, blush pink, sage green, soft yellow"},
    {"id": "clean-bright-kitchen", "topics": ["don-dep", "meo-don-dep"], "surface": "white quartz kitchen counter",
     "sleeve": "no sleeves visible", "light": "bright clean daylight, blurred white tiles and potted herbs behind",
     "palette": "white, fresh mint, lemon yellow, light grey"},
    {"id": "tet-bright-festive", "topics": ["tet"], "surface": "light wooden table with a red silk runner",
     "sleeve": "no sleeves visible", "light": "bright warm sunlight, blurred apricot blossoms and red lanterns behind",
     "palette": "lucky red, gold, warm yellow, cream"},
    {"id": "noel-forest-linen", "topics": ["noel"], "surface": "dark moss-green linen tablecloth",
     "sleeve": "burgundy knit sweater sleeves", "light": "warm evening lamp light with soft golden bokeh",
     "palette": "deep green, burgundy, warm gold"},
    {"id": "noel-white-oak", "topics": ["noel"], "surface": "pale whitewashed oak table",
     "sleeve": "cream cable-knit sweater sleeves", "light": "soft cool daylight from a window",
     "palette": "white, silver, pine green"},
    {"id": "tet-lacquer-red", "topics": ["tet"], "surface": "glossy red lacquer tray on a dark teak table",
     "sleeve": "mustard yellow long sleeves", "light": "bright morning sunlight, crisp shadows",
     "palette": "lucky red, gold, warm yellow"},
    {"id": "tet-bamboo-mat", "topics": ["tet", "cam-hoa"], "surface": "natural woven bamboo mat",
     "sleeve": "ivory linen long sleeves", "light": "late-afternoon golden sun at a low angle",
     "palette": "straw beige, peach pink, jade green"},
    {"id": "clean-white-marble", "topics": ["don-dep", "meo-don-dep"], "surface": "white Carrara marble countertop",
     "sleeve": "light grey cotton sleeves with yellow rubber gloves where cleaning", "light": "bright neutral daylight",
     "palette": "white, grey, lemon yellow"},
    {"id": "clean-slate-kitchen", "topics": ["don-dep", "meo-don-dep"], "surface": "dark slate stone countertop",
     "sleeve": "denim-blue rolled sleeves", "light": "clean soft overhead light",
     "palette": "charcoal, denim blue, fresh mint"},
    {"id": "flower-pastel-linen", "topics": ["cam-hoa", "khac"], "surface": "pastel blush linen cloth",
     "sleeve": "sage green knit sleeves", "light": "soft diffused window light",
     "palette": "blush pink, sage, cream"},
    {"id": "craft-kraft-paper", "topics": ["khac", "noel", "tet"], "surface": "brown kraft paper over a wooden desk",
     "sleeve": "navy striped sleeves", "light": "even studio softbox light",
     "palette": "kraft brown, navy, white"},
    {"id": "home-terrazzo", "topics": ["khac", "don-dep", "cam-hoa"], "surface": "speckled terrazzo tabletop",
     "sleeve": "terracotta knit sleeves", "light": "warm morning daylight",
     "palette": "terracotta, sand, olive"},
]


def pick(topic, previous_id=None):
    for pool in ([s for s in STYLES if topic in s["topics"]], STYLES):
        for s in pool:
            if s["id"] != previous_id:
                return s
    raise LookupError("no style available")


def describe(style):
    return (f"Surface: {style['surface']}. Sleeves: {style['sleeve']}. Lighting: {style['light']}. "
            f"Colour palette: {style['palette']}.")
