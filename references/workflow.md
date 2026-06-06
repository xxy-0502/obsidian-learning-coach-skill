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
8. Create a first lesson, a small checkpoint, and an initial knowledge map.
9. In source sections, write: `通用知识讲解；用户未提供外部资料`.

Do not invent sources. For time-sensitive or high-risk content, recommend verification before use.

## Route B: Source-First Learning

Use when the user provides PDF, image, Office file, webpage, GitHub repo, pasted text, or existing notes.

1. Initialize the vault.
2. Put raw local material under `LearningVault/inbox/待处理资料/` when the user has not specified another location.
3. Convert complex files with `scripts/convert_to_markdown.py` when needed.
4. Use the converted source at `LearningVault/inbox/converted/[source-name]/full.md` as the primary source. Related media stay in the same converted source directory, such as `images/`.
5. If the user provides readable `.md`, `.txt`, pasted text, webpage text, or an existing note, read that directly instead of reconverting.
6. Ask the start assessment unless the user already answered it or asked to begin directly.
7. If assessment answers are missing, stop after asking the four questions; do not create the first lesson yet.
8. Initialize the topic with `scripts/init_topic.py --mode source-first`.
9. Record assessment answers that are specific to this topic in `progress/[主题]/进度.md`.
10. If the answers include stable learner preferences, ask whether to update `settings/background.md` unless the user explicitly asked to update it.
11. Build `notes/[主题]/sources/来源索引.md`, recording the raw source path and the converted Markdown path when both exist.
12. Create the first lesson and concept notes grounded in the supplied material.
13. Mark material outside the supplied source as `资料外补充`.

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
- 本课讲解
- 例子
- 主动回忆检查
- 写入/更新的 Obsidian 文件
- 下一步
