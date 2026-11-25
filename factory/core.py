"""Local batch checkpoints. A checkpoint is committed only after output evaluation."""
import hashlib
import json
import sqlite3
from pathlib import Path


def encode(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False)


class Checkpoints:
    def __init__(self, path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path

    def run(self, specification, produce, evaluate, attempts=2):
        if not isinstance(attempts, int) or attempts < 1:
            raise ValueError("Expected at least one attempt")
        key = hashlib.sha256(encode(specification).encode()).hexdigest()
        connection = sqlite3.connect(self.path, timeout=60)
        try:
            with connection:
                connection.execute(
                    "CREATE TABLE IF NOT EXISTS jobs (key TEXT PRIMARY KEY, result TEXT NOT NULL)"
                )
                connection.execute("BEGIN IMMEDIATE")
                existing = connection.execute(
                    "SELECT result FROM jobs WHERE key = ?", (key,)
                ).fetchone()
                if existing:
                    result = json.loads(existing[0])
                    evaluate(result)
                    return result, True
                for attempt in range(attempts):
                    try:
                        result = produce()
                        break
                    except TimeoutError:
                        if attempt + 1 == attempts:
                            raise
                evaluate(result)
                connection.execute("INSERT INTO jobs VALUES (?, ?)", (key, encode(result)))
                return result, False
        finally:
            connection.close()
