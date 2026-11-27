# Plan and recovery log

Project: DIY step-by-step faceless video factory (Google Sheet → AI steps →
AI images → Remotion video → reviewed publishing).

- Approved specification: [IDEA.md](IDEA.md), SHA-256
  `37c05f9473c524e2d18e366cf95ce5b6bf9f933966476c36fefb391776a398e6` (revision 4; revision 1 `6cc292ac…f3371` superseded)
- Approval evidence: [IDEA_REVIEW.md](IDEA_REVIEW.md#approval-record) — user words "duyệt IDEA", 2026-11-27 (revision 4)
- Delivery profile: MVP ([profiles/mvp.md](profiles/mvp.md))
- Branch: `claude/quirky-planck-wgev52`, draft PR t2adung/create-affiliate-video#2
- Approved spend: ≤15,000 VND/video, ≤900,000 VND/month (revision 4). Pilot budget 50,000 VND used 47,735 VND.
  Further live runs during development need a new explicit approval; CI uses mocks only.

Before any work on resume: run `sha256sum IDEA.md` and compare with the digest above. A mismatch returns
to Idea Discovery.

## Stages

| # | Stage | Skills | Exit evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Idea | idea-builder, product-manager | IDEA.md approved, digest recorded | done (commit 7c0710a + approval) |
| 2 | Research | ai-engineer, tool-architect, security-reviewer | [docs/research.md](docs/research.md) R1–R7 from official pages (done 2026-11-26); paid image-continuity pilot pending user approval + key | in progress |
| 3 | Input/Output specification | data-engineer, tool-architect | `docs/specification.md` from the template: Sheet A/B schemas, report.json schema, error envelope, status machine, stable keys | done (docs/specification.md) |
| 4 | Pipeline design | tool-architect, automation-engineer, prompt-engineer | [docs/pipeline.md](docs/pipeline.md) | done |
| 5 | Implementation | data-engineer, ai-engineer, remotion-developer, video-engineer, automation-engineer | `diyvideo/` package + Remotion DIY template + GitHub Actions workflow, mocks first | in progress (slices 1–2 done) |
| 6 | Testing | qa-engineer | unit + fixture tests for MVP-1…MVP-9 incl. negative controls, offline in CI | pending |
| 7 | Output evaluation | content-quality-reviewer, qa-engineer | `docs/templates/evaluation.md` filled: Schema, Hallucination, Batch/recovery, Idempotency, Usage, Visuals, Video, Licensing, Security | pending |
| 8 | Fix / Retest | qa-engineer | failed gates rerun with regressions | pending |
| 9 | Delivery | release-manager, security-reviewer | `scripts/verify.sh` pass, PR ready for review, live pilot (approved) evidence | pending |

## Acceptance checks (from IDEA.md)

MVP-1 source ingestion + error rows + prompt-injection control; MVP-2 Sheet B 6–10 steps, no ≥12-word verbatim
copy, no invented steps; MVP-3 N+1 9:16 images with ≥90% adjacent continuity (pilot); MVP-4 verifier ≥9/10
on defect set, ≤2 retries then flag; MVP-5 1080×1920 H.264/AAC 30 fps 20–30 s, ≥2.5 s/step, safe area, AI label
every frame, peak ≤ −1 dBFS; MVP-6 Drive package + Sheet B update + regenerate; MVP-7 approved-only publishing,
AI flag, no duplicate on retry, export_only fallback; MVP-8 per-video and monthly cost stops, no secrets in
logs; MVP-9 resume without re-billing, max 2 new rows per run.

## Decisions

- D1 (2026-11-26, refined by research R1): `gemini-nano-banana-2.1` in Batch mode for step images ($0.0168 per
  1K image), `gemini-3.5-flash-lite` for script and verifier. Lite image model rejected (not for sequential
  editing). Estimated 5,200–7,800 VND/video. Reversal: Gemini pilot fails the continuity gate → compare FLUX.2 /
  GPT Image 2.
- D2: Motion via Remotion 4.0.547 + FFmpeg (already pinned in examples/video); no AI video in MVP (cost).
- D3: Python CLI + SQLite checkpoints reusing the repository's factory patterns; provider adapters with
  deterministic mocks so CI never calls paid APIs.
- D4: Text + licensed music only (no TTS) per user; on-screen AI label always, platform AI flags where APIs allow.
- D5: Publishing only after user sets `approved`; platforms without public-posting permission use draft upload or
  `export_only` package.
- D6 (research R2): Google OAuth desktop client + user refresh token (consent screen "In production",
  `drive.file` scope) instead of a service account, because service accounts cannot upload to a personal
  My Drive. Technical change only; IDEA scope unchanged.
- D7 (R3–R5): TikTok inbox (draft) upload until audit, then direct post `is_aigc=true`; YouTube public upload with
  `containsSyntheticMedia=true`; Facebook Page Reels with on-screen + caption AI label; encode fixed 30 fps,
  closed 2 s GOP.
- D8 (R6): default music = original tracks synthesized in-repo; user-licensed tracks optional; Lyria library
  only after approval.
- D9 (2026-11-27, user chose "A"): repository becomes public so GitHub-hosted Actions minutes are free; schedule
  2 runs/day (06:00 and 18:00 Asia/Ho_Chi_Minh), each run finishes one guide end to end, waiting on Batch jobs
  inside the job (measured ≈2.3 min per frame). Pre-publication scan: no secrets in history, noreply author
  emails only, no media files. Secrets stay in GitHub Secrets. Reversal: if the user wants private code, run 1
  guide/day (≈1,650 min/month) or move batch polling to Apps Script.
- Feasibility evidence carried from discovery: local Remotion render of three 1080×1920 18 s demos, full decode
  pass, ~47 s render each (scratchpad, not tracked).

## Checkpoint log

### 2026-11-26 — Handoff

- Stage: 1 → 2. Commit: approval/handoff commit after 7c0710a.
- Verification: `python3 -m unittest tests.test_idea_discovery` → OK (4 tests). Full local suite: 8 pass,
  2 errors from missing local PyMuPDF (environment only; CI installs it and passed on 7c0710a).
- Open failures: none.
- Next executable action: R1 — read official docs (no spend) for Gemini image models pricing/editing, Google
  Sheets/Drive service-account access, TikTok Content Posting (direct + inbox, `is_aigc`), YouTube
  `containsSyntheticMedia` and verification, Meta Reels publishing, and CC0/commercial music sources; write
  `docs/research.md`.
- External dependencies (need user): Gemini API key and approval of ≤50,000 VND pilot (bake-off); Google
  service account access to the Sheet/Drive; TikTok/YouTube/Facebook developer accounts and OAuth consent.

### 2026-11-26 — Research R1–R7

- Network: created personal environment `create-affiliate-video` (user approved) and added `aistudio.google.com`.
- Commands: `curl -sL` official pages into the session scratchpad, parsed with `python3 -I tools/h2t.py`;
  Gemini docs via `.md.txt`. Pixabay returned 403 (unverified).
- Artifact: docs/research.md. Open failures: none. Unverified: Meta App Review needs, music terms.
- Next executable action: Stage 3 specification (no spend). In parallel ask the user for: Gemini API key via the
  secure credential form + approval of the ≤50,000 VND continuity pilot; Google OAuth client setup; TikTok and
  Meta developer apps.

### 2026-11-27 — Pilot approval and specification

- User approved the paid pilot (≤50,000 VND) and has a Gemini API key: "đồng ý, da co gemini api key".
- The credential form only injects `Authorization: Bearer`; native Gemini endpoints (Batch, image editing) need
  `x-goog-api-key`, so the user must add the key as a network secret for `generativelanguage.googleapis.com`
  with header `x-goog-api-key` in the environment settings (pending).
- Stage 3 artifact: docs/specification.md (Sheet A/B schemas, state machine, Drive package, video spec,
  stage interfaces, recovery and idempotency, fixtures, cost guard, credentials).
- Next executable action: Stage 4 pipeline design + mock implementation skeleton; run the pilot once the key works.

### 2026-11-27 — Gemini key check

- User added the key as a network secret (header `x-goog-api-key`). `GET /v1beta/models` → 200; 65 models incl.
  `gemini-nano-banana-2.1`, `gemini-3.5-flash-lite`.
- Images use `POST /v1beta/interactions` (`Api-Revision: 2026-05-20`), `response_format` `{type:image,
  mime_type:image/jpeg (png rejected), aspect_ratio:9:16, image_size:1K}`; multi-turn via
  `previous_interaction_id`.
- Blocker: HTTP 429 "limit: 0 requests per day on Free Tier" for `gemini-nano-banana-2.1`. The project needs the
  paid tier (billing linked). Spend so far: 0.
- Next action: user links billing in Google AI Studio; then rerun the probe and the ≤50,000 VND pilot.

### 2026-11-27 — Paid pilot done

- Billing linked by the user. Pilot spend 34,658 VND (cap 50,000; code stop 45,000). Results: docs/research.md R8.
- Gates observed: continuity good by manual review; verifier too lenient (0/2 known defects caught) → MVP-4 at
  risk; video format gates pass after `-t` trim; batch cost estimate 5,400–6,200 VND/video.
- Three pilot videos sent to the user for feedback.
- Next executable action: Stage 4 pipeline design incl. stronger verifier and scene-bible composition rules;
  collect the user's feedback on the pilot videos.

### 2026-11-27 — User feedback on pilot + AI video test

- Feedback: colours OK but every video has the same look (vary styles); AI label → smaller, fainter, first 3 s
  only (changes IDEA MVP-5 "every frame" → needs IDEA revision); wants smoother AI transitions.
- Omni interpolation test done (research R9): natural hand motion but a hard cut caused by framing mismatch;
  5,629 VND. Pilot total 40,286 / 50,000 VND.
- Next: user chooses A (Remotion, ≈6k), B (3 AI moments, ≈22k) or C (all AI, ≈50k); then revise IDEA.md
  (style rotation, label rule, AI video scope and cap if B/C) and request re-approval.

### 2026-11-27 — Locked camera + stop-motion test

- Framing gate works (caught tet drift, retry fixed). Stop-motion frames lock well; interpolation between
  locked frames is usable. New prompt rule needed: lock hand entry direction. Pilot total 47,735 / 50,000 VND
  (pilot budget effectively exhausted; further paid tests need new approval).
- Next: user chooses the motion approach (A / B / C / stop-motion variants); then revise IDEA.md (style
  rotation, AI-label rule, framing gate, motion approach, cap) for re-approval.

### 2026-11-27 — Scope reopened (IDEA revision 2)

- User chose SM-1 with pure interpolation. IDEA.md revision 2 (SHA-256 53d56e5f…1091f6) drafted: style rotation,
  locked camera + framing gate, key-step in-betweens + minterpolate, AI label 0–3 s, OAuth, cap 15,000 VND/video
  and 900,000 VND/month. Planning/implementation paused until explicit re-approval (digest must match).

### 2026-11-27 — IDEA revisions 3–4

- Rev 3 added self-filmed mode; user then deferred it to phase 2. Rev 4 (MVP = AI mode only, 15,000 VND/video,
  900,000 VND/month) awaits explicit approval. Phase-2 hooks to keep in design: Sheet `mode` column, shared
  Remotion template, Drive clip folder convention.

### 2026-11-27 — Revision 4 approved

- Approved digest 37c05f94…776a398e6 ("duyệt IDEA"). Scope: AI mode only (MVP-1…MVP-9 as revised); self-filmed
  mode is phase 2. Cap 15,000 VND/video, 900,000 VND/month.
- Next executable action: Stage 4 design doc, then mock-first implementation of ingest → script → images
  (chain + keyframes + framing gate + verifier) → render → package, with tests.

### 2026-11-27 — Stage 4 done, implementation slice 1

- docs/pipeline.md written. `diyvideo/`: config, ledger (cost guard, results, publish records), ingest (URL
  rules, SSRF guard, limits), styles (9 looks), script (schema, copy check, URL ban, delimiter neutralising),
  providers (mocks), framing gate, image chain (key-step in-betweens, gate → verifier, ≤2 retries, flag).
- Bugs found by tests and fixed: drift cascade after a flagged frame (chain now continues from the last
  accepted frame); source text could close the SOURCE block (delimiters neutralised); truncation whitespace.
- Commands: `python3 -m unittest tests.test_diy` → 17 OK; `python3 -m unittest discover -s tests` → 27 OK.
- Next: Gemini adapters (Interactions API, batch), render (Remotion DIY template in repo, minterpolate key-step
  clips, final encode + probes), package/report, LocalSheetStore + CLI, then Google Sheets/Drive adapters.

### 2026-11-27 — Implementation slice 2

- Added: gemini.py (generateContent + resumable batchGenerateContent, PendingBatch, key from env or proxy,
  redacted errors), render.py + diyvideo/remotion (hook, steps, key-step minterpolate clips, end card, AI label
  0–3 s, original audio), package.py (output folder + report.json), sheets.py (LocalSheetStore), run.py
  (≤2 new guides/run, regenerate path, flag/cost-cap/pending handling), CLI `python -m diyvideo run`
  (paid provider refused unless DIY_ALLOW_SPEND=1).
- Fix: image cache keys use only visual fields, so text edits re-render without re-billing (tested).
- Research: no Flex tier for the image model; Batch is required to stay under the 15,000 VND cap (standard ≈
  17–21k for 16–20 frames). Batch latency is unmeasured → needs a small approved live test.
- Commands: `python3 -m unittest discover -s tests` → 31 OK (1 skipped); `DIY_RENDER=1 python3 -m unittest
  tests.test_diy.RenderGate` → OK in 242 s (1080×1920, 30 fps, exact duration, peak ≤ −1 dBFS, label 0–3 s).
- CI: installs requirements-diy.txt, `npm ci --prefix diyvideo/remotion`, DIY_RENDER=1, timeout 30 min.
- Next: Google Sheets/Drive/YouTube OAuth adapters, publishing (YouTube, TikTok inbox, Facebook Page) with
  idempotency, scheduled GitHub Actions workflow, then a live approved test (batch latency + quality).

### 2026-11-27 — First live end-to-end run (R11)

- Live run passed: 16 frames, 0 flagged, video passes MVP-5 probes; batch ≈2.4 min/frame. Spend 15,939 VND
  under the approved 20,000 test cap (clean-run estimate ≈13,200 VND). Verifier v1 over-strict → v2 fixed.
- CI green on 11f1c28 (concurrency fix for 2-core runners).
- Next: cost optimisation to restore headroom under 15,000 VND; user feedback on the video; Google OAuth
  setup with the user; scheduled workflow (2 runs/day) after the repo becomes public; publishing adapters.

## Template baseline (legacy)

The repository template's own reference plan (four synthetic examples, PyMuPDF, SQLite jobs, mock providers,
Remotion title card, preview-only publishing) remains verified by `scripts/verify.sh` and
[docs/verification.md](docs/verification.md). Keep those references passing while building this project.
