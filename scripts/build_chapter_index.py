#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path


HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
INVALID_FILENAME_RE = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
CJK_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
WORD_RE = re.compile(r"[A-Za-z0-9]+(?:[-_'][A-Za-z0-9]+)*")


def count_text_units(text: str) -> int:
    cjk_count = len(CJK_RE.findall(text))
    latin_count = len(WORD_RE.findall(CJK_RE.sub(" ", text)))
    return cjk_count + latin_count


def safe_filename(value: str, max_length: int = 64) -> str:
    value = INVALID_FILENAME_RE.sub("_", value)
    value = re.sub(r"\s+", "_", value).strip("._ ")
    return (value[:max_length].strip("._ ") or "chapter")


def heading_match(line: str) -> tuple[int, str] | None:
    match = HEADING_RE.match(line)
    if not match:
        return None
    title = match.group(2).strip().strip("#").strip()
    if not title:
        return None
    return len(match.group(1)), title


def find_headings(lines: list[str]) -> list[dict[str, object]]:
    headings: list[dict[str, object]] = []
    in_fence = False
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        parsed = heading_match(line)
        if parsed is None:
            continue
        level, title = parsed
        headings.append({"index": index, "line": index + 1, "level": level, "title": title})
    return headings


def recommend_split_level(headings: list[dict[str, object]]) -> int | None:
    counts = Counter(int(item["level"]) for item in headings)
    if counts[1] >= 2:
        return 1
    if counts[2] >= 2:
        return 2
    for level in range(3, 7):
        if counts[level] >= 2:
            return level
    return None


def collect_sections(
    lines: list[str],
    headings: list[dict[str, object]],
    split_level: int,
    include_preface: bool,
) -> list[dict[str, object]]:
    boundaries = [item for item in headings if int(item["level"]) == split_level]
    if not boundaries:
        return []

    sections: list[dict[str, object]] = []
    first_start = int(boundaries[0]["index"])
    if include_preface and first_start > 0:
        preface_text = "\n".join(lines[:first_start]).strip()
        if count_text_units(preface_text) > 0:
            sections.append(
                {
                    "title": "Preface",
                    "level": 0,
                    "start_index": 0,
                    "end_index": first_start,
                    "start_line": 1,
                    "end_line": first_start,
                    "content": preface_text + "\n",
                }
            )

    for index, boundary in enumerate(boundaries):
        start = int(boundary["index"])
        end = int(boundaries[index + 1]["index"]) if index + 1 < len(boundaries) else len(lines)
        content = "\n".join(lines[start:end]).strip()
        if not content:
            continue
        sections.append(
            {
                "title": str(boundary["title"]),
                "level": split_level,
                "start_index": start,
                "end_index": end,
                "start_line": start + 1,
                "end_line": end,
                "content": content + "\n",
            }
        )
    return sections


def write_chapters(src: Path, output_dir: Path, split_level: int, include_preface: bool) -> dict[str, object]:
    text = src.read_text(encoding="utf-8")
    lines = text.splitlines()
    headings = find_headings(lines)
    sections = collect_sections(lines, headings, split_level, include_preface)
    if not sections:
        raise SystemExit(f"No H{split_level} sections found in {src}.")

    chapters_dir = output_dir / "chapters"
    chapters_dir.mkdir(parents=True, exist_ok=True)
    chapters: list[dict[str, object]] = []

    for number, section in enumerate(sections, start=1):
        chapter_id = f"C{number:03d}"
        title = str(section["title"])
        filename = f"{chapter_id}_{safe_filename(title)}.md"
        relative_file = Path("chapters") / filename
        chapter_path = output_dir / relative_file
        content = str(section["content"])
        header = (
            f"<!-- chapter_id: {chapter_id}; source: {src.name}; "
            f"lines: {section['start_line']}-{section['end_line']} -->\n\n"
        )
        chapter_path.write_text(header + content, encoding="utf-8")
        chapters.append(
            {
                "id": chapter_id,
                "title": title,
                "level": section["level"],
                "file": str(relative_file).replace("\\", "/"),
                "start_line": section["start_line"],
                "end_line": section["end_line"],
                "unit_count": count_text_units(content),
            }
        )

    result = {
        "input": str(src),
        "split_level": split_level,
        "chapter_count": len(chapters),
        "chapters_dir": str(chapters_dir),
        "chapters": chapters,
    }
    return result


def write_index_markdown(result: dict[str, object], path: Path) -> None:
    chapters = result["chapters"]
    assert isinstance(chapters, list)
    chunks = [
        "# Chapter Index",
        "",
        f"- Source: `{result['input']}`",
        f"- Split level: `H{result['split_level']}`",
        f"- Chapter count: {result['chapter_count']}",
        "",
        "| ID | Title | Level | File | Lines | Readable size |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for chapter in chapters:
        assert isinstance(chapter, dict)
        title = str(chapter["title"]).replace("|", "\\|")
        chunks.append(
            f"| {chapter['id']} | {title} | H{chapter['level']} | "
            f"`{chapter['file']}` | {chapter['start_line']}-{chapter['end_line']} | {chapter['unit_count']} |"
        )
    path.write_text("\n".join(chunks) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a chapter index and chapter files from a converted Markdown source.")
    parser.add_argument("--input", required=True, help="Path to a converted Markdown source, usually full.md.")
    parser.add_argument("--output-dir", help="Directory for chapter_index.md/json and chapters/. Defaults to the input parent.")
    parser.add_argument("--level", default="auto", help="Heading level to split on, such as 1 or 2. Defaults to auto.")
    parser.add_argument("--include-preface", action="store_true", help="Write content before the first split heading as C001_Preface.md.")
    args = parser.parse_args()

    src = Path(args.input)
    if not src.exists():
        raise SystemExit(f"Input not found: {src}")
    output_dir = Path(args.output_dir) if args.output_dir else src.parent
    output_dir.mkdir(parents=True, exist_ok=True)

    lines = src.read_text(encoding="utf-8").splitlines()
    headings = find_headings(lines)
    if args.level == "auto":
        split_level = recommend_split_level(headings)
        if split_level is None:
            raise SystemExit("No stable heading level found. Run analyze_source_structure.py and keep this source unsplit.")
    else:
        split_level = int(args.level)
        if split_level < 1 or split_level > 6:
            raise SystemExit("--level must be between 1 and 6.")

    result = write_chapters(src, output_dir, split_level, args.include_preface)
    json_path = output_dir / "chapter_index.json"
    md_path = output_dir / "chapter_index.md"
    json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_index_markdown(result, md_path)
    print(md_path)
    print(json_path)
    print(f"chapter_count={result['chapter_count']} split_level=H{result['split_level']}")


if __name__ == "__main__":
    main()
