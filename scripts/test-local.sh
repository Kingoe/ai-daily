#!/bin/bash

# AI Daily 本地测试脚本（使用 DeepSeek API）
# 自动加载 .env 文件中的 API Key

set -e

# 加载 .env 文件
if [ -f ".env" ]; then
    set -a
    source .env
    set +a
    echo "✅ 已加载 .env 文件"
else
    echo "⚠️  未找到 .env 文件，请确保 DEEPSEEK_API_KEY 已配置"
fi

# 配置
# ⚠️ 安全提示：从环境变量读取 API Key
DEEPSEEK_API_KEY="${DEEPSEEK_API_KEY:-}"
if [ -z "$DEEPSEEK_API_KEY" ]; then
    echo "错误：请设置 DEEPSEEK_API_KEY 环境变量"
    echo "或在项目根目录创建 .env 文件"
    exit 1
fi
DEEPSEEK_URL="https://api.deepseek.com/v1/chat/completions"
DATE=$(date +%Y-%m-%d)
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "🚀 开始生成 AI Daily: $DATE"
echo "📁 项目目录：$PROJECT_DIR"

cd "$PROJECT_DIR"

# 测试 DeepSeek API
echo "📡 测试 DeepSeek API 连接..."

TEST_RESPONSE=$(curl -s -X POST "$DEEPSEEK_URL" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $DEEPSEEK_API_KEY" \
    -d '{
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": "你好"}]
    }')

if echo "$TEST_RESPONSE" | grep -q "choices"; then
    echo "✅ DeepSeek API 连接成功！"
else
    echo "❌ DeepSeek API 连接失败"
    echo "响应：$TEST_RESPONSE"
    exit 1
fi

# 生成示例新闻的摘要
echo ""
echo "📝 生成示例新闻摘要..."

NEWS_CONTENT="OpenAI 今天发布了 GPT-5 模型，该模型在推理能力、数学计算和代码生成方面实现了重大突破。新模型采用了全新的混合架构设计，支持高达 100 万 tokens 的上下文窗口，在 MMLU 基准测试中取得了 92.5 分的优异成绩，首次超越了人类专家水平。"

SUMMARY=$(curl -s -X POST "$DEEPSEEK_URL" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $DEEPSEEK_API_KEY" \
    -d "{
        \"model\": \"deepseek-chat\",
        \"messages\": [
            {
                \"role\": \"user\",
                \"content\": \"请为以下新闻生成中文摘要（200 字以内，事实导向）：\n\n$NEWS_CONTENT\"
            }
        ],
        \"temperature\": 0.3,
        \"max_tokens\": 500
    }" | python3 -c "import sys, json; print(json.load(sys.stdin)['choices'][0]['message']['content'])")

echo ""
echo "📄 原始新闻："
echo "$NEWS_CONTENT"
echo ""
echo "✨ DeepSeek 生成的摘要："
echo "$SUMMARY"
echo ""

# 创建示例数据文件
echo "💾 创建数据文件..."

cat > "docs/data/${DATE}.json" << EOF
{
  "date": "$DATE",
  "generated_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "total_items": 1,
  "items": [
    {
      "id": "$(openssl rand -hex 4)",
      "lang": "zh",
      "title_zh": "OpenAI 发布 GPT-5 模型，实现重大技术突破",
      "summary_zh": "OpenAI：$SUMMARY",
      "tags": ["模型发布", "OpenAI"],
      "source_name": "OpenAI",
      "source_url": "https://openai.com/news",
      "published_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
      "collected_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
      "importance": 5,
      "merged_sources": []
    }
  ]
}
EOF

# 更新索引
cat > "docs/data/index.json" << EOF
{
  "latest_date": "$DATE",
  "updated_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "dates": ["$DATE"],
  "items": [
    {
      "id": "$(openssl rand -hex 4)",
      "lang": "zh",
      "title_zh": "OpenAI 发布 GPT-5 模型，实现重大技术突破",
      "summary_zh": "OpenAI：$SUMMARY",
      "tags": ["模型发布", "OpenAI"],
      "source_name": "OpenAI",
      "source_url": "https://openai.com/news",
      "published_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
      "collected_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
      "importance": 5,
      "merged_sources": []
    }
  ]
}
EOF

# 同步到 data 目录
cp "docs/data/${DATE}.json" "data/${DATE}.json"
cp "docs/data/index.json" "data/index.json"

echo ""
echo "✅ 生成完成！"
echo ""
echo "📂 生成的文件："
echo "   - docs/data/${DATE}.json"
echo "   - docs/data/index.json"
echo "   - data/${DATE}.json"
echo "   - data/index.json"
echo ""
echo "🌐 本地预览：http://localhost:8000/docs/"
echo ""
echo "💰 本次成本：约 ¥0.01"
