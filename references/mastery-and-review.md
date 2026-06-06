# Mastery And Review

## Mastery Judgment

| 掌握度 | 行动 |
| --- | --- |
| 完全掌握 | 更新进度，生成/更新概念笔记，安排复习，进入下一课 |
| 基本掌握 | 简短纠正，记录小遗漏，安排复习，进入下一课 |
| 部分理解 | 记录遗漏，生成补充课，不进入下一课 |
| 尚未理解 | 记录卡点，用苏格拉底追问重建理解 |

## Default Review Intervals

| 复习次 | 间隔 |
| --- | --- |
| 第 1 次 | 掌握后 1 天 |
| 第 2 次 | 第 1 次后 3 天 |
| 第 3 次 | 第 2 次后 7 天 |
| 第 4 次 | 第 3 次后 14 天 |
| 第 5 次 | 第 4 次后 30 天 |

Always write absolute dates.

## Active Recall Review

Start reviews with questions such as:

- 不看笔记，用自己的话解释这个概念。
- 这个概念为什么重要？
- 给一个新例子，并说明为什么它符合定义。
- 它最容易和什么概念混淆？

Update `错题与遗漏.md` when the learner cannot explain, misapplies a concept, or skips a key condition.

## Progress File Maintenance

Borrow the Plus-style learning loop: after every lesson or review session, update the learning record before moving on.

Maintain only these three files in `progress/[主题]/`:

- `进度.md`: basic topic metadata, last learning/review dates, course progress, and current status.
- `错题与遗漏.md`: active missed points and resolved missed points.
- `复习计划.md`: review rules, due-review queue, and review records.

Use exact filenames so review routes can find them reliably.

### 进度.md

```markdown
# [主题] 学习进度

## 基本信息

- 开始日期：YYYY-MM-DD
- 学习目标：
- 目标程度：了解概念 / 能独立运用 / 深度精通
- 先验知识：
- 最后学习日期：YYYY-MM-DD
- 最后复习日期：YYYY-MM-DD 或 —

## 课程进度

| 课程 | 完成日期 | 掌握程度 | 下次复习 | 关键误区 |
| --- | --- | --- | --- | --- |
| 01_核心概念 | — | — | — | — |

## 当前状态

- 正在学习：
- 最近卡点：
- 下一步建议：
```

### 错题与遗漏.md

```markdown
# [主题] 错题与遗漏

## 活跃遗漏

| 日期 | 来源课程 | 遗漏点 | 原回答问题 | 正确理解 | 下次复习重点 | 状态 |
| --- | --- | --- | --- | --- | --- | --- |

## 已解决遗漏

| 解决日期 | 来源课程 | 原遗漏点 | 解决证据 |
| --- | --- | --- | --- |
```

### 复习计划.md

```markdown
# [主题] 复习计划

## 复习规则

| 复习次 | 间隔 |
| --- | --- |
| 第 1 次 | 掌握后 1 天 |
| 第 2 次 | 第 1 次后 3 天 |
| 第 3 次 | 第 2 次后 7 天 |
| 第 4 次 | 第 3 次后 14 天 |
| 第 5 次 | 第 4 次后 30 天 |

## 待复习队列

| 下次复习 | 主题 | 课程 | 复习次 | 复习重点 | 状态 |
| --- | --- | --- | --- | --- | --- |

## 复习记录

| 日期 | 课程 | 结果 | 新增遗漏 | 下次复习 |
| --- | --- | --- | --- | --- |
```
