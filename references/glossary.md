# Glossary

Global glossary path: `LearningVault/settings/glossary.md`.

Template:

```markdown
# 术语表

| English | 中文 | 说明 | 来源 | 更新时间 |
| --- | --- | --- | --- | --- |
```

Rules:

- Prefer existing glossary translations in teaching, notes, and reviews.
- Use `scripts/extract_glossary.py` to produce candidate terms from Markdown or text.
- Do not automatically overwrite existing terms.
- If a term has conflicting translations, output a `待确认` candidate.
- The glossary standardizes wording; it does not replace source grounding.
