#!/usr/bin/env python3
"""Append a lightweight review row to a topic progress.md."""

from __future__ import annotations

import argparse
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Append a review row to LearningVault topic progress.md.")
    parser.add_argument("--progress", required=True, help="Path to progress.md.")
    parser.add_argument("--date", required=True, help="Review date in YYYY-MM-DD.")
    parser.add_argument("--content", required=True, help="Review content.")
    parser.add_argument("--reason", required=True, help="Why this review is scheduled.")
    parser.add_argument("--status", default="pending", help="Review status.")
    return parser.parse_args()


def ensure_review_section(text: str) -> str:
    if "## 轻量复看" in text:
        return text
    section = "\n## 轻量复看\n\n| 日期 | 状态 | 内容 | 触发原因 |\n| --- | --- | --- | --- |\n"
    return text.rstrip() + "\n" + section


def main() -> int:
    args = parse_args()
    progress = Path(args.progress)
    if not progress.exists():
        raise SystemExit(f"progress file not found: {progress}")
    text = ensure_review_section(progress.read_text(encoding="utf-8"))
    row = f"| {args.date} | {args.status} | {args.content} | {args.reason} |\n"
    progress.write_text(text.rstrip() + "\n" + row, encoding="utf-8")
    print(f"added review: {args.date} {args.content}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
