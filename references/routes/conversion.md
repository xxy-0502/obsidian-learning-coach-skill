# MinerU Conversion Route

Use when the user provides a PDF, image, Office file, or explicitly asks to convert source material.

## Rule

Complex-file conversion must use MinerU precise only. Do not use alternative converters.

## Supported Inputs

MinerU conversion applies to:

- `.pdf`
- `.png`, `.jpg`, `.jpeg`, `.webp`, `.tif`, `.tiff`
- `.doc`, `.docx`, `.ppt`, `.pptx`

Readable text inputs such as `.md`, `.markdown`, and `.txt` do not need conversion.

## Command

```powershell
python scripts/convert_to_markdown.py --input "[path]" --vault "LearningVault"
```

Default output:

```text
LearningVault/inbox/converted/[source]/full.md
```

## Configuration

MinerU precise requires a token.

Use one of:

- `LearningVault/settings/.env`
- explicit `--env`
- system environment variables

Required:

```env
MINERU_TOKEN=your_token
```

Common optional values:

```env
MINERU_API_BASE=https://mineru.net
MINERU_LANGUAGE=ch
MINERU_MODEL_VERSION=vlm
MINERU_ENABLE_TABLE=true
MINERU_ENABLE_FORMULA=true
MINERU_IS_OCR=false
```

Do not use `MARKDOWN_CONVERTER`. This skill does not support switching converters.

## After Conversion

Use `full.md` as the raw source for sparse lesson generation.

Do not create source indexes, chapter indexes, dashboards, knowledge maps, or detailed concept notes by default.

## Failure Handling

| Trigger | Action |
| --- | --- |
| `MINERU_TOKEN` missing | Stop and ask the user to configure MinerU or provide Markdown/text |
| MinerU task creation fails | Report the MinerU error and stop |
| MinerU parsing fails | Report the failed file and ask whether to retry |
| PDF page count cannot be inspected while auto-split is enabled | Stop and ask the user to provide text/Markdown or retry with a readable PDF |
| Unsupported file extension | Ask for PDF/image/Office/Markdown/text |
