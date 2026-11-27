from pathlib import Path
_DIR = Path(__file__).parent / "prompts"


def load(name):
    return (_DIR / f"{name}.txt").read_text(encoding="utf-8")


def fill(template, **values):
    # literal replacement so braces inside source text are never interpreted
    for k, v in values.items():
        template = template.replace("{" + k + "}", str(v))
    return template
