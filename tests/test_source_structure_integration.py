from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module(relative: str, name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class SourceStructureIntegrationTests(unittest.TestCase):
    def test_bom_markdown_chapter_sequence_is_analyzed_and_split(self):
        analyzer = load_module("scripts/analyze_source_structure.py", "analyze_source_structure_under_test")
        builder = load_module("scripts/build_chapter_index.py", "build_chapter_index_under_test")

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source = tmp_path / "full.md"
            repeated = "network protocol packet routing switching application transport layer\n" * 8000
            source.write_text(
                "\ufeff# Chapter 1\n"
                "overview\n"
                f"{repeated}\n"
                "# Chapter 2\n"
                "physical layer\n"
                f"{repeated}\n"
                "# Chapter 3\n"
                "data link layer\n"
                f"{repeated}\n",
                encoding="utf-8",
            )

            analysis = analyzer.analyze_source(source, small_unit_limit=20, large_unit_limit=100, min_headings=3)
            result = builder.write_chapters(source, tmp_path, split_level=1, include_preface=False)

            self.assertTrue(analysis["should_split"])
            self.assertEqual(analysis["recommendation"], "split_by_chapter_sequence")
            self.assertEqual(analysis["chapter_boundary_count"], 3)
            self.assertEqual(result["chapter_count"], 3)
            self.assertTrue((tmp_path / "chapters" / "C001_Chapter_1.md").exists())

    def test_chinese_chapter_titles_without_space_are_analyzed_and_split(self):
        analyzer = load_module("scripts/analyze_source_structure.py", "analyze_source_structure_chinese_under_test")
        builder = load_module("scripts/build_chapter_index.py", "build_chapter_index_chinese_under_test")

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source = tmp_path / "full.md"
            repeated = "网络 协议 分组 路由 交换 应用 运输 分层\n" * 8000
            source.write_text(
                "\ufeff# 第1章概述\n"
                f"{repeated}\n"
                "# 第2章物理层\n"
                f"{repeated}\n"
                "# 第3章数据链路层\n"
                f"{repeated}\n",
                encoding="utf-8",
            )

            analysis = analyzer.analyze_source(source, small_unit_limit=20, large_unit_limit=100, min_headings=3)
            result = builder.write_chapters(source, tmp_path, split_level=1, include_preface=False)

            self.assertTrue(analysis["should_split"])
            self.assertEqual(analysis["recommendation"], "split_by_chapter_sequence")
            self.assertEqual(analysis["chapter_boundary_count"], 3)
            self.assertEqual(result["chapter_count"], 3)
            self.assertTrue((tmp_path / "chapters" / "C001_第1章概述.md").exists())

    def test_chinese_numeral_chapter_titles_without_space_are_detected(self):
        analyzer = load_module("scripts/analyze_source_structure.py", "analyze_source_structure_cn_numeral_under_test")

        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "full.md"
            repeated = "网络 协议 分组 路由 交换 应用 运输 分层\n" * 8000
            source.write_text(
                "# 第一章概述\n"
                f"{repeated}\n"
                "# 第二章物理层\n"
                f"{repeated}\n"
                "# 第三章数据链路层\n"
                f"{repeated}\n",
                encoding="utf-8",
            )

            analysis = analyzer.analyze_source(source, small_unit_limit=20, large_unit_limit=100, min_headings=3)

            self.assertTrue(analysis["should_split"])
            self.assertEqual(analysis["chapter_boundary_count"], 3)


if __name__ == "__main__":
    unittest.main()
