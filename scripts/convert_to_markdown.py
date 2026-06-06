#!/usr/bin/env python
from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path


TEXT_EXTS = {".md", ".markdown", ".txt"}
COMPLEX_EXTS = {".pdf", ".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff", ".doc", ".docx", ".ppt", ".pptx"}


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
    for key in ["MINERU_API_KEY", "MARKDOWN_CONVERTER", "MINERU_API_URL"]:
        if os.environ.get(key):
            config[key] = os.environ[key]
    config.setdefault("MARKDOWN_CONVERTER", "mineru")
    return config


def copy_text_input(src: Path, output: Path | None, vault: Path) -> Path:
    if output is None:
        return src
    output.parent.mkdir(parents=True, exist_ok=True)
    if src.resolve() != output.resolve():
        shutil.copyfile(src, output)
    return output


def mineru_convert(src: Path, output: Path, config: dict[str, str]) -> tuple[bool, str]:
    api_key = config.get("MINERU_API_KEY")
    if not api_key:
        return False, (
            "Missing MINERU_API_KEY. Configure LearningVault/settings/.env, pass --env, "
            "set the system environment variable, provide Markdown/text, or continue only with readable text."
        )
    api_url = config.get("MINERU_API_URL")
    if not api_url:
        return False, (
            "MINERU_API_KEY is set, but this script needs MINERU_API_URL for the current MinerU endpoint. "
            "Add MINERU_API_URL to the env file or patch mineru_convert() to match your MinerU deployment."
        )
    try:
        import requests  # type: ignore
    except Exception:
        return False, "The requests package is required for MinerU API conversion."

    with src.open("rb") as fh:
        response = requests.post(
            api_url,
            headers={"Authorization": f"Bearer {api_key}"},
            files={"file": (src.name, fh)},
            timeout=120,
        )
    if response.status_code >= 400:
        return False, f"MinerU request failed with HTTP {response.status_code}: {response.text[:500]}"
    output.parent.mkdir(parents=True, exist_ok=True)
    text = response.text
    try:
        data = response.json()
        text = data.get("markdown") or data.get("content") or response.text
    except Exception:
        pass
    output.write_text(text, encoding="utf-8")
    return True, str(output)


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert supported learning material to Markdown.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output")
    parser.add_argument("--vault", default="LearningVault")
    parser.add_argument("--env")
    args = parser.parse_args()

    src = Path(args.input)
    vault = Path(args.vault)
    if not src.exists():
        print(f"Input not found: {src}", file=sys.stderr)
        sys.exit(2)

    output = Path(args.output) if args.output else vault / "inbox" / "待处理资料" / f"{src.stem}.md"
    ext = src.suffix.lower()
    if ext in TEXT_EXTS:
        result = copy_text_input(src, output if args.output else None, vault)
        print(result)
        return
    if ext not in COMPLEX_EXTS:
        print(f"Unsupported file extension: {ext}. Provide Markdown/text or add converter support.", file=sys.stderr)
        sys.exit(3)

    config = load_config(vault, args.env)
    if config.get("MARKDOWN_CONVERTER", "mineru").lower() != "mineru":
        print(f"Unsupported MARKDOWN_CONVERTER: {config.get('MARKDOWN_CONVERTER')}", file=sys.stderr)
        sys.exit(4)
    ok, message = mineru_convert(src, output, config)
    print(message)
    if not ok:
        sys.exit(5)


if __name__ == "__main__":
    main()
