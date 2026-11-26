# Idea review

## Resume checkpoint

- Mode: INTERACTIVE
- User language: Vietnamese
- State: clarifying
- Raw input reference and revision: RAW_IDEA.md at commit 7e559a1, SHA-256 fc75d1c34716b9f9695c5aeb9498cc99dadf8f70a4cda489dbaf0468f8ce76cd
- Draft IDEA.md SHA-256: pending (root IDEA.md is still the template description)
- Last completed action: rendered three free local demo videos (A skit, B problem→solution, C price quiz) from the user's sample product images and sent them for feedback
- Next action: collect demo feedback, the product's real price, and remaining round-1 answers (or defaults), then draft IDEA.md

## Clarifications and assumptions

Confirmed from the raw idea:

- Input is a Google Sheet with columns: product name, product description, affiliate link, Google Drive folder name holding product images.
- Each row produces one short video of 15–20 s. Script must be creative, cheerful and meaningful.
- People shown are real or faceless; output must not look fake/"AI giả trân".
- Rendering via Remotion + FFmpeg or an AI video tool.
- GitHub Actions posts finished videos to social platforms.

Round 1 questions (sent 2026-11-26, awaiting answers):

1. Target platforms and affiliate network.
2. Visual source for "real or faceless people".
3. Human review before publishing vs. fully automatic posting.
4. Which AI subscription the user has, monthly budget cap and videos per day.
5. Voice-over language/voice and target audience.

Proposed defaults if the user accepts them: TikTok + YouTube Shorts + Facebook Reels; product photos + motion + Vietnamese AI voice (faceless); human approval in the Sheet before posting; Gemini API (pay-as-you-go text/TTS, no paid AI video) with cap ≤ 10 USD/month; 1–3 videos/day.

Round 2 (2026-11-26). User follow-up: still unsure about scripting and editing; wants AI to make clips polished and engaging within ~5,000 VND per clip; asks about 1–3 recurring decorative characters across all videos; offers sample product images and asks for 2–3 trend-friendly demo templates or a list of options. Round-1 questions remain unanswered.

Proposed defaults sent in round 2:

- Per-clip stack: LLM script + TTS + 0–2 AI-generated images + Remotion motion graphics; paid AI video excluded by default (premium opt-in).
- Mascots: 1 main + 1 sidekick 2D original characters designed once, with a reusable pose/expression/mouth-shape library animated in Remotion (zero per-clip cost, consistent look).
- Demo templates: (1) mascot skit/reaction, (2) problem → solution (before/after), (3) price-guess quiz. Demos rendered locally for free; sample images stay out of git.

Questions sent: pick demo templates; mascot count/style/personality; how to share sample images; round-1 items (defaults apply if unanswered).

Round 3 (2026-11-26). User answers: approve demo templates A + B + C; 2 mascots — a decor expert and a family homemaker expert. Supplied 5 product images (chat upload, kept out of git) and a product description for a Christmas mesh ribbon roll. Round-1 items still unanswered; defaults proposed.

Feasibility demo (local, zero spend): Remotion 4.0.547 + React 19 in the session scratchpad (not tracked), Be Vietnam Pro font from npm @fontsource, original SVG mascots ("Mi Decor" cat decor expert, "Cô Gấu Đảm Đang" bear homemaker), synthesized public-domain melody (Jingle Bells, 1857) and SFX generated with numpy. Output: three 1080x1920 H.264/AAC 30 fps clips of 18.0 s; ffmpeg full decode passed; mean loudness about −24 dB, peak −1 to −2 dB. Render time about 2 min 21 s for all three on this container. No voice-over yet (TTS not used to keep spend at zero); price in template C is a labeled placeholder (35K).

Data-quality findings from the sample description: it claims "lụa cao cấp" while the image says PP mesh fibre; dimensions mix "9M long, 26cm wide" with roll photos labelled 26cm/15cm. The pipeline needs a fact list per product so scripts only use verifiable claims.

## Research and decisions

Sources checked 2026-11-26 (web search summaries; verify against live docs during the Research stage):

- TikTok Content Posting API: unaudited clients can only post to private accounts (SELF_ONLY); public posting requires an app audit. https://developers.tiktok.com/doc/content-posting-api-get-started , https://developers.tiktok.com/doc/content-posting-api-reference-direct-post
- YouTube Data API videos.insert: uploads from unverified API projects historically restricted to private; a reported Nov 2026 change is unconfirmed. Default quota allows ~100 uploads/day. https://developers.google.com/youtube/v3/docs/videos/insert , https://developers.google.com/youtube/v3/determine_quota_cost
- Gemini API Veo video generation: no free tier; roughly 0.05–0.40 USD per generated second depending on model (secondary sources). https://ai.google.dev/gemini-api/docs/pricing
- Gemini 2.5 Flash Image: about 0.039 USD per 1024x1024 image (1,290 output tokens); batch about half. https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models/gemini/2-5-flash-image , https://blog.laozhang.ai/en/posts/cheapest-gemini-image-generation-api (secondary). TTS price not yet confirmed from an official page.
- Exchange rate Nov 2026: SBV central rate ~25,640 VND/USD; commercial bank selling ~25,900. Planning rate: 26,000 VND/USD, so 5,000 VND ≈ 0.19 USD per clip. https://thoibaotaichinhvietnam.vn/sang-2611-ty-gia-trung-tam-giam-1-dong-gia-usd-on-dinh-26756.html
- Consequence: Veo 3.1 Lite 720p at ~0.05 USD/s means even a 4 s AI clip (~5,200 VND) exceeds the per-clip cap, so AI video is an opt-in premium tier only.
- Local tooling check: examples/video already pins Remotion 4.0.547 with React 19; node 22 and ffmpeg are available, so free local demo renders are feasible.
- Consumer AI subscriptions (ChatGPT Plus, Claude Pro, Gemini Advanced) are chat products; unattended GitHub Actions automation needs an API key billed per use (to confirm with the user's chosen provider).

## Vietnamese approval summary

Pending draft.

## Approval record

- Decision: pending
- Approver and evidence reference: pending
- Approval timestamp: pending
- Approved IDEA.md SHA-256: pending

## Handoff

- Project plan and first action: pending
- Handoff checkpoint: pending
