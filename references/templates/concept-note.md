# Concept Note Template

Use `level: foundation` for beginner prerequisites, notation, tools, or background concepts that must be understood before the main lesson. Use `level: core` or `level: advanced` for later concepts. Foundation-level concept notes should be smaller and plainer than advanced concept notes.

Concept notes are durable explanations, not placeholders. Every concept note must be useful when opened on its own. Do not create a concept file that contains only a title, aliases, backlinks, or a one-line definition.

Minimum complete concept note sections:

- One-sentence definition
- Problem solved
- Why it matters
- Core explanation
- Example
- Common confusion or boundary condition
- Active recall
- Relationship notes
- Source/provenance

````markdown
---
type: concept
topic: [主题]
level: foundation/core/advanced
status: learning
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags:
  - learning/[主题]
  - concept
---

# 概念名

## 一句话解释

## 它解决什么问题

## 为什么重要

## 核心理解

## STEM 结构化补充

Use this section for engineering, mathematics, physics, chemistry, computer science, statistics, circuits, mechanics, thermodynamics, signals, algorithms, or other technical topics. Omit irrelevant fields, but do not replace the whole note with loose prose.

- 定义：
- 适用条件/前提假设：
- 符号与变量：

| 符号 | 含义 | 单位/类型 | 备注 |
| --- | --- | --- | --- |

- 核心公式/定理/算法：

```text
公式或伪代码
```

- 推导/原理步骤：
  1. ...
  2. ...
- 边界条件/特例：
- 量纲/复杂度/误差来源：

## 常见误区

## 例子

## 主动回忆

## 关系说明

- [[相关概念A]] 是理解本概念的前置知识。
- 本概念容易和 [[相关概念B]] 混淆，区别在于……

## 来源
````

## Concept Completion Checklist

Before finishing a lesson, every stable `[[concept]]` link used by that lesson should have a corresponding file under `notes/[topic]/concepts/`. Check each concept file for real explanatory content:

| Check | Required |
| --- | --- |
| Has frontmatter with `type: concept` | yes |
| Explains the concept in one sentence | yes |
| Explains what problem it solves | yes |
| Explains why it matters for the topic | yes |
| Gives at least one concrete example | yes |
| Includes common confusion, boundary condition, or failure case | yes |
| Includes at least one active-recall question | yes |
| States relationships to other concepts | yes |
| Cites source/provenance | yes |
