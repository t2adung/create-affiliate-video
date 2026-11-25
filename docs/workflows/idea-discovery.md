# Idea Discovery

RAW_IDEA.md → Idea Discovery → Clarification → Research → Draft IDEA.md →
User Approval → Project Planning → Autonomous Development → Testing →
Evaluation → Delivery

## Start or resume

Use this workflow for new projects and revisions to approved product scope.
Use a few Vietnamese or English sentences from chat or [RAW_IDEA.md](../../RAW_IDEA.md).
If entered in chat, preserve the idea in the file or keep a safe local reference.
Keep secrets, personal information and proprietary examples out of tracked files.
Use sanitized notes and synthetic examples when sharing work.

Create IDEA_REVIEW.md at the repository root from [the review template](../templates/idea-review.md).
Read it before restarting discovery. Use states `intake`, `clarifying`,
`researching`, `awaiting-approval`, `approved`, and `handed-off`.
Record the raw-input revision (commit, hash or safe conversation reference),
mode, user language, questions and answers, sources and decisions, draft
digest, last completed action and next action. Save after each state change
and before pausing. On resume, compare the source revision and draft digest
and continue from the earliest affected step. Leave an unrelated legacy plan
intact during discovery.

## Choose a mode

| Mode | Behavior |
| --- | --- |
| QUICK | Draft with documented reversible assumptions. Ask only when a missing answer blocks a usable and safe scope. |
| INTERACTIVE | Default. Ask essential questions before finalizing requirements. If the idea already answers them, proceed with the draft. |
| RESEARCH | Compare feasible solutions, constraints, effort and costs before recommending an approach. Ask only for business or product decisions that still block the draft. |

## Clarification and research

Extract the problem, users, existing task and desired results. Ask in the
user's language and group questions that materially change scope, acceptance,
data handling, cost or permissions. Give plain-language options when helpful.
Record each material assumption and distinguish it from confirmed requirements.
If research could resolve a technical uncertainty in any mode, use free
sources or local inspection and record dated sources, findings and limitations.
Compare a minimal local approach with alternatives where they are viable.
Use mocks or synthetic inputs for feasibility checks. Keep unapproved external
spending at zero and obtain explicit authorization before paid usage, sending
private data to a provider, publishing or deployment.

## Draft and review

Write root IDEA.md using [the idea template](../templates/idea-template.md).
Adapt contracts and checks to the domain, for example citations for document
outputs, timing for media, or delivery side effects for automation. Cover
scope, exclusions, MVP and future features, input validation, output errors,
technology tradeoffs, complexity, usage-based cost assumptions and the approved
spend cap, privacy, security, licensing, risks and evaluation. Resolve blocking
questions before asking for approval. Match every MVP requirement to an observable
test and include invalid-input behavior when relevant.

Record the SHA-256 of the exact IDEA.md bytes, for example with
`sha256sum IDEA.md`, and set the state to `awaiting-approval`. Show the
user a short Vietnamese summary of the product, MVP scope, result, material
assumptions and risks, and approved cost cap. Identify the draft and ask
whether they approve it or want changes.

## Approval gate

Wait for explicit user approval of the presented IDEA.md revision. Silence,
an agent-authored status value, and general encouragement are insufficient.
Record the approver, timestamp, exact approval words or a durable conversation
reference, and the approved SHA-256. Set the state to `approved`. Before
planning or resuming implementation, verify the evidence and compare the
current file digest to the approved digest. Any edit to IDEA.md requires a
new review and explicit approval. A changed raw idea that may affect scope
returns to discovery before work resumes. Keep previous approval evidence
as history when superseded. A rejected or ambiguous response stays in discovery.

## Project planning and handoff

After the gate passes, initialize project-specific PLANS.md with the approved
IDEA.md digest and evidence link, delivery profile, ordered stages, acceptance
checks, decisions, evidence, and first executable action. Preserve current
project checkpoints when revising an existing plan. Link the plan from
IDEA_REVIEW.md, set `handed-off`, and invoke the existing
[orchestrator](../../.agents/skills/orchestrator/SKILL.md). Resume from PLANS.md
and the [checkpoint template](../templates/checkpoint.md) for implementation,
testing, evaluation and delivery. Reopen discovery when approved scope changes.

See [synthetic examples](../examples/idea-builder/) for complete specifications
from short raw ideas. The examples illustrate drafts awaiting user approval.
