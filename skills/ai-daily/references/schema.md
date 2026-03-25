# AI Daily JSON Schema

## 索引文件结构 (index.json)

```json
{
  "latest_date": "2026-03-25",
  "updated_at": "2026-03-26T08:00:00Z",
  "dates": ["2026-03-25", "2026-03-24", "2026-03-23"],
  "items": []
}
```

### 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| latest_date | string | 最新一期日期（YYYY-MM-DD 格式） |
| updated_at | string | 最后更新时间（ISO 8601 格式） |
| dates | string[] | 所有可用日期列表（降序排列） |
| items | Item[] | 最新一期的所有新闻条目 |

## 新闻条目结构 (Item)

### 英文条目

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

### 中文条目

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

### 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string | ✅ | 唯一标识符（8 位十六进制） |
| lang | string | ✅ | 语言类型："en" 或 "zh" |
| title_en | string | lang=en 时必填 | 英文标题 |
| title_zh | string | ✅ | 中文标题（英文源翻译，中文源原文） |
| summary_zh | string | ✅ | 中文摘要（≤200 字） |
| summary_en | string | lang=en 时必填 | 英文摘要（≤200 词） |
| tags | string[] | ✅ | 标签列表 |
| source_name | string | ✅ | 来源名称 |
| source_url | string | ✅ | 来源 URL |
| published_at | string | ✅ | 发布时间（ISO 8601） |
| collected_at | string | ✅ | 采集时间（ISO 8601） |
| importance | integer | ✅ | 重要性评分（1-5） |
| merged_sources | Source[] | ✅ | 合并的其他来源（去重后） |

### Source 结构（merged_sources 数组元素）

```json
{
  "name": "The Verge",
  "url": "https://www.theverge.com/..."
}
```

## 标签体系

### 一级分类
- 模型发布
- 产品更新
- 融资并购
- 研究论文
- 行业合作
- 政策法规
- Agent 编程
- 多模态
- 机器人
- 评测基准

### 来源标签
- Anthropic
- OpenAI
- Google DeepMind
- 量子位
- 机器之心
- TechCrunch
- The Verge

## 重要性评分标准

| 分数 | 标准 | 示例 |
|------|------|------|
| 5 | 重大产品发布/战略级合作 | GPT-5 发布、OpenAI 与苹果合作 |
| 4 | 重要产品更新/大额融资 | Claude 大版本更新、B 轮以上融资 |
| 3 | 常规产品迭代/学术研究 | 小版本更新、arXiv 论文 |
| 2 | 行业资讯/ minor 更新 | 人事变动、小功能优化 |
| 1 | 简讯/转载内容 | 短消息、会议预告 |

## 每日数据文件 (YYYY-MM-DD.json)

```json
{
  "date": "2026-03-25",
  "generated_at": "2026-03-26T08:00:00Z",
  "total_items": 15,
  "items": [ /* Item 数组 */ ]
}
```
