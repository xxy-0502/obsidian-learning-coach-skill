from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_repo_file(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def read_note_templates(*names: str) -> str:
    return "\n".join(
        read_repo_file(f"references/templates/{name}.md") for name in names
    )


def read_routes(*names: str) -> str:
    return "\n".join(
        read_repo_file(f"references/routes/{name}.md") for name in names
    )


class SkillRuleTests(unittest.TestCase):
    def test_planning_route_keeps_roadmaps_out_of_lessons(self):
        skill = read_repo_file("SKILL.md")
        workflow = read_routes("planning")
        note_format = read_note_templates("progress-plan")
        combined = "\n".join([skill, workflow, note_format])

        self.assertIn("Use Planning Route", skill)
        self.assertIn("progress/[topic]/", combined)
        self.assertIn("Do not create", combined)
        self.assertIn("lessons/00_学习路径.md", combined)
        self.assertIn("00_考试学习路径.md", combined)
        self.assertIn("exam plans, learning paths, roadmaps, or schedules", note_format)

    def test_long_pdf_page_count_failure_is_a_stop_condition(self):
        skill = read_repo_file("SKILL.md")
        converter = read_repo_file("scripts/convert_to_markdown.py")

        self.assertIn("PDF page count cannot be inspected", skill)
        self.assertIn("STOP: Cannot inspect PDF page count", converter)
        self.assertIn("sys.exit(6)", converter)
        self.assertIn("do not upload the unsplit PDF", skill)

    def test_stem_notes_require_reviewable_structure(self):
        skill = read_repo_file("SKILL.md")
        note_format = read_note_templates("lesson-note")

        required_terms = [
            "definitions",
            "assumptions",
            "variables",
            "formulas",
            "boundary conditions",
            "common mistakes",
            "active-recall checks",
        ]
        for term in required_terms:
            self.assertIn(term, skill)

        required_headings = [
            "### 定义与目标",
            "### 前提假设与适用范围",
            "### 符号、变量与单位",
            "### 核心公式、定理或算法",
            "### 边界条件、近似与失效场景",
            "### 常见错误与检查方法",
        ]
        for heading in required_headings:
            self.assertIn(heading, note_format)

    def test_lessons_must_create_complete_concept_notes(self):
        skill = read_repo_file("SKILL.md")
        workflow = read_routes(
            "topic-first",
            "source-first",
            "concept-completion-gate",
        )
        note_format = read_note_templates("concept-note")
        combined = "\n".join([skill, workflow, note_format])

        self.assertIn("Do not leave `concepts/` empty", skill)
        self.assertIn("Concept Completion Gate", workflow)
        self.assertIn("Concept Completion Checklist", note_format)
        self.assertIn("scripts/validate_concepts.py", skill)
        self.assertIn("scripts/validate_concepts.py", workflow)
        self.assertIn("scripts/run_learning_eval.py", skill)
        self.assertIn("scripts/run_learning_eval.py", workflow)
        self.assertIn("at least 3 concept notes", combined)

        required_content = [
            "one-sentence definition",
            "problem solved",
            "why it matters",
            "core explanation",
            "example",
            "common confusion",
            "active-recall question",
            "source/provenance",
        ]
        for phrase in required_content:
            self.assertIn(phrase, combined)

        anti_placeholder_rules = [
            "only a title",
            "one-line definition",
            "headings/backlinks",
        ]
        for phrase in anti_placeholder_rules:
            self.assertIn(phrase, combined)


if __name__ == "__main__":
    unittest.main()
