# Conversion

Default configuration path: `LearningVault/settings/.env`.

`.env.example`:

```env
MINERU_API_KEY=
MARKDOWN_CONVERTER=mineru
```

Configuration lookup order:

1. Explicit `--env` file
2. `LearningVault/settings/.env`
3. Current project `./settings/.env`
4. System environment variable `MINERU_API_KEY`

Use:

```powershell
python scripts/convert_to_markdown.py `
  --input "LearningVault/inbox/待处理资料/my-paper.pdf" `
  --output "LearningVault/inbox/待处理资料/my-paper.md" `
  --vault "LearningVault"
```

Behavior:

- `.md` and `.txt`: return the original path or copy it to the requested output.
- PDF, images, and Office files: require `MINERU_API_KEY` for MinerU conversion.
- Missing key: do not fail the learning session; ask the user to configure the key, provide Markdown/text, or continue only with readable text.
- Save converted files under `LearningVault/inbox/待处理资料/` unless the user specified another output.

MinerU is optional for v1. If the API changes or a local converter is preferred, patch `scripts/convert_to_markdown.py` rather than changing learning workflows.
