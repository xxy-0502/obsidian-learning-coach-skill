#!/usr/bin/env python
from __future__ import annotations

import argparse
import re
from datetime import date, timedelta
from pathlib import Path


LINK_RE = re.compile(r"\[\[([^\]\|#]+)(?:#[^\]\|]+)?(?:\|[^\]]+)?\]\]")


def parse_review_rows(path: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or "---" in stripped or "下次复习" in stripped:
            continue
        parts = [part.strip() for part in stripped.strip("|").split("|")]
        if len(parts) >= 6:
            rows.append(
                {
                    "date": parts[0],
                    "topic": parts[1],
                    "lesson": parts[2],
                    "review": parts[3],
                    "focus": parts[4],
                    "status": parts[5],
                }
            )
    return rows


def parse_active_misses(path: Path) -> int:
    if not path.exists():
        return 0
    count = 0
    in_active = False
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped == "## 活跃遗漏":
            in_active = True
            continue
        if in_active and stripped.startswith("## "):
            break
        if in_active and stripped.startswith("|") and "---" not in stripped and "日期" not in stripped:
            count += 1
    return count


def parse_learning_runs(path: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    if not path.exists():
        return rows
    in_section = False
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped == "## 学习实验记录":
            in_section = True
            continue
        if in_section and stripped.startswith("## "):
            break
        if not in_section or not stripped.startswith("|") or "---" in stripped or "日期" in stripped:
            continue
        parts = [part.strip() for part in stripped.strip("|").split("|")]
        if len(parts) >= 6:
            rows.append(
                {
                    "date": parts[0],
                    "lesson": parts[1],
                    "mastery": parts[2],
                    "eval": parts[3],
                    "decision": parts[4],
                    "reason": parts[5],
                }
            )
    return rows


def extract_links(text: str) -> set[str]:
    links = set()
    for match in LINK_RE.finditer(text):
        target = match.group(1).strip()
        if target and not target.endswith("知识地图") and target != "知识地图":
            links.add(target)
    return links


def concept_is_complete(path: Path) -> bool:
    if not path.exists():
        return False
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
    return len("\n".join(meaningful)) >= 120


def scan_topic(vault: Path, topic_dir: Path, today: date) -> dict[str, object]:
    topic = topic_dir.name
    notes_dir = vault / "notes" / topic
    lessons = sorted((notes_dir / "lessons").glob("*.md"))
    concepts_dir = notes_dir / "concepts"
    concepts = sorted(concepts_dir.glob("*.md"))
    plan_path = topic_dir / "复习计划.md"
    missed_path = topic_dir / "错题与遗漏.md"
    progress_path = topic_dir / "进度.md"

    overdue: list[dict[str, str]] = []
    due_today: list[dict[str, str]] = []
    due_soon: list[dict[str, str]] = []
    pending_reviews = 0
    for row in parse_review_rows(plan_path):
        if row["status"] not in {"pending", "待复习", ""}:
            continue
        pending_reviews += 1
        try:
            due = date.fromisoformat(row["date"])
        except ValueError:
            continue
        item = {"topic": topic, **row}
        if due < today:
            overdue.append(item)
        elif due == today:
            due_today.append(item)
        elif due <= today + timedelta(days=3):
            due_soon.append(item)

    missing: set[str] = set()
    incomplete: set[str] = set()
    for lesson in lessons:
        for link in extract_links(lesson.read_text(encoding="utf-8")):
            concept_path = concepts_dir / f"{link}.md"
            if not concept_path.exists():
                missing.add(link)
            elif not concept_is_complete(concept_path):
                incomplete.add(link)
    for concept in concepts:
        if not concept_is_complete(concept):
            incomplete.add(concept.stem)

    learning_runs = parse_learning_runs(progress_path)
    blocked_runs = [row for row in learning_runs if row["decision"] != "continue"]

    return {
        "topic": topic,
        "lesson_count": len(lessons),
        "concept_count": len(concepts),
        "active_misses": parse_active_misses(missed_path),
        "pending_reviews": pending_reviews,
        "latest_eval": learning_runs[0] if learning_runs else None,
        "blocked_runs": blocked_runs,
        "overdue": overdue,
        "due_today": due_today,
        "due_soon": due_soon,
        "missing_concepts": sorted(missing),
        "incomplete_concepts": sorted(incomplete),
    }


def scan_vault(vault: Path, today: date) -> list[dict[str, object]]:
    progress_root = vault / "progress"
    if not progress_root.exists():
        return []
    return [scan_topic(vault, topic_dir, today) for topic_dir in sorted(progress_root.iterdir()) if topic_dir.is_dir()]


def render_review_rows(items: list[dict[str, str]]) -> list[str]:
    if not items:
        return ["无"]
    lines = ["| 主题 | 日期 | 课程 | 复习次 | 重点 | 状态 |", "| --- | --- | --- | --- | --- | --- |"]
    for item in items:
        lines.append(f"| {item['topic']} | {item['date']} | {item['lesson']} | {item['review']} | {item['focus']} | {item['status']} |")
    return lines


def render_dashboard(topics: list[dict[str, object]], today: date) -> str:
    overdue = [item for topic in topics for item in topic["overdue"]]  # type: ignore[index]
    due_today = [item for topic in topics for item in topic["due_today"]]  # type: ignore[index]
    due_soon = [item for topic in topics for item in topic["due_soon"]]  # type: ignore[index]
    missing = [(topic["topic"], concept) for topic in topics for concept in topic["missing_concepts"]]  # type: ignore[index]
    incomplete = [(topic["topic"], concept) for topic in topics for concept in topic["incomplete_concepts"]]  # type: ignore[index]
    blocked = [(topic["topic"], row) for topic in topics for row in topic["blocked_runs"]]  # type: ignore[index]

    lines = [
        "# Learning Dashboard",
        "",
        f"生成日期：{today.isoformat()}",
        "",
        "## 今天该做",
        "",
    ]
    if overdue:
        lines.append(f"- 处理已过期复习：{len(overdue)} 项")
    if due_today:
        lines.append(f"- 完成今天到期复习：{len(due_today)} 项")
    if missing:
        lines.append(f"- 补建缺失概念笔记：{len(missing)} 个")
    if incomplete:
        lines.append(f"- 补全不完整概念笔记：{len(incomplete)} 个")
    if blocked:
        lines.append(f"- 处理未通过学习 Eval：{len(blocked)} 项")
    if not any([overdue, due_today, missing, incomplete, blocked]):
        lines.append("- 今天没有硬性学习维护项")

    lines.extend(["", "## 主题概览", "", "| 主题 | 课程 | 概念 | 活跃遗漏 | 待复习 |", "| --- | --- | --- | --- | --- |"])
    if topics:
        for topic in topics:
            lines.append(
                f"| {topic['topic']} | {topic['lesson_count']} | {topic['concept_count']} | {topic['active_misses']} | {topic['pending_reviews']} |"
            )
    else:
        lines.append("| 无 | 0 | 0 | 0 | 0 |")

    lines.extend(["", "## 学习 Eval", ""])
    if topics:
        lines.extend(["| 主题 | 最近课程 | Eval结果 | 决策 | 原因 |", "| --- | --- | --- | --- | --- |"])
        for topic in topics:
            latest = topic["latest_eval"]
            if latest:
                lines.append(f"| {topic['topic']} | {latest['lesson']} | {latest['eval']} | {latest['decision']} | {latest['reason']} |")  # type: ignore[index]
            else:
                lines.append(f"| {topic['topic']} | — | — | — | — |")
    else:
        lines.append("无")

    lines.extend(["", "## 到期复习", "", "### 已过期", ""])
    lines.extend(render_review_rows(overdue))
    lines.extend(["", "### 今天到期", ""])
    lines.extend(render_review_rows(due_today))
    lines.extend(["", "### 未来 3 天", ""])
    lines.extend(render_review_rows(due_soon))

    lines.extend(["", "## 概念缺口", ""])
    if missing:
        lines.extend(f"- {topic}: [[{concept}]]" for topic, concept in missing)
    else:
        lines.append("- 无缺失概念笔记")

    lines.extend(["", "## 待补全概念", ""])
    if incomplete:
        lines.extend(f"- {topic}: [[{concept}]]" for topic, concept in incomplete)
    else:
        lines.append("- 无明显占位概念笔记")

    lines.append("")
    return "\n".join(lines)


def build_dashboard(vault: Path, today: date, output: Path | None = None) -> Path:
    output_path = output or (vault / "dashboard.md")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_dashboard(scan_vault(vault, today), today), encoding="utf-8")
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a LearningVault dashboard.")
    parser.add_argument("--vault", default="LearningVault")
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--output", help="Defaults to LearningVault/dashboard.md")
    args = parser.parse_args()
    output = Path(args.output) if args.output else None
    path = build_dashboard(Path(args.vault), date.fromisoformat(args.date), output)
    print(f"Updated dashboard: {path}")


if __name__ == "__main__":
    main()
