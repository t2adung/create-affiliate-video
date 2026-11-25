# IDEA

Library event caption preview. [Raw idea](RAW_IDEA.md). Draft awaiting user approval.

## Problem and target users

Library staff need a consistent starting caption for event announcements without manual reformatting.

## Desired outcomes

Produce a caption from an approved fact in one local step so staff can review and copy it.

## MVP requirements

Delivery profile: MVP.

- MVP-1. Convert one validated event fact to a caption using a fixed template.
- MVP-2. Emit a copyable local JSON preview labeled as pending review and return clear errors for invalid input.

## Exclusions

Publishing, account integrations, generated claims and image generation.

## Future enhancements

Add brand tone options and a bulk review view.

## Input contract

A local UTF-8 JSON object, at most 4 KiB, with exactly two strings: `topic` (1–60 Unicode code points after trimming) and `fact` (1–180 after trimming). Reject line breaks and control characters within either field. Example `{"topic":"Library workshop","fact":"The workshop starts at 2 p.m."}`.

## Output contract

Print `{"caption":"Library workshop — The workshop starts at 2 p.m.","status":"pending_review"}` on success. For invalid input, exit 2 with a field-specific stderr message and no stdout. The user copies the caption manually.

## Technical approach and alternatives

Repository reference at base commit a77ff69: README.md and examples/social/sample.json describe a local fact-to-preview pipeline, making reuse feasible. Compare its deterministic rendering to a hosted model, which could vary tone but adds data transfer, evaluation and usage charges. Recommend deterministic rendering and check the stricter bounds during planning.

## Complexity and operating costs

Low, estimated 1–2 days for contract adaptation and tests. At 100 previews per month on an existing computer, estimated service cost and authorized external spend are both USD 0.

## Privacy, security, licensing and risks

Staff supply approved public event facts and retain files locally until deletion. Tests use invented events. Render plain text with JSON escaping and preserve supplied facts exactly to reduce accidental claims.

## Assumptions and open decisions

Confirmed: staff review and no autopost. Proposed default: one neutral caption and manual copy. Open blocking decisions: none.

## Acceptance and evaluation

- MVP-1: five synthetic facts produce exact expected captions, including Unicode and boundary lengths, with no new claims.
- MVP-2: each valid result has `pending_review` status and succeeds offline; missing, extra and over-limit fields return exit 2 with empty stdout.

## Vietnamese approval summary

Công cụ tạo bản nháp thông báo thư viện từ thông tin đã duyệt để nhân viên xem và sao chép. Bản MVP dùng mẫu cố định, chạy ngoại tuyến và có chi phí dịch vụ dự kiến 0 USD. Bạn duyệt bản này hay muốn chỉnh sửa?
