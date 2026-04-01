# AI Daily Skill 执行指南

## 概述

这是一个真正的 Skill 自动触发系统。当你在 Claude Code 中说特定的触发语句时，Claude 会自动加载并执行这个 Skill，按照定义的 8 步流水线生成 AI 日报。

## 触发语句

### 方式 1：完整流水线执行

```
帮我运行今天的 AI 日报流水线
```

```
生成 2026-03-29 的日报数据
```

```
今天的 AI 新闻有哪些
```

### 方式 2：单步执行

```
执行 Fetch 步骤，采集今天的新闻
```

```
为这些新闻生成摘要
```

```
更新索引文件
```

## 8 步流水线详解

### 第 1 步：Fetch（采集）

**目标**：从预定义的信息源获取最新的 AI 行业资讯

**执行方式**：
- 使用 Python 的 feedparser 库读取 RSS 源
- 使用 requests 库获取网页内容
- 按目标日期过滤新闻

**信息源**：
- 官方博客：OpenAI、Anthropic、Google DeepMind、Cursor
- 科技媒体：TechCrunch、The Verge、MIT Technology Review
- 社区聚合：Hacker News
- 中文媒体：量子位、机器之心、InfoQ

**输出**：raw_items 数组，包含标题、URL、内容、发布时间、来源等

---

### 第 2 步：Filter（过滤）

**目标**：筛选出与 AI 相关的高质量内容

**过滤规则**：
1. **内容质量**
   - 排除标题党（纯感叹号、过度夸张）
   - 排除广告推广内容
   - 排除重复发布

2. **相关性**
   - 必须与 AI 直接相关
   - 排除泛科技新闻

3. **时效性**
   - 只保留目标日期范围内的内容

**输出**：filtered_items 数组

---

### 第 3 步：Dedup（去重）

**目标**：使用语义去重技术，合并同一事件的不同来源报道

**去重策略**：
1. **URL 去重**：相同 URL 直接合并
2. **标题相似度**：计算标题 Jaccard 相似度 > 0.8
3. **语义去重**：使用 AI 判断两条新闻是否报道同一事件

**合并规则**：
- 保留最早发布的版本作为主条目
- 将其他来源添加到 merged_sources 数组

**输出**：deduped_items 数组（带 merged_sources 字段）

---

### 第 4 步：Verify（验证）

**目标**：验证信息的真实性和准确性

**验证维度**：
1. **来源可信度**
   - 官方源：直接信任
   - 权威媒体：高信任度
   - 自媒体/博客：需交叉验证

2. **内容一致性**
   - 检查多个来源是否一致
   - 标注存疑信息

3. **事实核查**
   - 数字信息需至少 2 个来源

**输出**：verified_items 数组（带 confidence 字段）

---

### 第 5 步：Summarize（摘要）

**目标**：为每条新闻生成中英文双语摘要

**摘要要求**：
- 中文摘要：≤200 字，严格事实导向
- 英文摘要：≤200 词，严格事实导向
- 结构：来源 + 核心事实 + 关键细节
- 格式：`来源：核心内容...`

**输出**：summarized_items 数组（带 summary_zh 和 summary_en 字段）

---

### 第 6 步：Tag（打标签）

**目标**：为每条新闻自动分类打标签

**标签体系**：
- 一级分类：模型发布、产品更新、融资并购、研究论文、行业合作、政策法规、Agent 编程、多模态、机器人、评测基准
- 来源标签：直接使用 source_name 作为标签

**输出**：tagged_items 数组（带 tags 字段）

---

### 第 7 步：Score（评分）

**目标**：根据新闻重要性进行评分（1-5 分）

**评分标准**：
- 5 分：重大产品发布/战略级合作
- 4 分：重要产品更新/大额融资
- 3 分：常规产品迭代/学术研究
- 2 分：行业资讯/minor 更新
- 1 分：简讯/转载内容

**输出**：scored_items 数组（带 importance 字段，1-5）

---

### 第 8 步：Write（写入）

**目标**：将结果写入 JSON 文件并更新索引

**写入文件**：
1. `data/YYYY-MM-DD.json`：每日归档数据
2. `docs/data/YYYY-MM-DD.json`：GitHub Pages 副本
3. `data/index.json`：最新数据索引
4. `docs/data/index.json`：GitHub Pages 索引副本

**原子更新**：
1. 先写入临时文件
2. 验证 JSON 格式
3. 重命名临时文件到目标位置
4. 更新索引文件

---

## 输出文件格式

### 每日数据文件 (data/YYYY-MM-DD.json)

```json
{
  "date": "2026-03-29",
  "generated_at": "2026-03-29T21:28:21.607417Z",
  "total_items": 9,
  "items": [
    {
      "id": "713755c2",
      "lang": "en",
      "title_en": "Miasma: A tool to trap AI web scrapers in an endless poison pit",
      "title_zh": "Miasma: A tool to trap AI web scrapers in an endless poison pit",
      "summary_zh": "Hacker News AI：开源工具Miasma发布，可将Python代码转为可独立运行的二进制文件...",
      "summary_en": "Hacker News AI: Open source tool Miasma released...",
      "tags": ["Hacker News AI", "工具发布"],
      "source_name": "Hacker News AI",
      "source_url": "https://github.com/austin-weeks/miasma",
      "published_at": "Sun, 29 Mar 2026 10:10:12 +0000",
      "collected_at": "2026-03-29T21:27:52.128705Z",
      "importance": 3,
      "merged_sources": []
    }
  ]
}
```

### 索引文件 (data/index.json)

```json
{
  "latest_date": "2026-03-29",
  "updated_at": "2026-03-29T21:28:21.612871Z",
  "dates": ["2026-03-29", "2026-03-28", "2026-03-27"],
  "items": [/* 最新一天的所有条目 */]
}
```

---

## 使用示例

### 示例 1：完整流水线

**用户输入**：
```
帮我运行今天的 AI 日报流水线
```

**Claude 执行**：
1. ✅ 识别到触发语句，加载 AI Daily Skill
2. 🚀 开始执行 8 步流水线
3. 📡 Fetch：从 RSS 源采集新闻
4. 🔍 Filter：过滤无关内容
5. 🔄 Dedup：语义去重
6. ✅ Verify：验证信息真实性
7. 📝 Summarize：生成中英文摘要
8. 🏷️ Tag：自动分类打标签
9. ⭐ Score：重要性评分
10. 💾 Write：写入 JSON 文件并更新索引
11. 🎉 完成！

---

### 示例 2：指定日期

**用户输入**：
```
生成 2026-03-28 的日报数据
```

**Claude 执行**：
- 使用目标日期 2026-03-28 执行完整流水线

---

### 示例 3：单步执行

**用户输入**：
```
先采集一下今天的新闻看看
```

**Claude 执行**：
- 只执行 Fetch 步骤
- 显示采集到的原始新闻

---

## 最佳实践

### 日常使用

```
在 Claude 中直接说："帮我运行今天的 AI 日报流水线"
```

### 查看结果

```
"查看今天生成的 AI 日报数据"
```

### 本地预览

```bash
python3 -m http.server 8000
```

然后访问：http://localhost:8000/docs/

---

## 注意事项

1. **Skill 自动触发**：Claude 会自动识别 `skills/ai-daily/SKILL.md` 和 `.claude-plugin/plugin.json`
2. **数据覆盖**：如果目标日期已存在数据，会提示是否覆盖
3. **API 调用**：摘要生成可能需要调用 AI API，确保有足够的额度
4. **网络连接**：Fetch 步骤需要网络连接来访问 RSS 源

---

## 相关文档

- [SKILL.md](skills/ai-daily/SKILL.md) - Skill 定义
- [pipeline.md](skills/ai-daily/references/pipeline.md) - 流水线详细说明
- [schema.md](skills/ai-daily/references/schema.md) - 数据格式规范
- [sources.md](skills/ai-daily/references/sources.md) - 信息源清单
- [prompts.md](skills/ai-daily/references/prompts.md) - 提示词模板

---

**祝你使用愉快！** 🎉
