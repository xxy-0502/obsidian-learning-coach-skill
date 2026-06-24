# Topic-First Courseware Route

Use when the user gives a topic or asks for courseware.

## Steps

1. Identify the topic and the intended outcome.
2. If the user's level is unknown, ask at most two questions. If they say "直接开始", assume beginner.
3. Create a lightweight plan in `progress.md` before the first lesson when writing files.
4. Generate one sparse lesson only: the first item in the plan.
5. If writing files, place the lesson under:

```text
LearningVault/topics/[topic]/lessons/
```

6. Create `LearningVault/topics/[topic]/notes/README.md` if missing.
7. Do not write the user's personal note.
8. End with a reconstruction task and offer one interactive checkpoint.

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
- one next interactive checkpoint

The lesson must not contain complete personal understanding, polished summaries, or long explanatory paragraphs.

## Plan Contract

`progress.md` must include:

- 3-7 planned lessons or checkpoints, depending on topic size
- for each item: status, target, lesson file, interaction, note task, review trigger
- likely pitfalls before learning starts
- exact next action
