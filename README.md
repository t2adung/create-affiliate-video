# AI Content Factory Template

A Codex Cloud and Codex CLI starter for building document intelligence, structured
AI generation, media, and automation tools.

## Start a project

Clone or fork this repository. In Codex Cloud select the project repository and
start a review branch. With Codex CLI, run `codex` from the checkout.

1. Write a few sentences in [RAW_IDEA.md](RAW_IDEA.md) or paste them into chat
   and ask Codex to run Idea Builder. Vietnamese and English both work.
2. Use INTERACTIVE for essential questions (the default), QUICK to move ahead
   with reasonable assumptions, or RESEARCH to compare options and costs.
3. Review the proposed IDEA.md and its Vietnamese summary. Explicitly approve
   the presented revision or ask for changes.
4. After approval, Codex sets up the project plan in PLANS.md and hands it to
   the factory orchestrator. On a new session, ask Codex to resume from
   IDEA_REVIEW.md or PLANS.md.

For example, write “Tôi muốn biến ghi chú bài học thành thẻ hỏi đáp có dẫn
nguồn để học sinh ôn tập.” See [Idea Discovery](docs/workflows/idea-discovery.md)
and [three draft specifications](docs/examples/idea-builder/).

## Run the examples

Use Python 3.12+, FFmpeg and ffprobe on PATH for audio/video, and Node.js 22+
for Remotion. Install the optional document or video dependencies only when
using those examples.

```sh
mkdir -p out

# PDF text layer → cited question/answer records
python -m pip install -r requirements-documents.txt
python examples/documents/make_fixture.py out/lesson.pdf
python -m factory education out/lesson.pdf

# Fixture speech → translated SRT and timed dub WAV
python examples/speech/make_fixture.py out/lesson.wav
python -m factory speech out/lesson.wav out/dub

# JSON → H.264 MP4
npm ci --prefix examples/video
node examples/video/render.mjs examples/video/sample.json out/lesson.mp4

# Fact JSON → publishing preview
python -m factory social examples/social/sample.json
```

The PDF example accepts text-layer documents containing `Term = Definition`
lines. Its independent verifier checks each answer against the cited text,
checks record coverage and rejects fabricated answers. The speech provider
supplies a fixed transcript, phrase translations and synthetic timing tones.
Replace it with an ASR, translation and TTS adapter for real recordings.
The Remotion example accepts a bounded ASCII title and subtitle and checks
resolution, frame count, codec and full decode before replacing the result.
The social preview accepts exactly two strings, `topic` and `fact`, and
returns caption, action and estimated usage. The preview has no publishing client.

Pass multiple paths to `education` or `social` for JSONL batch output. Use
`python -m factory --state .factory/jobs.sqlite ...` to specify the SQLite path.
Reruns with identical inputs and provider version reuse evaluated results.
Timeouts receive one retry. Invalid inputs produce per-file errors and a
nonzero exit after the rest of the batch. SQLite serializes work per database
and stores generated results locally. Use a restricted directory for private
state and delete it according to the project's retention policy.

## Verify

Run `scripts/verify.sh` after installing document and video dependencies.
Set `PYTHON` for a virtual environment interpreter and `CHROME_BIN` for a
local Chromium installation. GitHub Actions runs the same checks, including
structural checks for Idea Discovery and its examples. To run only those
checks, use `python -m unittest discover -s tests -p test_idea_discovery.py -v`.
See [verification evidence](docs/verification.md) and
[fixture provenance](examples/ASSETS.md). Live model evaluation, speech
intelligibility, and external publishing require project-specific adapters,
reference datasets, and approvals.
