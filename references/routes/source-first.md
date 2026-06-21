# Source-First Learning Route

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
19. Create detailed concept notes grounded in the supplied material for the lesson's reusable concepts. A normal source-first lesson should create at least 3 concept notes under `notes/[主题]/concepts/`, unless the selected source section truly has fewer reusable concepts.
20. Create the first lesson grounded in the supplied material. The first lesson must include `基础概念补齐` and link only to concept notes that exist and contain complete explanations.
21. Before finishing, load `references/routes/concept-completion-gate.md` and run `python scripts/validate_concepts.py --vault LearningVault --topic "[主题]" --lesson "[lesson path]"`. If it fails, complete the missing concept notes and rerun it.
22. Run `python scripts/run_learning_eval.py --vault LearningVault --topic "[主题]" --lesson "[lesson path]" --result "[掌握度]"`. Continue only when the decision is `continue`.
23. Run `python scripts/update_knowledge_map.py --vault LearningVault --topic "[主题]"`.
24. Mark material outside the supplied source as `资料外补充`.
