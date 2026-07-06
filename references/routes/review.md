# Review Route

Use when the user asks to review, when a review date is due, or when pitfalls need retesting.

## Rule

Review starts with retrieval, not explanation.

## Steps

1. Read `复习计划.md`.
2. Select due rows from `## 复习队列`.
3. Prioritize rows linked to `错题遗漏.md`.
4. Ask one recall, diagram, boundary, or error-spotting question.
5. Stop and wait for the user's answer.
6. Check the answer.
7. If passed, schedule a later review.
8. If failed, record or update the pitfall in `错题遗漏.md` and schedule a nearer review in `复习计划.md`.

## Feedback

If passed:

```markdown
复习通过：[item]

下次复看：YYYY-MM-DD
```

If failed:

```markdown
## 复习未通过

- 坑点：
- 缺失条件：
- 重新安排：YYYY-MM-DD

下一题只回答：
...
```

Do not provide a full re-lesson unless the user asks.
