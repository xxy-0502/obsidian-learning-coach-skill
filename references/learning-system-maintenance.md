# Learning System Maintenance

Use these scripts to keep the vault navigable after lessons, plans, and reviews.

## Knowledge Map Migration

Run when a topic may still use the old `maps/知识地图.md` filename:

```powershell
python scripts/migrate_knowledge_maps.py --vault LearningVault
```

This renames legacy maps to `maps/[主题]知识地图.md` when no target file exists, updates `index.md` links from `[[知识地图]]` to `[[主题知识地图|主题 知识地图]]`, and leaves existing target maps untouched.

## Knowledge Map Update

Run after creating or revising lessons, concept notes, learning plans, or review notes:

```powershell
python scripts/update_knowledge_map.py --vault LearningVault --topic "[主题]"
```

The script scans lesson and concept `[[双链]]` links, preserves manual map content, and rewrites only the marked `AUTO-KNOWLEDGE-MAP` section.

## Dashboard Refresh

Run when the user asks what to study today, what is missing, which reviews are due, or whether the vault is healthy:

```powershell
python scripts/build_dashboard.py --vault LearningVault --date YYYY-MM-DD
```

The dashboard is written to `LearningVault/dashboard.md` and summarizes due reviews, topic counts, active missed points, missing concept notes, and incomplete concept notes.

## Learning Eval Gate

Run after concept validation and before advancing to the next lesson:

```powershell
python scripts/run_learning_eval.py --vault LearningVault --topic "[主题]" --lesson "[lesson path]" --result "[掌握度]"
```

The script writes one row to `progress/[主题]/进度.md` under `学习实验记录` and returns `continue`, `remedial_lesson`, or `prerequisite_rebuild`.
