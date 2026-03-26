# Trae IDE 使用指南

## 🎯 在 Trae 中使用 AI Daily Skill

你当前就在 **Trae IDE** 中！Trae 集成了 AI 能力，可以直接执行 Skill。

---

## 📝 使用方式

### 方式 1：直接使用 Trae AI（推荐）

在 Trae 的对话框中输入以下任意命令：

```
帮我运行今天的 AI 日报流水线
```

或

```
生成 2026-03-26 的日报数据
```

或

```
今天的 AI 新闻有哪些
```

Trae 会自动：
1. 加载 `skills/ai-daily/SKILL.md` 定义
2. 执行完整的 8 步流水线
3. 生成日报数据到 `data/` 目录

---

### 方式 2：使用 Python 脚本

如果你更喜欢手动控制：

```bash
# 在项目根目录执行
python3 scripts/fetch_news.py
```

这会：
1. 从 RSS 源抓取最新新闻
2. 调用 DeepSeek API 生成摘要
3. 保存数据到 `data/` 目录

---

## 🔧 配置说明

### 环境变量

确保已配置 DeepSeek API Key：

**方式 1：使用 .env 文件（推荐）**
```bash
# 项目根目录的 .env 文件
DEEPSEEK_API_KEY=sk-你的 API_Key
```

**方式 2：直接设置环境变量**
```bash
export DEEPSEEK_API_KEY="sk-你的 API_Key"
```

---

## 📊 执行流程

### Trae AI 执行流程

```
用户触发
    ↓
加载 AI Daily Skill
    ↓
自动执行 8 步流水线：
  1. Fetch - 从信息源采集
  2. Filter - 过滤低质量内容
  3. Dedup - 语义去重
  4. Verify - 验证真实性
  5. Summarize - 生成摘要
  6. Tag - 打标签
  7. Score - 评分
  8. Write - 写入 JSON
    ↓
生成数据文件
```

### Python 脚本执行流程

```
python3 scripts/fetch_news.py
    ↓
1. 加载 .env 文件
2. RSS 抓取（OpenAI、TechCrunch、The Verge）
3. 网页爬取（量子位等）
4. 调用 DeepSeek API 生成摘要
5. 去重、评分
6. 保存 JSON 文件
    ↓
完成
```

---

## 🎨 两种方式的对比

| 特性 | Trae AI | Python 脚本 |
|------|---------|-------------|
| **触发方式** | 自然语言对话 | 命令行执行 |
| **执行引擎** | Trae AI | Python |
| **智能程度** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **速度** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **成本** | Trae 额度 | DeepSeek API |
| **灵活性** | 高 | 高 |
| **推荐场景** | 日常使用 | 自动化部署 |

---

## 💡 最佳实践

### 日常使用
```
在 Trae 中直接说：
"帮我运行今天的 AI 日报流水线"
```

### 服务器自动化
```bash
# Crontab 定时任务
0 8 * * * cd /var/www/ai-daily && python3 scripts/fetch_news.py
```

### 本地测试
```bash
# 快速测试
bash scripts/test-local.sh

# 完整抓取
python3 scripts/fetch_news.py
```

---

## 🆘 常见问题

### Q1: Trae 无法识别 Skill？

A: 确保：
- `skills/ai-daily/SKILL.md` 文件存在
- 在 Trae 项目目录中打开
- 使用正确的触发语句

### Q2: DeepSeek API 调用失败？

A: 检查：
- `.env` 文件是否存在
- API Key 是否正确
- 网络是否通畅

### Q3: 如何在 Trae 中查看生成的数据？

A: 
```
# 在 Trae 中说
"查看今天生成的 AI 日报数据"

# 或直接打开文件
data/2026-03-26.json
```

---

## 📚 相关文档

- [Skill 定义](skills/ai-daily/SKILL.md) - 完整的 Skill 规范
- [数据来源](skills/ai-daily/references/sources.md) - 信息源清单
- [数据格式](skills/ai-daily/references/schema.md) - JSON Schema
- [处理流程](skills/ai-daily/references/pipeline.md) - 8 步流水线详解
- [提示词模板](skills/ai-daily/references/prompts.md) - AI 提示词

---

## 🚀 快速开始

**第一次使用**：

1. **配置 API Key**
   ```bash
   # 检查 .env 文件
   cat .env
   ```

2. **测试运行**
   ```bash
   python3 scripts/fetch_news.py
   ```

3. **使用 Trae AI**
   ```
   在 Trae 中输入："帮我生成今天的 AI 日报"
   ```

4. **查看结果**
   - 数据文件：`data/2026-03-26.json`
   - 网站预览：http://localhost:8000/docs/

---

**祝你使用愉快！** 🎉
