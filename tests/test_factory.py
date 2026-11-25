import json
import subprocess
import sys
import tempfile
import unittest
import wave
from array import array
from pathlib import Path

from factory.core import Checkpoints
from factory.pipelines import MockProvider, duration, educational_data, social_dry_run, subtitle_and_dub


class FactoryTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.state = Checkpoints(self.root / "jobs.sqlite")

    def fixture(self, name, output):
        subprocess.run([sys.executable, f"examples/{name}/make_fixture.py", output], check=True)

    def test_reference_education(self):
        pdf = self.root / "textbook.pdf"
        self.fixture("documents", pdf)
        result, cached = educational_data(pdf, self.state)
        self.assertFalse(cached)
        self.assertEqual(result["data"], [
            {"question": "Define Evaporation.", "answer": "Liquid water becomes vapor.",
             "page": 1, "quote": "Evaporation = Liquid water becomes vapor."},
            {"question": "Define Condensation.", "answer": "Water vapor becomes liquid.",
             "page": 1, "quote": "Condensation = Water vapor becomes liquid."},
        ])
        self.assertEqual(result["usage"]["cost_usd"], 0)
        self.assertEqual(educational_data(pdf, self.state), (result, True))

    def test_rejects_ungrounded_answer(self):
        class Incorrect(MockProvider):
            def complete(self, text, transform):
                result = super().complete(text, transform)
                result["data"][0]["answer"] = "Incorrect"
                return result

        pdf = self.root / "textbook.pdf"
        self.fixture("documents", pdf)
        with self.assertRaisesRegex(ValueError, "disagrees"):
            educational_data(pdf, self.state, Incorrect())
        self.assertFalse(educational_data(pdf, self.state)[1])

    def test_retry_recovery_and_idempotency(self):
        calls = []

        def produce():
            calls.append(1)
            if len(calls) == 1:
                raise TimeoutError()
            return {"count": 1}

        def evaluate(result):
            self.assertEqual(result, {"count": 1})

        self.assertEqual(self.state.run(["job"], produce, evaluate), ({"count": 1}, False))
        reopened = Checkpoints(self.root / "jobs.sqlite")
        self.assertEqual(reopened.run(["job"], produce, evaluate), ({"count": 1}, True))
        self.assertEqual(len(calls), 2)

    def test_worker_interruption_releases_unfinished_job(self):
        interrupted = subprocess.run([
            sys.executable, "-c",
            "import os, sys; from factory.core import Checkpoints; "
            "Checkpoints(sys.argv[1]).run(['interrupted'], lambda: os._exit(23), print)",
            str(self.state.path),
        ])
        self.assertEqual(interrupted.returncode, 23)
        result = self.state.run(["interrupted"], lambda: {"ready": True}, self.assertTrue)
        self.assertEqual(result, ({"ready": True}, False))

    def test_social_batch_recovers_after_invalid_input(self):
        invalid = self.root / "invalid.json"
        invalid.write_text("{}")
        completed = subprocess.run([
            sys.executable, "-m", "factory", "--state", str(self.root / "batch.sqlite"),
            "social", str(invalid), "examples/social/sample.json",
        ], capture_output=True, text=True)
        self.assertEqual(completed.returncode, 1)
        bad, good = map(json.loads, completed.stdout.splitlines())
        self.assertIn("error", bad)
        self.assertEqual(good["result"]["data"]["action"], "dry_run")
        self.assertEqual(good["result"]["usage"]["cost_usd"], 0)

    def test_speech_sync_and_duration(self):
        audio = self.root / "input.wav"
        self.fixture("speech", audio)
        subtitle_and_dub(audio, self.root)
        srt = (self.root / "subtitles.srt").read_text()
        self.assertIn("00:00:00,000 --> 00:00:01,000\nHola, clase.", srt)
        self.assertIn("00:00:01,250 --> 00:00:02,250\nHasta pronto.", srt)
        dub = self.root / "dub.wav"
        self.assertAlmostEqual(duration(dub), 2.5, places=2)
        with wave.open(str(dub)) as track:
            self.assertEqual((track.getnchannels(), track.getframerate(), track.getsampwidth()),
                             (1, 16000, 2))
            samples = array("h", track.readframes(track.getnframes()))
        if sys.byteorder != "little":
            samples.byteswap()
        self.assertGreater(max(map(abs, samples[:16000])), 100)
        self.assertEqual(max(map(abs, samples[16000:20000])), 0)
        self.assertGreater(max(map(abs, samples[20000:36000])), 100)
        self.assertLess(max(map(abs, samples)), 32767)
