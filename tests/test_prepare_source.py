from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "prepare_source.py"


def load_module():
    spec = importlib.util.spec_from_file_location("prepare_source_under_test", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class PrepareSourceTests(unittest.TestCase):
    def test_parse_last_path_uses_last_matching_suffix(self):
        module = load_module()

        output = "noise\nC:/tmp/old/source_structure.json\nmore\nC:/tmp/new/source_structure.json\n"

        self.assertEqual(module.parse_last_path(output, "source_structure.json"), Path("C:/tmp/new/source_structure.json"))

    def test_run_command_preserves_stdout_and_stderr_on_failure(self):
        module = load_module()
        completed = mock.Mock(returncode=2, stdout="created path before failure", stderr="actual error")

        with mock.patch.object(module.subprocess, "run", return_value=completed):
            with self.assertRaisesRegex(RuntimeError, "(?s)created path before failure.*actual error"):
                module.run_command(["fake"])

    def test_main_passes_conversion_flags_and_skips_small_chapter_index(self):
        module = load_module()

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            src = tmp_path / "source.md"
            src.write_text("# tiny\n", encoding="utf-8")
            converted = tmp_path / "vault" / "inbox" / "converted" / "source" / "full.md"
            converted.parent.mkdir(parents=True)
            analysis_json = converted.parent / "source_structure.json"
            analysis_json.write_text(
                json.dumps({"unit_count": 12, "should_split": False, "recommendation": "single_lesson"}),
                encoding="utf-8",
            )

            calls: list[list[str]] = []

            def fake_run_command(args):
                calls.append(args)
                if args[1].endswith("convert_to_markdown.py"):
                    converted.write_text("# converted\n", encoding="utf-8")
                    return str(converted)
                if args[1].endswith("analyze_source_structure.py"):
                    return f"wrote {analysis_json}"
                raise AssertionError(f"unexpected command: {args}")

            argv = [
                "prepare_source.py",
                "--input",
                str(src),
                "--vault",
                str(tmp_path / "vault"),
                "--env",
                str(tmp_path / ".env"),
                "--split-pages",
                "99",
                "--keep-parts",
                "--no-auto-split",
            ]

            stdout = io.StringIO()
            with mock.patch.object(sys, "argv", argv), mock.patch.object(module, "run_command", fake_run_command):
                with contextlib.redirect_stdout(stdout):
                    module.main()

        convert_call = calls[0]
        self.assertIn("--env", convert_call)
        self.assertIn("--split-pages", convert_call)
        self.assertIn("99", convert_call)
        self.assertIn("--keep-parts", convert_call)
        self.assertIn("--no-auto-split", convert_call)
        self.assertNotIn("build_chapter_index.py", "\n".join(" ".join(call) for call in calls))
        self.assertIn("chapter_index: none", stdout.getvalue())

    def test_main_builds_chapter_index_when_analysis_should_split(self):
        module = load_module()

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            src = tmp_path / "book.md"
            src.write_text("# book\n", encoding="utf-8")
            converted = tmp_path / "vault" / "inbox" / "converted" / "book" / "full.md"
            converted.parent.mkdir(parents=True)
            analysis_json = converted.parent / "source_structure.json"
            chapter_json = converted.parent / "chapter_index.json"
            chapter_md = converted.parent / "chapter_index.md"
            chapters_dir = converted.parent / "chapters"
            chapters_dir.mkdir()
            analysis_json.write_text(
                json.dumps({"unit_count": 30000, "should_split": True, "recommendation": "chapter_split"}),
                encoding="utf-8",
            )
            chapter_json.write_text("{}", encoding="utf-8")
            chapter_md.write_text("# chapters\n", encoding="utf-8")

            def fake_run_command(args):
                if args[1].endswith("convert_to_markdown.py"):
                    converted.write_text("# converted\n", encoding="utf-8")
                    return str(converted)
                if args[1].endswith("analyze_source_structure.py"):
                    return str(analysis_json)
                if args[1].endswith("build_chapter_index.py"):
                    return str(chapter_json)
                raise AssertionError(f"unexpected command: {args}")

            argv = ["prepare_source.py", "--input", str(src), "--vault", str(tmp_path / "vault")]
            stdout = io.StringIO()
            with mock.patch.object(sys, "argv", argv), mock.patch.object(module, "run_command", fake_run_command):
                with contextlib.redirect_stdout(stdout):
                    module.main()

        output = stdout.getvalue()
        self.assertIn("chapter_index:", output)
        self.assertIn("chapters:", output)

    def test_main_exits_cleanly_when_conversion_stops(self):
        module = load_module()

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            src = tmp_path / "book.pdf"
            src.write_bytes(b"pdf")

            def fake_run_command(args):
                if args[1].endswith("convert_to_markdown.py"):
                    raise RuntimeError("STOP: Cannot inspect PDF page count")
                raise AssertionError(f"unexpected command: {args}")

            argv = ["prepare_source.py", "--input", str(src), "--vault", str(tmp_path / "vault")]
            with mock.patch.object(sys, "argv", argv), mock.patch.object(module, "run_command", fake_run_command):
                with self.assertRaises(SystemExit) as raised:
                    module.main()

        self.assertIn("STOP: Cannot inspect PDF page count", str(raised.exception))

    def test_main_prints_stop_when_recommended_chapter_split_fails(self):
        module = load_module()

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            src = tmp_path / "book.md"
            src.write_text("# book\n", encoding="utf-8")
            converted = tmp_path / "vault" / "inbox" / "converted" / "book" / "full.md"
            converted.parent.mkdir(parents=True)
            analysis_json = converted.parent / "source_structure.json"
            analysis_json.write_text(
                json.dumps({"unit_count": 30000, "should_split": True, "recommendation": "chapter_split"}),
                encoding="utf-8",
            )

            def fake_run_command(args):
                if args[1].endswith("convert_to_markdown.py"):
                    converted.write_text("# converted\n", encoding="utf-8")
                    return str(converted)
                if args[1].endswith("analyze_source_structure.py"):
                    return str(analysis_json)
                if args[1].endswith("build_chapter_index.py"):
                    raise RuntimeError("no headings found")
                raise AssertionError(f"unexpected command: {args}")

            argv = ["prepare_source.py", "--input", str(src), "--vault", str(tmp_path / "vault")]
            stdout = io.StringIO()
            with mock.patch.object(sys, "argv", argv), mock.patch.object(module, "run_command", fake_run_command):
                with contextlib.redirect_stdout(stdout):
                    module.main()

        output = stdout.getvalue()
        self.assertIn("STOP: Chapter splitting was recommended but failed", output)
        self.assertIn("source is long", output)


if __name__ == "__main__":
    unittest.main()
