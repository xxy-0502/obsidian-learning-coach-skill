#!/usr/bin/env python
from __future__ import annotations

import argparse
import re
from datetime import date
from pathlib import Path


START = "<!-- AUTO-KNOWLEDGE-MAP:START -->"
END = "<!-- AUTO-KNOWLEDGE-MAP:END -->"
LINK_RE = re.compile(r"\[\[([^\]\|#]+)(?:#[^\]\|]+)?(?:\|[^\]]+)?\]\]")
RELATION_KEYWORDS = ("前置", "依赖", "混淆", "区别", "属于", "导致", "影响", "组成", "实现", "应用")


def safe_topic(topic: str) -> str:
    return "".join("_" if ch in '<>:"/\\|?*' else ch for ch in topic).strip() or "未命名主题"


def extract_links(text: str) -> set[str]:
    links: set[str] = set()
    for match in LINK_RE.finditer(text):
        target = match.group(1).strip()
        if not target or target == "知识地图" or target.endswith("知识地图"):
            continue
        links.add(target)
    return links


def is_placeholder(path: Path) -> bool:
    if not path.exists():
        return True
    text = path.read_text(encoding="utf-8").strip()
    meaningful = [
        line
        for line in text.splitlines()
        if line.strip()
        and not line.lstrip().startswith("#")
        and not line.lstrip().startswith("---")
        and not line.lstrip().startswith("type:")
        and not line.lstrip().startswith("topic:")
        and not line.lstrip().startswith("tags:")
    ]
    return len("\n".join(meaningful)) < 120


def collect_topic(notes_dir: Path) -> dict[str, object]:
    concepts_dir = notes_dir / "concepts"
    lessons_dir = notes_dir / "lessons"
    concepts = {path.stem for path in concepts_dir.glob("*.md")}
    lesson_links: dict[str, set[str]] = {}
    relationship_lines: list[str] = []

    for path in sorted(list(lessons_dir.glob("*.md")) + list(concepts_dir.glob("*.md"))):
        text = path.read_text(encoding="utf-8")
        links = extract_links(text)
        if path.parent == lessons_dir:
            lesson_links[path.stem] = links
        concepts.update(links)
        for raw_line in text.splitlines():
            line = raw_line.strip()
            if len(extract_links(line)) >= 2 and any(keyword in line for keyword in RELATION_KEYWORDS):
                relationship_lines.append(line)

    incomplete = sorted(
        concept
        for concept in concepts
        if is_placeholder(concepts_dir / f"{concept}.md")
    )

    return {
        "concepts": sorted(concepts),
        "lesson_links": lesson_links,
        "relationships": sorted(dict.fromkeys(relationship_lines)),
        "incomplete": incomplete,
    }


def render_auto_block(topic: str, data: dict[str, object], today: str) -> str:
    concepts: list[str] = data["concepts"]  # type: ignore[assignment]
    lesson_links: dict[str, set[str]] = data["lesson_links"]  # type: ignore[assignment]
    relationships: list[str] = data["relationships"]  # type: ignore[assignment]
    incomplete: list[str] = data["incomplete"]  # type: ignore[assignment]

    lines = [
        START,
        "",
        "## 自动维护区",
        "",
        f"- 更新时间：{today}",
        f"- 主题：{topic}",
        "",
        "### 概念索引",
        "",
    ]
    if concepts:
        lines.extend(f"- [[{concept}]]" for concept in concepts)
    else:
        lines.append("- 暂无概念链接")

    lines.extend(["", "### 课程链接概览", ""])
    if lesson_links:
        for lesson, links in sorted(lesson_links.items()):
            linked = "、".join(f"[[{link}]]" for link in sorted(links)) or "暂无稳定概念链接"
            lines.append(f"- [[{lesson}]]：{linked}")
    else:
        lines.append("- 暂无课程笔记")

    lines.extend(["", "### 关系线索", ""])
    if relationships:
        lines.extend(f"- {line}" for line in relationships)
    else:
        lines.append("- 暂无自动识别的关系句")

    lines.extend(["", "### 待补全概念", ""])
    if incomplete:
        lines.extend(f"- [[{concept}]]" for concept in incomplete)
    else:
        lines.append("- 无")

    lines.extend(["", END, ""])
    return "\n".join(lines)


def replace_auto_block(existing: str, block: str) -> str:
    if START in existing and END in existing:
        before, rest = existing.split(START, 1)
        _, after = rest.split(END, 1)
        return before.rstrip() + "\n\n" + block.rstrip() + "\n" + after.lstrip()
    return existing.rstrip() + "\n\n" + block


def update_knowledge_map(vault: Path, topic: str, today: str) -> Path:
    name = safe_topic(topic)
    notes_dir = vault / "notes" / name
    map_path = notes_dir / "maps" / f"{name}知识地图.md"
    map_path.parent.mkdir(parents=True, exist_ok=True)
    if map_path.exists():
        existing = map_path.read_text(encoding="utf-8")
    else:
        existing = f"# {topic} 知识地图\n\n## 学习路径\n\n## 前置关系\n\n## 复习重点\n"
    block = render_auto_block(topic, collect_topic(notes_dir), today)
    map_path.write_text(replace_auto_block(existing, block), encoding="utf-8")
    return map_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Update a topic knowledge map from lessons and concept links.")
    parser.add_argument("--vault", default="LearningVault")
    parser.add_argument("--topic", required=True)
    parser.add_argument("--date", default=date.today().isoformat())
    args = parser.parse_args()
    path = update_knowledge_map(Path(args.vault), args.topic, args.date)
    print(f"Updated knowledge map: {path}")


if __name__ == "__main__":
    main()
