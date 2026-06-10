# Workflow

## Route A: Topic-First Learning

Use when the user only gives a topic.

1. Initialize the vault with `scripts/init_vault.py`.
2. Read `settings/background.md` and `settings/glossary.md`.
3. Ask the start assessment unless the user already answered it or asked to begin directly.
4. If assessment answers are missing, stop after asking the four questions; do not create the first lesson yet.
5. Initialize the topic with `scripts/init_topic.py --mode topic-first`.
6. Record assessment answers that are specific to this topic in `progress/[主题]/进度.md`.
7. If the answers include stable learner preferences, ask whether to update `settings/background.md` unless the user explicitly asked to update it.
8. Check the prior-knowledge answer. If it says "完全不懂", "零基础", "没学过", "不知道", "不理解", "只听过名字", "基础很差", or equivalent, mark the topic as foundation-first in `progress/[主题]/进度.md`.
9. Create a foundation map before the first substantive lesson. Include prerequisites, beginner definitions, notation/tooling requirements, and a checkpoint for each item.
10. If the topic is foundation-first or any prerequisite is not confirmed as mastered, write one or more foundation-level concept notes under `notes/[主题]/concepts/` before writing advanced concept notes. Use `level: foundation`.
11. Create a first lesson, a small checkpoint, and an initial knowledge map. The first lesson must include `基础概念补齐`.
12. In source sections, write: `通用知识讲解；用户未提供外部资料`.

Do not invent sources. For time-sensitive or high-risk content, recommend verification before use.

## Route B: Source-First Learning

Use when the user provides PDF, image, Office file, webpage, GitHub repo, pasted text, or existing notes.

1. Initialize the vault.
2. Put raw local material under `LearningVault/inbox/待处理资料/` when the user has not specified another location.
3. For books, textbooks, manuals, long reports, long PDFs, or any source likely to exceed one lesson, run `scripts/prepare_source.py --input [path] --vault LearningVault`. This converts, analyzes structure, builds `chapter_index.md` when possible, and cleans temporary PDF split files unless `--keep-parts` is passed.
4. For small complex files, convert with `scripts/convert_to_markdown.py` when needed, then run `scripts/analyze_source_structure.py --input [full.md]` if the result is long or complex.
5. Use the converted source at `LearningVault/inbox/converted/[source-name]/full.md` as provenance. Related media stay in the same converted source directory, such as `images/`.
6. If the user provides readable `.md`, `.txt`, pasted text, webpage text, or an existing note, read that directly instead of reconverting; still run structure analysis if it is book-like or long.
7. If `source_structure.json` says `should_split=true`, run `scripts/build_chapter_index.py --input [full.md]` unless `prepare_source.py` already did it. This creates `chapter_index.md`, `chapter_index.json`, and `chapters/`.
8. If a source is long or book-like and no `chapter_index.md` exists, stop before teaching. Explain the reason from `source_structure.md` and ask whether to force a split level, use a smaller section, or continue unsplit.
9. Ask the start assessment unless the user already answered it or asked to begin directly.
10. If assessment answers are missing, stop after asking the four questions; do not create the first lesson yet.
11. Initialize the topic with `scripts/init_topic.py --mode source-first`.
12. Record assessment answers that are specific to this topic in `progress/[主题]/进度.md`.
13. If the answers include stable learner preferences, ask whether to update `settings/background.md` unless the user explicitly asked to update it.
14. Build `notes/[主题]/sources/来源索引.md`, recording the raw source path, converted Markdown path, `source_structure.md`, and chapter-index path when they exist. Do not record temporary `parts/` files unless the user chose `--keep-parts` for debugging.
15. If `chapter_index.md` exists, read it before reading chapter content. Select only the relevant `chapters/Cxxx_*.md` files for the current lesson, and use `full.md` only as fallback or provenance.
16. Check the prior-knowledge answer. If it says "完全不懂", "零基础", "没学过", "不知道", "不理解", "只听过名字", "基础很差", or equivalent, mark the topic as foundation-first in `progress/[主题]/进度.md`.
17. Create a foundation map from the selected chapter/source section before the first substantive lesson. Identify terms, notation, tools, math, or background ideas that a beginner would need.
18. If the topic is foundation-first or a prerequisite is needed and not confirmed as mastered, write it under `notes/[主题]/concepts/` as a foundation-level concept note before writing advanced concept notes. Use `level: foundation`. Mark source-grounded foundation items with the source ID; mark outside-source background as `资料外补充`.
19. Create the first lesson and concept notes grounded in the supplied material. The first lesson must include `基础概念补齐`.
20. Mark material outside the supplied source as `资料外补充`.

## Conversion Route

Use when the user asks only to convert a file to Markdown.

1. Run conversion.
2. Return the converted Markdown path, usually `LearningVault/inbox/converted/[source-name]/full.md`.
3. Mention related media directory when present.
4. Do not start lessons unless the user also asks to learn from it.

## Review Route

Use when the user asks for due reviews, review of a topic, missed points, or time since last study.

1. Use `scripts/scan_due_reviews.py` for due-review discovery.
2. Use active recall first.
3. Update review state with `scripts/update_review_plan.py`.
4. Record missed points in `progress/[主题]/错题与遗漏.md`.

## Session Output Shape

For learning sessions, keep the response focused:

- 今日目标
- 基础概念补齐
- 本课讲解
- STEM 结构化笔记, when the topic is technical: definitions, assumptions, symbols/units, formulas or algorithms, derivation/mechanism, boundary conditions, common mistakes
- 例子
- 主动回忆检查
- 写入/更新的 Obsidian 文件
- 下一步

For STEM topics, the chat explanation may use plain language, but the durable lesson and concept notes must be structured. Do not save only conversational prose.
