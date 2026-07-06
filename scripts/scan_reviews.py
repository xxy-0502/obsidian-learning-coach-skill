#!/usr/bin/env python3
"""Scan lightweight review plan files for due review rows."""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scan LearningVault 复习计划.md files for due review items.")
    parser.add_argument("--vault", default="LearningVault", help="Vault root path.")
    parser.add_argument("--date", default=date.today().isoformat(), help="Review date in YYYY-MM-DD.")
    return parser.parse_args()


def iter_review_files(vault: Path):
    topics = vault / "topics"
    if topics.exists():
        yield from topics.glob("*/复习计划.md")
    legacy_notes = vault / "notes"
    if legacy_notes.exists():
        yield from legacy_notes.glob("*/复习计划.md")


def in_review_section(line: str, active: bool) -> bool:
    if line.startswith("## "):
        return line.strip() == "## 复习队列"
    return active


def parse_table_row(line: str):
    if not line.startswith("|"):
        return None
    cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
    if len(cells) < 5 or cells[0] in {"日期", "---"}:
        return None
    return cells[:5]


def main() -> int:
    args = parse_args()
    vault = Path(args.vault)
    due_date = args.date
    rows = []
    for review_file in iter_review_files(vault):
        active = False
        for line in review_file.read_text(encoding="utf-8").splitlines():
            active = in_review_section(line, active)
            if not active:
                continue
            row = parse_table_row(line)
            if not row:
                continue
            review_date, status, content, reason, pitfall = row
            if review_date <= due_date and status not in {"done", "通过", "completed"}:
                rows.append((review_date, review_file.parent.name, content, reason, pitfall, str(review_file)))
    if not rows:
        print(f"{due_date} 没有到期复看。")
        return 0
    print(f"{due_date} 到期复看：")
    for review_date, topic, content, reason, pitfall, review_file in sorted(rows):
        pitfall_note = f"，关联坑点 {pitfall}" if pitfall else ""
        print(f"- [{topic}] {content}（{reason}{pitfall_note}，日期 {review_date}，{review_file}）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
