# Topic-First Courseware Route

Use when the user gives a topic or asks for courseware.

## Steps

1. Identify the topic and the intended outcome.
2. If the user's level is unknown, ask at most two questions. If they say "直接开始", assume beginner.
3. Generate one sparse lesson only.
4. If writing files, place the lesson under:

```text
LearningVault/topics/[topic]/lessons/
```

5. Create `LearningVault/topics/[topic]/notes/README.md` if missing.
6. Do not write the user's personal note.
7. End with a reconstruction task and tell the user to write their own note in `notes/`.

## Beginner Handling

For a zero-base learner, include prerequisite concepts, but keep each definition to one sentence.

Do not compensate for beginner status by writing a long explanation. Add smaller reconstruction tasks instead.

## Output Contract

The lesson must contain:

- prerequisite concepts
- core definitions
- principle skeleton
- boundary conditions
- common misconceptions
- diagram or reconstruction task
- self-check questions

The lesson must not contain complete personal understanding, polished summaries, or long explanatory paragraphs.
