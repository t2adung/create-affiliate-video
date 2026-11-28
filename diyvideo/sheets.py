"""Sheet storage. LocalSheetStore keeps Sheet A/B as a JSON file (tests, local runs); the Google Sheets adapter
implements the same three methods."""
import json
from pathlib import Path

B_EDITABLE = ("title", "summary", "materials", "steps", "safety_notes", "caption", "hashtags", "status")


class LocalSheetStore:
    def __init__(self, path):
        self.path = Path(path)
        if not self.path.exists():
            self.path.write_text(json.dumps({"A": [], "B": []}, ensure_ascii=False, indent=1))

    def _load(self):
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _save(self, d):
        tmp = self.path.with_suffix(".tmp"); tmp.write_text(json.dumps(d, ensure_ascii=False, indent=1)); tmp.replace(self.path)

    def rows_a(self):
        return self._load()["A"]

    def update_a(self, index, **fields):
        d = self._load(); d["A"][index].update(fields); self._save(d)

    def rows_b(self):
        return self._load()["B"]

    def upsert_b(self, guide_id, **fields):
        d = self._load()
        row = next((r for r in d["B"] if r.get("guide_id") == guide_id), None)
        if row is None:
            row = {"guide_id": guide_id}; d["B"].append(row)
        row.update(fields); self._save(d)
        return row


def steps_to_cells(script):
    """Sheet B text cells as specified (one line per item)."""
    return {
        "materials": "\n".join(f"{m['name']} | {m.get('qty', '')} | {m.get('link', '')}" for m in script["materials"]),
        "steps": "\n".join(f"{s['n']} | {s['on_screen']} | {s['detail']}" for s in script["steps"]),
        "safety_notes": "\n".join(script.get("safety_notes") or []),
        "hashtags": " ".join(script["hashtags"]),
    }
