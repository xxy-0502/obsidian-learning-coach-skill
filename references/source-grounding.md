# Source Grounding

## Topic-First Source Label

When no external material is provided, write:

```text
通用知识讲解；用户未提供外部资料
```

Do not invent exact page numbers, papers, URLs, or quotations.

## Source-First Reading Priority

For local files, separate raw files from converted sources:

- Raw files: `LearningVault/inbox/待处理资料/[original-file]`
- Converted Markdown: `LearningVault/inbox/converted/[source-name]/full.md`
- Converted media: `LearningVault/inbox/converted/[source-name]/images/`

When `full.md` exists, read it as the primary learning source. Use the raw file path only as provenance unless the converted Markdown is missing or incomplete. If the user directly provides Markdown, text, pasted content, webpage text, or an existing note, read that provided source directly.

## Source-First Index

`notes/[主题]/sources/来源索引.md` should include:

```markdown
# 来源索引

| ID | 类型 | 标题/文件 | 原始位置 | 可读来源 | 说明 |
| --- | --- | --- | --- | --- | --- |
| S1 | PDF/网页/GitHub/文档/图片/文本 | ... | `LearningVault/inbox/待处理资料/...` | `LearningVault/inbox/converted/.../full.md` | ... |
```

Use source IDs in lessons and concept notes. If exact page or paragraph anchors are unavailable, say so plainly. If a lesson uses content outside the provided source, label that part as supplement.

## Supplement Label

When adding content not present in the supplied material, mark it:

```text
资料外补充
```

High-risk domains such as medicine, law, finance, and safety require a brief professional-advice disclaimer and current verification when decisions depend on the information.
