# Topic-First Learning Route

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
11. Create detailed concept notes for the lesson's reusable concepts before or alongside the lesson. A normal first lesson should create at least 3 concept notes under `notes/[主题]/concepts/`.
12. Create a first lesson, a small checkpoint, and an initial knowledge map. The first lesson must include `基础概念补齐` and link only to concept notes that exist and contain complete explanations.
13. Before finishing, load `references/routes/concept-completion-gate.md` and run `python scripts/validate_concepts.py --vault LearningVault --topic "[主题]" --lesson "[lesson path]"`. If it fails, complete the missing concept notes and rerun it.
14. Run `python scripts/run_learning_eval.py --vault LearningVault --topic "[主题]" --lesson "[lesson path]" --result "[掌握度]"`. Continue only when the decision is `continue`.
15. Run `python scripts/update_knowledge_map.py --vault LearningVault --topic "[主题]"`.
16. In source sections, write: `通用知识讲解；用户未提供外部资料`.

Do not invent sources. For time-sensitive or high-risk content, recommend verification before use.
