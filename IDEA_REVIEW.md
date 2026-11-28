# Idea review

## Resume checkpoint

- Mode: INTERACTIVE
- User language: Vietnamese
- State: clarifying
- Raw input reference and revision: RAW_IDEA.md revision 3 (2026-11-28), SHA-256 9f58d99f580e5b20d4e1e49356d5c199a1c0465d6cb161ebb3240146224c847c
- Draft IDEA.md SHA-256: 37c05f9473c524e2d18e366cf95ce5b6bf9f933966476c36fefb391776a398e6 (revision 4)
- Last completed action: user reopened scope after live AI-image tests (cost vs. realism); RAW_IDEA revision 3 recorded; round 9 proposal sent
- Next action: get round-9 answers (who films, subscription owned, where editing runs, first topic), then draft IDEA.md revision 5

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

Round 4 (2026-11-26). User feedback: no mascots; wants faceless people and a real story, not a photo slideshow. Willing to spend more tokens, or use ChatGPT Pro / Gemini Pro, or any tool that generates story-like video. Asks what is needed to render such videos.

Proposed in round 4: hybrid story pipeline — LLM writes a 3–4 shot faceless story (hands, back view, silhouettes, POV) + AI text-to-video/image-to-video shots with product reference images + real product-photo inserts for accuracy + Vietnamese TTS narration + subtitles/music assembled in Remotion/FFmpeg. Routes: (1) Gemini API pay-as-you-go, fully automated, about 30–45k VND/video incl. retries; (2) Google AI Pro subscription + Flow, semi-manual (no API; user pastes prompts and drops clips into Drive); (3) user films hands-only clips, AI writes script/voice/edit. Sora excluded (reported discontinued). Platform AI labels are mandatory for realistic AI video; Shopee may affect commissions for AI-labelled videos (unverified).

Round 5 (2026-11-26) — scope change. User revised RAW_IDEA.md: DIY clips (Christmas decor, house cleaning, Tết, cleaning tips, flower arranging); the Sheet holds DIY guides as steps; AI turns them into many faceless step-by-step images; effects stitch them into a video; affiliate links are added based on the video. Rounds 1–4 proposals for product-centred videos and AI story video are superseded; carried forward: no mascots, faceless people, avoid plain slideshow feel, review before publishing (proposed), AI-content labelling.

Proposed in round 5: one Sheet row per guide (topic, title, steps, materials with affiliate link per material, optional real product image folder); 4–6 steps, 20–30 s; image chain where each step edits the previous step image for continuity (same hands, table, light); motion effects in Remotion (camera push/pan, parallax, before/after wipe, step counter, kinetic subtitles, SFX), optional cheap image-to-video for 1 hero shot; Vietnamese TTS narration; end card with real product photos and "link in bio/giỏ hàng" mapping each material to its affiliate link. Estimated 4,000–8,000 VND/video using batch image generation (unverified until a paid test).

Round 5 answers (2026-11-26): (1) Sheet A holds links to DIY tip content; AI summarises, lists materials and writes detailed steps into Sheet B, clear and complete enough for image/video generation; (2) affiliate links left blank for now; (3) 20–30 s, as many detailed steps as possible, not sketchy; (4) photoreal top-down hands-only with AI label; (5) text + music for now (no voice); (6) budget agreed (≤10,000 VND/video, 1–2/day); (7) platforms TikTok, YouTube Shorts, Facebook Reels with review before posting agreed.

Round 6 (2026-11-27) — feedback after paid pilot: colours fine but monotonous across videos; AI label smaller, fainter, first 3 s only ("a (nhỏ và mờ hơn 3s)"); wants smoother motion while keeping Remotion; camera framing locked between steps; chose "SM-1, nội suy thuần" (stop-motion in-betweens for 3–4 key steps rendered with pure optical-flow interpolation). Scope change → IDEA.md revision 2 with a higher cap, re-approval required.

Round 7 (2026-11-27): user asked whether self-filmed footage makes transitions easier and how to film; answered with a filming guide. Decision: "thêm chế độ tự quay, giữ 900k, tôi sẽ thử chạy test trước" → revision 3 adds MVP-10 (self-filmed mode); the user will shoot a test first.

Round 8 (2026-11-27): self-filmed mode moved to phase 2; MVP prioritises AI mode. Revision 4 removes MVP-10 and records it under future enhancements.

Round 9 (2026-11-28) — scope reopened. User: AI-image tutorials cost money yet would flop because the details are not realistic; wants cooking/decor/DIY tutorials that look as real as possible at zero or very low cost, quality over volume (one strong video instead of many weak ones), and an AI subscription instead of API tokens. Approved revision 4 stays the last approved spec until a new revision is approved; implementation paused.

Proposal sent: real phone footage (overhead/eye-level, fixed mount) + subscription AI used manually through a prompt pack (script, shot list, captions) + free automated editing (FFmpeg/OpenCV/Remotion on public-repo GitHub Actions or the user's computer) reusing the existing render/Sheets/Drive code; AI image/video generation dropped from MVP; optional licensed stock B-roll only.

## Research and decisions

Sources checked 2026-11-26 (web search summaries; verify against live docs during the Research stage):

- TikTok Content Posting API: unaudited clients can only post to private accounts (SELF_ONLY); public posting requires an app audit. https://developers.tiktok.com/doc/content-posting-api-get-started , https://developers.tiktok.com/doc/content-posting-api-reference-direct-post
- YouTube Data API videos.insert: uploads from unverified API projects historically restricted to private; a reported Nov 2026 change is unconfirmed. Default quota allows ~100 uploads/day. https://developers.google.com/youtube/v3/docs/videos/insert , https://developers.google.com/youtube/v3/determine_quota_cost
- Gemini API Veo video generation: no free tier; roughly 0.05–0.40 USD per generated second depending on model (secondary sources). https://ai.google.dev/gemini-api/docs/pricing
- Gemini 2.5 Flash Image: about 0.039 USD per 1024x1024 image (1,290 output tokens); batch about half. https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models/gemini/2-5-flash-image , https://blog.laozhang.ai/en/posts/cheapest-gemini-image-generation-api (secondary). TTS price not yet confirmed from an official page.
- Exchange rate Nov 2026: SBV central rate ~25,640 VND/USD; commercial bank selling ~25,900. Planning rate: 26,000 VND/USD, so 5,000 VND ≈ 0.19 USD per clip. https://thoibaotaichinhvietnam.vn/sang-2611-ty-gia-trung-tam-giam-1-dong-gia-usd-on-dinh-26756.html
- Consequence: Veo 3.1 Lite 720p at ~0.05 USD/s means even a 4 s AI clip (~5,200 VND) exceeds the per-clip cap, so AI video is an opt-in premium tier only.
- Local tooling check: examples/video already pins Remotion 4.0.547 with React 19; node 22 and ffmpeg are available, so free local demo renders are feasible.
- Veo 3.1 preview models in the Gemini API reportedly shut down 2026-10-22; successor Gemini Omni Flash. Omni 1.2 Flash GA 2026-11-05 at about 0.07 USD/s for 720p, clips up to 15 s, no free tier (secondary sources). https://ai.google.dev/gemini-api/docs/veo , https://fourweekmba.com/ai-google-cuts-gemini-omni-video-price-30-to-0-07-a-second/ , https://xenospectrum.com/en/gemini-omni-flash-video-pricing/
- Veo 3.1 "ingredients to video": up to 3 reference images for object/character consistency; first/last-frame control. https://developers.googleblog.com/en/introducing-veo-3-1-and-new-creative-capabilities-in-the-gemini-api/
- Google Flow credits (third-party summaries): AI Pro 19.99 USD/month adds 1,000 credits; Veo 3.1 Lite about 10 credits/clip, Fast 20, Quality 100; Flow has no public API. https://inferencehub.org/blog/google-flow-pricing-2026 , https://toyboxai.io/blog/veo-3-pricing/
- Sora: consumer app reportedly discontinued 2026-04-26 and Videos API 2026-09-24 (third-party). https://costgoat.com/pricing/sora , https://framesurfer.com/blogs/sora-2-pricing
- Other APIs: Kling 3.0 about 0.084 USD/s at 720p (prepaid packages); Hailuo about 0.025–0.08 USD/s; Seedance varies widely by reseller. https://apiframe.ai/blog/ai-video-api-pricing-2026 , https://promptsrush.com/blog/kling-ai-pricing
- AI disclosure: TikTok and YouTube require labels for realistic AI content; Shopee Video AI-content guidelines effective 2026-08-01 with penalties for non-disclosure; commission impact of AI labels unconfirmed. https://help.shopee.sg/portal/10/article/201777 , https://billo.app/blog/ai-labeling/ , https://www.bigseller.pro/blog/articleDetails/4649/shopee-video-AI-2026.htm
- Consumer AI subscriptions (ChatGPT Plus, Claude Pro, Gemini Advanced) are chat products; unattended GitHub Actions automation needs an API key billed per use (to confirm with the user's chosen provider).

## Vietnamese approval summary

See the Vietnamese approval summary at the end of IDEA.md (draft digest above).

## Approval record

- Decision: approved (revision 4)
- Approver and evidence reference: repository owner (session user), Claude Code session https://claude.ai/code/session_01Sw1Ye7QBU59wV8h5hqYohk, exact words: "duyệt IDEA"
- Approval timestamp: 2026-11-27 (UTC, after the 08:40 UTC CI run on commit bf5a8e9)
- Approved IDEA.md SHA-256: 37c05f9473c524e2d18e366cf95ce5b6bf9f933966476c36fefb391776a398e6

History (superseded): revisions 2 and 3 were drafted and never approved. Revision 1 approved 2026-11-26 by the repository owner, words "duyệt IDEA", SHA-256 6cc292ac50468275a5a5d054a962a2cda9e11c2f3e681b0d6ba116b7737f3371.

## Handoff

- Project plan and first action: [PLANS.md](PLANS.md) — Research stage, R1: verify official provider pricing and API capabilities (no spend)
- Handoff checkpoint: commit following 7c0710a on branch claude/quirky-planck-wgev52; state handed-off
