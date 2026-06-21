# Review Route

Use when the user asks for due reviews, review of a topic, missed points, or time since last study.

1. Use `scripts/scan_due_reviews.py` for due-review discovery.
2. Use active recall first.
3. Update review state with `scripts/update_review_plan.py`.
4. Record missed points in `progress/[主题]/错题与遗漏.md`.
5. Refresh the topic map with `scripts/update_knowledge_map.py` and the vault dashboard with `scripts/build_dashboard.py`.
