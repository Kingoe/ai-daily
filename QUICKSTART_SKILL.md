# AI Daily Skill 快速开始

## 🎉 恭喜！你已成功配置 AI Daily Skill

现在你可以通过两种方式使用这个 Skill：

---

## 方式一：自然语言触发（推荐）

直接在 Claude Code 中说：

```
帮我运行今天的 AI 日报流水线
```

Claude 会自动：
1. 识别触发语句
2. 加载 `skills/ai-daily/SKILL.md`
3. 执行完整的 8 步流水线
4. 生成日报数据

---

## 方式二：使用 Skill 流水线脚本

```bash
# 运行今天的完整流水线
python3 scripts/skill_pipeline.py --today

# 运行指定日期的流水线
python3 scripts/skill_pipeline.py --date 2026-03-29

# 只执行 Fetch 步骤（查看采集结果）
python3 scripts/skill_pipeline.py --date 2026-03-29 --fetch-only
```

---

## 8 步流水线演示

让我为你演示一下完整的流水线执行过程：

### 📡 第 1 步：Fetch（采集）
从 10 个 RSS 源采集新闻，按日期过滤

### 🔍 第 2 步：Filter（过滤）
排除标题党、广告、非 AI 相关内容

### 🔄 第 3 步：Dedup（去重）
基于 URL 和标题去重

### ✅ 第 4 步：Verify（验证）
评估来源可信度

### 📝 第 5 步：Summarize（摘要）
生成中英文摘要

### 🏷️ 第 6 步：Tag（打标签）
自动分类打标签

### ⭐ 第 7 步：Score（评分）
重要性评分（1-5 分）

### 💾 第 8 步：Write（写入）
写入 JSON 文件并更新索引

---

## 输出文件

生成的数据会保存到：
- `data/YYYY-MM-DD.json` - 每日归档
- `docs/data/YYYY-MM-DD.json` - GitHub Pages 副本
- `data/index.json` - 最新索引
- `docs/data/index.json` - GitHub Pages 索引副本

---

## 本地预览

```bash
python3 -m http.server 8000
```

然后访问：http://localhost:8000/docs/

---

## 相关文档

- [SKILL_EXECUTION_GUIDE.md](SKILL_EXECUTION_GUIDE.md) - 详细的 Skill 执行指南
- [skills/ai-daily/SKILL.md](skills/ai-daily/SKILL.md) - Skill 定义
- [.claude-plugin/plugin.json](.claude-plugin/plugin.json) - 插件配置
- [scripts/skill_pipeline.py](scripts/skill_pipeline.py) - Skill 流水线脚本

---

## 现在试试看！

在 Claude Code 中输入：

```
帮我运行今天的 AI 日报流水线
```

看看会发生什么！🚀
