# Obsidian Note Format

## Vault Layout

```text
LearningVault/
├── settings/
│   ├── background.md
│   ├── glossary.md
│   ├── .env
│   └── .env.example
├── notes/
│   └── [主题]/
│       ├── index.md
│       ├── concepts/
│       ├── lessons/
│       ├── maps/
│       │   └── 知识地图.md
│       └── sources/
│           └── 来源索引.md
├── progress/
│   └── [主题]/
│       ├── 进度.md
│       ├── 错题与遗漏.md
│       └── 复习计划.md
└── inbox/
    └── 待处理资料/
```

## Concept Note Template

```markdown
---
type: concept
topic: [主题]
status: learning
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags:
  - learning/[主题]
  - concept
---

# 概念名

## 一句话解释

## 为什么重要

## 核心理解

## 常见误区

## 例子

## 相关概念

- [[相关概念A]]
- [[相关概念B]]

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

## 前置知识

## 核心讲解

## 例子

## 主动回忆

## 本课概念

## 来源
```

## Map Template

Use `[[概念名]]` links and short relationship notes. Keep maps maintainable rather than exhaustive.
