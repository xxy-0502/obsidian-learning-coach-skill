# Workflow

Load this index only when unsure which route applies. If the user's intent is clear, load the exact route file under `references/routes/`; do not load every route by default.

## Route Routing

| User intent | Load |
| --- | --- |
| Topic-first learning: user only gives a topic | `references/routes/topic-first.md` |
| Source-first learning: user provides PDF, image, Office file, webpage, GitHub repo, pasted text, or existing notes | `references/routes/source-first.md` |
| Conversion only: user asks only to convert material to Markdown | `references/routes/conversion.md` |
| Planning only: user asks for an exam plan, learning path, roadmap, schedule, best path, or study arrangement | `references/routes/planning.md` |
| Review: user asks about due reviews, reviewing a topic, missed points, or time since last study | `references/routes/review.md` |
| Learning response shape | `references/routes/session-output.md` |
| Lesson completion gate | `references/routes/concept-completion-gate.md` |

## Composition Rules

- For normal topic-first lessons, load `topic-first.md`, then `session-output.md` and `concept-completion-gate.md` before finishing.
- For normal source-first lessons, load `source-first.md`, then `session-output.md` and `concept-completion-gate.md` before finishing.
- For planning, conversion, or review-only requests, load only that route unless the task turns into a lesson.
