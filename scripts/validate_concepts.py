#!/usr/bin/env python
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


WIKI_LINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]")
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*", re.DOTALL)
INVALID_FILENAME_RE = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)
PLACEHOLDER_RE = re.compile(
    r"(TODO|TBD|placeholder|待补|待完善|稍后补充|未填写|这里填写)",
    re.IGNORECASE,
)

REQUIRED_SECTION_GROUPS = {
    "definition": ["## 一句话解释", "## 定义", "## One-sentence definition"],
    "problem": ["## 它解决什么问题", "## Problem solved"],
    "importance": ["## 为什么重要", "## Why it matters"],
    "core": ["## 核心理解", "## Core explanation"],
    "example": ["## 例子", "## Example"],
    "confusion": ["## 常见混淆", "## 边界条件", "## Common confusion", "## Boundary"],
    "recall": ["## 主动回忆", "## Active recall"],
    "relations": ["## 关系说明", "## Relationship"],
    "source": ["## 来源", "## Source", "## Provenance"],
}
MIN_SECTION_CHARS = {
    "source": 8,
}
CONCEPT_SECTION_TITLES = {
    "本课概念",
    "基础概念补齐",
    "Concepts",
    "Lesson concepts",
    "Foundation concepts",
}


def strip_fenced_blocks(text: str) -> str:
    lines: list[str] = []
    in_fence = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if not in_fence:
            lines.append(line)
    return "\n".join(lines)


def safe_filename(value: str) -> str:
    return INVALID_FILENAME_RE.sub("_", value).strip().strip(".") or "concept"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def extract_wiki_concepts(text: str) -> list[str]:
    seen: set[str] = set()
    concepts: list[str] = []
    for match in WIKI_LINK_RE.finditer(text):
        name = match.group(1).strip()
        if not name or name in seen:
            continue
        seen.add(name)
        concepts.append(name)
    return concepts


def add_concept(concepts: list[str], seen: set[str], raw: str) -> None:
    name = raw.strip().strip("`*_：:，,。；;")
    name = re.sub(r"^\d+[\.\)]\s*", "", name)
    name = re.sub(r"^[-+]\s*", "", name)
    name = name.strip()
    if not name or name in seen:
        return
    seen.add(name)
    concepts.append(name)


def extract_plain_concepts_from_sections(text: str) -> list[str]:
    sections = markdown_sections(text)
    concepts: list[str] = []
    seen: set[str] = set()
    for title, body in sections.items():
        if title not in CONCEPT_SECTION_TITLES:
            continue
        for line in body.splitlines():
            stripped = line.strip()
            if not stripped.startswith(("-", "+")):
                continue
            item = stripped.lstrip("-+").strip()
            if not item or "[[" in item:
                continue
            item = re.split(r"\s+[：:]\s+|\s+-\s+|\s+—\s+", item, maxsplit=1)[0]
            add_concept(concepts, seen, item)
    return concepts


def extract_lesson_concepts(text: str) -> list[str]:
    concepts: list[str] = []
    seen: set[str] = set()
    for name in extract_wiki_concepts(text) + extract_plain_concepts_from_sections(text):
        add_concept(concepts, seen, name)
    return concepts


def concept_path(concepts_dir: Path, concept: str) -> Path:
    direct = concepts_dir / f"{concept}.md"
    if direct.exists():
        return direct
    return concepts_dir / f"{safe_filename(concept)}.md"


def has_type_concept(text: str) -> bool:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return False
    return re.search(r"(?m)^type:\s*concept\s*$", match.group(1)) is not None


def heading_name(value: str) -> str:
    return value.lstrip("#").strip()


def markdown_sections(text: str) -> dict[str, str]:
    clean = strip_fenced_blocks(text)
    matches = list(HEADING_RE.finditer(clean))
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        title = match.group(2).strip().strip("#").strip()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(clean)
        sections[title] = clean[start:end].strip()
    return sections


def find_section(sections: dict[str, str], candidates: list[str]) -> tuple[str, str] | None:
    names = {heading_name(candidate) for candidate in candidates}
    for title, body in sections.items():
        if title in names:
            return title, body
    return None


def meaningful_text_length(text: str) -> int:
    no_links = re.sub(r"\[\[[^\]]+\]\]", "", text)
    no_md = re.sub(r"[#>*_`\-\|\[\]\(\):：\s]", "", no_links)
    return len(no_md)


def validate_concept_file(path: Path, min_chars: int) -> list[str]:
    errors: list[str] = []
    if not path.exists():
        return [f"missing concept file: {path}"]
    text = read_text(path).strip()
    if len(text) < min_chars:
        errors.append(f"concept file too short ({len(text)} < {min_chars} chars): {path}")
    if not has_type_concept(text):
        errors.append(f"missing frontmatter type: concept: {path}")
    if PLACEHOLDER_RE.search(text):
        errors.append(f"placeholder text remains: {path}")
    sections = markdown_sections(text)
    for group, headings in REQUIRED_SECTION_GROUPS.items():
        section = find_section(sections, headings)
        if section is None:
            errors.append(f"missing required section {group}: {path}")
            continue
        title, body = section
        min_section_chars = MIN_SECTION_CHARS.get(group, 20)
        if meaningful_text_length(body) < min_section_chars:
            errors.append(f"required section {group} has too little content under '{title}': {path}")
    return errors


def validate_lesson(
    vault: Path,
    topic: str,
    lesson: Path,
    min_concepts: int,
    min_chars: int,
) -> list[str]:
    lesson_text = read_text(lesson)
    concepts = extract_lesson_concepts(lesson_text)
    errors: list[str] = []
    if len(concepts) < min_concepts:
        errors.append(f"lesson has too few concept links ({len(concepts)} < {min_concepts}): {lesson}")

    concepts_dir = vault / "notes" / topic / "concepts"
    if not concepts_dir.exists():
        errors.append(f"missing concepts directory: {concepts_dir}")
        return errors

    for concept in concepts:
        errors.extend(validate_concept_file(concept_path(concepts_dir, concept), min_chars))
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate that lesson concept links have complete concept notes.")
    parser.add_argument("--vault", default="LearningVault")
    parser.add_argument("--topic", required=True)
    parser.add_argument("--lesson", required=True, help="Lesson file path or lesson filename under notes/[topic]/lessons.")
    parser.add_argument("--min-concepts", type=int, default=3)
    parser.add_argument("--min-chars", type=int, default=500)
    args = parser.parse_args()

    vault = Path(args.vault)
    lesson = Path(args.lesson)
    if not lesson.exists():
        lesson = vault / "notes" / args.topic / "lessons" / args.lesson
    if not lesson.exists():
        raise SystemExit(f"Lesson not found: {args.lesson}")

    errors = validate_lesson(vault, args.topic, lesson, args.min_concepts, args.min_chars)
    if errors:
        print("STOP: Concept completion gate failed.")
        for error in errors:
            print(f"- {error}")
        sys.exit(1)

    print("Concept completion gate passed.")
    print(f"- lesson: {lesson}")


if __name__ == "__main__":
    main()
