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
- Optional structure report: `LearningVault/inbox/converted/[source-name]/source_structure.md`
- Optional chapter index: `LearningVault/inbox/converted/[source-name]/chapter_index.md`
- Optional chapter files: `LearningVault/inbox/converted/[source-name]/chapters/Cxxx_*.md`

When `chapter_index.md` exists, read it first and choose the relevant chapter file for the current lesson. Read `full.md` directly only when no chapter index exists, when the source is small, when chapter splitting was not recommended, or when a fallback check is needed. Use the raw file path only as provenance unless the converted Markdown is missing or incomplete. If the user directly provides Markdown, text, pasted content, webpage text, or an existing note, read that provided source directly.

## Source-First Index

`notes/[主题]/sources/来源索引.md` should include:

```markdown
# 来源索引

| ID | 类型 | 标题/文件 | 原始位置 | 可读来源 | 章节索引 | 说明 |
| --- | --- | --- | --- | --- | --- | --- |
| S1 | PDF/网页/GitHub/文档/图片/文本 | ... | `LearningVault/inbox/待处理资料/...` | `LearningVault/inbox/converted/.../full.md` | `LearningVault/inbox/converted/.../chapter_index.md` 或 未拆分 | ... |
```

Use source IDs in lessons and concept notes. If exact page or paragraph anchors are unavailable, say so plainly. If a lesson uses content outside the provided source, label that part as supplement.

## Supplement Label

When adding content not present in the supplied material, mark it:

```text
资料外补充
```

High-risk domains such as medicine, law, finance, and safety require a brief professional-advice disclaimer and current verification when decisions depend on the information.
