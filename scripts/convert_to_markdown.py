#!/usr/bin/env python
from __future__ import annotations

import argparse
import http.client
import json
import os
import shutil
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from io import BytesIO
from pathlib import Path


TEXT_EXTS = {".md", ".markdown", ".txt"}
COMPLEX_EXTS = {".pdf", ".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff", ".doc", ".docx", ".ppt", ".pptx"}
RESOURCE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg", ".bmp", ".tif", ".tiff"}
DEFAULT_SPLIT_PAGES = 180


def load_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def load_config(vault: Path, explicit_env: str | None) -> dict[str, str]:
    config: dict[str, str] = {}
    candidates = []
    if explicit_env:
        candidates.append(Path(explicit_env))
    candidates.extend([vault / "settings" / ".env", Path.cwd() / "settings" / ".env"])
    for path in candidates:
        config.update({k: v for k, v in load_env_file(path).items() if v})
    for key in [
        "MINERU_API_KEY",
        "MINERU_TOKEN",
        "MARKDOWN_CONVERTER",
        "MINERU_API_BASE",
        "MINERU_API_URL",
        "MINERU_LANGUAGE",
        "MINERU_ENABLE_TABLE",
        "MINERU_ENABLE_FORMULA",
        "MINERU_IS_OCR",
        "MINERU_MODEL_VERSION",
        "MINERU_POLL_COUNT",
        "MINERU_POLL_INTERVAL",
    ]:
        if os.environ.get(key):
            config[key] = os.environ[key]
    config.setdefault("MARKDOWN_CONVERTER", "mineru-precise")
    config.setdefault("MINERU_API_BASE", "https://mineru.net")
    return config


def copy_text_input(src: Path, output: Path | None, vault: Path) -> Path:
    if output is None:
        return src
    output.parent.mkdir(parents=True, exist_ok=True)
    if src.resolve() != output.resolve():
        shutil.copyfile(src, output)
    return output


def default_output_path(src: Path, vault: Path) -> Path:
    return vault / "inbox" / "converted" / src.stem / "full.md"


def pdf_page_count(src: Path) -> int | None:
    try:
        from pypdf import PdfReader  # type: ignore
    except Exception:
        return None
    reader = PdfReader(str(src))
    return len(reader.pages)


def split_pdf(src: Path, parts_dir: Path, max_pages: int) -> list[tuple[Path, int, int]]:
    try:
        from pypdf import PdfReader, PdfWriter  # type: ignore
    except Exception as exc:
        raise RuntimeError("The pypdf package is required to auto-split large PDFs.") from exc

    reader = PdfReader(str(src))
    total = len(reader.pages)
    parts_dir.mkdir(parents=True, exist_ok=True)
    parts: list[tuple[Path, int, int]] = []
    for part_index, start in enumerate(range(0, total, max_pages), start=1):
        end = min(start + max_pages, total)
        writer = PdfWriter()
        for page_index in range(start, end):
            writer.add_page(reader.pages[page_index])
        part_path = parts_dir / f"part_{part_index:03d}.pdf"
        writer.write(str(part_path))
        parts.append((part_path, start + 1, end))
    return parts


def rewrite_part_links(markdown: str, part_name: str) -> str:
    return (
        markdown
        .replace("](images/", f"](images/{part_name}/")
        .replace("](./images/", f"](images/{part_name}/")
        .replace('src="images/', f'src="images/{part_name}/')
        .replace("src='images/", f"src='images/{part_name}/")
    )


def copy_part_resources(part_output: Path, merged_output: Path, part_name: str) -> None:
    src_images = part_output.parent / "images"
    if not src_images.exists():
        return
    dest_images = merged_output.parent / "images" / part_name
    dest_images.mkdir(parents=True, exist_ok=True)
    for item in src_images.rglob("*"):
        if not item.is_file():
            continue
        rel = item.relative_to(src_images)
        dest = dest_images / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(item, dest)


def merge_part_markdown(parts: list[tuple[Path, int, int, Path]], output: Path, source_name: str) -> None:
    chunks = [f"# {source_name}\n\n"]
    for index, (part_pdf, start_page, end_page, part_md) in enumerate(parts, start=1):
        part_name = f"part_{index:03d}"
        text = part_md.read_text(encoding="utf-8")
        copy_part_resources(part_md, output, part_name)
        text = rewrite_part_links(text, part_name)
        chunks.append(
            f"\n\n<!-- Source part: {part_pdf.name}; pages {start_page}-{end_page} -->\n\n"
            f"## Part {index}: pages {start_page}-{end_page}\n\n"
            f"{text.strip()}\n"
        )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(chunks), encoding="utf-8")


def mineru_agent_convert(src: Path, output: Path, config: dict[str, str]) -> tuple[bool, str]:
    api_base = config.get("MINERU_API_BASE", "https://mineru.net").rstrip("/")
    create_url = config.get("MINERU_API_URL") or f"{api_base}/api/v1/agent/parse/file"
    try:
        import requests  # type: ignore
    except Exception:
        return False, "The requests package is required for MinerU Agent API conversion."

    payload = {
        "file_name": src.name,
        "language": config.get("MINERU_LANGUAGE", "ch"),
        "enable_table": config.get("MINERU_ENABLE_TABLE", "true").lower() != "false",
        "is_ocr": config.get("MINERU_IS_OCR", "false").lower() == "true",
        "enable_formula": config.get("MINERU_ENABLE_FORMULA", "true").lower() != "false",
    }
    if config.get("MINERU_PAGE_RANGE"):
        payload["page_range"] = config["MINERU_PAGE_RANGE"]

    response = requests.post(create_url, json=payload, timeout=60)
    if response.status_code >= 400:
        return False, f"MinerU task creation failed with HTTP {response.status_code}: {response.text[:500]}"
    data = response.json()
    if data.get("code") != 0:
        return False, f"MinerU task creation failed: {data.get('msg') or data}"
    task = data.get("data", {})
    task_id = task.get("task_id")
    file_url = task.get("file_url")
    if not task_id or not file_url:
        return False, f"MinerU response did not include task_id/file_url: {data}"

    # Signed OSS upload URL must be used exactly as returned by MinerU.
    with src.open("rb") as fh:
        upload_response = requests.put(file_url, data=fh, timeout=120)
    if upload_response.status_code >= 400:
        return False, f"MinerU file upload failed with HTTP {upload_response.status_code}: {upload_response.text[:500]}"

    result_url = f"{api_base}/api/v1/agent/parse/{task_id}"
    for _ in range(int(config.get("MINERU_POLL_COUNT", "60"))):
        result_response = requests.get(result_url, timeout=30)
        if result_response.status_code >= 400:
            return False, f"MinerU result query failed with HTTP {result_response.status_code}: {result_response.text[:500]}"
        result = result_response.json()
        result_data = result.get("data", {})
        state = result_data.get("state")
        if state == "done":
            markdown_url = result_data.get("markdown_url")
            if not markdown_url:
                return False, f"MinerU result is done but markdown_url is missing: {result}"
            markdown_response = requests.get(markdown_url, timeout=60)
            if markdown_response.status_code >= 400:
                return False, f"MinerU Markdown download failed with HTTP {markdown_response.status_code}: {markdown_response.text[:500]}"
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(markdown_response.text, encoding="utf-8")
            return True, str(output)
        if state == "failed":
            return False, f"MinerU parsing failed: {result_data.get('err_msg') or result}"
        time.sleep(float(config.get("MINERU_POLL_INTERVAL", "2")))
    return False, f"MinerU parsing did not finish before timeout. task_id={task_id}"


def extract_mineru_zip(zip_bytes: bytes, output: Path, preferred_stem: str) -> None:
    with zipfile.ZipFile(BytesIO(zip_bytes)) as archive:
        names = archive.namelist()
        preferred = [
            name for name in names
            if name.endswith("/full.md") or name == "full.md" or name.endswith(f"/{preferred_stem}.md")
        ]
        markdown_names = preferred or [name for name in names if name.lower().endswith(".md")]
        if not markdown_names:
            raise ValueError("MinerU result zip did not contain a Markdown file.")
        with archive.open(markdown_names[0]) as fh:
            markdown = fh.read().decode("utf-8")

        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(markdown, encoding="utf-8")

        for name in names:
            if name.endswith("/") or Path(name).suffix.lower() not in RESOURCE_EXTS:
                continue
            target = (output.parent / name).resolve()
            if not str(target).startswith(str(output.parent.resolve())):
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(name) as src, target.open("wb") as dst:
                shutil.copyfileobj(src, dst)


def bearer_headers(config: dict[str, str]) -> dict[str, str]:
    token = config.get("MINERU_TOKEN") or config.get("MINERU_API_KEY")
    if not token:
        raise ValueError(
            "Missing MINERU_TOKEN. Configure LearningVault/settings/.env, pass --env, "
            "set a system environment variable, provide Markdown/text, or switch to MARKDOWN_CONVERTER=mineru-agent."
        )
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def http_error_message(exc: urllib.error.HTTPError) -> str:
    try:
        body = exc.read().decode("utf-8", errors="replace")
    except Exception:
        body = ""
    return f"HTTP {exc.code}: {body[:500]}"


def post_json(url: str, headers: dict[str, str], payload: dict, timeout: int = 60) -> dict:
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise RuntimeError(http_error_message(exc)) from exc


def get_json(url: str, headers: dict[str, str], timeout: int = 30) -> dict:
    request = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise RuntimeError(http_error_message(exc)) from exc


def get_bytes(url: str, timeout: int = 120) -> bytes:
    request = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.read()
    except urllib.error.HTTPError as exc:
        raise RuntimeError(http_error_message(exc)) from exc


def put_file(url: str, src: Path, timeout: int = 180) -> None:
    data = src.read_bytes()
    parsed = urllib.parse.urlsplit(url)
    path = urllib.parse.urlunsplit(("", "", parsed.path or "/", parsed.query, ""))
    connection_cls = http.client.HTTPSConnection if parsed.scheme == "https" else http.client.HTTPConnection
    conn = connection_cls(parsed.netloc, timeout=timeout)
    try:
        conn.putrequest("PUT", path)
        conn.putheader("Content-Length", str(len(data)))
        conn.endheaders(data)
        response = conn.getresponse()
        body = response.read().decode("utf-8", errors="replace")
        if response.status >= 400:
            raise RuntimeError(f"HTTP {response.status}: {body[:500]}")
    finally:
        conn.close()


def mineru_precise_convert(src: Path, output: Path, config: dict[str, str]) -> tuple[bool, str]:
    api_base = config.get("MINERU_API_BASE", "https://mineru.net").rstrip("/")
    create_url = config.get("MINERU_API_URL") or f"{api_base}/api/v4/file-urls/batch"

    try:
        headers = bearer_headers(config)
    except ValueError as exc:
        return False, str(exc)

    payload = {
        "enable_formula": config.get("MINERU_ENABLE_FORMULA", "true").lower() != "false",
        "enable_table": config.get("MINERU_ENABLE_TABLE", "true").lower() != "false",
        "language": config.get("MINERU_LANGUAGE", "ch"),
        "model_version": config.get("MINERU_MODEL_VERSION", "vlm"),
        "files": [
            {
                "name": src.name,
                "is_ocr": config.get("MINERU_IS_OCR", "false").lower() == "true",
            }
        ],
    }

    try:
        data = post_json(create_url, headers, payload, timeout=60)
    except RuntimeError as exc:
        return False, f"MinerU precise task creation failed with {exc}"
    if data.get("code") not in {0, "0", None}:
        return False, f"MinerU precise task creation failed: {data.get('msg') or data}"
    task_data = data.get("data", {})
    batch_id = task_data.get("batch_id")
    file_urls = task_data.get("file_urls") or task_data.get("file_url") or []
    if isinstance(file_urls, str):
        file_urls = [file_urls]
    if not batch_id or not file_urls:
        return False, f"MinerU response did not include batch_id/file_urls: {data}"

    try:
        put_file(file_urls[0], src, timeout=180)
    except RuntimeError as exc:
        return False, f"MinerU precise file upload failed with {exc}"

    result_url = f"{api_base}/api/v4/extract-results/batch/{batch_id}"
    for _ in range(int(config.get("MINERU_POLL_COUNT", "120"))):
        try:
            result = get_json(result_url, headers, timeout=30)
        except RuntimeError as exc:
            return False, f"MinerU precise result query failed with {exc}"
        result_data = result.get("data", {})
        results = result_data.get("extract_result") or result_data.get("extract_results") or result_data.get("results") or []
        if isinstance(results, dict):
            results = [results]
        item = results[0] if results else result_data
        state = item.get("state") or result_data.get("state")
        if state == "done":
            zip_url = item.get("full_zip_url") or item.get("zip_url") or result_data.get("full_zip_url")
            if not zip_url:
                return False, f"MinerU precise result is done but full_zip_url is missing: {result}"
            try:
                zip_bytes = get_bytes(zip_url, timeout=120)
            except RuntimeError as exc:
                return False, f"MinerU precise zip download failed with {exc}"
            extract_mineru_zip(zip_bytes, output, src.stem)
            return True, str(output)
        if state == "failed":
            return False, f"MinerU precise parsing failed: {item.get('err_msg') or item.get('message') or result}"
        time.sleep(float(config.get("MINERU_POLL_INTERVAL", "3")))
    return False, f"MinerU precise parsing did not finish before timeout. batch_id={batch_id}"


def convert_large_pdf_by_parts(
    src: Path,
    output: Path,
    config: dict[str, str],
    max_pages: int,
    cleanup_temp: bool,
) -> tuple[bool, str]:
    parts_root = output.parent / "parts"
    try:
        split_parts = split_pdf(src, parts_root, max_pages)
    except RuntimeError as exc:
        return False, str(exc)

    converted_parts: list[tuple[Path, int, int, Path]] = []
    for index, (part_pdf, start_page, end_page) in enumerate(split_parts, start=1):
        part_name = f"part_{index:03d}"
        part_output = parts_root / part_name / "full.md"
        ok, message = mineru_precise_convert(part_pdf, part_output, config)
        if not ok:
            return False, f"Part {index} pages {start_page}-{end_page} failed: {message}"
        converted_parts.append((part_pdf, start_page, end_page, part_output))

    merge_part_markdown(converted_parts, output, src.stem)
    ranges = ", ".join(f"{start}-{end}" for _, start, end, _ in converted_parts)
    if cleanup_temp:
        shutil.rmtree(parts_root, ignore_errors=True)
        cleanup_note = "\nCleaned temporary split files under parts/."
    else:
        cleanup_note = "\nKept temporary split files under parts/."
    return True, f"{output}\nSplit source into {len(converted_parts)} parts with page ranges: {ranges}{cleanup_note}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert supported learning material to Markdown.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output")
    parser.add_argument("--vault", default="LearningVault")
    parser.add_argument("--env")
    parser.add_argument("--split-pages", type=int, default=DEFAULT_SPLIT_PAGES, help="Auto-split PDFs above this page count before MinerU conversion.")
    parser.add_argument("--no-auto-split", action="store_true", help="Disable automatic PDF splitting.")
    parser.add_argument("--keep-parts", action="store_true", help="Keep temporary split PDFs and per-part Markdown under parts/.")
    args = parser.parse_args()

    src = Path(args.input)
    vault = Path(args.vault)
    if not src.exists():
        print(f"Input not found: {src}", file=sys.stderr)
        sys.exit(2)

    output = Path(args.output) if args.output else default_output_path(src, vault)
    ext = src.suffix.lower()
    if ext in TEXT_EXTS:
        result = copy_text_input(src, output if args.output else None, vault)
        print(result)
        return
    if ext not in COMPLEX_EXTS:
        print(f"Unsupported file extension: {ext}. Provide Markdown/text or add converter support.", file=sys.stderr)
        sys.exit(3)

    config = load_config(vault, args.env)
    converter = config.get("MARKDOWN_CONVERTER", "mineru-precise").lower()
    if (
        converter in {"mineru-precise", "mineru_precise"}
        and ext == ".pdf"
        and not args.no_auto_split
        and args.split_pages > 0
    ):
        page_count = pdf_page_count(src)
        if page_count is not None and page_count > args.split_pages:
            ok, message = convert_large_pdf_by_parts(src, output, config, args.split_pages, cleanup_temp=not args.keep_parts)
            print(message)
            if not ok:
                sys.exit(5)
            return

    if converter in {"mineru", "mineru-agent", "mineru_agent"}:
        ok, message = mineru_agent_convert(src, output, config)
    elif converter in {"mineru-precise", "mineru_precise"}:
        ok, message = mineru_precise_convert(src, output, config)
    else:
        print(f"Unsupported MARKDOWN_CONVERTER: {config.get('MARKDOWN_CONVERTER')}", file=sys.stderr)
        sys.exit(4)
    print(message)
    if not ok:
        sys.exit(5)


if __name__ == "__main__":
    main()
