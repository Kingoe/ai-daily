# AI Daily 自动化执行指南

## 📋 概述

AI Daily 支持三种自动化执行方式：

| 方案 | 适用场景 | 自动化程度 | 复杂度 |
|------|---------|-----------|--------|
| **方案 1：GitHub Actions** | GitHub Pages 部署 | ⭐⭐⭐⭐⭐ | 简单 |
| **方案 2：服务器 Crontab** | 自有服务器部署 | ⭐⭐⭐⭐⭐ | 中等 |
| **方案 3：Python 脚本** | 自定义需求 | ⭐⭐⭐⭐ | 较复杂 |

---

## 🚀 方案 1：GitHub Actions（推荐）

### 优势
- ✅ 完全免费（GitHub Actions 每月 2000 分钟额度）
- ✅ 无需服务器
- ✅ 配置简单
- ✅ 自动部署到 GitHub Pages

### 配置步骤

#### 1. 获取 Anthropic API Key

访问：https://console.anthropic.com/settings/keys

创建新的 API Key。

#### 2. 在 GitHub 配置 Secrets

进入你的仓库：https://github.com/Kingoe/ai-daily/settings/secrets/actions

添加以下 Secrets：

| Name | Value |
|------|-------|
| `ANTHROPIC_API_KEY` | 你的 Anthropic API Key |
| `SERVER_SSH_KEY` | （可选）服务器 SSH 私钥 |
| `SERVER_HOST` | （可选）服务器 IP |

#### 3. 启用 GitHub Actions

进入：https://github.com/Kingoe/ai-daily/actions

确认工作流已启用。

#### 4. 手动测试

点击 "Run workflow" 手动触发一次。

#### 5. 等待自动执行

工作流会在每天 UTC 8:00（北京时间 16:00）自动运行。

### 执行流程

```
GitHub Actions 触发
    ↓
Checkout 代码
    ↓
安装 Claude Code
    ↓
调用 Claude Code 生成日报
    ↓
提交并推送到 GitHub
    ↓
GitHub Pages 自动构建
    ↓
网站更新完成
```

---

## 🖥️ 方案 2：服务器 Crontab（推荐用于自有服务器）

### 优势
- ✅ 完全控制
- ✅ 可结合服务器其他服务
- ✅ 不受 GitHub Actions 限制

### 配置步骤

#### 1. SSH 登录服务器

```bash
ssh root@你的服务器 IP
```

#### 2. 安装依赖

```bash
# 安装 Node.js（如果使用 Claude Code）
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt install -y nodejs

# 安装 Claude Code
npm install -g @anthropic-ai/claude-code
```

#### 3. 配置 API Key

```bash
# 编辑环境变量
nano ~/.bashrc

# 添加到文件末尾
export ANTHROPIC_API_KEY="你的 API 密钥"

# 使配置生效
source ~/.bashrc
```

#### 4. 上传自动化脚本

```bash
# 创建脚本目录
mkdir -p /usr/local/bin/ai-daily

# 从 GitHub 下载脚本
cd /usr/local/bin/ai-daily
wget https://raw.githubusercontent.com/Kingoe/ai-daily/main/scripts/auto-generate.sh
chmod +x auto-generate.sh
```

#### 5. 配置 Crontab

```bash
# 编辑 crontab
crontab -e
```

添加以下行：

```bash
# 每天下午 4 点生成 AI 日报
0 8 * * * /usr/local/bin/ai-daily/auto-generate.sh >> /var/log/ai-daily/cron.log 2>&1
```

#### 6. 创建日志目录

```bash
mkdir -p /var/log/ai-daily
chmod 755 /var/log/ai-daily
```

#### 7. 测试脚本

```bash
# 手动运行一次
/usr/local/bin/ai-daily/auto-generate.sh

# 查看日志
tail -f /var/log/ai-daily/generate.log
```

### 执行流程

```
Crontab 定时触发
    ↓
执行 auto-generate.sh
    ↓
调用 Claude Code 生成日报
    ↓
Git 提交并推送
    ↓
GitHub 仓库更新
    ↓
服务器自动拉取（可选）
    ↓
网站更新完成
```

---

## 🐍 方案 3：Python 脚本（高级定制）

### 优势
- ✅ 完全自定义采集逻辑
- ✅ 可扩展性强
- ✅ 可集成其他 API

### 配置步骤

#### 1. 安装 Python 依赖

```bash
# 在服务器上执行
pip3 install anthropic requests beautifulsoup4 feedparser
```

#### 2. 配置 API Key

```bash
export ANTHROPIC_API_KEY="你的 API 密钥"
```

#### 3. 运行脚本

```bash
cd /var/www/ai-daily/scripts
python3 auto_generate.py
```

#### 4. 配置 Crontab

```bash
crontab -e
```

添加：

```bash
# 每天下午 4 点执行 Python 脚本
0 8 * * * cd /var/www/ai-daily/scripts && python3 auto_generate.py >> /var/log/ai-daily/python.log 2>&1
```

### 自定义采集逻辑

编辑 `auto_generate.py` 中的 `fetch_news_from_source()` 函数：

```python
def fetch_news_from_source(source):
    """从信息源采集新闻"""
    import requests
    from bs4 import BeautifulSoup
    
    response = requests.get(source["url"])
    soup = BeautifulSoup(response.text, 'html.parser')
    
    news_list = []
    
    # 根据网站结构调整选择器
    for item in soup.select('.news-item'):
        news_list.append({
            "title": item.select_one('.title').text,
            "url": item.select_one('a')['href'],
            "content": item.select_one('.content').text,
            "published_at": item.select_one('.date').text,
            "source": source["name"]
        })
    
    return news_list
```

---

## 📊 三种方案对比

| 特性 | GitHub Actions | 服务器 Crontab | Python 脚本 |
|------|---------------|----------------|-------------|
| **成本** | 免费 | 服务器成本 | 服务器成本 |
| **配置难度** | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **灵活性** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **维护成本** | 低 | 中 | 高 |
| **适用场景** | GitHub Pages | 自有服务器 | 自定义需求 |

---

## 🔧 混合方案（最佳实践）

结合 GitHub Actions 和服务器部署：

```yaml
# .github/workflows/generate-daily.yml

name: Generate AI Daily

on:
  schedule:
    - cron: '0 8 * * *'  # 每天 UTC 8:00
  workflow_dispatch:

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Generate with Claude
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          claude "帮我运行今天的 AI 日报流水线"
      
      - name: Push to GitHub
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add .
          git commit -m "chore: daily update $(date +%Y-%m-%d)" || true
          git push
      
      - name: Deploy to Server
        uses: easingthemes/ssh-deploy@v2.1.1
        with:
          SSH_PRIVATE_KEY: ${{ secrets.SERVER_SSH_KEY }}
          REMOTE_HOST: ${{ secrets.SERVER_HOST }}
          REMOTE_USER: root
          SOURCE: docs/
          TARGET: /var/www/ai-daily/docs
```

这样：
- ✅ GitHub Actions 负责生成数据
- ✅ 自动部署到 GitHub Pages
- ✅ 同步部署到自有服务器
- ✅ 双重备份，更可靠

---

## 📝 成本估算

### GitHub Actions
- 免费额度：2000 分钟/月
- 每次运行：约 5-10 分钟
- 每天运行：足够使用

### 服务器 Crontab
- 服务器成本：已存在（部署 Open Claw）
- 额外成本：无

### API 调用成本
- Anthropic API：约 $0.01-0.05/次
- 每天 1 次：约 $0.30-1.50/月

---

## 🆘 常见问题

### Q1: API Key 如何获取？

访问 https://console.anthropic.com/settings/keys 创建。

### Q2: 如何查看执行日志？

**GitHub Actions**：
- 进入仓库 → Actions → 查看运行日志

**服务器 Crontab**：
```bash
tail -f /var/log/ai-daily/generate.log
```

### Q3: 如何手动触发？

**GitHub Actions**：
- Actions → "Generate AI Daily" → "Run workflow"

**服务器**：
```bash
/usr/local/bin/ai-daily/auto-generate.sh
```

### Q4: 失败了怎么办？

检查日志，常见问题：
- API Key 过期 → 重新生成
- 网络问题 → 检查服务器网络
- 采集失败 → 检查信息源 URL

---

## 🎯 推荐方案

**对于你的情况**（有阿里云服务器 + GitHub Pages）：

使用 **混合方案**：

1. **GitHub Actions** 负责：
   - 每天定时生成数据
   - 部署到 GitHub Pages
   - 作为主用方案

2. **服务器** 负责：
   - 作为备用部署
   - 提供 API 接口（未来扩展）
   - 存储历史数据

这样既有 GitHub 的免费托管，又有服务器的灵活性！

---

需要我帮你配置具体的自动化方案吗？😊
