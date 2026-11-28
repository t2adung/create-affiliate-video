"""SQLite run state: committed stage results, cost records and publish records, plus the cost guard."""
import json, sqlite3, time
from datetime import datetime, timezone
from pathlib import Path
from . import config


class CostCapExceeded(RuntimeError):
    pass


class Ledger:
    def __init__(self, path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path, timeout=60)
        with self.db:
            self.db.execute("CREATE TABLE IF NOT EXISTS results (key TEXT PRIMARY KEY, value TEXT NOT NULL, ts REAL)")
            self.db.execute("CREATE TABLE IF NOT EXISTS costs (id INTEGER PRIMARY KEY, guide TEXT, label TEXT,"
                            " model TEXT, usd REAL, month TEXT, ts REAL)")
            self.db.execute("CREATE TABLE IF NOT EXISTS batches (key TEXT PRIMARY KEY, job TEXT, ts REAL)")
            self.db.execute("CREATE TABLE IF NOT EXISTS publish (guide TEXT, platform TEXT, state TEXT, url TEXT,"
                            " PRIMARY KEY (guide, platform))")

    # committed results -------------------------------------------------
    def get(self, key):
        row = self.db.execute("SELECT value FROM results WHERE key = ?", (key,)).fetchone()
        return json.loads(row[0]) if row else None

    def put(self, key, value):
        with self.db:
            self.db.execute("INSERT OR REPLACE INTO results VALUES (?, ?, ?)",
                            (key, json.dumps(value, ensure_ascii=False, sort_keys=True), time.time()))

    # pending batch jobs (resumable across runs) ----------------------------
    def batch_job(self, key):
        row = self.db.execute("SELECT job FROM batches WHERE key = ?", (key,)).fetchone()
        return row[0] if row else None

    def set_batch_job(self, key, job):
        with self.db:
            if job is None:
                self.db.execute("DELETE FROM batches WHERE key = ?", (key,))
            else:
                self.db.execute("INSERT OR REPLACE INTO batches VALUES (?, ?, ?)", (key, job, time.time()))

    # costs -------------------------------------------------------------
    @staticmethod
    def month(now=None):
        return (now or datetime.now(timezone.utc)).strftime("%Y-%m")

    def record(self, guide, label, model, usd):
        with self.db:
            self.db.execute("INSERT INTO costs (guide, label, model, usd, month, ts) VALUES (?, ?, ?, ?, ?, ?)",
                            (guide, label, model, usd, self.month(), time.time()))

    def spent_vnd(self, guide=None, month=None):
        q, args = "SELECT COALESCE(SUM(usd), 0) FROM costs WHERE month = ?", [month or self.month()]
        if guide:
            q, args = "SELECT COALESCE(SUM(usd), 0) FROM costs WHERE guide = ?", [guide]
        return self.db.execute(q, args).fetchone()[0] * config.VND_PER_USD

    def guard(self, guide, next_usd):
        """Raise before a request that could push the guide or the month over its cap."""
        nxt = next_usd * config.VND_PER_USD
        if self.spent_vnd(guide=guide) + nxt > config.CAP_GUIDE_VND:
            raise CostCapExceeded(f"guide {guide}: {self.spent_vnd(guide=guide):.0f} + {nxt:.0f} VND > "
                                  f"{config.CAP_GUIDE_VND} VND")
        if self.spent_vnd() + nxt > config.CAP_MONTH_VND:
            raise CostCapExceeded(f"month: {self.spent_vnd():.0f} + {nxt:.0f} VND > {config.CAP_MONTH_VND} VND")

    def preflight(self, guide, frames, tier="batch"):
        est = frames * config.EST_FRAME_USD[tier] + config.EST_TEXT_USD
        self.guard(guide, est)
        return est * config.VND_PER_USD

    # publishing ----------------------------------------------------------
    def publish_state(self, guide, platform):
        row = self.db.execute("SELECT state, url FROM publish WHERE guide = ? AND platform = ?",
                              (guide, platform)).fetchone()
        return row

    def set_publish(self, guide, platform, state, url=None):
        with self.db:
            self.db.execute("INSERT OR REPLACE INTO publish VALUES (?, ?, ?, ?)", (guide, platform, state, url))
