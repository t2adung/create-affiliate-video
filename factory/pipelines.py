"""Offline reference pipelines with synthetic fixtures and deterministic providers."""
import hashlib
import json
import re
import subprocess
import tempfile
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


class MockProvider:
    name = "mock-v1"

    def complete(self, text, transform):
        result = transform(text)
        return {
            "data": result,
            "usage": {
                "provider": self.name,
                "estimated_input_tokens": len(text.split()),
                "estimated_output_tokens": len(json.dumps(result).split()),
                "cost_usd": 0,
            },
        }


def educational_data(pdf, checkpoints, provider=None):
    import pymupdf

    provider = provider or MockProvider()
    content = Path(pdf).read_bytes()
    with pymupdf.open(stream=content, filetype="pdf") as document:
        pages = [page.get_text() for page in document]
    # The fixture grammar is explicit so a verifier can derive answers from source.
    pattern = re.compile(r"^([A-Za-z0-9 -]{1,60}) = ([^\n]{1,120})$", re.MULTILINE)
    source = {
        (number, match.group(0))
        for number, page in enumerate(pages, 1)
        for match in pattern.finditer(page)
    }
    require(bool(source), "PDF must contain at least one 'Term = Definition' line")

    def generate(_):
        return list({
            (number, match.group(0)): {"question": f"Define {match.group(1)}.", "answer": match.group(2),
             "page": number, "quote": match.group(0)}
            for number, page in enumerate(pages, 1)
            for match in pattern.finditer(page)
        }.values())

    def verify(result):
        rows = result["data"]
        require(isinstance(rows, list) and bool(rows), "Expected educational records")
        observed = set()
        for row in rows:
            require(isinstance(row, dict) and set(row) == {"question", "answer", "page", "quote"}, "Invalid record schema")
            require(type(row["page"]) is int and all(
                isinstance(row[field], str) for field in ("question", "answer", "quote")
            ), "Invalid record types")
            citation = (row["page"], row["quote"])
            require(citation in source, "Citation absent from source")
            term, answer = row["quote"].split(" = ", 1)
            require(row["answer"] == answer and row["question"] == f"Define {term}.",
                    "Answer or question disagrees with the cited text")
            observed.add(citation)
        require(observed == source and len(rows) == len(source),
                "Missing or duplicate source records")

    key = ["education-v1", provider.name, hashlib.sha256(content).hexdigest()]
    return checkpoints.run(key, lambda: provider.complete("\n".join(pages), generate), verify)


def social_dry_run(source, checkpoints, provider=None):
    provider = provider or MockProvider()
    require(isinstance(source, dict) and set(source) == {"topic", "fact"}, "Expected topic and fact")
    require(all(isinstance(value, str) and 0 < len(value.strip()) <= 120
                and "\n" not in value for value in source.values()), "Invalid topic or fact")
    caption = f"{source['topic']}: {source['fact']}"

    def verify(result):
        require(result["data"] == {"caption": caption, "action": "dry_run"}
                and len(caption) <= 280, "Invalid or ungrounded preview")

    return checkpoints.run(
        ["social-v1", provider.name, source],
        lambda: provider.complete(caption, lambda text: {"caption": text, "action": "dry_run"}),
        verify,
    )


def media_command(*args):
    return subprocess.check_output(args, text=True, timeout=120)


class MockSpeech:
    """Fixture ASR, phrase translation and an audible timing stand-in for TTS."""
    name = "mock-speech-v1"
    translations = {"Hello class.": "Hola, clase.", "See you soon.": "Hasta pronto."}

    def transcribe(self, audio):
        require(Path(audio).is_file(), "Expected local audio")
        return [(0, 1000, "Hello class."), (1250, 2250, "See you soon.")]

    def translate(self, text):
        return self.translations[text]

    def synthesize(self, text, duration_ms, output):
        frequency = 440 + len(text) * 10
        media_command("ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                      f"sine=frequency={frequency}:sample_rate=16000",
                      "-t", str(duration_ms / 1000), str(output))


def duration(path):
    return float(media_command("ffprobe", "-v", "error", "-show_entries",
                               "format=duration", "-of", "csv=p=0",
                               "-protocol_whitelist", "file", str(Path(path).resolve())).strip())


def timestamp(milliseconds):
    seconds, fraction = divmod(milliseconds, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02},{fraction:03}"


def subtitle_and_dub(audio, destination, speech=None):
    speech = speech or MockSpeech()
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    audio_ms = round(duration(audio) * 1000)
    require(0 < audio_ms <= 60_000, "Reference pipeline supports clips up to one minute")
    previous = 0
    captions = []
    filters = []
    inputs = []
    with tempfile.TemporaryDirectory(dir=destination) as directory:
        stage = Path(directory)
        for index, (start, end, text) in enumerate(speech.transcribe(audio)):
            require(type(start) is int and type(end) is int and previous <= start < end <= audio_ms,
                    "Subtitle timing is invalid")
            translated = speech.translate(text)
            require(isinstance(translated, str) and 0 < len(translated) <= 84
                    and "\n" not in translated and "\r" not in translated, "Invalid subtitle text")
            captions.append(f"{index + 1}\n{timestamp(start)} --> {timestamp(end)}\n{translated}\n")
            segment = stage / f"{index}.wav"
            speech.synthesize(translated, end - start, segment)
            require(abs(duration(segment) - (end - start) / 1000) <= 0.03,
                    "Synthesized segment deviates from the subtitle duration")
            inputs.extend(["-i", str(segment)])
            filters.append(f"[{index}:a]adelay={start}:all=1[a{index}]")
            previous = end
        require(bool(captions), "No subtitle segments")
        mix = "".join(f"[a{index}]" for index in range(len(captions)))
        filters.append(f"{mix}amix=inputs={len(captions)},apad")
        dub = stage / "dub.wav"
        media_command("ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex",
                      ";".join(filters), "-t", str(audio_ms / 1000), "-ar", "16000", str(dub))
        require(abs(duration(dub) * 1000 - audio_ms) <= 25, "Dub duration mismatch")
        subtitles = stage / "subtitles.srt"
        subtitles.write_text("\n".join(captions), encoding="utf-8")
        subtitles.replace(destination / subtitles.name)
        dub.replace(destination / dub.name)
