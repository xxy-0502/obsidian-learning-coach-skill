#!/usr/bin/env python3
"""Append a lightweight review row to a topic 复习计划.md."""

from __future__ import annotations

import argparse
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Append a review row to LearningVault topic 复习计划.md.")
    parser.add_argument("--review-plan", required=True, help="Path to 复习计划.md.")
    parser.add_argument("--date", required=True, help="Review date in YYYY-MM-DD.")
    parser.add_argument("--content", required=True, help="Review content.")
    parser.add_argument("--reason", required=True, help="Why this review is scheduled.")
    parser.add_argument("--pitfall", default="", help="Related pitfall from 错题遗漏.md.")
    parser.add_argument("--status", default="pending", help="Review status.")
    return parser.parse_args()


def ensure_review_section(text: str) -> str:
    if "## 复习队列" in text:
        return text
    section = "\n## 复习队列\n\n| 日期 | 状态 | 内容 | 触发原因 | 关联坑点 |\n| --- | --- | --- | --- | --- |\n"
    return text.rstrip() + "\n" + section


def main() -> int:
    args = parse_args()
    review_plan = Path(args.review_plan)
    if not review_plan.exists():
        raise SystemExit(f"review plan file not found: {review_plan}")
    text = ensure_review_section(review_plan.read_text(encoding="utf-8"))
    row = f"| {args.date} | {args.status} | {args.content} | {args.reason} | {args.pitfall} |\n"
    review_plan.write_text(text.rstrip() + "\n" + row, encoding="utf-8")
    print(f"added review: {args.date} {args.content}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
