#!/usr/bin/env python
from __future__ import annotations

import argparse
from pathlib import Path


BACKGROUND = """# 学习者背景

## 正在读的年级

## 正在学习的科目、知识等

## 目前遇到的问题

## 学习偏好

## 目标程度

## 例子偏好

## 不喜欢的讲解方式
"""

GLOSSARY = """# 术语表

| English | 中文 | 说明 | 来源 | 更新时间 |
| --- | --- | --- | --- | --- |
"""

ENV_EXAMPLE = """MINERU_API_KEY=
MARKDOWN_CONVERTER=mineru
"""


def write_if_missing(path: Path, content: str) -> bool:
    if path.exists():
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def init_vault(vault: Path) -> list[Path]:
    created: list[Path] = []
    for rel in [
        "settings",
        "notes",
        "progress",
        "inbox/待处理资料",
    ]:
        path = vault / rel
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            created.append(path)
    for rel, content in [
        ("settings/background.md", BACKGROUND),
        ("settings/glossary.md", GLOSSARY),
        ("settings/.env.example", ENV_EXAMPLE),
    ]:
        path = vault / rel
        if write_if_missing(path, content):
            created.append(path)
    return created


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize a LearningVault without overwriting existing files.")
    parser.add_argument("--vault", default="LearningVault", help="Vault path")
    args = parser.parse_args()
    vault = Path(args.vault)
    created = init_vault(vault)
    print(f"Vault: {vault.resolve()}")
    if created:
        print("Created:")
        for path in created:
            print(f"- {path}")
    else:
        print("No changes; vault already had the expected files.")


if __name__ == "__main__":
    main()
