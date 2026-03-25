#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI Daily 自动化采集脚本

使用方式：
1. 配置 ANTHROPIC_API_KEY 环境变量
2. 运行：python3 auto_generate.py
3. 设置 crontab 定时执行

依赖：
pip install anthropic requests beautifulsoup4
"""

import os
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

# 配置
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DOCS_DATA_DIR = PROJECT_ROOT / "docs" / "data"

# 信息源列表
SOURCES = [
    {
        "name": "OpenAI",
        "url": "https://openai.com/news",
        "type": "official"
    },
    {
        "name": "Anthropic",
        "url": "https://www.anthropic.com/news",
        "type": "official"
    },
    {
        "name": "Google DeepMind",
        "url": "https://deepmind.google/discover/",
        "type": "official"
    },
    {
        "name": "TechCrunch AI",
        "url": "https://techcrunch.com/category/artificial-intelligence/",
        "type": "media"
    },
    {
        "name": "量子位",
        "url": "https://www.qbitai.com/",
        "type": "media_cn"
    }
]


def fetch_news_from_source(source):
    """从信息源采集新闻"""
    # TODO: 实现 RSS 或 API 采集
    print(f"Fetching from {source['name']}...")
    return []


def generate_summary_with_claude(content):
    """使用 Claude 生成摘要"""
    import anthropic
    
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": f"请为以下新闻生成中文摘要（200 字以内）：\n\n{content}"
            }
        ]
    )
    
    return response.content[0].text


def deduplicate_news(news_list):
    """语义去重"""
    # TODO: 使用 embedding 进行语义相似度计算
    return news_list


def save_daily_data(date, items):
    """保存每日数据"""
    data = {
        "date": date,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "total_items": len(items),
        "items": items
    }
    
    # 保存到 data 目录
    with open(DATA_DIR / f"{date}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # 同步到 docs/data 目录
    with open(DOCS_DATA_DIR / f"{date}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # 更新索引
    update_index(date, items)
    
    print(f"Saved {len(items)} items for {date}")


def update_index(date, items):
    """更新索引文件"""
    index_data = {
        "latest_date": date,
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "dates": [date],  # TODO: 从历史文件读取所有日期
        "items": items
    }
    
    with open(DATA_DIR / "index.json", "w", encoding="utf-8") as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)
    
    with open(DOCS_DATA_DIR / "index.json", "w", encoding="utf-8") as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)


def git_commit_and_push(date):
    """提交并推送到 GitHub"""
    subprocess.run(["git", "add", "."], cwd=PROJECT_ROOT, check=True)
    
    result = subprocess.run(
        ["git", "diff", "--staged", "--quiet"],
        cwd=PROJECT_ROOT,
        capture_output=True
    )
    
    if result.returncode != 0:
        subprocess.run(
            ["git", "commit", "-m", f"chore: auto generate AI daily for {date}"],
            cwd=PROJECT_ROOT,
            check=True
        )
        subprocess.run(["git", "push", "origin", "main"], cwd=PROJECT_ROOT, check=True)
        print(f"Pushed to GitHub for {date}")
    else:
        print("No changes to commit")


def main():
    """主函数"""
    # 获取日期（默认为今天）
    today = datetime.now().strftime("%Y-%m-%d")
    
    print(f"Starting AI Daily generation for {today}...")
    
    # 1. 采集新闻
    all_news = []
    for source in SOURCES:
        news = fetch_news_from_source(source)
        all_news.extend(news)
    
    print(f"Fetched {len(all_news)} news items")
    
    # 2. 去重
    unique_news = deduplicate_news(all_news)
    print(f"After deduplication: {len(unique_news)} items")
    
    # 3. 生成摘要（使用 Claude）
    for news in unique_news:
        summary = generate_summary_with_claude(news["content"])
        news["summary_zh"] = summary
    
    # 4. 保存数据
    save_daily_data(today, unique_news)
    
    # 5. 提交并推送
    git_commit_and_push(today)
    
    print(f"Completed AI Daily generation for {today}")


if __name__ == "__main__":
    main()
