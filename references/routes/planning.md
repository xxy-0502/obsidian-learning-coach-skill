# Planning Route

Use when the user asks for an exam plan, learning path, roadmap, schedule, best path, or "how should I study before [date]" and does not ask for a concrete lesson.

1. Initialize the vault and topic if needed.
2. Read `settings/background.md`, `settings/glossary.md`, and the topic progress files.
3. If source material exists, read `chapter_index.md` first. Use the chapter index to sequence the plan; do not read or summarize the whole `full.md` just to make a plan.
4. Write goals, deadline, baseline, constraints, weekly/daily path, and next action to `progress/[topic]/进度.md`.
5. Write review timing, mock checkpoints, and spaced review dates to `progress/[topic]/复习计划.md`.
6. Update `notes/[topic]/maps/[主题]知识地图.md` only for prerequisite order and major chapter relationships. Use the same safe topic name as the topic folder, followed by `知识地图`.
7. Update `notes/[topic]/index.md` only as a light entry page linking to the progress plan, review plan, knowledge map, and current lesson if one exists.
8. Do not create a file under `notes/[topic]/lessons/` for the plan. Create a lesson only when the user asks to learn a concrete chapter, concept cluster, worked example, or checkpoint.
9. Run `scripts/update_knowledge_map.py` after changing the map, then run `scripts/build_dashboard.py` if the plan changes near-term study priorities.
