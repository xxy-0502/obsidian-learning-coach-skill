#!/usr/bin/env python
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any


HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)
PASS_STATUSES = {"pass", "passed", "通过", "已通过", "done", "完成"}
RESOLVED_STATUSES = {"resolved", "closed", "done", "已解决", "完成", "关闭"}


def load_validator() -> Any:
    path = Path(__file__).with_name("validate_concepts.py")
    spec = importlib.util.spec_from_file_location("validate_concepts_for_eval", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def safe_topic(topic: str) -> str:
    return "".join("_" if ch in '<>:"/\\|?*' else ch for ch in topic).strip() or "未命名主题"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def resolve_lesson(vault: Path, topic: str, lesson: str) -> Path:
    path = Path(lesson)
    if path.exists():
        return path
    candidate = vault / "notes" / safe_topic(topic) / "lessons" / lesson
    if candidate.exists():
        return candidate
    if not lesson.endswith(".md"):
        candidate = vault / "notes" / safe_topic(topic) / "lessons" / f"{lesson}.md"
        if candidate.exists():
            return candidate
    raise FileNotFoundError(f"Lesson not found: {lesson}")


def section_body(text: str, title_names: set[str]) -> str:
    matches = list(HEADING_RE.finditer(text))
    for index, match in enumerate(matches):
        title = match.group(2).strip().strip("#").strip()
        if title not in title_names:
            continue
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        return text[start:end].strip()
    return ""


def meaningful_text_length(text: str) -> int:
    no_links = re.sub(r"\[\[[^\]]+\]\]", "", text)
    no_md = re.sub(r"[#>*_`\-\|\[\]\(\):：\s]", "", no_links)
    return len(no_md)


def has_active_recall(lesson_path: Path) -> bool:
    body = section_body(read_text(lesson_path), {"主动回忆", "Active recall"})
    return meaningful_text_length(body) >= 20 and any(marker in body for marker in ("?", "？", "- ", "1."))


def section_lines(path: Path, section: str) -> list[str]:
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    result: list[str] = []
    in_section = False
    for line in lines:
        stripped = line.strip()
        if stripped == f"## {section}":
            in_section = True
            continue
        if in_section and stripped.startswith("## "):
            break
        if in_section:
            result.append(line)
    return result


def table_rows(path: Path, section: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in section_lines(path, section):
        stripped = line.strip()
        if not stripped.startswith("|") or "---" in stripped or "日期" in stripped:
            continue
        rows.append([part.strip() for part in stripped.strip("|").split("|")])
    return rows


def count_eval_questions(missed_path: Path, lesson_id: str) -> int:
    count = 0
    for row in table_rows(missed_path, "验证题库"):
        if len(row) < 6:
            continue
        _, source, _kind, question, evidence, status = row[:6]
        if status in PASS_STATUSES:
            continue
        if source in {lesson_id, f"{lesson_id}.md"} and question and evidence:
            count += 1
    return count


def active_missed_points(missed_path: Path) -> list[list[str]]:
    active: list[list[str]] = []
    for row in table_rows(missed_path, "活跃遗漏"):
        if len(row) < 7:
            continue
        if row[6] not in RESOLVED_STATUSES:
            active.append(row)
    return active


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
            lines.insert(idx, row)
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return True
        if in_section and line.strip().startswith("| ---"):
            separator_seen = True
            continue
        if in_section and separator_seen and line.strip().startswith("|"):
            continue
        if in_section and separator_seen:
            lines.insert(idx, row)
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return True
    if in_section:
        lines.append(row)
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return True
    return False


def ensure_learning_runs_section(progress_path: Path) -> None:
    if progress_path.exists() and "## 学习实验记录" in progress_path.read_text(encoding="utf-8"):
        return
    progress_path.parent.mkdir(parents=True, exist_ok=True)
    existing = progress_path.read_text(encoding="utf-8") if progress_path.exists() else ""
    section = (
        "\n## 学习实验记录\n\n"
        "| 日期 | 课程 | 掌握判断 | Eval结果 | 决策 | 主要原因 |\n"
        "| --- | --- | --- | --- | --- | --- |\n"
    )
    progress_path.write_text(existing.rstrip() + "\n" + section, encoding="utf-8")


def record_learning_run(progress_path: Path, today: str, lesson_id: str, result: str, eval_result: str, decision: str, reasons: list[str]) -> None:
    ensure_learning_runs_section(progress_path)
    reason = "; ".join(reasons[:3]) if reasons else "passed"
    reason = reason.replace("|", "/")
    row = f"| {today} | {lesson_id} | {result or '未记录'} | {eval_result} | {decision} | {reason} |"
    insert_table_row(progress_path, "学习实验记录", row)


def evaluate_learning(
    vault: Path,
    topic: str,
    lesson: str,
    result: str = "",
    today: str | None = None,
    min_concepts: int = 3,
    min_chars: int = 500,
    min_eval_questions: int = 3,
    allow_active_misses: bool = False,
    record: bool = True,
) -> dict[str, object]:
    today = today or date.today().isoformat()
    topic_name = safe_topic(topic)
    lesson_path = resolve_lesson(vault, topic, lesson)
    lesson_id = lesson_path.stem
    progress_path = vault / "progress" / topic_name / "进度.md"
    missed_path = vault / "progress" / topic_name / "错题与遗漏.md"

    validator = load_validator()
    concept_errors = validator.validate_lesson(vault, topic_name, lesson_path, min_concepts, min_chars)
    eval_questions = count_eval_questions(missed_path, lesson_id)
    missed_points = active_missed_points(missed_path)

    failures: list[str] = []
    warnings: list[str] = []
    if concept_errors:
        failures.append(f"concept_gate_failed:{len(concept_errors)}")
    if not has_active_recall(lesson_path):
        failures.append("missing_active_recall")
    if eval_questions < min_eval_questions:
        failures.append(f"eval_questions:{eval_questions}<{min_eval_questions}")
    if missed_points and not allow_active_misses:
        failures.append(f"active_missed_points:{len(missed_points)}")
    elif missed_points:
        warnings.append(f"active_missed_points:{len(missed_points)}")

    if result == "尚未理解":
        decision = "prerequisite_rebuild"
        failures.append("mastery_result:尚未理解")
    elif result == "部分理解":
        decision = "remedial_lesson"
        failures.append("mastery_result:部分理解")
    elif failures:
        decision = "remedial_lesson"
    else:
        decision = "continue"

    eval_result = "pass" if decision == "continue" else "fail"
    reasons = failures + warnings
    if record:
        record_learning_run(progress_path, today, lesson_id, result, eval_result, decision, reasons)

    return {
        "topic": topic_name,
        "lesson": str(lesson_path),
        "lesson_id": lesson_id,
        "eval_result": eval_result,
        "decision": decision,
        "reasons": reasons,
        "concept_errors": concept_errors,
        "eval_questions": eval_questions,
        "active_missed_points": len(missed_points),
    }


def render_markdown(result: dict[str, object]) -> str:
    lines = [
        "# Learning Eval",
        "",
        f"- 主题：{result['topic']}",
        f"- 课程：{result['lesson_id']}",
        f"- Eval结果：{result['eval_result']}",
        f"- 决策：{result['decision']}",
        f"- 验证题数：{result['eval_questions']}",
        f"- 活跃遗漏：{result['active_missed_points']}",
        "",
        "## 原因",
    ]
    reasons = result["reasons"]
    if reasons:
        lines.extend(f"- {reason}" for reason in reasons)  # type: ignore[union-attr]
    else:
        lines.append("- passed")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the learning eval gate for a lesson.")
    parser.add_argument("--vault", default="LearningVault")
    parser.add_argument("--topic", required=True)
    parser.add_argument("--lesson", required=True)
    parser.add_argument("--result", default="", choices=["", "完全掌握", "基本掌握", "部分理解", "尚未理解"])
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--min-concepts", type=int, default=3)
    parser.add_argument("--min-chars", type=int, default=500)
    parser.add_argument("--min-eval-questions", type=int, default=3)
    parser.add_argument("--allow-active-misses", action="store_true")
    parser.add_argument("--no-record", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        result = evaluate_learning(
            Path(args.vault),
            args.topic,
            args.lesson,
            result=args.result,
            today=args.date,
            min_concepts=args.min_concepts,
            min_chars=args.min_chars,
            min_eval_questions=args.min_eval_questions,
            allow_active_misses=args.allow_active_misses,
            record=not args.no_record,
        )
    except FileNotFoundError as exc:
        raise SystemExit(str(exc)) from exc

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(render_markdown(result))
    if result["decision"] != "continue":
        sys.exit(2)


if __name__ == "__main__":
    main()
