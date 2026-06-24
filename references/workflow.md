# Workflow

Load this index only when the route is unclear.

## Routes

| User intent | Load |
| --- | --- |
| New topic or courseware request | `references/routes/topic-first.md` |
| Lesson response shape | `references/routes/session-output.md` |
| Fact-check user notes | `references/routes/fact-check.md` |

## Composition

- For a new lesson, load `topic-first.md`, then `session-output.md`.
- For a user note check, load only `fact-check.md`.
- Do not load source conversion, long-document processing, dashboards, knowledge maps, or review scheduling. They are outside the default scope of this lightweight skill.
