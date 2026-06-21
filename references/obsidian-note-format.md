# Obsidian Note Format

Load this index only when unsure which template applies. If the task already identifies the needed artifact, load the exact matching file under `references/templates/`; do not load every template by default.

## Template Routing

| Task | Load |
| --- | --- |
| Check vault structure or initialize paths | `references/templates/vault-layout.md` |
| Create or update a topic entry page | `references/templates/topic-index.md` |
| Record source-first provenance | `references/templates/source-index.md` |
| Create exam plans, learning paths, roadmaps, schedules, or best-path plans | `references/templates/progress-plan.md` |
| Create or validate reusable concept notes | `references/templates/concept-note.md` |
| Create a concrete lesson, chapter note, worked example, lab, problem set, or checkpoint | `references/templates/lesson-note.md` |
| Create or update prerequisite maps and concept relationships | `references/templates/knowledge-map.md` |

## General Placement Rules

- `notes/[主题]/index.md` is a light course entry page, not a knowledge map or progress page.
- Put concept relationships, learning paths, prerequisites, comparisons, and review structure in `notes/[主题]/maps/[主题]知识地图.md`.
- Put goals, mastery state, review dates, mistakes, next steps, exam plans, learning paths, roadmaps, and schedules in `progress/[topic]/`.
- Lessons are only for concrete teaching sessions. Do not create exam plans, learning paths, roadmaps, or schedules under `notes/[topic]/lessons/`.
- Before finishing a lesson, load `references/templates/concept-note.md` and check the Concept Completion Checklist for every stable concept link.
