# Fact Check Route

Use when the user asks to check their own note, diagram, explanation, or summary.

## Scope

Check only:

- definitions
- causal relationships
- diagram arrows or sequence order
- formulas, symbols, and units
- boundary conditions
- missing necessary conditions
- misleading terminology

## If Correct

Respond only:

```text
事实无误
```

## If Incorrect

Use this shape:

```markdown
## 事实错误

1. 错误点：
   - 你的表述：
   - 问题：
   - 正确边界：

## 缺失的必要条件

- ...
```

## Hard Bans

Do not:

- rewrite the note
- polish wording
- summarize the note
- add examples unless needed to identify the factual boundary
- generate a replacement note
