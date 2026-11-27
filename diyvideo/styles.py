"""Style library: per-video looks so consecutive videos differ (IDEA revision 4)."""
STYLES = [
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
