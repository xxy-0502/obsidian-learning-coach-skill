from __future__ import annotations

import contextlib
import importlib.util
import io
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "validate_concepts.py"


def load_module():
    spec = importlib.util.spec_from_file_location("validate_concepts_under_test", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def complete_concept(name: str) -> str:
    return f"""---
type: concept
topic: networking
level: foundation
status: learning
---

# {name}

## One-sentence definition

{name} is a reusable concept note that can be studied without opening the lesson.

## Problem solved

It prevents lessons from creating empty wiki links without durable explanations.

## Why it matters

A complete concept note supports review, backlinks, and later lessons that reuse the idea.

## Core explanation

The note explains the concept in enough detail to stand alone, including what it means, when it applies, and how it connects to the surrounding topic.

## Example

If a lesson links [[{name}]], the file concepts/{name}.md must exist and contain a complete explanation.

## Common confusion

A short definition inside a lesson is not the same as a durable concept note.

## Active recall

Why should a concept note be useful when opened independently from the lesson?

## Relationship

[[{name}]] should connect to other stable concepts that explain the same lesson.

## Source

- test fixture for concept validation
"""


def concept_with_empty_example(name: str) -> str:
    return f"""---
type: concept
topic: networking
level: foundation
status: learning
---

# {name}

## One-sentence definition

{name} is a reusable concept note that can be studied without opening the lesson.

## Problem solved

It prevents lessons from creating empty wiki links without durable explanations.

## Why it matters

A complete concept note supports review, backlinks, and later lessons that reuse the idea.

## Core explanation

The note explains the concept in enough detail to stand alone.

## Example

## Common confusion

A short definition inside a lesson is not the same as a durable concept note.

## Active recall

Why should a concept note be useful when opened independently from the lesson?

## Relationship

[[{name}]] should connect to other stable concepts that explain the same lesson.

## Source

- test fixture for concept validation
"""


class ValidateConceptsTests(unittest.TestCase):
    def make_vault(self):
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        topic = "networking"
        lesson = root / "notes" / topic / "lessons" / "01.md"
        concepts_dir = root / "notes" / topic / "concepts"
        lesson.parent.mkdir(parents=True)
        concepts_dir.mkdir(parents=True)
        lesson.write_text(
            "# Lesson\n\n## Concepts\n\n- [[Network edge]]\n- [[Network core]]\n- [[Packet switching]]\n",
            encoding="utf-8",
        )
        return tmp, root, topic, lesson, concepts_dir

    def lesson_concepts(self, module, lesson: Path) -> list[str]:
        return module.extract_wiki_concepts(lesson.read_text(encoding="utf-8"))

    def test_complete_concepts_pass_gate(self):
        module = load_module()
        tmp, root, topic, lesson, concepts_dir = self.make_vault()
        self.addCleanup(tmp.cleanup)
        for name in self.lesson_concepts(module, lesson):
            (concepts_dir / f"{name}.md").write_text(complete_concept(name), encoding="utf-8")

        errors = module.validate_lesson(root, topic, lesson, min_concepts=3, min_chars=300)

        self.assertEqual(errors, [])

    def test_missing_concept_fails_gate(self):
        module = load_module()
        tmp, root, topic, lesson, concepts_dir = self.make_vault()
        self.addCleanup(tmp.cleanup)
        for name in self.lesson_concepts(module, lesson)[:2]:
            (concepts_dir / f"{name}.md").write_text(complete_concept(name), encoding="utf-8")

        errors = module.validate_lesson(root, topic, lesson, min_concepts=3, min_chars=300)

        self.assertTrue(any("missing concept file" in error for error in errors))

    def test_short_placeholder_concept_fails_gate(self):
        module = load_module()
        tmp, root, topic, lesson, concepts_dir = self.make_vault()
        self.addCleanup(tmp.cleanup)
        names = self.lesson_concepts(module, lesson)
        for name in names:
            text = complete_concept(name) if name != names[2] else f"# {name}\n\nOne-line definition.\n"
            (concepts_dir / f"{name}.md").write_text(text, encoding="utf-8")

        errors = module.validate_lesson(root, topic, lesson, min_concepts=3, min_chars=300)

        self.assertTrue(any("concept file too short" in error for error in errors))
        self.assertTrue(any("missing frontmatter type: concept" in error for error in errors))

    def test_heading_skeleton_with_placeholder_text_fails_gate(self):
        module = load_module()
        tmp, root, topic, lesson, concepts_dir = self.make_vault()
        self.addCleanup(tmp.cleanup)
        names = self.lesson_concepts(module, lesson)
        for name in names[:2]:
            (concepts_dir / f"{name}.md").write_text(complete_concept(name), encoding="utf-8")
        (concepts_dir / f"{names[2]}.md").write_text(complete_concept(names[2]) + "\nTODO\n", encoding="utf-8")

        errors = module.validate_lesson(root, topic, lesson, min_concepts=3, min_chars=300)

        self.assertTrue(any("placeholder text remains" in error for error in errors))

    def test_section_with_no_body_fails_gate(self):
        module = load_module()
        tmp, root, topic, lesson, concepts_dir = self.make_vault()
        self.addCleanup(tmp.cleanup)
        names = self.lesson_concepts(module, lesson)
        for name in names[:2]:
            (concepts_dir / f"{name}.md").write_text(complete_concept(name), encoding="utf-8")
        (concepts_dir / f"{names[2]}.md").write_text(concept_with_empty_example(names[2]), encoding="utf-8")

        errors = module.validate_lesson(root, topic, lesson, min_concepts=3, min_chars=300)

        self.assertTrue(any("required section example has too little content" in error for error in errors))

    def test_too_few_concept_links_fails_gate(self):
        module = load_module()
        tmp, root, topic, lesson, concepts_dir = self.make_vault()
        self.addCleanup(tmp.cleanup)
        lesson.write_text("# Lesson\n\n## Concepts\n\n- [[Network edge]]\n", encoding="utf-8")
        (concepts_dir / "Network edge.md").write_text(complete_concept("Network edge"), encoding="utf-8")

        errors = module.validate_lesson(root, topic, lesson, min_concepts=3, min_chars=300)

        self.assertTrue(any("too few concept links" in error for error in errors))

    def test_plain_concept_items_are_validated_too(self):
        module = load_module()
        tmp, root, topic, lesson, concepts_dir = self.make_vault()
        self.addCleanup(tmp.cleanup)
        lesson.write_text(
            "# Lesson\n\n"
            "## Concepts\n\n"
            "- [[Network edge]]\n"
            "- [[Network core]]\n"
            "- [[Packet switching]]\n"
            "- Routing protocol: plain text concept without wiki link\n",
            encoding="utf-8",
        )
        for name in ["Network edge", "Network core", "Packet switching"]:
            (concepts_dir / f"{name}.md").write_text(complete_concept(name), encoding="utf-8")

        errors = module.validate_lesson(root, topic, lesson, min_concepts=3, min_chars=300)

        self.assertTrue(any("Routing protocol" in error and "missing concept file" in error for error in errors))

    def test_chinese_placeholder_variants_fail_gate(self):
        module = load_module()
        tmp, root, topic, lesson, concepts_dir = self.make_vault()
        self.addCleanup(tmp.cleanup)
        names = self.lesson_concepts(module, lesson)
        for name in names[:2]:
            (concepts_dir / f"{name}.md").write_text(complete_concept(name), encoding="utf-8")
        (concepts_dir / f"{names[2]}.md").write_text(complete_concept(names[2]) + "\n待补\n", encoding="utf-8")

        errors = module.validate_lesson(root, topic, lesson, min_concepts=3, min_chars=300)

        self.assertTrue(any("placeholder text remains" in error for error in errors))

    def test_cli_failure_prints_stop_and_exits_one(self):
        module = load_module()
        tmp, root, topic, lesson, _concepts_dir = self.make_vault()
        self.addCleanup(tmp.cleanup)
        argv = [
            "validate_concepts.py",
            "--vault",
            str(root),
            "--topic",
            topic,
            "--lesson",
            str(lesson),
        ]
        stdout = io.StringIO()
        old_argv = sys.argv
        try:
            sys.argv = argv
            with contextlib.redirect_stdout(stdout):
                with self.assertRaises(SystemExit) as raised:
                    module.main()
        finally:
            sys.argv = old_argv

        self.assertEqual(raised.exception.code, 1)
        self.assertIn("STOP: Concept completion gate failed.", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
