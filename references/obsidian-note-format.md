# Obsidian Note Format

## Vault Layout

```text
LearningVault/
├─ settings/
│  ├─ background.md
│  ├─ glossary.md
│  ├─ .env
│  └─ .env.example
├─ notes/
│  └─ [主题]/
│     ├─ index.md
│     ├─ concepts/
│     ├─ lessons/
│     ├─ maps/
│     │  └─ 知识地图.md
│     └─ sources/
│        └─ 来源索引.md
├─ progress/
│  └─ [主题]/
│     ├─ 进度.md
│     ├─ 错题与遗漏.md
│     └─ 复习计划.md
└─ inbox/
   ├─ 待处理资料/
   └─ converted/
      └─ [资料名]/
         ├─ full.md
         ├─ source_structure.md
         ├─ chapter_index.md
         ├─ chapters/
         └─ images/
```

## Topic Index Template

`notes/[主题]/index.md` is a light course entry page, not a knowledge map or progress page. Keep only a few navigation links. Put concept relationships in `maps/知识地图.md`; put goals, mastery, review dates, mistakes, and next steps in `progress/[主题]/`.

```markdown
# [主题]

- 模式：[topic-first/source-first]
- 创建日期：YYYY-MM-DD

## 入口

- 知识结构：[[知识地图]]
- 当前课程：

## 说明

概念关系维护在 [[知识地图]]。
学习目标、掌握程度、复习安排和错题遗漏维护在 `progress/[主题]/`。
```

## Source Index Template

```markdown
# 来源索引

| ID | 类型 | 标题/文件 | 原始位置 | 可读来源 | 章节索引 | 说明 |
| --- | --- | --- | --- | --- | --- | --- |
| S1 | PDF/网页/GitHub/文档/图片/文本 | ... | `LearningVault/inbox/待处理资料/...` | `LearningVault/inbox/converted/.../full.md` | `LearningVault/inbox/converted/.../chapter_index.md` 或 未拆分 | ... |
```

## Progress And Plan Template

Use this for exam plans, learning paths, roadmaps, schedules, and "best path before [date]" outputs. These files belong in `progress/[topic]/`, not in `notes/[topic]/lessons/`.

```markdown
# [topic] 学习进度

## 目标与截止日期

- 目标：
- 截止日期：
- 当前基础：
- 可用资料：

## 最佳学习路径

| 阶段 | 日期范围 | 目标 | 对应资料/章节 | 产出 | 检查点 |
| --- | --- | --- | --- | --- | --- |
| 1 | YYYY-MM-DD - YYYY-MM-DD | ... | ... | ... | ... |

## 今日下一步

1. ...

## 状态记录

| 日期 | 完成内容 | 掌握度 | 下一步 |
| --- | --- | --- | --- |
```

## Concept Note Template

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

```markdown
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
```

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

## Lesson Note Template

Lessons are for concrete teaching sessions only: a chapter, concept cluster, worked example, lab, problem set, or checkpoint. Do not use the lesson template for exam plans, learning paths, roadmaps, or schedules.

```markdown
---
type: lesson
topic: [主题]
lesson: [课程名]
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags:
  - learning/[主题]
  - lesson
---

# [课程名]

## 今日目标

## 基础概念补齐

## 前置知识

## 核心讲解

## STEM 结构化笔记

Use this section when the lesson is technical. Keep explanations concise and organized for later review.

### 定义与目标

### 前提假设与适用范围

### 符号、变量与单位

| 符号 | 含义 | 单位/类型 | 来源 |
| --- | --- | --- | --- |

### 核心公式、定理或算法

```text
公式、定理陈述或伪代码
```

### 推导、证明或机制

1.

### 解题/实现步骤

1.

### 边界条件、近似与失效场景

### 常见错误与检查方法

## 例子

## 主动回忆

## 本课概念

## 来源
```

## Map Template

Use `[[概念名]]` links and short relationship notes. Keep maps maintainable rather than exhaustive. Prefer learning paths, prerequisites, comparisons, and review-worthy relationships over complete concept inventories.
