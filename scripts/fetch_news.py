#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI Daily 自动化采集脚本（RSS + 网页爬虫）

功能：
1. 从 RSS 源自动获取最新新闻
2. 调用 DeepSeek API 生成摘要
3. 生成符合 Schema 的 JSON 数据

使用方式：
python3 fetch_news.py
"""

import os
import json
import requests
import feedparser
from datetime import datetime
from bs4 import BeautifulSoup
import re
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
    print(f"✅ 已加载环境变量：{env_path}")
else:
    print("⚠️  未找到 .env 文件，请确保 DEEPSEEK_API_KEY 已配置")

# ==================== 配置区域 ====================

# DeepSeek API 配置
# ⚠️ 安全提示：请在环境变量中配置 API Key
# export DEEPSEEK_API_KEY="sk-xxx"
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")
if not DEEPSEEK_API_KEY:
    print("错误：请设置 DEEPSEEK_API_KEY 环境变量")
    print("获取 API Key: https://platform.deepseek.com/")
    print("或在项目根目录创建 .env 文件")
    exit(1)
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"

# RSS 源列表（这些源提供 RSS 订阅）
RSS_FEEDS = [
    {
        "name": "OpenAI Blog",
        "url": "https://openai.com/blog/rss.xml",
        "type": "official",
        "language": "en"
    },
    {
        "name": "TechCrunch AI",
        "url": "https://techcrunch.com/category/artificial-intelligence/feed/",
        "type": "media",
        "language": "en"
    },
    {
        "name": "The Verge",
        "url": "https://www.theverge.com/rss/index.xml",
        "type": "media",
        "language": "en"
    }
]

# 网页爬虫源（需要解析 HTML）
WEB_SOURCES = [
    {
        "name": "量子位",
        "url": "https://www.qbitai.com/",
        "type": "media_cn",
        "language": "zh",
        "selector": {
            "item": "article.post",
            "title": "h2 a",
            "link": "a",
            "summary": ".excerpt"
        }
    }
]

# 输出目录
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs", "data")


# ==================== 核心功能 ====================

def fetch_from_rss(feed_info):
    """从 RSS 源抓取新闻"""
    print(f"📡 抓取 RSS: {feed_info['name']}")
    
    feed = feedparser.parse(feed_info['url'])
    news_list = []
    
    for entry in feed.entries[:5]:  # 每个源抓取最新的 5 条
        news = {
            "title": entry.title,
            "url": entry.link,
            "content": entry.get('summary', entry.title),
            "published_at": entry.get('published', datetime.now().isoformat()),
            "source_name": feed_info['name'],
            "source_type": feed_info['type'],
            "language": feed_info['language']
        }
        news_list.append(news)
    
    print(f"  ✅ 获取 {len(news_list)} 条新闻")
    return news_list


def fetch_from_web(source_info):
    """从网页抓取新闻（需要解析 HTML）"""
    print(f"🕷️ 爬取网页：{source_info['name']}")
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; AI Daily Bot/1.0)"
        }
        response = requests.get(source_info['url'], headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        news_list = []
        selector = source_info['selector']
        
        for item in soup.select(selector['item'])[:5]:
            title_elem = item.select_one(selector['title'])
            link_elem = item.select_one(selector['link'])
            summary_elem = item.select_one(selector.get('summary', ''))
            
            if title_elem and link_elem:
                news = {
                    "title": title_elem.text.strip(),
                    "url": link_elem.get('href', ''),
                    "content": summary_elem.text.strip() if summary_elem else title_elem.text.strip(),
                    "published_at": datetime.now().isoformat(),
                    "source_name": source_info['name'],
                    "source_type": source_info['type'],
                    "language": source_info['language']
                }
                news_list.append(news)
        
        print(f"  ✅ 获取 {len(news_list)} 条新闻")
        return news_list
    
    except Exception as e:
        print(f"  ❌ 爬取失败：{e}")
        return []


def generate_summary_with_deepseek(content, language="zh"):
    """使用 DeepSeek 生成摘要"""
    if language == "en":
        prompt = f"Please summarize the following news in Chinese (within 200 characters, factual only):\n\n{content}"
    else:
        prompt = f"请为以下新闻生成中文摘要（200 字以内，只陈述事实）：\n\n{content}"
    
    try:
        response = requests.post(
            DEEPSEEK_URL,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
            },
            json={
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "max_tokens": 500
            },
            timeout=30
        )
        
        result = response.json()
        summary = result['choices'][0]['message']['content']
        return summary
    
    except Exception as e:
        print(f"  ⚠️ 摘要生成失败：{e}")
        return content[:200]


def deduplicate_news(news_list):
    """简单去重（基于标题相似度）"""
    seen_titles = set()
    unique_news = []
    
    for news in news_list:
        title_key = news['title'][:50]  # 使用前 50 个字符作为标识
        if title_key not in seen_titles:
            seen_titles.add(title_key)
            unique_news.append(news)
    
    return unique_news


def calculate_importance(news):
    """计算新闻重要性（1-5 分）"""
    source_type = news.get('source_type', 'media')
    title = news.get('title', '').lower()
    
    # 基础分
    if source_type == 'official':
        score = 4
    else:
        score = 3
    
    # 关键词加分
    important_keywords = ['发布', 'release', 'launch', '融资', 'fund', '突破', 'breakthrough']
    for keyword in important_keywords:
        if keyword in title:
            score += 1
            break
    
    return min(score, 5)


def get_existing_dates(data_dir):
    """获取已有的日期列表"""
    index_file = os.path.join(data_dir, "index.json")
    if os.path.exists(index_file):
        try:
            with open(index_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('dates', [])
        except:
            pass
    return []
    
def save_daily_data(news_list, date):
    """保存每日数据到 JSON 文件"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    items = []
    for news in news_list:
        # 生成摘要
        print(f"  📝 生成摘要：{news['title'][:30]}...")
        summary = generate_summary_with_deepseek(news['content'], news['language'])
        
        item = {
            "id": f"{hash(news['url']) & 0xFFFFFFFF:08x}",
            "lang": news['language'],
            "tags": [news['source_name']],
            "source_name": news['source_name'],
            "source_url": news['url'],
            "published_at": news['published_at'],
            "collected_at": datetime.now().isoformat() + "Z",
            "importance": calculate_importance(news),
            "merged_sources": []
        }
        
        if news['language'] == 'en':
            item['title_en'] = news['title']
            item['title_zh'] = news['title']  # TODO: 可以调用翻译 API
            item['summary_en'] = summary
            item['summary_zh'] = f"{news['source_name']}：{summary}"
        else:
            item['title_zh'] = news['title']
            item['summary_zh'] = f"{news['source_name']}：{summary}"
        
        items.append(item)
    
    # 生成每日数据文件
    daily_data = {
        "date": date,
        "generated_at": datetime.now().isoformat() + "Z",
        "total_items": len(items),
        "items": items
    }
    
    # 保存到文件
    daily_file = os.path.join(OUTPUT_DIR, f"{date}.json")
    with open(daily_file, 'w', encoding='utf-8') as f:
        json.dump(daily_data, f, ensure_ascii=False, indent=2)
    
    # 获取已有日期列表
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    existing_dates = get_existing_dates(data_dir)
    
    # 更新或添加新日期
    if date not in existing_dates:
        existing_dates.insert(0, date)  # 新日期放在最前面
    
    # 更新索引文件
    index_data = {
        "latest_date": date,
        "updated_at": datetime.now().isoformat() + "Z",
        "dates": existing_dates,  # 保留所有日期
        "items": items
    }
    
    index_file = os.path.join(OUTPUT_DIR, "index.json")
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)
    
    # 同步到 data 目录
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    os.makedirs(data_dir, exist_ok=True)
    
    with open(os.path.join(data_dir, f"{date}.json"), 'w', encoding='utf-8') as f:
        json.dump(daily_data, f, ensure_ascii=False, indent=2)
    
    with open(os.path.join(data_dir, "index.json"), 'w', encoding='utf-8') as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 数据已保存到：")
    print(f"   - {daily_file}")
    print(f"   - {index_file}")


# ==================== 主流程 ====================

def main():
    """主函数：执行完整的采集流程"""
    print("🚀 开始采集 AI 每日新闻...\n")
    
    all_news = []
    
    # 1. 从 RSS 源抓取
    print("=" * 50)
    print("📡 阶段 1: RSS 抓取")
    print("=" * 50)
    
    for feed_info in RSS_FEEDS:
        news = fetch_from_rss(feed_info)
        all_news.extend(news)
    
    # 2. 从网页抓取
    print("\n" + "=" * 50)
    print("🕷️ 阶段 2: 网页爬取")
    print("=" * 50)
    
    for source_info in WEB_SOURCES:
        news = fetch_from_web(source_info)
        all_news.extend(news)
    
    # 3. 去重
    print("\n" + "=" * 50)
    print("🔄 阶段 3: 去重")
    print("=" * 50)
    
    unique_news = deduplicate_news(all_news)
    print(f"原始：{len(all_news)} 条 → 去重后：{len(unique_news)} 条")
    
    # 4. 保存数据（包含调用 DeepSeek 生成摘要）
    print("\n" + "=" * 50)
    print("📝 阶段 4: 生成摘要并保存")
    print("=" * 50)
    
    date = datetime.now().strftime("%Y-%m-%d")
    save_daily_data(unique_news, date)
    
    # 5. 完成
    print("\n" + "=" * 50)
    print("✅ 采集完成！")
    print("=" * 50)
    print(f"\n📊 统计：")
    print(f"   - 共采集：{len(unique_news)} 条新闻")
    print(f"   - 日期：{date}")
    print(f"   - 本地预览：http://localhost:8000/docs/")


if __name__ == "__main__":
    main()
