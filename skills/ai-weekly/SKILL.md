# AI Weekly Skill

## 触发条件

当用户请求生成 AI 周报、运行周报流水线、或指定周次生成数据时触发此 Skill。

典型触发语句：
- "帮我运行本周的 AI 周报流水线"
- "生成 2026年第13周 的周报数据"
- "本周的 AI 新闻汇总"
- "采集本周的 AI 行业资讯"

## 执行管道

按照以下顺序执行 6 个步骤：

### 1. Collect（收集）
从本周的每日归档中收集所有新闻

### 2. Aggregate（聚合）
按类别聚合新闻，统计趋势

### 3. Highlight（精选）
选出本周最重要的 5 条新闻

### 4. Trend（趋势分析）
分析本周热点话题和关键词

### 5. Format（格式化）
生成周报格式的内容

### 6. Write（写入）
将结果写入 JSON 文件

## 输出文件

- `data/weekly/YYYY-Www.json`：每周归档数据
- `docs/data/weekly/YYYY-Www.json`：GitHub Pages 副本

## 数据格式

### 周报结构

```json
{
  "year": 2026,
  "week": 13,
  "start_date": "2026-03-24",
  "end_date": "2026-03-31",
  "total_items": 45,
  "highlights": [
    {
      "title": "OpenAI 完成史上最大规模融资",
      "importance": 5,
      "summary": "..."
    }
  ],
  "trends": {
    "top_categories": ["融资并购", "模型发布", "产品更新"],
    "top_keywords": ["GPT", "Claude", "Agent"]
  },
  "all_items": [/* 所有新闻条目 */]
}
```

---

## 相关文档

详见同目录下的参考文档（如有）。
