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

MinerU is optional for v1. If the API changes or a local converter is preferred, patch `scripts/convert_to_markdown.py` rather than changing learning workflows.
