# Plan and recovery log

Project: DIY step-by-step faceless video factory (Google Sheet → AI steps →
AI images → Remotion video → reviewed publishing).

- Approved specification: [IDEA.md](IDEA.md), SHA-256
  `6cc292ac50468275a5a5d054a962a2cda9e11c2f3e681b0d6ba116b7737f3371`
- Approval evidence: [IDEA_REVIEW.md](IDEA_REVIEW.md#approval-record) — user words "duyệt IDEA", 2026-11-26
- Delivery profile: MVP ([profiles/mvp.md](profiles/mvp.md))
- Branch: `claude/quirky-planck-wgev52`, draft PR t2adung/create-affiliate-video#2
- Approved spend: ≤10,000 VND/video, ≤600,000 VND/month. Current authorized live spend: **0** until the user
  approves the first paid pilot (≤50,000 VND) and supplies credentials.

Before any work on resume: run `sha256sum IDEA.md` and compare with the digest above. A mismatch returns
to Idea Discovery.

## Stages

| # | Stage | Skills | Exit evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Idea | idea-builder, product-manager | IDEA.md approved, digest recorded | done (commit 7c0710a + approval) |
| 2 | Research | ai-engineer, tool-architect, security-reviewer | `docs/research.md` with dated official sources: image model prices/limits, editing-chain support, Sheets/Drive auth, TikTok/YouTube/Meta posting + AI-label fields, music licenses; provider bake-off result (needs approval) | next |
| 3 | Input/Output specification | data-engineer, tool-architect | `docs/specification.md` from the template: Sheet A/B schemas, report.json schema, error envelope, status machine, stable keys | pending |
| 4 | Pipeline design | tool-architect, automation-engineer, prompt-engineer | stage diagram, provider interfaces (mock + real), SQLite checkpoint schema, cost guard, prompt templates with versions | pending |
| 5 | Implementation | data-engineer, ai-engineer, remotion-developer, video-engineer, automation-engineer | Python package + Remotion DIY template + GitHub Actions workflow, mocks first | pending |
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

- D1 (2026-11-26): Default AI provider Gemini API (text, image, verifier as a separate call), batch mode for
  images. Reversal: Research bake-off shows FLUX.2 or GPT Image 2 clearly better on continuity/price.
- D2: Motion via Remotion 4.0.547 + FFmpeg (already pinned in examples/video); no AI video in MVP (cost).
- D3: Python CLI + SQLite checkpoints reusing the repository's factory patterns; provider adapters with
  deterministic mocks so CI never calls paid APIs.
- D4: Text + licensed music only (no TTS) per user; on-screen AI label always, platform AI flags where APIs allow.
- D5: Publishing only after user sets `approved`; platforms without public-posting permission use draft upload or
  `export_only` package.
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

## Template baseline (legacy)

The repository template's own reference plan (four synthetic examples, PyMuPDF, SQLite jobs, mock providers,
Remotion title card, preview-only publishing) remains verified by `scripts/verify.sh` and
[docs/verification.md](docs/verification.md). Keep those references passing while building this project.
