# Verification

Local environment: Python 3.12.14, Node.js 24.22.3, Chromium 156 and FFmpeg 7.1.5.

| Check | Command and evidence |
| --- | --- |
| Python references | Passed. The first step of `scripts/verify.sh` ran six tests covering PDF extraction against two reference answers, an unsupported-answer negative control, batch partial failure, simulated process interruption, retry, checkpoint reuse, subtitle timing and WAV format/signal checks. |
| Remotion and FFmpeg | Passed. `scripts/verify.sh` renders the reference JSON and maximum-length fixture through Chromium. The composition checks the text safe area. Each video is probed for H.264, 640×360 and 24 frames, then fully decoded. An over-limit title must fail before producing a file. |
| Node dependency audit | `npm --prefix examples/video audit --omit=dev --audit-level=high` reported zero vulnerabilities after updating Remotion to 4.0.547. |
| Asset origins and privacy | The examples use locally generated fixtures listed in examples/ASSETS.md. The publishing workflow builds a local payload. Structured mock results report estimated tokens and zero API cost. |

Run the suite with
`PYTHON=.venv/bin/python CHROME_BIN=/usr/bin/chromium scripts/verify.sh`.

Evaluation measures the supplied synthetic fixtures. Real speech recognition,
translation quality, voice intelligibility, production-scale recovery and
live publishing require project-specific adapters and evaluation. Checkpoint
recovery and caching apply to the structured PDF and social batches. Media
uses temporary files and validates before writing final outputs.

## Idea Builder

The full `scripts/verify.sh` suite passed locally using Python 3.12.14,
Node.js v24.22.3, Chromium 156 and FFmpeg 7.1.5. It ran 10 Python tests
(six reference pipeline tests and four Idea Builder tests), rendered and
decoded both video fixtures, and rejected the out-of-bounds video input.

The four structural checks cover the intake and review templates, discovery
modes and approval gate text, local links, and three filled specifications
with an acceptance check for each MVP requirement. They run in the existing
GitHub Actions quality job and require no provider calls. The examples are
synthetic drafts. Live conversational behavior and real user approval are
outside the automated checks.
