#!/usr/bin/env python
from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path


def safe_topic(topic: str) -> str:
    return "".join("_" if ch in '<>:"/\\|?*' else ch for ch in topic).strip() or "未命名主题"


def write_if_missing(path: Path, content: str) -> bool:
    if path.exists():
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def init_topic(vault: Path, topic: str, mode: str, today: str) -> list[Path]:
    name = safe_topic(topic)
    notes = vault / "notes" / name
    progress = vault / "progress" / name
    created: list[Path] = []
    for path in [
        notes / "concepts",
        notes / "lessons",
        notes / "maps",
        notes / "sources",
        progress,
    ]:
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            created.append(path)

    files = {
        notes / "index.md": f"# {topic}\n\n- 模式：{mode}\n- 创建日期：{today}\n\n## 入口\n\n- 知识结构：[[知识地图]]\n- 当前课程：\n\n## 说明\n\n概念关系维护在 [[知识地图]]。\n学习目标、掌握程度、复习安排和错题遗漏维护在 `progress/{name}/`。\n",
        notes / "maps" / "知识地图.md": f"# {topic} 知识地图\n\n## 核心概念\n\n## 关系\n\n",
        notes / "sources" / "来源索引.md": "# 来源索引\n\n| ID | 类型 | 标题/文件 | 原始位置 | 可读来源 | 章节索引 | 说明 |\n| --- | --- | --- | --- | --- | --- | --- |\n",
        progress / "进度.md": f"# {topic} 学习进度\n\n## 基本信息\n\n- 开始日期：{today}\n- 学习目标：\n- 目标程度：了解概念 / 能独立运用 / 深度精通\n- 先验知识：\n- 最后学习日期：{today}\n- 最后复习日期：—\n\n## 课程进度\n\n| 课程 | 完成日期 | 掌握程度 | 下次复习 | 关键误区 |\n| --- | --- | --- | --- | --- |\n| 01_核心概念 | — | — | — | — |\n\n## 当前状态\n\n- 正在学习：\n- 最近卡点：\n- 下一步建议：\n",
        progress / "错题与遗漏.md": f"# {topic} 错题与遗漏\n\n## 活跃遗漏\n\n| 日期 | 来源课程 | 遗漏点 | 原回答问题 | 正确理解 | 下次复习重点 | 状态 |\n| --- | --- | --- | --- | --- | --- | --- |\n\n## 已解决遗漏\n\n| 解决日期 | 来源课程 | 原遗漏点 | 解决证据 |\n| --- | --- | --- | --- |\n",
        progress / "复习计划.md": f"# {topic} 复习计划\n\n## 复习规则\n\n| 复习次 | 间隔 |\n| --- | --- |\n| 第 1 次 | 掌握后 1 天 |\n| 第 2 次 | 第 1 次后 3 天 |\n| 第 3 次 | 第 2 次后 7 天 |\n| 第 4 次 | 第 3 次后 14 天 |\n| 第 5 次 | 第 4 次后 30 天 |\n\n## 待复习队列\n\n| 下次复习 | 主题 | 课程 | 复习次 | 复习重点 | 状态 |\n| --- | --- | --- | --- | --- | --- |\n\n## 复习记录\n\n| 日期 | 课程 | 结果 | 新增遗漏 | 下次复习 |\n| --- | --- | --- | --- | --- |\n",
    }
    for path, content in files.items():
        if write_if_missing(path, content):
            created.append(path)
    return created


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize topic folders and progress files.")
    parser.add_argument("--vault", default="LearningVault")
    parser.add_argument("--topic", required=True)
    parser.add_argument("--mode", choices=["topic-first", "source-first"], default="topic-first")
    parser.add_argument("--date", default=date.today().isoformat())
    args = parser.parse_args()
    created = init_topic(Path(args.vault), args.topic, args.mode, args.date)
    print(f"Topic: {args.topic}")
    if created:
        print("Created:")
        for path in created:
            print(f"- {path}")
    else:
        print("No changes; topic already had the expected files.")


if __name__ == "__main__":
    main()
