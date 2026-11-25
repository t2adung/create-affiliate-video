"""Verify the Idea Builder documents and synthetic specifications."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = Path("RAW_IDEA.md")
SPEC = Path("docs/templates/idea-template.md")
REVIEW = Path("docs/templates/idea-review.md")
WORKFLOW = Path("docs/workflows/idea-discovery.md")
SKILL = Path(".agents/skills/idea-builder/SKILL.md")
EXAMPLES = Path("docs/examples/idea-builder")
RAW_HEADINGS = ("Your idea / Ý tưởng của bạn", "Discovery mode / Chế độ khám phá")
SPEC_HEADINGS = (
    "Problem and target users", "Desired outcomes", "MVP requirements",
    "Exclusions", "Future enhancements", "Input contract", "Output contract",
    "Technical approach and alternatives", "Complexity and operating costs",
    "Privacy, security, licensing and risks", "Assumptions and open decisions",
    "Acceptance and evaluation",
)
MODES = {"QUICK", "INTERACTIVE", "RESEARCH"}


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


def sections(markdown):
    parts = re.split(r"^## ([^\n]+)\n", markdown, flags=re.MULTILINE)
    return {
        title: re.sub(r"<!--.*?-->", "", body, flags=re.DOTALL).strip()
        for title, body in zip(parts[1::2], parts[2::2])
    }


class IdeaDiscoveryTests(unittest.TestCase):
    def test_template_structure(self):
        raw = sections(read(RAW))
        self.assertEqual(tuple(raw), RAW_HEADINGS)
        self.assertEqual(raw[RAW_HEADINGS[1]], "INTERACTIVE")
        self.assertEqual(tuple(sections(read(SPEC))), SPEC_HEADINGS)
        review = sections(read(REVIEW))
        self.assertEqual(tuple(review), (
            "Resume checkpoint", "Clarifications and assumptions",
            "Research and decisions", "Vietnamese approval summary",
            "Approval record", "Handoff",
        ))
        for field in ("Mode", "State", "User language", "Raw input reference and revision",
                      "Draft IDEA.md SHA-256", "Last completed action", "Next action"):
            self.assertIn(f"- {field}:", review["Resume checkpoint"])
        for field in ("Decision", "Approver and evidence reference",
                      "Approval timestamp", "Approved IDEA.md SHA-256"):
            self.assertIn(f"- {field}: pending", review["Approval record"])

    def test_workflow_structure_and_gate(self):
        self.assertTrue(read(SKILL).startswith("---\nname: idea-builder\n"))
        workflow = sections(read(WORKFLOW))
        self.assertEqual(tuple(workflow), (
            "Start or resume", "Choose a mode", "Clarification and research",
            "Draft and review", "Approval gate", "Project planning and handoff",
        ))
        self.assertEqual(set(re.findall(r"^\| ([A-Z]+) \|", workflow["Choose a mode"],
                                        re.MULTILINE)), MODES)
        gate = workflow["Approval gate"]
        self.assertIn("explicit user approval", gate)
        self.assertIn("approved SHA-256", gate)
        self.assertIn("current file digest", gate)
        self.assertIn("PLANS.md", workflow["Project planning and handoff"])

    def test_examples_cover_modes_and_all_mvp_requirements(self):
        drafts = sorted((ROOT / EXAMPLES).glob("*/IDEA.md"))
        self.assertGreaterEqual(len(drafts), 3)
        modes = set()
        for draft in drafts:
            with self.subTest(example=draft.parent.name):
                raw = sections(read(draft.with_name("RAW_IDEA.md")))
                self.assertEqual(tuple(raw), RAW_HEADINGS)
                self.assertTrue(raw[RAW_HEADINGS[0]])
                modes.add(raw[RAW_HEADINGS[1]])
                spec = sections(read(draft))
                self.assertEqual(tuple(spec), (*SPEC_HEADINGS, "Vietnamese approval summary"))
                for heading, body in spec.items():
                    self.assertTrue(body, heading)
                required = set(re.findall(r"^- (MVP-\d+)\.", spec["MVP requirements"],
                                          re.MULTILINE))
                evaluated = set(re.findall(r"^- (MVP-\d+):", spec["Acceptance and evaluation"],
                                           re.MULTILINE))
                self.assertTrue(required)
                self.assertEqual(required, evaluated)
        self.assertEqual(modes, MODES)

    def test_local_links_resolve(self):
        documents = [
            Path("AGENTS.md"), Path("README.md"), RAW, SPEC, REVIEW, WORKFLOW, SKILL,
            Path(".agents/skills/orchestrator/SKILL.md"),
            *(ROOT / EXAMPLES).rglob("*.md"),
        ]
        for document in documents:
            for target in re.findall(r"\]\(([^)\s]+)\)", read(document)):
                if "://" in target or target.startswith("#"):
                    continue
                with self.subTest(document=document, target=target):
                    self.assertTrue(((ROOT / document).parent / target).exists())
