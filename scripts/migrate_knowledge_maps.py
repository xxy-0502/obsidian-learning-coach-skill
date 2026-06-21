#!/usr/bin/env python
from __future__ import annotations

import argparse
from pathlib import Path


def map_link(topic_name: str, display_topic: str | None = None) -> str:
    label = display_topic or topic_name
    return f"[[{topic_name}知识地图|{label} 知识地图]]"


def topic_title(index_path: Path, fallback: str) -> str:
    if not index_path.exists():
        return fallback
    for line in index_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip() or fallback
    return fallback


def rewrite_title(text: str, topic_name: str, display_topic: str) -> str:
    lines = text.splitlines()
    if not lines:
        return f"# {display_topic} 知识地图\n"
    if lines[0].strip() in {"# 知识地图", "# [主题] 知识地图"}:
        lines[0] = f"# {display_topic} 知识地图"
    elif lines[0].startswith("# ") and "知识地图" not in lines[0]:
        lines[0] = f"# {display_topic} 知识地图"
    return "\n".join(lines) + "\n"


def rewrite_index_links(index_path: Path, topic_name: str, display_topic: str) -> bool:
    if not index_path.exists():
        return False
    text = index_path.read_text(encoding="utf-8")
    updated = text.replace("[[知识地图]]", map_link(topic_name, display_topic))
    updated = updated.replace("[[知识地图|知识地图]]", map_link(topic_name, display_topic))
    if updated != text:
        index_path.write_text(updated, encoding="utf-8")
        return True
    return False


def migrate_topic(topic_dir: Path) -> dict[str, str]:
    topic_name = topic_dir.name
    index_path = topic_dir / "index.md"
    display_topic = topic_title(index_path, topic_name)
    maps_dir = topic_dir / "maps"
    legacy = maps_dir / "知识地图.md"
    target = maps_dir / f"{topic_name}知识地图.md"
    status = "no_legacy_map"

    if legacy.exists() and not target.exists():
        target.write_text(rewrite_title(legacy.read_text(encoding="utf-8"), topic_name, display_topic), encoding="utf-8")
        legacy.unlink()
        status = "migrated"
    elif legacy.exists() and target.exists():
        status = "target_exists"

    index_status = "index_updated" if rewrite_index_links(index_path, topic_name, display_topic) else "index_unchanged"
    return {"topic": topic_name, "map": status, "index": index_status, "target": str(target)}


def migrate(vault: Path, topic: str | None = None) -> list[dict[str, str]]:
    notes_root = vault / "notes"
    if topic:
        topics = [notes_root / topic]
    else:
        topics = sorted(path for path in notes_root.iterdir() if path.is_dir()) if notes_root.exists() else []
    return [migrate_topic(path) for path in topics if path.exists()]


def main() -> None:
    parser = argparse.ArgumentParser(description="Migrate legacy maps/知识地图.md files to maps/[topic]知识地图.md.")
    parser.add_argument("--vault", default="LearningVault")
    parser.add_argument("--topic", help="Optional safe topic folder name. Omit to migrate every topic.")
    args = parser.parse_args()
    for item in migrate(Path(args.vault), args.topic):
        print(f"{item['topic']}: {item['map']}, {item['index']} -> {item['target']}")


if __name__ == "__main__":
    main()
