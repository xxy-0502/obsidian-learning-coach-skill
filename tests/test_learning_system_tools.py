from __future__ import annotations

import importlib.util
import tempfile
import unittest
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module(relative: str, name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def complete_concept(name: str) -> str:
    return (
        "---\n"
        "type: concept\n"
        "topic: 机器学习\n"
        "level: core\n"
        "---\n\n"
        f"# {name}\n\n"
        "## 一句话解释\n"
        f"{name} 是本课需要掌握的核心概念，用来连接问题条件、方法步骤和可验证的学习输出。\n\n"
        "## 它解决什么问题\n"
        "它帮助学习者把问题、条件和方法连接起来，避免只记住术语。\n\n"
        "## 为什么重要\n"
        "掌握它之后可以解释新例子、识别适用边界，并迁移到练习题。\n\n"
        "## 核心理解\n"
        "核心理解包括定义、使用条件、关键步骤、例子、反例和常见误区。\n\n"
        "## 例子\n"
        "给一个具体例子，并说明它为什么满足定义和适用条件。\n\n"
        "## 常见混淆\n"
        "容易和相邻概念混淆，区别在于目标、输入、输出和边界条件不同。\n\n"
        "## 主动回忆\n"
        "不看笔记解释这个概念，并给出一个新的例子。\n\n"
        "## 关系说明\n"
        "它和其他概念通过前置关系、应用关系或混淆关系连接。\n\n"
        "## 来源\n"
        "本课 lesson 和用户提供资料。\n"
    )


class LearningSystemToolTests(unittest.TestCase):
    def test_update_knowledge_map_preserves_manual_content_and_updates_auto_block(self):
        updater = load_module("scripts/update_knowledge_map.py", "update_knowledge_map_under_test")

        with tempfile.TemporaryDirectory() as tmp:
            vault = Path(tmp) / "LearningVault"
            notes = vault / "notes" / "机器学习"
            write(notes / "maps" / "机器学习知识地图.md", "# 机器学习 知识地图\n\n## 手写结构\n\n- 保留这一行\n")
            write(
                notes / "lessons" / "01.md",
                "# 01\n\n[[监督学习]] 是 [[线性回归]] 的前置背景。\n",
            )
            write(
                notes / "concepts" / "线性回归.md",
                "# 线性回归\n\n"
                "线性回归是一种监督学习方法，用连续变量之间的线性关系进行预测。"
                "它解决数值预测问题，包含假设、变量、损失函数、边界条件、例子和主动回忆。",
            )

            path = updater.update_knowledge_map(vault, "机器学习", "2026-06-21")
            text = path.read_text(encoding="utf-8")

            self.assertIn("## 手写结构", text)
            self.assertIn("AUTO-KNOWLEDGE-MAP:START", text)
            self.assertIn("[[线性回归]]", text)
            self.assertIn("[[监督学习]]", text)
            self.assertIn("前置背景", text)
            self.assertIn("### 待补全概念", text)

            updater.update_knowledge_map(vault, "机器学习", "2026-06-22")
            updated = path.read_text(encoding="utf-8")
            self.assertEqual(updated.count("AUTO-KNOWLEDGE-MAP:START"), 1)
            self.assertIn("更新时间：2026-06-22", updated)

    def test_migrate_knowledge_maps_renames_legacy_map_and_rewrites_index_link(self):
        migrator = load_module("scripts/migrate_knowledge_maps.py", "migrate_knowledge_maps_under_test")

        with tempfile.TemporaryDirectory() as tmp:
            vault = Path(tmp) / "LearningVault"
            topic = vault / "notes" / "机器学习"
            write(topic / "index.md", "# 机器学习\n\n- 知识结构：[[知识地图]]\n")
            write(topic / "maps" / "知识地图.md", "# 知识地图\n\n## 核心概念\n")

            result = migrator.migrate(vault)
            target = topic / "maps" / "机器学习知识地图.md"

            self.assertEqual(result[0]["map"], "migrated")
            self.assertTrue(target.exists())
            self.assertFalse((topic / "maps" / "知识地图.md").exists())
            self.assertIn("# 机器学习 知识地图", target.read_text(encoding="utf-8"))
            self.assertIn(
                "[[机器学习知识地图|机器学习 知识地图]]",
                (topic / "index.md").read_text(encoding="utf-8"),
            )

    def test_build_dashboard_summarizes_reviews_and_concept_gaps(self):
        dashboard = load_module("scripts/build_dashboard.py", "build_dashboard_under_test")

        with tempfile.TemporaryDirectory() as tmp:
            vault = Path(tmp) / "LearningVault"
            progress = vault / "progress" / "机器学习"
            notes = vault / "notes" / "机器学习"
            write(
                progress / "复习计划.md",
                "# 机器学习 复习计划\n\n"
                "## 待复习队列\n\n"
                "| 下次复习 | 主题 | 课程 | 复习次 | 复习重点 | 状态 |\n"
                "| --- | --- | --- | --- | --- | --- |\n"
                "| 2026-06-20 | 机器学习 | 01 | 第 1 次 | 核心概念 | 待复习 |\n"
                "| 2026-06-21 | 机器学习 | 02 | 第 1 次 | 例子 | 待复习 |\n",
            )
            write(
                progress / "错题与遗漏.md",
                "# 机器学习 错题与遗漏\n\n"
                "## 活跃遗漏\n\n"
                "| 日期 | 来源课程 | 遗漏点 | 原回答问题 | 正确理解 | 下次复习重点 | 状态 |\n"
                "| --- | --- | --- | --- | --- | --- | --- |\n"
                "| 2026-06-21 | 01 | 漏掉假设 | Q | A | 假设 | open |\n",
            )
            write(notes / "lessons" / "01.md", "# 01\n\n本课概念：[[线性回归]]、[[梯度下降]]\n")
            write(
                notes / "concepts" / "线性回归.md",
                "# 线性回归\n\n"
                "线性回归是一种监督学习方法，用连续变量之间的线性关系进行预测。"
                "它解决数值预测问题，包含假设、变量、损失函数、边界条件、例子和主动回忆。",
            )

            path = dashboard.build_dashboard(vault, date(2026, 6, 21))
            text = path.read_text(encoding="utf-8")

            self.assertIn("# Learning Dashboard", text)
            self.assertIn("处理已过期复习：1 项", text)
            self.assertIn("完成今天到期复习：1 项", text)
            self.assertIn("| 机器学习 | 1 | 1 | 1 | 2 |", text)
            self.assertIn("机器学习: [[梯度下降]]", text)

    def test_run_learning_eval_records_continue_decision(self):
        evaluator = load_module("scripts/run_learning_eval.py", "run_learning_eval_under_test")

        with tempfile.TemporaryDirectory() as tmp:
            vault = Path(tmp) / "LearningVault"
            progress = vault / "progress" / "机器学习"
            notes = vault / "notes" / "机器学习"
            write(
                progress / "进度.md",
                "# 机器学习 学习进度\n\n"
                "## 学习实验记录\n\n"
                "| 日期 | 课程 | 掌握判断 | Eval结果 | 决策 | 主要原因 |\n"
                "| --- | --- | --- | --- | --- | --- |\n",
            )
            write(
                progress / "错题与遗漏.md",
                "# 机器学习 错题与遗漏\n\n"
                "## 活跃遗漏\n\n"
                "| 日期 | 来源课程 | 遗漏点 | 原回答问题 | 正确理解 | 下次复习重点 | 状态 |\n"
                "| --- | --- | --- | --- | --- | --- | --- |\n\n"
                "## 验证题库\n\n"
                "| 日期 | 来源课程 | 题型 | 题目 | 期望证据 | 状态 |\n"
                "| --- | --- | --- | --- | --- | --- |\n"
                "| 2026-06-21 | 01 | 闭卷解释 | 解释监督学习 | 能说出定义和例子 | 待验证 |\n"
                "| 2026-06-21 | 01 | 迁移应用 | 判断新例子 | 能说明理由 | 待验证 |\n"
                "| 2026-06-21 | 01 | 易混淆 | 区分训练和预测 | 能说出边界 | 待验证 |\n",
            )
            write(
                notes / "lessons" / "01.md",
                "# 01\n\n"
                "## 本课概念\n\n"
                "- [[监督学习]]\n"
                "- [[线性回归]]\n"
                "- [[梯度下降]]\n\n"
                "## 主动回忆\n\n"
                "- 什么是监督学习？\n"
                "- 给一个线性回归的新例子？\n",
            )
            for concept in ("监督学习", "线性回归", "梯度下降"):
                write(notes / "concepts" / f"{concept}.md", complete_concept(concept))

            result = evaluator.evaluate_learning(
                vault,
                "机器学习",
                "01.md",
                result="完全掌握",
                today="2026-06-21",
                min_chars=100,
            )

            self.assertEqual(result["decision"], "continue")
            self.assertEqual(result["eval_result"], "pass")
            record = (progress / "进度.md").read_text(encoding="utf-8")
            self.assertIn("| 2026-06-21 | 01 | 完全掌握 | pass | continue | passed |", record)

    def test_dashboard_shows_latest_eval_and_blocked_actions(self):
        dashboard = load_module("scripts/build_dashboard.py", "build_dashboard_eval_under_test")

        with tempfile.TemporaryDirectory() as tmp:
            vault = Path(tmp) / "LearningVault"
            progress = vault / "progress" / "机器学习"
            write(
                progress / "进度.md",
                "# 机器学习 学习进度\n\n"
                "## 学习实验记录\n\n"
                "| 日期 | 课程 | 掌握判断 | Eval结果 | 决策 | 主要原因 |\n"
                "| --- | --- | --- | --- | --- | --- |\n"
                "| 2026-06-21 | 01 | 部分理解 | fail | remedial_lesson | eval_questions:1<3 |\n",
            )
            write(progress / "复习计划.md", "# 机器学习 复习计划\n")
            write(progress / "错题与遗漏.md", "# 机器学习 错题与遗漏\n")

            path = dashboard.build_dashboard(vault, date(2026, 6, 21))
            text = path.read_text(encoding="utf-8")

            self.assertIn("处理未通过学习 Eval：1 项", text)
            self.assertIn("| 机器学习 | 01 | fail | remedial_lesson | eval_questions:1<3 |", text)

    def test_end_to_end_learning_loop_updates_eval_map_and_dashboard(self):
        init_topic = load_module("scripts/init_topic.py", "init_topic_e2e_under_test")
        evaluator = load_module("scripts/run_learning_eval.py", "run_learning_eval_e2e_under_test")
        mapper = load_module("scripts/update_knowledge_map.py", "update_knowledge_map_e2e_under_test")
        dashboard = load_module("scripts/build_dashboard.py", "build_dashboard_e2e_under_test")

        with tempfile.TemporaryDirectory() as tmp:
            vault = Path(tmp) / "LearningVault"
            init_topic.init_topic(vault, "机器学习", "topic-first", "2026-06-21")

            notes = vault / "notes" / "机器学习"
            progress = vault / "progress" / "机器学习"
            lesson_name = "01_核心概念"
            write(
                notes / "lessons" / f"{lesson_name}.md",
                "# 01 核心概念\n\n"
                "## 本课概念\n\n"
                "- [[监督学习]]\n"
                "- [[线性回归]]\n"
                "- [[梯度下降]]\n\n"
                "[[监督学习]] 是 [[线性回归]] 的前置概念。\n\n"
                "## 主动回忆\n\n"
                "- 不看笔记解释监督学习。\n"
                "- 给一个线性回归的新例子。\n",
            )
            for concept in ("监督学习", "线性回归", "梯度下降"):
                write(notes / "concepts" / f"{concept}.md", complete_concept(concept))

            write(
                progress / "错题与遗漏.md",
                "# 机器学习 错题与遗漏\n\n"
                "## 活跃遗漏\n\n"
                "| 日期 | 来源课程 | 遗漏点 | 原回答问题 | 正确理解 | 下次复习重点 | 状态 |\n"
                "| --- | --- | --- | --- | --- | --- | --- |\n\n"
                "## 验证题库\n\n"
                "| 日期 | 来源课程 | 题型 | 题目 | 期望证据 | 状态 |\n"
                "| --- | --- | --- | --- | --- | --- |\n"
                f"| 2026-06-21 | {lesson_name} | 闭卷解释 | 解释监督学习 | 能说出定义和例子 | 待验证 |\n"
                f"| 2026-06-21 | {lesson_name} | 迁移应用 | 判断线性回归例子 | 能说明理由 | 待验证 |\n"
                f"| 2026-06-21 | {lesson_name} | 易混淆 | 区分梯度下降和模型 | 能说出边界 | 待验证 |\n\n"
                "## 已解决遗漏\n\n"
                "| 解决日期 | 来源课程 | 原遗漏点 | 解决证据 |\n"
                "| --- | --- | --- | --- |\n",
            )

            eval_result = evaluator.evaluate_learning(
                vault,
                "机器学习",
                f"{lesson_name}.md",
                result="完全掌握",
                today="2026-06-21",
                min_chars=100,
            )
            map_path = mapper.update_knowledge_map(vault, "机器学习", "2026-06-21")
            dashboard_path = dashboard.build_dashboard(vault, date(2026, 6, 21))

            self.assertEqual(eval_result["decision"], "continue")
            progress_text = (progress / "进度.md").read_text(encoding="utf-8")
            self.assertIn(f"| 2026-06-21 | {lesson_name} | 完全掌握 | pass | continue | passed |", progress_text)

            map_text = map_path.read_text(encoding="utf-8")
            self.assertIn("AUTO-KNOWLEDGE-MAP:START", map_text)
            self.assertIn("[[监督学习]]", map_text)
            self.assertIn("前置概念", map_text)

            dashboard_text = dashboard_path.read_text(encoding="utf-8")
            self.assertIn(f"| 机器学习 | {lesson_name} | pass | continue | passed |", dashboard_text)
            self.assertIn("| 机器学习 | 1 | 3 | 0 | 0 |", dashboard_text)


if __name__ == "__main__":
    unittest.main()
