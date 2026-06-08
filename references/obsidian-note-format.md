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

## Concept Note Template

Use `level: foundation` for beginner prerequisites, notation, tools, or background concepts that must be understood before the main lesson. Use `level: core` or `level: advanced` for later concepts. Foundation-level concept notes should be smaller and plainer than advanced concept notes.

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

## 常见误区

## 例子

## 主动回忆

## 关系说明

- [[相关概念A]] 是理解本概念的前置知识。
- 本概念容易和 [[相关概念B]] 混淆，区别在于……

## 来源
```

## Lesson Note Template

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

## 例子

## 主动回忆

## 本课概念

## 来源
```

## Map Template

Use `[[概念名]]` links and short relationship notes. Keep maps maintainable rather than exhaustive. Prefer learning paths, prerequisites, comparisons, and review-worthy relationships over complete concept inventories.
