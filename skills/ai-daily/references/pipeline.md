# AI Daily 数据处理管道

## 1. Fetch（采集）

### 输入
- 信息源列表（sources.md）
- 目标日期范围（默认最近 24 小时）

### 处理步骤
1. 遍历所有信息源的 RSS/Atom 订阅源
2. 提取文章标题、链接、发布时间、作者
3. 获取文章正文内容
4. 过滤掉非 AI 相关内容

### 输出
```json
{
  "raw_items": [
    {
      "source": "Anthropic",
      "url": "https://...",
      "title": "...",
      "published_at": "...",
      "content": "..."
    }
  ]
}
```

### 注意事项
- 优先使用官方 API（如有）
- 遵守 robots.txt 和网站使用条款
- 设置合理的请求间隔（至少 1 秒）
- 处理反爬机制（User-Agent、重试逻辑）

---

## 2. Filter（过滤）

### 输入
- raw_items 数组

### 过滤规则
1. **内容质量**
   - 排除标题党（纯感叹号、过度夸张）
   - 排除广告推广内容
   - 排除重复发布（同一文章多次推送）

2. **相关性**
   - 必须与 AI 直接相关
   - 排除泛科技新闻（除非涉及重大 AI 合作）

3. **时效性**
   - 只保留目标日期范围内的内容
   - 排除旧闻重发

### 输出
- filtered_items 数组

---

## 3. Dedup（去重）

### 输入
- filtered_items 数组

### 去重策略
1. **URL 去重**：相同 URL 直接合并
2. **标题相似度**：计算标题 Jaccard 相似度 > 0.8
3. **语义去重**：使用 embedding 计算语义相似度 > 0.85

### 合并规则
- 保留最早发布的版本作为主条目
- 将其他来源添加到 merged_sources 数组
- 合并多个来源的摘要信息

### 输出
- deduped_items 数组（带 merged_sources 字段）

---

## 4. Verify（验证）

### 输入
- deduped_items 数组

### 验证维度
1. **来源可信度**
   - 官方源：直接信任
   - 权威媒体：高信任度
   - 自媒体/博客：需交叉验证

2. **内容一致性**
   - 检查多个来源是否一致
   - 标注存疑信息（如"据传"、"疑似"）

3. **事实核查**
   - 数字信息（融资金额、参数等）需至少 2 个来源
   - 引用内容需可追溯原文

### 输出
- verified_items 数组（带 confidence 字段）

---

## 5. Summarize（摘要）

### 输入
- verified_items 数组

### 摘要要求

#### 中文摘要
- 长度：≤200 字
- 结构：来源 + 核心事实 + 关键细节
- 风格：客观陈述，避免主观评价
- 格式：`来源：核心内容...`

#### 英文摘要
- 长度：≤200 词
- 结构：同中文摘要
- 风格：同中文摘要
- 格式：`Source: Core content...`

### 示例

**原文**：
> Anthropic today announced Claude 4, the latest version of its large language model. The new model features significant improvements in reasoning capabilities, with a 40% increase in math benchmark scores compared to Claude 3.5. Claude 4 also introduces enhanced coding abilities, supporting over 50 programming languages and featuring an integrated development environment...

**英文摘要**：
> Anthropic: Anthropic officially releases Claude 4, achieving major breakthroughs in reasoning and coding capabilities. The model shows 40% improvement in math benchmarks compared to Claude 3.5, and supports over 50 programming languages with an integrated development environment.

**中文摘要**：
> Anthropic：Anthropic 正式发布 Claude 4，在推理能力和编码能力上实现重大突破。相比 Claude 3.5，该模型在数学基准测试中提升 40%，支持超过 50 种编程语言，并配备集成开发环境。

### 输出
- summarized_items 数组（带 summary_zh 和 summary_en 字段）

---

## 6. Tag（打标签）

### 输入
- summarized_items 数组

### 标签体系

#### 自动分类标签
根据内容关键词自动分配：
- 包含"发布"、"release"、"launch" → 产品发布
- 包含"融资"、"fund"、"investment" → 融资并购
- 包含"论文"、"paper"、"arXiv" → 研究论文
- 包含"合作"、"partnership" → 行业合作
- 包含"Agent"、"代理" → Agent 编程
- 包含"多模态"、"multimodal" → 多模态
- 包含"机器人"、"robot" → 机器人

#### 来源标签
直接使用 source_name 作为标签

### 输出
- tagged_items 数组（带 tags 字段）

---

## 7. Score（评分）

### 输入
- tagged_items 数组

### 评分规则

#### 基础分（1-3 分）
- 简讯/快讯：1 分
- 常规更新：2 分
- 重要新闻：3 分

#### 加分项
- 官方来源：+1 分
- 独家报道：+1 分
- 重大影响（行业级）：+1 分
- 首次/突破性：+1 分

#### 封顶
- 最高 5 分

### 输出
- scored_items 数组（带 importance 字段，1-5）

---

## 8. Write（写入）

### 输入
- scored_items 数组
- 目标日期

### 写入文件

#### 1. 每日数据文件
路径：`data/YYYY-MM-DD.json`
```json
{
  "date": "2026-03-25",
  "generated_at": "2026-03-26T08:00:00Z",
  "total_items": 15,
  "items": [...]
}
```

#### 2. GitHub Pages 副本
路径：`docs/data/YYYY-MM-DD.json`
- 内容与每日数据文件相同

#### 3. 索引文件
路径：`data/index.json` 和 `docs/data/index.json`
```json
{
  "latest_date": "2026-03-25",
  "updated_at": "2026-03-26T08:00:00Z",
  "dates": ["2026-03-25", "2026-03-24"],
  "items": [最新一天的所有条目]
}
```

### 原子更新
1. 先写入临时文件
2. 验证 JSON 格式
3. 重命名临时文件到目标位置
4. 更新索引文件

---

## 错误处理

### 采集失败
- 单个源失败：跳过并记录日志
- 全部失败：终止流程并报错

### 处理异常
- 单条记录异常：跳过该记录
- 批量异常：回滚并重新处理

### 写入失败
- 保留备份文件
- 回滚到上一个可用版本
