# Output evaluation

For each applicable gate, record the fixture, metric, threshold, command,
result, and artifact. Include representative failures and negative controls.

| Gate | Evidence to collect |
| --- | --- |
| Schema | Valid and invalid inputs, required output fields and types |
| Grounding | Locate citations in original sources and compare claims |
| Independent verification | Reference answers or independent source derivation |
| Hallucination detection | Inject unsupported claims and check rejection |
| Reference dataset | Versioned truth set, provenance and per-slice scores |
| Batch and recovery | Partial failure, restart, retry limits and duplicate handling |
| Idempotency | Stable keys, concurrent duplicates and no repeated side effects |
| Usage | Provider metadata, units, pricing version, budget and mock estimates |
| Audio | Channel count, duration, clipping, silence and intelligibility |
| Subtitles | Timestamp order, drift, reading speed and language |
| Visuals | Bounding boxes, worst-case strings, font availability and contrast |
| Video | Codec, dimensions, duration and a full decode |
| Licensing | Asset inventory with origin, license and obligations |
| Security and privacy | Untrusted inputs, retention, redaction, secrets and approved destinations |
