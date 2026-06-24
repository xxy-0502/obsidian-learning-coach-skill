# Workflow

Load this index only when the route is unclear.

## Routes

| User intent | Load |
| --- | --- |
| New topic or courseware request | `references/routes/topic-first.md` |
| Continue a planned topic | `references/routes/progress-driven.md` |
| Lesson response shape | `references/routes/session-output.md` |
| Interactive checkpoint learning | `references/routes/interactive.md` |
| Review due items | `references/routes/review.md` |
| Fact-check user notes | `references/routes/fact-check.md` |

## Composition

- For a new lesson, load `topic-first.md`, then `session-output.md`.
- For continuing a topic, load `progress-driven.md` before generating any new lesson or checkpoint.
- For interactive learning, load `interactive.md`; if no lesson exists, create or propose one sparse lesson first.
- For review, load `review.md` and prioritize due items and pitfalls from `progress.md`.
- For a user note check, load only `fact-check.md`.
- Do not load source conversion, long-document processing, dashboards, knowledge maps, or automated review scheduling. They are outside the default scope of this lightweight skill.
