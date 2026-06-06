#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from datetime import date, timedelta
from pathlib import Path


def parse_rows(path: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line.startswith("|") or "---" in line or "日期" in line:
            continue
        parts = [p.strip() for p in line.strip("|").split("|")]
        if len(parts) >= 6:
            rows.append({"date": parts[0], "topic": parts[1], "lesson": parts[2], "review": parts[3], "note": parts[4], "status": parts[5]})
        elif len(parts) >= 5:
            rows.append({"date": parts[0], "lesson": parts[1], "review": parts[2], "status": parts[3], "note": parts[4]})
    return rows


def scan(vault: Path, today: date) -> dict[str, list[dict[str, str]]]:
    groups = {"overdue": [], "today": [], "next_3_days": []}
    for plan in (vault / "progress").glob("*/复习计划.md"):
        topic = plan.parent.name
        for row in parse_rows(plan):
            if row["status"] not in {"pending", "待复习", ""}:
                continue
            try:
                due = date.fromisoformat(row["date"])
            except ValueError:
                continue
            item = {"topic": row.get("topic") or topic, **row}
            if due < today:
                groups["overdue"].append(item)
            elif due == today:
                groups["today"].append(item)
            elif due <= today + timedelta(days=3):
                groups["next_3_days"].append(item)
    return groups


def render_markdown(groups: dict[str, list[dict[str, str]]]) -> str:
    labels = [("overdue", "已过期"), ("today", "今天到期"), ("next_3_days", "未来 3 天")]
    if not any(groups.values()):
        return "今天没有到期复习。"
    chunks = ["# 到期复习\n"]
    for key, label in labels:
        chunks.append(f"## {label}\n")
        if not groups[key]:
            chunks.append("无\n")
            continue
        chunks.append("| 主题 | 日期 | 课程 | 复习次 | 状态 | 备注 |")
        chunks.append("| --- | --- | --- | --- | --- | --- |")
        for item in groups[key]:
            chunks.append(f"| {item['topic']} | {item['date']} | {item['lesson']} | {item['review']} | {item['status']} | {item['note']} |")
        chunks.append("")
    return "\n".join(chunks)


def main() -> None:
    parser = argparse.ArgumentParser(description="Scan LearningVault review plans.")
    parser.add_argument("--vault", default="LearningVault")
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--json", action="store_true", help="Output JSON instead of Markdown")
    args = parser.parse_args()
    groups = scan(Path(args.vault), date.fromisoformat(args.date))
    if args.json:
        print(json.dumps(groups, ensure_ascii=False, indent=2))
    else:
        print(render_markdown(groups))


if __name__ == "__main__":
    main()
