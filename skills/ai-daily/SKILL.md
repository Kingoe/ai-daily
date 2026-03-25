# AI Daily Skill

## 触发条件

当用户请求生成 AI 日报、运行日报流水线、或指定日期生成数据时触发此 Skill。

典型触发语句：
- "帮我运行今天的 AI 日报流水线"
- "生成 2026-03-25 的日报数据"
- "今天的 AI 新闻有哪些"
- "采集最新的 AI 行业资讯"

## 执行管道

按照以下顺序执行 8 个步骤：

### 1. Fetch（采集）
从预定义的信息源获取最新的 AI 行业资讯

### 2. Filter（过滤）
筛选出与 AI 相关的高质量内容，排除广告、重复发布等低质量信息

### 3. Dedup（去重）
使用语义去重技术，合并同一事件的不同来源报道

### 4. Verify（验证）
验证信息的真实性和准确性，排除虚假新闻

### 5. Summarize（摘要）
为每条新闻生成中英文双语摘要（≤200 字/词，严格事实导向）

### 6. Tag（打标签）
为每条新闻自动分类打标签（如：模型发布、产品更新、融资并购等）

### 7. Score（评分）
根据新闻重要性进行评分（1-5 分）

### 8. Write（写入）
将结果写入 JSON 文件并更新索引

## 输出文件

- `data/YYYY-MM-DD.json`：每日归档数据
- `docs/data/YYYY-MM-DD.json`：用于 GitHub Pages 的副本
- `data/index.json`：最新数据索引（前端读取入口）
- `docs/data/index.json`：GitHub Pages 索引副本

## 数据来源

详见 [sources.md](references/sources.md)

## 数据格式

详见 [schema.md](references/schema.md)

## 提示词模板

详见 [prompts.md](references/prompts.md)

## 管道详细说明

详见 [pipeline.md](references/pipeline.md)
