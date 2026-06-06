#!/usr/bin/env python
from __future__ import annotations

import argparse
from datetime import date, timedelta
from pathlib import Path


INTERVALS = [1, 3, 7, 14, 30]


def append(path: Path, line: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text("", encoding="utf-8")
    with path.open("a", encoding="utf-8") as fh:
        fh.write(line.rstrip() + "\n")


def insert_table_row(path: Path, section: str, row: str) -> bool:
    if not path.exists():
        return False
    lines = path.read_text(encoding="utf-8").splitlines()
    in_section = False
    separator_seen = False
    for idx, line in enumerate(lines):
        if line.strip() == f"## {section}":
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if in_section and line.strip().startswith("| ---"):
            separator_seen = True
            continue
        if in_section and separator_seen:
            lines.insert(idx, row)
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return True
    if in_section and separator_seen:
        lines.append(row)
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return True
    return False


def record(path: Path, section: str, row: str) -> None:
    if not insert_table_row(path, section, row):
        append(path, row)


def replace_prefixed_line(path: Path, prefix: str, value: str) -> None:
    if not path.exists():
        return
    lines = path.read_text(encoding="utf-8").splitlines()
    for idx, line in enumerate(lines):
        if line.startswith(prefix):
            lines[idx] = f"{prefix}{value}"
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return


def next_review_label(current: str) -> tuple[str, int]:
    digits = "".join(ch for ch in current if ch.isdigit())
    n = int(digits) if digits else 0
    next_n = min(n + 1, len(INTERVALS))
    return f"第 {next_n} 次", INTERVALS[next_n - 1]


def main() -> None:
    parser = argparse.ArgumentParser(description="Update review, progress, and missed-point records.")
    parser.add_argument("--vault", default="LearningVault")
    parser.add_argument("--topic", required=True)
    parser.add_argument("--lesson", required=True)
    parser.add_argument("--result", required=True, choices=["完全掌握", "基本掌握", "部分理解", "尚未理解"])
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--review", default="第 0 次")
    parser.add_argument("--missed", default="")
    parser.add_argument("--question", default="", help="Question or prompt where the missed point appeared")
    parser.add_argument("--correct", default="", help="Correct understanding for the missed point")
    args = parser.parse_args()

    today = date.fromisoformat(args.date)
    base = Path(args.vault) / "progress" / args.topic
    progress = base / "进度.md"
    misses = base / "错题与遗漏.md"
    plan = base / "复习计划.md"
    if args.result in {"完全掌握", "基本掌握"}:
        label, days = next_review_label(args.review)
        due = today + timedelta(days=days)
        focus = args.missed or "核心概念主动回忆"
        replace_prefixed_line(progress, "- 最后学习日期：", today.isoformat())
        replace_prefixed_line(progress, "- 最后复习日期：", today.isoformat())
        replace_prefixed_line(progress, "- 正在学习：", args.lesson)
        replace_prefixed_line(progress, "- 最近卡点：", args.missed or "无")
        replace_prefixed_line(progress, "- 下一步建议：", f"进入下一课或在 {due.isoformat()} 复习")
        record(plan, "待复习队列", f"| {due.isoformat()} | {args.topic} | {args.lesson} | {label} | {focus} | 待复习 |")
        record(plan, "复习记录", f"| {today.isoformat()} | {args.lesson} | {args.result} | {args.missed or '无'} | {due.isoformat()} |")
        record(progress, "课程进度", f"| {args.lesson} | {today.isoformat()} | {args.result} | {due.isoformat()} | {args.missed or '无'} |")
        if args.result == "基本掌握" and args.missed:
            record(misses, "活跃遗漏", f"| {today.isoformat()} | {args.lesson} | {args.missed} | {args.question or '未记录'} | {args.correct or '待补充'} | 下次复习检查 | 小遗漏 |")
    elif args.result == "部分理解":
        replace_prefixed_line(progress, "- 最后学习日期：", today.isoformat())
        replace_prefixed_line(progress, "- 正在学习：", args.lesson)
        replace_prefixed_line(progress, "- 最近卡点：", args.missed or "待补充")
        replace_prefixed_line(progress, "- 下一步建议：", "生成补充课，不进入下一课")
        record(misses, "活跃遗漏", f"| {today.isoformat()} | {args.lesson} | {args.missed or '待补充'} | {args.question or '未记录'} | {args.correct or '待补充'} | 补充课后复查 | open |")
        record(plan, "复习记录", f"| {today.isoformat()} | {args.lesson} | 部分理解 | {args.missed or '待补充'} | 暂不推进 |")
    else:
        replace_prefixed_line(progress, "- 最后学习日期：", today.isoformat())
        replace_prefixed_line(progress, "- 正在学习：", args.lesson)
        replace_prefixed_line(progress, "- 最近卡点：", args.missed or "核心卡点待定位")
        replace_prefixed_line(progress, "- 下一步建议：", "苏格拉底追问，重建理解")
        record(misses, "活跃遗漏", f"| {today.isoformat()} | {args.lesson} | {args.missed or '核心卡点待定位'} | {args.question or '未记录'} | {args.correct or '待补充'} | 追问澄清 | open |")
        record(plan, "复习记录", f"| {today.isoformat()} | {args.lesson} | 尚未理解 | {args.missed or '核心卡点待定位'} | 暂不推进 |")
    print(f"Updated review state for {args.topic} / {args.lesson} on {today.isoformat()}.")


if __name__ == "__main__":
    main()
