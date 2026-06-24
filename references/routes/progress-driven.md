# Progress-Driven Route

Use when continuing an existing topic or when the user says "继续", "下一步", "按进度走", or "我想学 X" and `progress.md` already exists.

## Rule

Read `progress.md` first. The plan decides the next learning action.

## Steps

1. Open `LearningVault/topics/[topic]/progress.md`.
2. Find the first unfinished row in `## 学习路线`.
3. Check `## 坑点记录` for unresolved or repeated mistakes related to that row.
4. Choose the next action:
   - missing lesson: generate sparse courseware for that row
   - lesson done but checkpoint pending: run one interactive checkpoint
   - checkpoint passed but note missing: ask the user to write the note
   - note written but unchecked: run fact check
   - review due: run Review Route first
5. Update status after the action.
6. Do not jump to a later route item unless the user explicitly changes the plan.

## Status Values

Use these values in `## 学习路线`:

- planned
- lesson_done
- interaction_pending
- interaction_passed
- note_pending
- note_checked
- review_due
- done

## Plan Changes

If the plan is wrong or too large, revise `progress.md` by splitting, merging, reordering, or removing route items. Keep the plan short and concrete.
