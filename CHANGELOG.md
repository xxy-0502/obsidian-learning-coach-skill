# Changelog

## v2.0.0 - 2026-07-07

这是一次破坏性重构：`obsidian-learning-coach` 从“大而全 Obsidian 学习系统”改为“轻量课件 + 交互式学习 + 复习闭环”。

### 核心变化

- AI 只生成 `lessons/` 课件原料，不代写用户个人笔记。
- 用户个人理解沉淀到 `notes/`，AI 只能做事实核查。
- 新增交互式学习流程：一次只问一个检查点，用户先回答，AI 再纠偏。
- 学习状态拆成三份文件：
  - `学习路线.md`：学习顺序、当前 lesson、note 任务、下一步。
  - `错题遗漏.md`：踩坑、遗漏条件、正确边界。
  - `复习计划.md`：复习队列、复习记录、下次复看。
- 新增复习脚本：
  - `scripts/scan_reviews.py`
  - `scripts/add_review.py`
- 复杂资料转换强制使用 MinerU precise：
  - `scripts/convert_to_markdown.py`
  - 不支持 `MARKDOWN_CONVERTER` 切换。
  - 不保留 `mineru-agent` fallback。

### 删除内容

- 删除旧版长资料拆章流程。
- 删除 dashboard 和知识地图维护。
- 删除复杂 concept validation / learning eval gate。
- 删除 AI 代写完整概念笔记的默认流程。

### 新工作流

```text
输入主题 / 资料
  -> MinerU 转换复杂资料
  -> 创建 学习路线.md / 错题遗漏.md / 复习计划.md
  -> 生成 sparse lesson
  -> 交互式检查
  -> 用户写 notes
  -> AI fact check
  -> 记录错题遗漏
  -> 安排复习
```

### 部署说明

本地 Codex skills 目录应只保留：

```text
C:\Users\15339\.codex\skills\obsidian-learning-coach
```

不要在 `.codex/skills` 下保留 `obsidian-learning-coach.backup-*` 或 `obsidian-learning-coach-lite`，避免 skill 扫描混乱。
