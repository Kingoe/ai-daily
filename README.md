# AI Daily - AI 行业资讯日报

每日自动采集、去重、摘要并归档 AI 行业资讯，驱动一个静态网站。

## 功能

- **新闻采集**：Anthropic、OpenAI、Google DeepMind、Cursor、TechCrunch、The Verge、Hacker News、MIT Technology Review、量子位、机器之心
- **智能去重**：语义去重，合并同一事件的不同来源报道
- **双语摘要**：自动生成中英文摘要（≤200 字/词，严格事实导向）
- **结构化归档**：每日一个 JSON 文件，持续追加
- **静态前端**：支持深色模式、标签/来源/语言过滤、移动端适配

## 快速开始

### 1. 使用 Claude Code 生成日报

在项目目录中打开 Claude Code，说：

```
帮我运行今天的 AI 日报流水线
```

或

```
生成 2026-03-25 的日报数据
```

Claude 会自动加载 ai-daily skill，按照 **Fetch → Filter → Dedup → Verify → Summarize → Tag → Score → Write** 的顺序执行，将结果写入：
- `data/YYYY-MM-DD.json`
- `docs/data/YYYY-MM-DD.json`
- 更新 `data/index.json` 与 `docs/data/index.json`

### 2. 本地预览网站

在项目根目录运行：

```bash
python3 -m http.server 8000
```

然后访问：http://localhost:8000/docs/

页面会读取 `docs/data/` 下的 JSON 数据并展示。

## 目录结构

```
ai-daily/
├── .claude-plugin/
│   └── plugin.json                 # Claude Code 插件元数据
├── skills/
│   └── ai-daily/
│       ├── SKILL.md                # Skill 定义（触发条件 + 管道概览）
│       └── references/
│           ├── sources.md          # 信息源清单
│           ├── schema.md           # JSON Schema
│           ├── pipeline.md         # 管道步骤详细说明
│           └── prompts.md          # AI 提示词模板
├── data/
│   ├── index.json                  # 最新一期数据（前端读取入口）
│   └── YYYY-MM-DD.json             # 每日归档文件
├── docs/
│   ├── index.html                  # GitHub Pages 静态前端
│   └── data/
│       ├── index.json              # GitHub Pages 数据索引
│       └── YYYY-MM-DD.json         # GitHub Pages 每日数据
└── README.md
```

## 数据格式

### 索引文件 (index.json)

```json
{
  "latest_date": "2026-03-25",
  "updated_at": "2026-03-26T08:00:00Z",
  "dates": ["2026-03-25", "2026-03-24"],
  "items": [ /* 最新一天的所有条目 */ ]
}
```

### 新闻条目

**英文条目**：
```json
{
  "id": "a3f9c21b",
  "lang": "en",
  "title_en": "Claude 4 Announced",
  "title_zh": "Claude 4 发布",
  "summary_zh": "Anthropic：Anthropic 正式发布 Claude 4，在推理能力和编码能力上实现重大突破...",
  "summary_en": "Anthropic: Anthropic officially releases Claude 4, achieving major breakthroughs in reasoning and coding capabilities...",
  "tags": ["模型发布", "Anthropic"],
  "source_name": "Anthropic",
  "source_url": "https://www.anthropic.com/news/claude-4",
  "published_at": "2026-03-25T18:00:00Z",
  "collected_at": "2026-03-26T08:00:00Z",
  "importance": 5,
  "merged_sources": []
}
```

**中文条目**（省略 `title_en` 和 `summary_en`）：
```json
{
  "id": "b7e2d41c",
  "lang": "zh",
  "title_zh": "昆仑万维 AI 音乐模型登顶榜单",
  "summary_zh": "昆仑万维：昆仑万维旗下 AI 音乐模型 Mureka V8 在 Artificial Analysis 音乐模型榜单中登顶...",
  "tags": ["产品发布", "多模态评测基准"],
  "source_name": "量子位",
  "source_url": "https://www.qbitai.com/...",
  "published_at": "2026-03-25T08:00:00Z",
  "collected_at": "2026-03-26T08:00:00Z",
  "importance": 4,
  "merged_sources": []
}
```

## 部署到 GitHub Pages

### 1. 推送到 GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/ai-daily.git
git push -u origin main
```

### 2. 配置 GitHub Pages

1. 进入仓库 **Settings** → **Pages**
2. **Source** 选择 `Deploy from a branch`
3. **Branch** 选择 `main`，folder 选择 `/docs`
4. 点击 **Save**

### 3. 访问线上网站

部署完成后，访问：

```
https://YOUR_USERNAME.github.io/ai-daily/
```

## 自定义信息源

编辑 [`skills/ai-daily/references/sources.md`](skills/ai-daily/references/sources.md) 添加或删除信息源。

### 信息源优先级

- **P0（必采）**：Anthropic、OpenAI、Google DeepMind 官方公告
- **P1（重要）**：TechCrunch、The Verge 独家报道
- **P2（补充）**：量子位、机器之心中文资讯
- **P3（参考）**：Hacker News 社区热议

## 网站功能

- 🌙 **深色模式**：一键切换深色/浅色主题
- 📅 **日期切换**：浏览历史日报
- 🏷️ **标签过滤**：按标签筛选新闻
- 🌐 **语言过滤**：只看中文或英文内容
- 📰 **来源过滤**：按信息来源筛选
- ⭐ **重要性评分**：快速定位重要新闻
- 📱 **移动端适配**：完美支持手机浏览

## 数据处理流程

详见 [`skills/ai-daily/references/pipeline.md`](skills/ai-daily/references/pipeline.md)

### 8 个处理步骤

1. **Fetch**：从信息源采集内容
2. **Filter**：过滤低质量和无关内容
3. **Dedup**：语义去重，合并同源报道
4. **Verify**：验证信息真实性
5. **Summarize**：生成中英文摘要
6. **Tag**：自动分类打标签
7. **Score**：重要性评分（1-5 分）
8. **Write**：写入 JSON 文件

## 提示词模板

详见 [`skills/ai-daily/references/prompts.md`](skills/ai-daily/references/prompts.md)

包含：
- 摘要生成提示词
- 翻译提示词
- 分类打标签提示词
- 重要性评分提示词
- 去重判断提示词
- 完整流水线提示词

## 常见问题

### Q: 如何修改采集频率？

A: 编辑 `sources.md` 中的采集频率配置。

### Q: 如何调整重要性评分标准？

A: 编辑 `prompts.md` 中的评分提示词。

### Q: 网站样式如何自定义？

A: 编辑 `docs/index.html` 中的 CSS 部分。

### Q: 如何添加新的信息源？

A: 在 `sources.md` 中添加信息源信息，并在 `SKILL.md` 中更新采集逻辑。

## 作者

本项目由 Kingoe 独立开发和维护。

## 许可证

MIT License
