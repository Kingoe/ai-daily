# AI Daily 信息源清单

## 英文信息源

### 官方博客
| 名称 | URL | 说明 | 采集方式 |
|------|-----|------|---------|
| OpenAI | https://openai.com/blog/rss.xml | GPT、Sora 等产品官方公告 | RSS |
| Google DeepMind | https://deepmind.google/discover/rss/ | Gemini、AlphaGo 等研究成果 | RSS |
| Anthropic | https://www.anthropic.com/news | Claude 官方公告 | WebFetch 抓取 |
| Cursor | https://cursor.sh/blog | Cursor IDE 官方博客 | WebFetch 抓取 |

### 科技媒体
| 名称 | URL | 说明 | 采集方式 |
|------|-----|------|---------|
| TechCrunch | https://techcrunch.com/category/artificial-intelligence/feed/ | AI 创业、融资、产品发布 | RSS |
| MIT Technology Review | https://www.technologyreview.com/topic/artificial-intelligence/feed/ | 技术评论和趋势分析 | RSS |
| The Verge AI | https://www.theverge.com/ai-artificial-intelligence | AI 新闻报道 | WebFetch 抓取 |

### 社区聚合
| 名称 | URL | 说明 | 采集方式 |
|------|-----|------|---------|
| Hacker News | https://hnrss.org/frontpage?q=AI | 技术社区热门讨论 | RSS |

## 中文信息源

### 行业媒体
| 名称 | URL | 说明 | 采集方式 |
|------|-----|------|---------|
| 量子位 | https://www.qbitai.com/feed | 国内 AI 行业媒体 | RSS |
| 新智元 | https://www.aijingtai.com | 国内 AI 行业媒体 | WebFetch 抓取 |
| InfoQ AI | https://www.infoq.cn/feed.xml | AI 技术和行业资讯 | RSS |
| 机器之心 | https://www.jiqizhixin.com | 国内 AI 行业媒体 | WebFetch 抓取 |

## 信息源优先级

1. **P0（必采）**：OpenAI、Google DeepMind、Anthropic 官方公告
2. **P1（重要）**：TechCrunch 独家报道、Cursor 官方更新
3. **P2（补充）**：量子位、新智元、InfoQ、机器之心 中文资讯
4. **P3（参考）**：Hacker News、The Verge 社区热议

## 采集频率

- 官方博客：实时关注（重大发布通常在工作日 18:00-22:00 UTC）
- 科技媒体：每 2-4 小时
- 社区聚合：每 6 小时

## 注意事项

1. 优先采集原创报道，避免转载内容
2. 中文源注意甄别翻译质量
3. 交叉验证重要信息（特别是融资、产品发布等）
4. 标注信息来源，便于追溯
5. 对于无 RSS 的源，使用 WebFetch 直接抓取页面 HTML 解析
