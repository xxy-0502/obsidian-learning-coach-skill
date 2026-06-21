# Script Commands

Use these commands from the skill directory or adjust paths to the current workspace.

| Task | Command |
| --- | --- |
| Initialize vault | `python scripts/init_vault.py --vault LearningVault` |
| Initialize topic-first topic | `python scripts/init_topic.py --vault LearningVault --topic "[主题]" --mode topic-first` |
| Initialize source-first topic | `python scripts/init_topic.py --vault LearningVault --topic "[主题]" --mode source-first` |
| Prepare long or complex source | `python scripts/prepare_source.py --input "[path]" --vault LearningVault` |
| Convert material to Markdown | `python scripts/convert_to_markdown.py --input "[path]" --vault LearningVault` |
| Analyze converted source | `python scripts/analyze_source_structure.py --input "LearningVault/inbox/converted/[source-name]/full.md"` |
| Build chapter index | `python scripts/build_chapter_index.py --input "LearningVault/inbox/converted/[source-name]/full.md"` |
| Validate lesson concepts | `python scripts/validate_concepts.py --vault LearningVault --topic "[主题]" --lesson "notes/[主题]/lessons/[lesson].md"` |
| Run learning eval gate | `python scripts/run_learning_eval.py --vault LearningVault --topic "[主题]" --lesson "notes/[主题]/lessons/[lesson].md" --result "[掌握度]"` |
| Migrate legacy knowledge maps | `python scripts/migrate_knowledge_maps.py --vault LearningVault` |
| Update knowledge map | `python scripts/update_knowledge_map.py --vault LearningVault --topic "[主题]"` |
| Build learning dashboard | `python scripts/build_dashboard.py --vault LearningVault --date YYYY-MM-DD` |
| Scan due reviews | `python scripts/scan_due_reviews.py --vault LearningVault --date YYYY-MM-DD` |
| Update review state | `python scripts/update_review_plan.py --vault LearningVault --topic "[主题]" --lesson "[课程]" --result "[掌握度]" --date YYYY-MM-DD` |
