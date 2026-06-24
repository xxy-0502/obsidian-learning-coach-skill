# Interactive Learning Route

Use when the user wants step-by-step learning, active questioning, or checkpoint-based practice.

## Rule

One checkpoint per turn. The user answers first.

## Loop

1. Choose one small target from the current lesson.
2. Ask one question, diagram task, comparison, boundary judgment, or error-spotting task.
3. Stop and wait for the user's answer.
4. After the user answers, check only the attempted content.
5. If correct, say the checkpoint passed and give the next checkpoint.
6. If incorrect, identify the smallest error or missing condition, then ask a follow-up.
7. Update `progress.md` when file writing is in scope: current status, route item, pitfall, review queue, next action.
8. Append an interaction record under `interactions/` only when the user wants durable logs.

## Interaction Types

| Type | Task |
| --- | --- |
| recall | Ask the user to define or restate one item from memory |
| diagram | Ask the user to draw or describe arrows, order, or structure |
| compare | Ask the user to distinguish two similar concepts |
| boundary | Ask whether a statement is true under a condition |
| error-spotting | Ask the user to find the wrong part in a statement |
| transfer | Ask the user to apply the principle to a tiny new case |

## Feedback Shape

If correct:

```markdown
检查通过：[checkpoint name]

下一题：
...
```

If incorrect:

```markdown
## 需要修正

- 错误点：
- 缺失条件：
- 下一步只回答：
```

Do not provide a full replacement explanation unless the user explicitly asks.
