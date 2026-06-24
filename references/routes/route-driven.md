# Route-Driven Learning

Use when continuing an existing topic or when the user says "继续", "下一步", "按进度走", or "我想学 X" and the topic already has state files.

## Rule

Read the three state files first:

- `学习路线.md`
- `错题遗漏.md`
- `复习计划.md`

The route decides the next learning action.

## Steps

1. Open the topic state files.
2. Find the first unfinished row in `学习路线.md`.
3. Check `错题遗漏.md` for unresolved or repeated mistakes related to that row.
4. Check `复习计划.md` for due review rows. If a review is due, run Review Route first.
5. Choose the next action:
   - missing lesson: generate sparse courseware for that row
   - lesson done but checkpoint pending: run one interactive checkpoint
   - checkpoint passed but note missing: ask the user to write the note
   - note written but unchecked: run fact check
   - review due: run Review Route first
6. Update the corresponding state file after the action.
7. Do not jump to a later route item unless the user explicitly changes the plan.

## Status Values

Use these values in `学习路线.md`:

- planned
- lesson_done
- interaction_pending
- interaction_passed
- note_pending
- note_checked
- review_due
- done

## Plan Changes

If the plan is wrong or too large, revise `学习路线.md` by splitting, merging, reordering, or removing route items. Keep the plan short and concrete.
