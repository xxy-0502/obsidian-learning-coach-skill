# Conversion

Default configuration path: `LearningVault/settings/.env`.

`.env.example`:

```env
MARKDOWN_CONVERTER=mineru-precise
MINERU_API_BASE=https://mineru.net
MINERU_TOKEN=
MINERU_LANGUAGE=ch
MINERU_MODEL_VERSION=vlm
```

Configuration lookup order:

1. Explicit `--env` file
2. `LearningVault/settings/.env`
3. Current project `./settings/.env`
4. System environment variables such as `MARKDOWN_CONVERTER`, `MINERU_API_BASE`, `MINERU_TOKEN`, `MINERU_API_KEY`, `MINERU_LANGUAGE`, and `MINERU_MODEL_VERSION`

Use:

```powershell
python scripts/convert_to_markdown.py `
  --input "LearningVault/inbox/待处理资料/my-paper.pdf" `
  --vault "LearningVault"
```

Default output:

```text
LearningVault/inbox/converted/my-paper/full.md
LearningVault/inbox/converted/my-paper/images/
```

Large PDFs:

- MinerU precise API can reject PDFs above its page limit.
- The converter auto-splits oversized PDFs by default with `--split-pages 180`.
- Part PDFs and part Markdown are saved under `LearningVault/inbox/converted/[source-name]/parts/`.
- The merged readable source remains `LearningVault/inbox/converted/[source-name]/full.md`.
- Part image links are rewritten into `images/part_001/`, `images/part_002/`, etc. to avoid filename collisions.
- Use `--no-auto-split` to disable splitting.

Behavior:

- `.md` and `.txt`: return the original path or copy it to the requested output.
- PDF, images, and Office files: use MinerU precise API by default.
- MinerU precise API requires `MINERU_TOKEN` and is asynchronous: create a batch task with `/api/v4/file-urls/batch`, upload the file to the returned signed URL, query `/api/v4/extract-results/batch/{batch_id}`, then download `full_zip_url` and extract `full.md`.
- If token-based parsing is not available, set `MARKDOWN_CONVERTER=mineru-agent` to use the no-token Agent API.
- API failure: do not fail the learning session; ask the user to configure the token, provide Markdown/text, or continue only with currently readable text.
- Save converted files under `LearningVault/inbox/converted/[source-name]/full.md` unless the user specified another output.
- Extract Markdown-linked media such as images into the same converted source directory.
- Do not extract MinerU JSON intermediate files by default.

After conversion, source-first learning should read the converted `full.md` and record both raw and converted paths in `notes/[主题]/sources/来源索引.md`.

## Structure Analysis And Chapter Splitting

Do not split every source. After conversion, use structure analysis for long or complex sources:

```powershell
python scripts/analyze_source_structure.py `
  --input "LearningVault/inbox/converted/my-paper/full.md"
```

This writes:

```text
LearningVault/inbox/converted/my-paper/source_structure.md
LearningVault/inbox/converted/my-paper/source_structure.json
```

Default behavior:

- Sources below `20,000` readable units are not split.
- Sources with too few Markdown headings are not force-split.
- Sources with repeated chapter sequences such as `第1章` / `Chapter 1` are split by the best chapter sequence first.
- Sources with repeated heading levels but no chapter sequence are split by heading level.
- Very large sources still keep `full.md` as the canonical converted source.

When the analysis recommends splitting, run:

```powershell
python scripts/build_chapter_index.py `
  --input "LearningVault/inbox/converted/my-paper/full.md"
```

This writes:

```text
LearningVault/inbox/converted/my-paper/chapter_index.md
LearningVault/inbox/converted/my-paper/chapter_index.json
LearningVault/inbox/converted/my-paper/chapters/
```

For source-first learning, if `chapter_index.md` exists, read that index before reading chapter content. Then read only the relevant `chapters/Cxxx_*.md` files for the current lesson. Use `full.md` as fallback or provenance.

MinerU is optional for v1. If the API changes or a local converter is preferred, patch `scripts/convert_to_markdown.py` rather than changing learning workflows.
