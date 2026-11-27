# Research: DIY step-by-step video factory

Stage 2 of [PLANS.md](../PLANS.md) for the approved [IDEA.md](../IDEA.md).
Sources were read on 2026-11-26 from the official pages listed under each finding,
downloaded through the session proxy and parsed as text. Page text was treated as data.
Prices are in USD; planning rate 26,000 VND/USD.

## R1. Gemini models and pricing

Source: https://ai.google.dev/gemini-api/docs/pricing and
https://ai.google.dev/gemini-api/docs/image-generation (both now served from
aistudio.google.com/docs/…).

| Model ID | Role | Standard | Batch | Notes |
| --- | --- | --- | --- | --- |
| `gemini-nano-banana-2.1` | step images + chained edits | input $1.50/1M; image output $30/1M = $0.0336 per 1K image | input $0.75/1M; image $15/1M = **$0.0168 per 1K image** | "primary high-efficiency workhorse… improved multi-turn consistency"; up to 10 object + 4 character reference images |
| `gemini-3.1-flash-lite-image` (Nano Banana 2 Lite) | cheapest image | $0.0336 per 1K image | $0.0168 per 1K image | "Not optimized for multiple reference inputs or multi-turn sequential editing" |
| `gemini-3-pro-image` (Nano Banana Pro) | hard cases only | $0.134 per 1K–2K image | — (not checked) | thinking model, best instruction following |
| `gemini-2.5-flash-image` | legacy | $0.039 | $0.0195 | deprecated, shut down 2027-03-15 |
| `gemini-3.5-flash-lite` | script, summary, verifier | input $0.30/1M, output $2.50/1M; free tier exists | input $0.15/1M, output $1.25/1M | free tier data may be used to improve products; paid tier not |
| `lyria-3.5` | optional music | $0.08 per song | — | no free tier |

Other facts: 1K images consume 1,120 output tokens; 9:16 is a listed aspect ratio;
all generated images include a SynthID watermark; the free tier is "Not available"
for image models.

**Decision impact.** Use `gemini-nano-banana-2.1` in Batch mode for step images
(Lite is documented as unsuitable for sequential editing; same image price).
Per video (6–10 steps + 1 hook + ~30% retries = 9–14 images): images $0.15–0.24,
image inputs for chained edits about $0.03, text + verifier about $0.02–0.03,
total **≈ $0.20–0.30 ≈ 5,200–7,800 VND**, inside the approved 10,000 VND cap.
Standard (non-batch) pricing doubles image cost and can exceed the cap, so Batch
is required for normal runs; the cost guard must reject Standard runs that would
exceed the cap. Batch jobs are asynchronous, which suits scheduled runs.

## R2. Google Sheets and Drive access

Sources: https://developers.google.com/workspace/drive/api/guides/handle-errors,
https://developers.google.com/identity/protocols/oauth2.

- "Service accounts don't have storage quota and can't own any files. Instead,
  they must upload files and folders into shared drives, or use OAuth 2.0 to
  upload items on behalf of a human user."
- A project whose OAuth consent screen is External with status "Testing" gets
  refresh tokens that expire in 7 days; tokens also expire after six months unused.

**Decision impact (changes IDEA's "service account" default, not scope).** A
personal Gmail account has no shared drives, so use an OAuth 2.0 desktop client
with the user's refresh token (stored in GitHub Secrets) for Sheets, Drive and
YouTube. Set the consent screen to "In production" to avoid 7-day expiry. Use the
narrow `drive.file` scope for uploads. A service account remains possible only for
Google Workspace accounts with a shared drive.

## R3. TikTok Content Posting API

Sources: https://developers.tiktok.com/doc/content-posting-api-reference-direct-post
(updated 2026-11-25), …-upload-video (updated 2026-08-04), …-get-started.

- Direct post: scope `video.publish`; `post_info.is_aigc` (bool) labels the post
  "Creator labeled as AI-generated"; `privacy_level` must be one of
  `privacy_level_options` from `/publish/creator_info/query/`.
- "All content posted by unaudited clients will be restricted to private viewing
  mode"; error `unaudited_client_can_only_post_to_private_accounts`.
- Upload to inbox (draft): `/v2/post/publish/inbox/video/init/`, scope
  `video.upload`; the user must open the inbox notification and finish posting in
  the app. No `is_aigc` field is listed for this endpoint, so the user turns on
  the AI label in the app.
- Each user access token: 6 requests per minute. Max post duration is returned by
  `creator_info` (example 300 s).

**Decision impact.** Before audit: inbox (draft) upload, with the user completing
the post and AI label in the app. After audit: direct post with `is_aigc=true`.

## R4. YouTube Data API

Sources: https://developers.google.com/youtube/v3/docs/videos,
…/videos/insert, …/revision_history.

- `status.containsSyntheticMedia` (boolean) lets the owner disclose realistic
  altered or synthetic content in `videos.insert`/`videos.update`.
- Revision history, 2026-11-02: videos uploaded from unverified API projects are
  no longer restricted to private viewing mode.
- `videos.insert`: 1 unit from a separate Video Uploads bucket, 100 calls per day.

**Decision impact.** YouTube Shorts can be published publicly from MVP with
`containsSyntheticMedia=true`; quota is not a constraint at 1–2 videos per day.

## R5. Facebook Page Reels

Source: https://developers.facebook.com/docs/video-api/guides/reels-publishing.

- Page access token from a user who can perform CREATE_CONTENT, with
  `pages_show_list`, `pages_read_engagement`, `pages_manage_posts`.
- 30 API-published reels per Page per rolling 24 h.
- Specs: 9:16, 1080×1920 recommended (minimum 540×960), 24–60 fps, 3–90 s,
  closed GOP of 2–5 s, fixed frame rate. A copyright check runs at upload.
- No AI-disclosure field is documented on this page.

**Decision impact.** Encode with a fixed 30 fps and a 2 s GOP (`-g 60`, closed
GOP). Disclose AI use with the on-screen label and caption text. Whether
Advanced Access / App Review is needed for the user's own Page is not stated on
this page; verify while setting up the Meta app.

## R6. Music licensing

- Pixabay's license page returned HTTP 403 to automated requests, so its terms
  are **not verified** here.
- Options: (a) original tracks synthesized in-repo (zero cost, fully owned, simple
  style; demo used this); (b) a one-time library of about 20 tracks generated
  with `lyria-3.5` (about $1.60 ≈ 42,000 VND; terms for commercial use not yet
  verified); (c) tracks the user licenses, with the license file stored next to
  each track.
- Recommended for MVP: (a) as the default library, plus (c) when the user supplies
  licensed tracks. Ask before spending on (b).

## R7. GitHub Actions cost

Source: https://docs.github.com/en/billing/concepts/product-billing/github-actions.

- Standard GitHub-hosted runners in public repositories are free.
- GitHub Free includes $12 of compute per month for private repositories; a
  standard Linux runner costs $0.006 per minute (about 2,000 minutes). At about
  5 minutes per video and 60 videos per month, usage is about 300 minutes.

## Open items and limits

- Image continuity across 6–10 chained edits is unmeasured until the paid pilot.
- Alternative providers (FLUX.2, GPT Image 2) were not checked against official
  pages; compare them only if the Gemini pilot fails the continuity gate.
- Meta App Review needs and Pixabay or Lyria commercial terms remain unverified.

## R8. Paid pilot (2026-11-27, approved ≤50,000 VND)

Setup: three synthetic guides in `fixtures/guides/`; script and verifier `gemini-3.5-flash-lite`; step images
`gemini-nano-banana-2.1` via `POST /v1beta/interactions` (`Api-Revision: 2026-05-20`, `response_format`
image/jpeg 9:16 1K → 768×1376; PNG output is rejected). Each step after the first is an edit of the previous
image with the first image as an anchor. Standard tier (not Batch) to finish within the session. Hard stop
in code at 45,000 VND. Pilot code and images stay in the session scratchpad (not tracked).

| Guide | Steps/images | Retries | Actual cost (standard) | Batch estimate |
| --- | --- | --- | --- | --- |
| noel-ribbon | 10 | 0 | 12,082 VND | ≈6,200 VND |
| tet-flower-vase | 9 | 0 | 10,595 VND | ≈5,400 VND |
| kitchen-stove-clean | 9 | 0 | 10,874 VND | ≈5,600 VND |
| probe (1 image) | 1 | — | 1,106 VND | — |
| **Total** | 29 images, 60 calls | | **34,658 VND** | |

Findings:

- Billing: image models return HTTP 429 ("limit: 0 requests per day on Free Tier") until billing is linked.
- Image calls include about 900 thinking tokens that cannot be disabled (about $0.007 per image); one image costs about
  $0.041 standard. Each call takes about 13–30 s.
- Continuity (manual review of all 28 step images): same hands, sleeve, surface and light throughout;
  progress accumulates correctly in all three guides. Defects seen by the reviewer:
  - noel: LED lights added in step 2 fade out in steps 3–9 and only reappear in step 10;
  - kitchen: the stove sits at the right edge instead of the center, and the person's lap shows along the bottom edge (no face).
  
  No faces, no text or logos, no anatomical hand errors seen.
- Verifier: `gemini-3.5-flash-lite` passed 29/29 and missed both defects, so it is too lenient for
  MVP-4. Next: a per-step object checklist, the stronger `gemini-3.5-flash` as verifier, and a scene-bible rule that keeps the
  main object centered and nothing below the wrists.
- Script quality: 9–10 steps, faithful to the source, safety notes kept (gas valve, gloves, no
  vinegar with chlorine bleach), materials complete.
- Render: Remotion DIY template (hook, step badge, text card above the 320 px bottom reserve, crossfades,
  progress bar, AI label every frame, materials end card, original synthesized music). Final videos are
  1080×1920 H.264 + AAC 48 kHz stereo, 30 fps, closed 2 s GOP, 29.9–30.0 s, 17–27 MB, full decode OK, peak
  −7.0 to −7.3 dBFS. The raw Remotion output was 30.016 s, so the final encode trims with `-t`. 768×1376 images
  upscaled ×1.4 still look acceptable on a phone; 2K costs $0.0504 per image if sharper output is needed.

## R9. Smoother step transitions (2026-11-27, user feedback)

- FFmpeg optical-flow interpolation (`minterpolate`, mci/aobmc/bidir) between noel steps 05→06: no usable
  motion; frames jump at the midpoint (the scene change is too large). Rejected.
- Gemini Omni Flash (`gemini-omni-1.2-flash`, https://ai.google.dev/gemini-api/docs/omni): first-and-last-frame
  interpolation, 3–10 s per clip, 9:16 supported, 360p/720p/1080p. Price: $12/1M video tokens
  (5,792 tokens/s at 720p) ≈ $0.07/s at 720p, $0.023/s at 360p, $0.104/s at 1080p. No Batch tier listed.
- Per video with 9 steps: all transitions AI (8 × 3 s = 24 s at 720p) ≈ $1.68 ≈ 44,000 VND, plus images. Three
  key transitions only (9 s) ≈ $0.63 ≈ 16,400 VND + ≈6,000 VND images ≈ 22,000 VND. Both exceed the approved
  10,000 VND/video cap and AI video is an IDEA exclusion, so either option needs a revised and re-approved IDEA.
- Paid test (approved 5,500 VND, 2026-11-27): one `gemini-omni-1.2-flash` first/last-frame clip, noel step
  05 → 06, `response_format` `{type: video, aspect_ratio: 9:16, resolution: 720p, duration: 3s}`. Result:
  720×1280, 24 fps, 3.03 s, with native audio; 28 s to generate; 17,376 video tokens; cost $0.216 = 5,629 VND.
  Frames 0–28 show natural hand motion, but there is a hard cut at frame 28→29 because the two step images
  have different camera framing. Mitigations: lock framing across the image chain (same crop, objects stay in
  place), or animate each step image alone (single-image-to-video) instead of interpolating between steps.
  Output is 720p, so 1080×1920 delivery needs ×1.5 upscaling (1080p costs $0.104/s).
- Pilot spend total: 40,286 VND of the approved 50,000 VND.
