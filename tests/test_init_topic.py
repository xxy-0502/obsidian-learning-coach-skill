from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_init_topic():
    spec = importlib.util.spec_from_file_location(
        "init_topic_under_test",
        ROOT / "scripts" / "init_topic.py",
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class InitTopicTests(unittest.TestCase):
    def test_knowledge_map_filename_includes_topic_name(self):
        init_topic = load_init_topic()

        with tempfile.TemporaryDirectory() as tmp:
            vault = Path(tmp) / "LearningVault"
            init_topic.init_topic(vault, "机器学习", "topic-first", "2026-06-21")

            topic_dir = vault / "notes" / "机器学习"
            map_path = topic_dir / "maps" / "机器学习知识地图.md"
            legacy_map_path = topic_dir / "maps" / "知识地图.md"

            self.assertTrue(map_path.exists())
            self.assertFalse(legacy_map_path.exists())
            self.assertIn("# 机器学习 知识地图", map_path.read_text(encoding="utf-8"))

            index = (topic_dir / "index.md").read_text(encoding="utf-8")
            self.assertIn("[[机器学习知识地图|机器学习 知识地图]]", index)

            progress = (vault / "progress" / "机器学习" / "进度.md").read_text(encoding="utf-8")
            missed = (vault / "progress" / "机器学习" / "错题与遗漏.md").read_text(encoding="utf-8")
            self.assertIn("## 成功标准", progress)
            self.assertIn("## 学习实验记录", progress)
            self.assertIn("## 验证题库", missed)

    def test_knowledge_map_filename_uses_safe_topic_name(self):
        init_topic = load_init_topic()

        with tempfile.TemporaryDirectory() as tmp:
            vault = Path(tmp) / "LearningVault"
            init_topic.init_topic(vault, "C++/AI", "topic-first", "2026-06-21")

            topic_dir = vault / "notes" / "C++_AI"
            map_path = topic_dir / "maps" / "C++_AI知识地图.md"

            self.assertTrue(map_path.exists())
            index = (topic_dir / "index.md").read_text(encoding="utf-8")
            self.assertIn("[[C++_AI知识地图|C++/AI 知识地图]]", index)
