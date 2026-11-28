# Pipeline design (Stage 4)

Implements the approved [IDEA.md](../IDEA.md) (revision 4) and follows the contracts in
[specification.md](specification.md) and the evidence in [research.md](research.md). This design
supersedes the specification where they differ:
- `steps/NN.jpg` (JPEG output) replaces PNG;
- the hook uses the last step image;
- the AI label shows from 0 to 3 s only.

## Package layout

```
diyvideo/
  config.py      pricing table (version gemini-2026-11-26), caps, exchange rate, paths
  ledger.py      SQLite state: jobs, costs, publish records; cost guard
  ingest.py      Sheet A row → source text (URL rules, SSRF guard, limits, HTML → text)
  styles.py      style library (≥8 looks) and per-guide selection
  script.py      source → Sheet B fields + image plan (versioned prompt, schema and copy checks)
  providers.py   interfaces + deterministic mocks (text, image, verifier)
  gemini.py      real Gemini Interactions API adapters (network; never used in CI)
  framing.py     free framing gate (SIFT + RANSAC similarity transform)
  images.py      chained generation: steps, key-step in-betweens, gate, verifier, retries
  render.py      Remotion props, keyframe interpolation clips (FFmpeg minterpolate), final encode, probes
  package.py     output folder, report.json, caption.txt
  sheets.py      SheetStore interface + LocalSheetStore (JSON); Google adapter in a later step
  cli.py         python -m diyvideo run|status
  remotion/      DIY composition (hook, steps, key-step clips, end card, 0–3 s AI label)
```

## Stages and stable keys

| # | Stage | Input → output | Key | Retries |
| --- | --- | --- | --- | --- |
| 1 | ingest | Sheet A row → text | `ingest:{source_id}:{sha(url or text)}` | 1 fetch retry |
| 2 | script | text + topic → script JSON | `script:{guide_id}:{sha(text)}:{prompt_v}` | 2 on schema failure |
| 3 | style | guide → `style_id` | stored on the guide row; avoids the previous guide's style | — |
| 4 | images | script + style → frames | `img:{guide_id}:{step}:{k}:{sha(prompt, prev_hash, model, prompt_v)}` | ≤2 per frame (gate or verifier fail), then flag |
| 5 | render | frames + script → mp4 | `render:{guide_id}:{sha(frames, editable fields, template_v)}` | 1 |
| 6 | package | mp4 + metadata → output folder, Sheet B update | `pkg:{guide_id}:{render_key}` | 3 with backoff (remote stores) |
| 7 | publish | approved package → posts | record `(guide_id, platform)` with state pending/done | 0 automatic; reconcile first |

A stage result is committed only after its evaluation passes. A restart skips committed keys, so finished
images are never billed again (MVP-9). Each run handles at most 2 new guides.

## Image plan

- The script marks 3–4 **key steps**. Each gets 2 in-between frames `k=1,2` before its final frame `k=3`;
  the final frame is the step image. Other steps have a single frame.
- Every frame is an edit of the previous frame. The step 1 image is sent as an anchor reference once it
  exists.
- The prompt carries:
  - a camera lock: tripod overhead, identical crop, objects stay unless the step moves them;
  - a hand lock: hands enter from the bottom edge, same sleeve;
  - the style's surface, sleeve, light and palette;
  - required objects for the step.
- Framing gate on each frame against the previous frame:
  - pass if the inlier ratio is ≥0.30, scale is within ±2%, rotation is <1° and shift is <20 px;
  - drift that is smaller than that but non-zero is warped back;
  - a failure regenerates the frame with a stricter lock line.
- Verifier: a separate request with only the previous and current image plus the step text and required
  objects. It returns booleans: face, hands, matches step, continuity, text or logo, and required objects
  present.
- Order: gate first (free), then the verifier on gated frames only. After 2 failed retries the frame is kept
  but flagged; a guide with flags stops at `needs_review` with `error: image_flagged`.

## Style library

At least 8 looks; each look defines surface, sleeve, light, palette and props. Selection is deterministic:
the first look for the guide's topic whose id differs from the previous guide's `style_id`. MVP-3 checks
that two consecutive guides receive different `style_id` values.

## Render

- Timeline:
  - hook: 2 s;
  - each step: min(3.0, 25/n) s, which is at least 2.5 s for n ≤ 10;
  - end card: 3 s.
- Key steps play an interpolated clip: frames prev→k1→k2→k3 are joined with FFmpeg `minterpolate` (mci/aobmc,
  bidir) at 30 fps. The clip is time-fitted to the step slot and holds the final frame for the last
  0.6 s, so the step text stays readable.
- The AI label "Hình ảnh tạo bởi AI" is ≤32 px tall at ≤60% opacity and shows from 0 to 3 s only.
- Final encode:
  - video: H.264 High, yuv420p, constant 30 fps, closed GOP 60, `-t` exact duration;
  - audio: AAC 48 kHz stereo, limiter at −1 dBFS.
- Probes: dimensions, fps, codec, duration 20–30 s, full decode, peak level.

## Cost guard

- Estimate before a guide starts: frames × $0.050 (pessimistic standard rate), or frames × $0.025 in Batch
  mode, plus $0.02 for text.
- Refuse the guide if the estimate exceeds 15,000 VND or month-to-date plus the estimate exceeds 900,000 VND.
- Check before each paid request again, using actual recorded costs. Actual costs come from response usage
  with the versioned price table.

## Providers and tests

- CI uses `MockText`, `MockImage` and `MockVerifier`:
  - `MockText` returns a fixture script built from the source steps;
  - `MockImage` draws a deterministic synthetic scene: a fixed textured background with moving shapes for
    "hands" and per-step objects. The gate passes unless a test injects drift;
  - `MockVerifier` returns scripted results.
- Real adapters run only when the CLI is given `--provider gemini` and the user has approved spend.
- Tests cover:
  - URL rules, SSRF, size limits and the injection page;
  - script schema, the copy check (no 12-word overlap) and step count rules;
  - style rotation;
  - gate pass, warp and fail on synthetic drift;
  - retry-then-flag;
  - cost guard refusals;
  - resume without re-billing;
  - render probes on a short mock guide;
  - package contents.

## Prompt versions

`script_v1`, `image_v1` and `verify_v1` are stored in `diyvideo/prompts/` and recorded in report.json. A
change in any version invalidates only the stages that depend on it.

## Phase 2 hooks

The Sheet schema reserves a `mode` column (MVP writes `ai`), and the Remotion composition accepts clip
sources per step. Both let the self-filmed mode reuse the same render path.
