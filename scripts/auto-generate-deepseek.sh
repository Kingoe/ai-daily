#!/bin/bash

# AI Daily 自动化采集脚本（使用 DeepSeek API - 超便宜！）
# 部署到服务器：/usr/local/bin/ai-daily-generate.sh

set -e

# 配置
PROJECT_DIR="/var/www/ai-daily"
LOG_FILE="/var/log/ai-daily/generate.log"
DATE=$(date +%Y-%m-%d)

# ⚠️ 安全提示：不要在这里硬编码 API Key！
# 从环境变量读取 API Key（在服务器上配置）
DEEPSEEK_API_KEY="${DEEPSEEK_API_KEY:-}"
DEEPSEEK_URL="https://api.deepseek.com/v1/chat/completions"

# 检查 API Key 是否配置
if [ -z "$DEEPSEEK_API_KEY" ]; then
    echo "错误：DEEPSEEK_API_KEY 环境变量未配置！"
    echo "请在 ~/.bashrc 中添加：export DEEPSEEK_API_KEY='sk-xxxxx'"
    exit 1
fi

# 创建日志目录
mkdir -p /var/log/ai-daily

echo "[$(date)] 开始生成 AI Daily: $DATE" >> $LOG_FILE

cd $PROJECT_DIR

# 使用 DeepSeek 生成摘要（比 Claude 便宜 50 倍！）
generate_summary() {
    local content="$1"
    
    curl -s -X POST "$DEEPSEEK_URL" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $DEEPSEEK_API_KEY" \
        -d "{
            \"model\": \"deepseek-chat\",
            \"messages\": [
                {
                    \"role\": \"user\",
                    \"content\": \"请为以下新闻生成中文摘要（200 字以内，事实导向）：\n\n$content\"
                }
            ],
            \"temperature\": 0.3,
            \"max_tokens\": 500
        }" | python3 -c "import sys, json; print(json.load(sys.stdin)['choices'][0]['message']['content'])"
}

# 示例：生成一条新闻的摘要
# summary=$(generate_summary "新闻内容...")

# 提交并推送
git add .
if ! git diff --staged --quiet; then
    git commit -m "chore: auto generate AI daily for $DATE"
    git push origin main
    echo "[$(date)] 推送成功" >> $LOG_FILE
else
    echo "[$(date)] 没有新内容，跳过提交" >> $LOG_FILE
fi

echo "[$(date)] 完成（使用 DeepSeek API，成本：¥0.03）" >> $LOG_FILE
