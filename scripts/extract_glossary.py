#!/usr/bin/env python
from __future__ import annotations

import argparse
import re
from datetime import date
from pathlib import Path


PAIR_RE = re.compile(r"([A-Za-z][A-Za-z0-9 \-]{2,60})\s*[（(]\s*([\u4e00-\u9fff][\u4e00-\u9fff、，, ]{0,40})\s*[）)]")
EN_TERM_RE = re.compile(r"\b([A-Z][A-Za-z0-9]*(?:\s+[A-Z][A-Za-z0-9]*){0,4})\b")


def existing_terms(path: Path) -> dict[str, str]:
    terms: dict[str, str] = {}
    if not path.exists():
        return terms
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|") or "---" in line or "English" in line:
            continue
        parts = [p.strip() for p in line.strip("|").split("|")]
        if len(parts) >= 2 and parts[0]:
            terms[parts[0].lower()] = parts[1]
    return terms


def extract(text: str, source: str, known: dict[str, str]) -> list[tuple[str, str, str]]:
    candidates: dict[str, tuple[str, str]] = {}
    conflicts: dict[str, set[str]] = {}
    for en, zh in PAIR_RE.findall(text):
        key = " ".join(en.split())
        zh = zh.strip()
        lower = key.lower()
        if lower in known:
            if known[lower] != zh:
                conflicts.setdefault(key, set()).add(zh)
            continue
        candidates[key] = (zh, "中英括号配对")
    for en in EN_TERM_RE.findall(text):
        key = " ".join(en.split())
        if len(key) < 3 or key.lower() in known or key in candidates:
            continue
        candidates[key] = ("待确认", "英文大写术语候选")
    rows = [(en, zh, note) for en, (zh, note) in sorted(candidates.items())]
    for en, zhs in sorted(conflicts.items()):
        rows.append((en, "待确认", f"译法冲突：{', '.join(sorted(zhs))}"))
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract glossary candidates from Markdown or text.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--glossary", default="LearningVault/settings/glossary.md")
    parser.add_argument("--source", default="")
    args = parser.parse_args()
    src = Path(args.input)
    text = src.read_text(encoding="utf-8")
    known = existing_terms(Path(args.glossary))
    rows = extract(text, args.source or src.name, known)
    print("| English | 中文 | 说明 | 来源 | 更新时间 |")
    print("| --- | --- | --- | --- | --- |")
    today = date.today().isoformat()
    for en, zh, note in rows:
        print(f"| {en} | {zh} | {note} | {args.source or src.name} | {today} |")


if __name__ == "__main__":
    main()
