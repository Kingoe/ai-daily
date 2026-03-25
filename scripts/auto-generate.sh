#!/bin/bash

# AI Daily 自动化采集脚本
# 部署到服务器：/usr/local/bin/ai-daily-generate.sh

set -e

# 配置
PROJECT_DIR="/var/www/ai-daily"
LOG_FILE="/var/log/ai-daily/generate.log"
DATE=$(date +%Y-%m-%d)

# 创建日志目录
mkdir -p /var/log/ai-daily

echo "[$(date)] 开始生成 AI Daily: $DATE" >> $LOG_FILE

cd $PROJECT_DIR

# 使用 Claude Code 生成日报
# 需要预先配置 ANTHROPIC_API_KEY 环境变量
export ANTHROPIC_API_KEY="你的 API 密钥"

claude "生成 $DATE 的 AI 日报数据" >> $LOG_FILE 2>&1

# 提交并推送
git add .
if ! git diff --staged --quiet; then
    git commit -m "chore: auto generate AI daily for $DATE"
    git push origin main
    echo "[$(date)] 推送成功" >> $LOG_FILE
else
    echo "[$(date)] 没有新内容，跳过提交" >> $LOG_FILE
fi

echo "[$(date)] 完成" >> $LOG_FILE
