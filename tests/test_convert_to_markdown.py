from __future__ import annotations

import builtins
import contextlib
import importlib.util
import io
import sys
import tempfile
import unittest
import zipfile
from io import BytesIO
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "convert_to_markdown.py"


def load_module():
    spec = importlib.util.spec_from_file_location("convert_to_markdown_under_test", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class ConvertToMarkdownTests(unittest.TestCase):
    def test_text_input_without_output_returns_original_path(self):
        module = load_module()

        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "note.md"
            src.write_text("# note\n", encoding="utf-8")
            result = module.copy_text_input(src, None, Path(tmp) / "vault")

        self.assertEqual(result, src)

    def test_text_input_with_output_copies_file(self):
        module = load_module()

        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "note.md"
            dest = Path(tmp) / "vault" / "inbox" / "converted" / "note" / "full.md"
            src.write_text("# note\n", encoding="utf-8")
            result = module.copy_text_input(src, dest, Path(tmp) / "vault")

            self.assertEqual(result, dest)
            self.assertEqual(dest.read_text(encoding="utf-8"), "# note\n")

    def test_load_config_reads_mineru_page_range_from_env_file(self):
        module = load_module()

        with tempfile.TemporaryDirectory() as tmp:
            vault = Path(tmp) / "vault"
            settings = vault / "settings"
            settings.mkdir(parents=True)
            (settings / ".env").write_text("MINERU_PAGE_RANGE=1-10\n", encoding="utf-8")

            config = module.load_config(vault, None)

        self.assertEqual(config["MINERU_PAGE_RANGE"], "1-10")

    def test_pdf_page_count_stop_message_names_safe_options(self):
        module = load_module()

        message = module.pdf_page_count_stop_message(Path("book.pdf"), 180)

        self.assertIn("STOP", message)
        self.assertIn("pypdf", message)
        self.assertIn("--no-auto-split", message)
        self.assertIn("180", message)

    def test_mineru_precise_pdf_stops_before_upload_when_pypdf_missing(self):
        module = load_module()

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            src = tmp_path / "large-book.pdf"
            src.write_bytes(b"%PDF-1.4\n% fake pdf for import-failure path only\n")
            output = tmp_path / "converted" / "full.md"
            vault = tmp_path / "vault"

            original_import = builtins.__import__

            def guarded_import(name, *args, **kwargs):
                if name == "pypdf":
                    raise ImportError("pypdf intentionally hidden")
                return original_import(name, *args, **kwargs)

            argv = [
                "convert_to_markdown.py",
                "--input",
                str(src),
                "--output",
                str(output),
                "--vault",
                str(vault),
            ]

            with mock.patch.object(sys, "argv", argv), mock.patch.object(builtins, "__import__", guarded_import):
                with mock.patch.object(module, "mineru_precise_convert", side_effect=AssertionError("upload attempted")):
                    stderr = io.StringIO()
                    with contextlib.redirect_stderr(stderr):
                        with self.assertRaises(SystemExit) as raised:
                            module.main()

            self.assertEqual(raised.exception.code, 6)
            self.assertIn("Cannot inspect PDF page count", stderr.getvalue())
            self.assertFalse(output.exists())

    def test_extract_mineru_zip_writes_markdown_and_safe_resources(self):
        module = load_module()

        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "converted" / "full.md"
            payload = BytesIO()
            with zipfile.ZipFile(payload, "w") as archive:
                archive.writestr("nested/full.md", "# converted\n")
                archive.writestr("images/figure.png", b"png")
                archive.writestr("../escape.png", b"escape")

            module.extract_mineru_zip(payload.getvalue(), output, "source")

            self.assertEqual(output.read_text(encoding="utf-8"), "# converted\n")
            self.assertTrue((output.parent / "images" / "figure.png").exists())
            self.assertFalse((output.parent.parent / "escape.png").exists())

    def test_rewrite_part_links_points_images_to_part_folder(self):
        module = load_module()

        rewritten = module.rewrite_part_links('![](images/a.png)\n<img src="images/b.png">', "part_001")

        self.assertIn("images/part_001/a.png", rewritten)
        self.assertIn('src="images/part_001/b.png"', rewritten)

    def test_convert_large_pdf_by_parts_merges_and_cleans_temp_parts(self):
        module = load_module()

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            src = tmp_path / "book.pdf"
            src.write_bytes(b"pdf")
            output = tmp_path / "converted" / "full.md"
            part1 = output.parent / "parts" / "part_001.pdf"
            part2 = output.parent / "parts" / "part_002.pdf"

            def fake_split_pdf(_src, parts_root, _max_pages):
                parts_root.mkdir(parents=True)
                part1.write_bytes(b"1")
                part2.write_bytes(b"2")
                return [(part1, 1, 180), (part2, 181, 220)]

            def fake_convert(part_pdf, part_output, _config):
                part_output.parent.mkdir(parents=True)
                part_output.write_text(f"markdown for {part_pdf.name}\n![](images/a.png)", encoding="utf-8")
                images = part_output.parent / "images"
                images.mkdir()
                (images / "a.png").write_bytes(b"png")
                return True, str(part_output)

            with mock.patch.object(module, "split_pdf", fake_split_pdf):
                with mock.patch.object(module, "mineru_precise_convert", fake_convert):
                    ok, message = module.convert_large_pdf_by_parts(src, output, {}, 180, cleanup_temp=True)

            self.assertTrue(ok)
            self.assertIn("1-180", message)
            self.assertIn("181-220", message)
            self.assertFalse((output.parent / "parts").exists())
            merged = output.read_text(encoding="utf-8")
            self.assertIn("Part 1: pages 1-180", merged)
            self.assertIn("images/part_001/a.png", merged)
            self.assertTrue((output.parent / "images" / "part_001" / "a.png").exists())

    def test_unsupported_extension_exits_before_conversion(self):
        module = load_module()

        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "source.exe"
            src.write_text("x", encoding="utf-8")
            argv = ["convert_to_markdown.py", "--input", str(src), "--vault", str(Path(tmp) / "vault")]

            with mock.patch.object(sys, "argv", argv):
                with self.assertRaises(SystemExit) as raised:
                    module.main()

        self.assertEqual(raised.exception.code, 3)

    def test_mineru_precise_missing_token_returns_actionable_error(self):
        module = load_module()

        ok, message = module.mineru_precise_convert(Path("input.pdf"), Path("out.md"), {})

        self.assertFalse(ok)
        self.assertIn("Missing MINERU_TOKEN", message)


if __name__ == "__main__":
    unittest.main()
