#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


TEXT_EXTS = {".md", ".markdown", ".txt"}
COMPLEX_EXTS = {".pdf", ".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff", ".doc", ".docx", ".ppt", ".pptx"}
LONG_SOURCE_UNITS = 20000


def run_command(args: list[str]) -> str:
    result = subprocess.run(args, text=True, capture_output=True)
    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(message or f"Command failed: {' '.join(args)}")
    return result.stdout.strip()


def default_output_path(src: Path, vault: Path) -> Path:
    return vault / "inbox" / "converted" / src.stem / "full.md"


def parse_last_path(output: str, suffix: str) -> Path | None:
    for line in reversed(output.splitlines()):
        stripped = line.strip()
        if stripped.endswith(suffix):
            return Path(stripped)
    return None


def load_analysis(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Prepare a source for source-first learning: convert, analyze, split chapters, and report final paths."
    )
    parser.add_argument("--input", required=True)
    parser.add_argument("--vault", default="LearningVault")
    parser.add_argument("--output")
    parser.add_argument("--env")
    parser.add_argument("--split-pages", type=int, default=180)
    parser.add_argument("--keep-parts", action="store_true", help="Keep temporary PDF part files from conversion.")
    parser.add_argument("--force-chapters", action="store_true", help="Build a chapter index even when analysis is index_only.")
    parser.add_argument("--no-chapter-index", action="store_true", help="Only convert and analyze; do not build chapters.")
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    src = Path(args.input)
    vault = Path(args.vault)
    if not src.exists():
        raise SystemExit(f"Input not found: {src}")

    ext = src.suffix.lower()
    if ext not in TEXT_EXTS and ext not in COMPLEX_EXTS:
        raise SystemExit(f"Unsupported file extension: {ext}. Provide Markdown/text or add converter support.")

    converted = Path(args.output) if args.output else default_output_path(src, vault)

    command = [
        sys.executable,
        str(script_dir / "convert_to_markdown.py"),
        "--input",
        str(src),
        "--output",
        str(converted),
        "--vault",
        str(vault),
        "--split-pages",
        str(args.split_pages),
    ]
    if args.env:
        command.extend(["--env", args.env])
    if args.keep_parts:
        command.append("--keep-parts")
    print(run_command(command))

    analysis_output = run_command(
        [
            sys.executable,
            str(script_dir / "analyze_source_structure.py"),
            "--input",
            str(converted),
        ]
    )
    print(analysis_output)

    analysis_json = parse_last_path(analysis_output, "source_structure.json") or converted.parent / "source_structure.json"
    analysis = load_analysis(analysis_json)
    unit_count = int(analysis.get("unit_count", 0))
    should_split = bool(analysis.get("should_split"))
    recommendation = str(analysis.get("recommendation", "unknown"))

    chapter_index: Path | None = None
    if not args.no_chapter_index and (should_split or args.force_chapters):
        try:
            chapter_output = run_command(
                [
                    sys.executable,
                    str(script_dir / "build_chapter_index.py"),
                    "--input",
                    str(converted),
                ]
            )
        except RuntimeError as exc:
            if args.force_chapters:
                raise
            print(f"STOP: Chapter splitting was recommended but failed: {exc}")
            print("Ask the user whether to force a split level, use a smaller section, or keep the source unsplit.")
        else:
            print(chapter_output)
            chapter_index = parse_last_path(chapter_output, "chapter_index.json")
            if chapter_index is not None:
                chapter_index = chapter_index.with_suffix(".md")

    if not chapter_index:
        candidate = converted.parent / "chapter_index.md"
        if candidate.exists():
            chapter_index = candidate

    print("\nPrepared source:")
    print(f"- converted: {converted}")
    print(f"- structure: {analysis_json.with_suffix('.md')}")
    if chapter_index and chapter_index.exists():
        print(f"- chapter_index: {chapter_index}")
        print(f"- chapters: {chapter_index.parent / 'chapters'}")
    elif unit_count >= LONG_SOURCE_UNITS and not args.no_chapter_index:
        print(f"- STOP: source is long ({unit_count} units) but was not split; recommendation={recommendation}")
        print("- Ask the user whether to force chapter splitting or continue with a smaller section.")
    else:
        print(f"- chapter_index: none; recommendation={recommendation}")


if __name__ == "__main__":
    main()
