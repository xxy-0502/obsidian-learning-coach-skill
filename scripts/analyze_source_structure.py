#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path


HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
CJK_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
WORD_RE = re.compile(r"[A-Za-z0-9]+(?:[-_'][A-Za-z0-9]+)*")


def count_text_units(text: str) -> int:
    """Approximate readable size across Chinese and whitespace-delimited text."""
    cjk_count = len(CJK_RE.findall(text))
    latin_count = len(WORD_RE.findall(CJK_RE.sub(" ", text)))
    return cjk_count + latin_count


def iter_markdown_headings(text: str) -> list[dict[str, object]]:
    headings: list[dict[str, object]] = []
    in_fence = False
    for line_number, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        match = HEADING_RE.match(line)
        if not match:
            continue
        title = match.group(2).strip().strip("#").strip()
        if title:
            headings.append(
                {
                    "line": line_number,
                    "level": len(match.group(1)),
                    "title": title,
                }
            )
    return headings


def recommend_split_level(headings: list[dict[str, object]]) -> int | None:
    if not headings:
        return None
    counts = Counter(int(item["level"]) for item in headings)
    if counts[1] >= 2:
        return 1
    if counts[2] >= 2:
        return 2
    for level in range(3, 7):
        if counts[level] >= 2:
            return level
    return None


def analyze_source(
    path: Path,
    small_unit_limit: int,
    large_unit_limit: int,
    min_headings: int,
) -> dict[str, object]:
    text = path.read_text(encoding="utf-8")
    headings = iter_markdown_headings(text)
    heading_counts = Counter(int(item["level"]) for item in headings)
    unit_count = count_text_units(text)
    line_count = len(text.splitlines())
    split_level = recommend_split_level(headings)

    reasons: list[str] = []
    should_split = False
    recommendation = "do_not_split"

    if unit_count < small_unit_limit:
        reasons.append(
            f"Readable size is below the small-source limit ({unit_count} < {small_unit_limit})."
        )
    elif len(headings) < min_headings:
        reasons.append(
            f"Not enough Markdown headings for reliable chapter splitting ({len(headings)} < {min_headings})."
        )
        recommendation = "index_only"
    elif split_level is None:
        reasons.append("No heading level appears often enough to be used as chapter boundaries.")
        recommendation = "index_only"
    else:
        should_split = True
        recommendation = "split_by_headings"
        reasons.append(f"Use H{split_level} headings as chapter boundaries.")
        if unit_count >= large_unit_limit:
            reasons.append(
                f"Readable size is above the large-source limit ({unit_count} >= {large_unit_limit})."
            )

    return {
        "input": str(path),
        "unit_count": unit_count,
        "line_count": line_count,
        "heading_count": len(headings),
        "heading_counts": {f"H{level}": heading_counts[level] for level in range(1, 7)},
        "recommended_split_level": split_level,
        "recommendation": recommendation,
        "should_split": should_split,
        "reasons": reasons,
        "headings": headings,
    }


def write_markdown_report(analysis: dict[str, object], output: Path) -> None:
    heading_counts = analysis["heading_counts"]
    assert isinstance(heading_counts, dict)
    reasons = analysis["reasons"]
    assert isinstance(reasons, list)
    headings = analysis["headings"]
    assert isinstance(headings, list)

    chunks = [
        "# Source Structure",
        "",
        f"- Input: `{analysis['input']}`",
        f"- Readable size: {analysis['unit_count']}",
        f"- Lines: {analysis['line_count']}",
        f"- Headings: {analysis['heading_count']}",
        f"- Recommendation: `{analysis['recommendation']}`",
        f"- Should split: `{str(analysis['should_split']).lower()}`",
        f"- Recommended split level: `{analysis['recommended_split_level'] or 'none'}`",
        "",
        "## Heading Counts",
        "",
        "| Level | Count |",
        "| --- | --- |",
    ]
    for level in range(1, 7):
        chunks.append(f"| H{level} | {heading_counts.get(f'H{level}', 0)} |")

    chunks.extend(["", "## Reasons", ""])
    for reason in reasons:
        chunks.append(f"- {reason}")

    chunks.extend(["", "## Heading Outline", "", "| Line | Level | Title |", "| --- | --- | --- |"])
    for item in headings:
        assert isinstance(item, dict)
        title = str(item["title"]).replace("|", "\\|")
        chunks.append(f"| {item['line']} | H{item['level']} | {title} |")

    output.write_text("\n".join(chunks) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze whether a converted Markdown source should be split by chapters.")
    parser.add_argument("--input", required=True, help="Path to a converted Markdown source, usually full.md.")
    parser.add_argument("--output-dir", help="Directory for source_structure.md/json. Defaults to the input parent.")
    parser.add_argument("--small-unit-limit", type=int, default=20000)
    parser.add_argument("--large-unit-limit", type=int, default=80000)
    parser.add_argument("--min-headings", type=int, default=3)
    args = parser.parse_args()

    src = Path(args.input)
    if not src.exists():
        raise SystemExit(f"Input not found: {src}")
    output_dir = Path(args.output_dir) if args.output_dir else src.parent
    output_dir.mkdir(parents=True, exist_ok=True)

    analysis = analyze_source(src, args.small_unit_limit, args.large_unit_limit, args.min_headings)
    json_path = output_dir / "source_structure.json"
    md_path = output_dir / "source_structure.md"
    json_path.write_text(json.dumps(analysis, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown_report(analysis, md_path)
    print(md_path)
    print(json_path)
    print(f"recommendation={analysis['recommendation']} should_split={str(analysis['should_split']).lower()}")


if __name__ == "__main__":
    main()
