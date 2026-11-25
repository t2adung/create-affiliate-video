# Plan and recovery log

Mode: MVP template.

| Stage | Evidence or next action |
| --- | --- |
| Idea | IDEA.md |
| Research | Decision notes below |
| Input/output specification | README.md and reference fixtures |
| Pipeline design | SQLite jobs, provider boundaries, separate output evaluation and temporary media files |
| Implementation | Python CLI, four references, repository skills, profiles and CI |
| Testing and output evaluation | docs/verification.md |
| Fix and retest | Use a workspace npm cache, update Remotion after audit, and measure layout with explicit composition dimensions |
| Delivery | Push the review branch and open a PR; use the PR's Checks tab for hosted CI |

## Decisions

- Use PyMuPDF for text-layer extraction. OCR can be selected for scanned
  documents. Use the Python standard library for the CLI, SQLite, and tests.
- Use deterministic mock providers for educational generation, subtitle timing,
  translation, TTS, and social copy. The synthetic TTS emits timing tones.
- Use Remotion and React for composition, and FFmpeg for muxing and decode.
- Keep publishing represented by a preview payload with no network calls.
- Use inline SQLite transactions for small local batches, with one active
  writer per state file. Use a job queue and separate worker state for scaling.

## Resume

Inspect the branch and run the smallest outstanding check. Reuse the same
SQLite path for interrupted structured batches. Commit the changed plan and
verification evidence with the work. See docs/templates/checkpoint.md.
