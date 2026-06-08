# Obsidian Learning Coach Skill

Obsidian Learning Coach 是一个面向 Codex 的学习教练 Skill。它可以把“我想学一个主题”“我想读懂一份资料”“今天该复习什么”这类需求，整理成 Obsidian 友好的 Markdown 笔记、学习进度、错题遗漏和间隔复习计划。

它默认用中文教学，必要时提供中英双语术语，适合希望长期维护个人知识库、复盘学习过程、并把 AI 辅助学习沉淀到 Obsidian 的用户。

## 项目简介

这个项目不是一个单纯的问答提示词，而是一套完整的学习工作流：

- 先了解你的学习背景、目标和当前基础。
- 再按主题或资料生成一课一课的学习内容。
- 同步写入 Obsidian Markdown 笔记。
- 用主动回忆检查你是否真的掌握。
- 把没掌握的点记录为错题和遗漏。
- 自动维护后续复习计划。

默认知识库目录是 `LearningVault/`。你可以直接把它作为 Obsidian vault 打开，也可以指定自己的 vault 路径。

## 它能干什么

- 主题学习：输入“我想学 X”“教我 X”，它会从学习起点评估开始，逐步生成课程、概念笔记和知识地图。
- 资料学习：基于 PDF、网页、GitHub 仓库、Office 文档、图片、粘贴文本或已有笔记学习。
- Markdown 转换：把复杂资料转换成适合 Obsidian 管理的 Markdown。
- 自动分页转换：当 PDF 超过 MinerU 单次页数限制时，自动切分为多个分卷分别解析，再合并为一个 `full.md`。
- 来源索引：资料优先学习时，会维护 `sources/来源索引.md`，区分资料内信息和资料外补充。
- 概念笔记：把可复用概念写入 `concepts/`，并使用 Obsidian 双链连接相关概念；当学习者先验知识是零基础或完全不懂时，先写入 `level: foundation` 的基础概念笔记。
- 课程笔记：把每次学习内容写入 `lessons/`，包含目标、讲解、例子和主动回忆问题。
- 知识地图：维护 `maps/知识地图.md`，帮助看清概念关系。
- 掌握度判断：通过小测、复述、例子和追问判断是否可以进入下一课。
- 错题遗漏追踪：把理解错误、遗漏条件、混淆点记录到 `错题与遗漏.md`。
- 间隔复习：维护 `复习计划.md`，支持到期复习、复习记录和下次复习日期。
- 个性化学习：根据 `settings/background.md` 和 `settings/glossary.md` 调整讲解深度、例子风格和术语翻译。

## 核心优点

- 不只回答问题，而是维护长期学习系统。
- 不一次性生成完整课程，默认一课一课推进，避免信息过载。
- 优先主动回忆，而不是让你只被动阅读。
- 能追踪“我学到哪了、哪里没掌握、什么时候该复习”。
- 适合 Obsidian 工作流，支持双链、标签、知识地图和来源索引。
- 支持主题优先和资料优先两种学习方式。
- 尊重来源边界，不伪造论文、URL、页码或精确引用。
- 高风险主题会明确限制为概念学习，不替代专业建议。

## 采用的学习方法

这个 Skill 的设计不是“把资料总结一遍”就结束，而是结合了几种更适合长期学习的策略：

- 掌握学习：每次只推进一个小单元，通过复述、例子和检查题判断是否掌握；如果前置概念没懂，就先补齐再继续。
- 主动回忆：复习时先让学习者尝试自己解释、举例和回答问题，再根据回答纠偏，而不是一开始就重读笔记。
- 间隔重复：把已学内容写入 `复习计划.md`，按 1 天、3 天、7 天、14 天、30 天等间隔安排复习。
- 苏格拉底式提问：遇到卡点时不直接灌答案，而是用追问帮助学习者暴露假设、补全条件、重建理解。
- 费曼式解释：讲解时优先用朴素语言、类比和具体例子，把复杂概念拆到可以复述的程度。
- 错题与遗漏追踪：把理解错误、漏掉的关键条件、容易混淆的概念记录到 `错题与遗漏.md`，后续复习优先处理。
- 来源约束学习：资料学习时优先基于 `converted/[资料名]/full.md`，资料外内容会明确标注为补充，避免把生成解释误当作来源证据。
- 个性化脚手架：读取 `background.md` 和 `glossary.md`，根据学习目标、背景、术语偏好和例子风格调整讲解。

## 目录结构

```text
obsidian-learning-coach/
├─ SKILL.md
├─ README.md
├─ LICENSE
├─ agents/
│  └─ openai.yaml
├─ references/
│  ├─ workflow.md
│  ├─ obsidian-note-format.md
│  ├─ mastery-and-review.md
│  ├─ source-grounding.md
│  ├─ conversion.md
│  ├─ glossary.md
│  └─ personalization.md
└─ scripts/
   ├─ init_vault.py
   ├─ init_topic.py
   ├─ convert_to_markdown.py
   ├─ scan_due_reviews.py
   ├─ update_review_plan.py
   └─ extract_glossary.py
```

## 安装教程

### 方式一：作为 Codex Skill 使用

把本仓库放到你的 Codex skills 目录下，例如：

```text
C:\Users\<你的用户名>\.codex\skills\obsidian-learning-coach
```

确认目录中包含：

```text
SKILL.md
README.md
references/
scripts/
agents/
```

然后在 Codex 中使用：

```text
使用 $obsidian-learning-coach，我想学机器学习
```

或直接说：

```text
我想学机器学习
```

如果 Codex 已识别该 skill，它会自动进入 Obsidian 学习教练流程。

### 方式二：从 GitHub 克隆

```powershell
git clone https://github.com/xxy-0502/obsidian-learning-coach-skill.git
cd obsidian-learning-coach-skill
```

如果你要让 Codex 直接识别它，请把克隆后的目录放入 Codex skills 目录，或根据你的 Codex 配置将该目录加入可用 skills。

## 初始化 Obsidian 学习库

通常不需要手动初始化。你可以直接在 Codex 里说：

```text
使用 $obsidian-learning-coach，我想学机器学习
```

或：

```text
我想学机器学习
```

Skill 会先检查默认的 `LearningVault/` 是否存在；如果不存在，会自动调用初始化流程创建学习库，再继续进入学习起点评估和第一课准备。

如果你想提前创建学习库，或想指定 vault 路径，也可以手动运行脚本。

在项目根目录运行：

```powershell
python scripts/init_vault.py --vault LearningVault
```

脚本会创建：

```text
LearningVault/
├─ settings/
│  ├─ background.md
│  ├─ glossary.md
│  └─ .env.example
├─ notes/
├─ progress/
└─ inbox/
   ├─ 待处理资料/
   └─ converted/
```

你可以用 Obsidian 打开 `LearningVault/`，后续学习生成的课程、概念、复习记录都会写入这里。

## API 配置教程

API 配置主要用于把 PDF、图片、Office 文档等复杂资料转换为 Markdown。普通 `.md` 和 `.txt` 文件不需要 API。

当前转换脚本默认使用 MinerU 精准解析 API，也就是需要 Token 的版本：

```env
MARKDOWN_CONVERTER=mineru-precise
MINERU_API_BASE=https://mineru.net
MINERU_TOKEN=你的_MinerU_Token
MINERU_LANGUAGE=ch
MINERU_MODEL_VERSION=vlm
```

你不需要单独找 `MINERU_API_URL`。脚本会根据 `MINERU_API_BASE=https://mineru.net` 自动调用 MinerU 精准解析的本地文件接口：

- 创建批量文件任务：`POST /api/v4/file-urls/batch`
- 查询解析结果：`GET /api/v4/extract-results/batch/{batch_id}`

精准解析流程是异步的：先用 Token 创建任务，MinerU 返回 `batch_id` 和临时签名上传地址 `file_urls`；脚本把本地文件 `PUT` 到这个地址，然后轮询解析结果，拿到 `full_zip_url` 后下载 zip，并从里面提取 `full.md` 写成最终 Markdown。

Token 获取位置：登录 MinerU 后进入 API 管理页面，在 Token/API Key 管理处创建或复制 Token。不要把 Token 提交到 Git 仓库。

### 1. 创建 `.env`

初始化 vault 后，复制示例文件：

```powershell
Copy-Item LearningVault\settings\.env.example LearningVault\settings\.env
```

然后编辑：

```text
LearningVault/settings/.env
```

填入：

```env
MARKDOWN_CONVERTER=mineru-precise
MINERU_API_BASE=https://mineru.net
MINERU_TOKEN=你的_MinerU_Token
MINERU_LANGUAGE=ch
MINERU_MODEL_VERSION=vlm
```

### 2. 配置说明

- `MARKDOWN_CONVERTER`：转换器名称，目前默认是 `mineru-precise`。
- `MINERU_API_BASE`：MinerU API 基础地址，默认是 `https://mineru.net`。
- `MINERU_TOKEN`：MinerU 精准解析 API Token。脚本也兼容读取 `MINERU_API_KEY`。
- `MINERU_LANGUAGE`：文档语言，中文资料建议用 `ch`。
- `MINERU_MODEL_VERSION`：解析模型版本，默认 `vlm`。
- `MINERU_API_URL`：一般不需要配置。它只作为兼容字段，用来覆盖创建任务接口；默认会使用 `https://mineru.net/api/v4/file-urls/batch`。
- `MINERU_ENABLE_TABLE`：是否解析表格，默认 `true`。
- `MINERU_ENABLE_FORMULA`：是否解析公式，默认 `true`。
- `MINERU_IS_OCR`：是否强制 OCR，默认 `false`。

如果你想改用不需要 Token 的轻量解析接口，可以设置：

```env
MARKDOWN_CONVERTER=mineru-agent
```

### 3. 配置查找顺序

`scripts/convert_to_markdown.py` 会按以下顺序读取配置：

1. 命令行传入的 `--env` 文件。
2. `LearningVault/settings/.env`。
3. 当前目录下的 `settings/.env`。
4. 系统环境变量。

系统环境变量支持：

```text
MARKDOWN_CONVERTER
MINERU_API_BASE
MINERU_TOKEN
MINERU_API_KEY
MINERU_LANGUAGE
MINERU_MODEL_VERSION
MINERU_ENABLE_TABLE
MINERU_ENABLE_FORMULA
MINERU_IS_OCR
```

### 4. 测试资料转换

```powershell
python scripts/convert_to_markdown.py `
  --input "LearningVault/inbox/待处理资料/example.pdf" `
  --vault "LearningVault"
```

如果 MinerU API 调用失败，你也可以直接提供 Markdown 或纯文本资料，跳过复杂文件转换。

默认输出不会和原始 PDF 混在一起，而是放到独立目录：

```text
LearningVault/inbox/converted/example/full.md
LearningVault/inbox/converted/example/images/
```

如果你显式传入 `--output`，则会使用你指定的 Markdown 路径，并把图片资源解到该 Markdown 所在目录下。

如果 PDF 页数超过 MinerU 单次解析限制，脚本会默认按 `180` 页自动切分：

```powershell
python scripts/convert_to_markdown.py `
  --input "LearningVault/inbox/待处理资料/big-book.pdf" `
  --vault "LearningVault" `
  --split-pages 180
```

输出结构：

```text
LearningVault/inbox/converted/big-book/
├─ full.md
├─ parts/
│  ├─ part_001.pdf
│  ├─ part_001/
│  │  └─ full.md
│  ├─ part_002.pdf
│  └─ part_002/
│     └─ full.md
└─ images/
   ├─ part_001/
   └─ part_002/
```

合并后的 `full.md` 会按 part 标注页码范围。若你不想自动切分，可以加 `--no-auto-split`。

## 自动分页转换

MinerU 精准解析 API 对单次 PDF 页数有限制。为了让大书、长报告和教材类 PDF 也能直接进入学习流程，转换脚本内置了自动分页/分卷转换能力。

默认行为：

- 当输入文件是 PDF，且页数超过 `--split-pages` 设置时，脚本会自动切分。
- 默认每卷 `180` 页，低于 MinerU 的 200 页限制，给封面、空白页和接口统计差异留余量。
- 每个分卷会单独调用 MinerU 精准解析。
- 所有分卷解析完成后，会合并为一个统一的 `full.md`。
- 图片会按分卷放入 `images/part_001/`、`images/part_002/` 等目录，避免文件名冲突。
- MinerU 返回的 JSON 中间文件不会被解出，保持 Obsidian vault 清爽。

示例：

```powershell
python scripts/convert_to_markdown.py `
  --input "LearningVault/inbox/待处理资料/big-book.pdf" `
  --vault "LearningVault"
```

自定义每卷页数：

```powershell
python scripts/convert_to_markdown.py `
  --input "LearningVault/inbox/待处理资料/big-book.pdf" `
  --vault "LearningVault" `
  --split-pages 150
```

关闭自动分页：

```powershell
python scripts/convert_to_markdown.py `
  --input "LearningVault/inbox/待处理资料/big-book.pdf" `
  --vault "LearningVault" `
  --no-auto-split
```

合并后的可读来源仍然固定在：

```text
LearningVault/inbox/converted/[资料名]/full.md
```

AI 后续学习时会先判断资料规模和结构。短资料可以直接读取 `full.md`；长资料会优先建立章节索引，再按当前课程读取相关章节文件。

## 结构分析与章节索引

不是所有资料都需要拆分。转换完成后，长资料或结构复杂的资料可以先运行结构分析：

```powershell
python scripts/analyze_source_structure.py `
  --input "LearningVault/inbox/converted/example/full.md"
```

脚本会生成：

```text
LearningVault/inbox/converted/example/source_structure.md
LearningVault/inbox/converted/example/source_structure.json
```

默认策略比较保守：

- 少于 `20,000` 个可读单位的资料不拆。
- 标题太少或层级不清晰时，只生成结构报告，不强行拆分。
- 优先识别 `第1章` / `Chapter 1` 这类真实章序列；找不到章序列时，再按稳定标题层级拆分。
- `full.md` 始终保留为完整可读来源。

如果分析结果建议拆分，再运行：

```powershell
python scripts/build_chapter_index.py `
  --input "LearningVault/inbox/converted/example/full.md"
```

输出结构：

```text
LearningVault/inbox/converted/example/
├─ full.md
├─ source_structure.md
├─ chapter_index.md
├─ chapter_index.json
└─ chapters/
   ├─ C001_绪论.md
   └─ C002_第一章_xxx.md
```

后续学习时，如果存在 `chapter_index.md`，AI 应该先读取章节索引，再只读取当前 lesson 需要的 `chapters/Cxxx_*.md`，必要时才回查 `full.md`。

## 支持的原始文件类型

Skill 支持两类输入：可以直接读取的文本资料，以及需要先转换成 Markdown 的复杂资料。

### 可直接读取

这些文件不需要调用 MinerU：

```text
.md
.markdown
.txt
```

如果用户直接粘贴文本、提供网页正文、已有 Obsidian 笔记或已经整理好的 Markdown，也会直接作为学习资料读取。

### 需要转换为 Markdown

这些文件会通过 `scripts/convert_to_markdown.py` 转换，默认使用 MinerU 精准解析 API：

```text
.pdf
.png
.jpg
.jpeg
.webp
.tif
.tiff
.doc
.docx
.ppt
.pptx
```

转换后的可读来源会保存到：

```text
LearningVault/inbox/converted/[资料名]/full.md
```

图片资源会保存到同一资料目录下的 `images/` 中。对于超过页数限制的大 PDF，脚本会自动分页解析并合并为一个 `full.md`。

### 暂不支持

其他扩展名默认不会强行解析。遇到不支持的文件时，可以先手动转成 Markdown、TXT 或 PDF，再放入 `LearningVault/inbox/待处理资料/`。

## 常见用法

### 学一个新主题

```text
使用 $obsidian-learning-coach，我想学 Transformer
```

Skill 会先询问：

- 你现在知道什么？
- 学习目的是什么？
- 希望达到什么程度？
- 偏好什么学习方式？

如果你想跳过评估，可以说：

```text
不要问，直接开始
```

### 从资料学习

```text
使用 $obsidian-learning-coach，帮我学习这个 PDF，并整理成 Obsidian 笔记
```

它会优先把资料转换为 Markdown，再建立来源索引、课程笔记、概念笔记和知识地图。

### 只转换 Markdown

```text
把这个 PDF 转成 Markdown，不用开始教学
```

这会走转换流程，不会自动生成课程。

### 复习

```text
今天该复习什么？
```

或：

```text
复习 Transformer
```

Skill 会优先用主动回忆，而不是让你先看答案。

## 默认学习库结构

```text
LearningVault/
├─ settings/
│  ├─ background.md
│  ├─ glossary.md
│  └─ .env
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
         └─ images/
```

## 内置脚本

- `scripts/init_vault.py`：初始化 Obsidian 学习库。
- `scripts/init_topic.py`：初始化某个学习主题。
- `scripts/convert_to_markdown.py`：把资料转换为 Markdown。
- `scripts/analyze_source_structure.py`：分析转换后的 Markdown 是否适合建立章节索引。
- `scripts/build_chapter_index.py`：按稳定标题层级生成章节索引和 `chapters/` 文件。
- `scripts/scan_due_reviews.py`：扫描到期复习内容。
- `scripts/update_review_plan.py`：更新复习计划和复习记录。
- `scripts/extract_glossary.py`：从笔记或资料中辅助提取术语。

## 注意事项

- 医疗、法律、金融、安全等高风险主题仅用于概念学习，不构成专业建议。
- 资料学习会尽量基于用户提供的资料，不会编造来源。
- 如果资料外补充知识，会明确标注为资料外补充。
- `settings/background.md` 属于私人学习背景，不会被复制进公开知识笔记。
- 如果 MinerU API 形式发生变化，可以调整 `scripts/convert_to_markdown.py` 中的转换逻辑。
