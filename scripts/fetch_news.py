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
        "name": "Anthropic",
        "url": "https://www.anthropic.com/updates/rss",
        "type": "official",
        "language": "en"
    },
    {
        "name": "Google DeepMind",
        "url": "https://deepmind.google/discover/rss/",
        "type": "official",
        "language": "en"
    },
    {
        "name": "Cursor Blog",
        "url": "https://cursor.com/blog/rss",
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
        "name": "The Verge AI",
        "url": "https://www.theverge.com/rss/ai-artificial-intelligence",
        "type": "media",
        "language": "en"
    },
    {
        "name": "MIT Tech Review AI",
        "url": "https://www.technologyreview.com/topic/artificial-intelligence/feed/",
        "type": "media",
        "language": "en"
    },
    {
        "name": "Hacker News AI",
        "url": "https://hnrss.org/frontpage?q=AI",
        "type": "community",
        "language": "en"
    },
    {
        "name": "量子位",
        "url": "https://www.qbitai.com/feed",
        "type": "media_cn",
        "language": "zh"
    },
    {
        "name": "InfoQ AI",
        "url": "https://www.infoq.cn/feed.xml",
        "type": "media_cn",
        "language": "zh"
    }
]

# API 源列表（使用自定义 API 接口）
API_SOURCES = [
    {
        "name": "机器之心",
        "url": "https://www.jiqizhixin.com/api/article_library/articles.json?sort=time&page=1&per=5",
        "type": "media_cn",
        "language": "zh"
    }
]

# 网页爬虫源（需要解析 HTML）- 目前无

# 输出目录
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs", "data")


# ==================== 核心功能 ====================

def fetch_from_rss(feed_info, target_date):
    """从 RSS 源抓取指定日期的新闻"""
    print(f"📡 抓取 RSS: {feed_info['name']}")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "application/rss+xml, application/xml, text/xml, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
    }
    
    try:
        response = requests.get(feed_info['url'], headers=headers, timeout=10)
        feed = feedparser.parse(response.content)
    except Exception as e:
        print(f"  ❌ 请求失败：{e}")
        return []
    
    news_list = []
    
    for entry in feed.entries:
        # 解析发布时间
        published_at = entry.get('published', datetime.now().isoformat())
        
        # 检查是否是目标日期的新闻
        if not is_same_date(published_at, target_date):
            continue
        
        news = {
            "title": entry.title,
            "url": entry.link,
            "content": entry.get('summary', entry.title),
            "published_at": published_at,
            "source_name": feed_info['name'],
            "source_type": feed_info['type'],
            "language": feed_info['language']
        }
        news_list.append(news)
        
        if len(news_list) >= 5:  # 每个源最多抓取 5 条
            break
    
    print(f"  ✅ 获取 {len(news_list)} 条新闻")
    return news_list


def fetch_from_rss_latest(feed_info):
    """从 RSS 源抓取最新的新闻（不过滤日期）"""
    print(f"📡 抓取 RSS: {feed_info['name']}")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "application/rss+xml, application/xml, text/xml, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
    }
    
    try:
        response = requests.get(feed_info['url'], headers=headers, timeout=10)
        feed = feedparser.parse(response.content)
    except Exception as e:
        print(f"  ❌ 请求失败：{e}")
        return []
    
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


def fetch_from_api(source_info, target_date):
    """从 API 接口抓取新闻"""
    print(f"🔌 抓取 API: {source_info['name']}")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "application/json",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
    }
    
    try:
        response = requests.get(source_info['url'], headers=headers, timeout=10)
        data = response.json()
    except Exception as e:
        print(f"  ❌ 请求失败：{e}")
        return []
    
    news_list = []
    
    # 解析 API 返回的文章数据
    articles = data.get('articles', [])
    for article in articles:
        # 检查是否是目标日期的新闻
        published_at = article.get('publishedAt', '')
        if not is_same_date(published_at, target_date):
            continue
        
        # 构建文章链接
        article_url = f"https://www.jiqizhixin.com/articles/{article.get('slug', '')}"
        
        news = {
            "title": article.get('title', ''),
            "url": article_url,
            "content": article.get('content', article.get('title', '')),
            "published_at": published_at,
            "source_name": source_info['name'],
            "source_type": source_info['type'],
            "language": source_info['language']
        }
        news_list.append(news)
        
        if len(news_list) >= 5:  # 每个源最多抓取 5 条
            break
    
    print(f"  ✅ 获取 {len(news_list)} 条新闻")
    return news_list


def is_same_date(date_str, target_date):
    """检查日期字符串是否与目标日期匹配"""
    try:
        # 先清理常见的时区后缀
        clean_date = date_str.replace(' GMT', '').replace(' UTC', '').strip()
        
        # 尝试解析多种日期格式
        date_formats = [
            "%Y-%m-%d",
            "%Y/%m/%d %H:%M",
            "%a, %d %b %Y %H:%M:%S",  # 不含时区
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S"
        ]
        
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(clean_date[:len(fmt)], fmt)
                result = parsed_date.strftime("%Y-%m-%d") == target_date
                return result
            except (ValueError, IndexError):
                continue
        
        # 如果都失败，检查字符串是否包含目标日期
        return target_date in date_str
        
    except Exception:
        return False


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
    
    # 获取目标日期（默认为今天）
    target_date = datetime.now().strftime("%Y-%m-%d")
    print(f"📅 采集日期：{target_date}\n")
    
    all_news = []
    
    # 1. 从 RSS 源抓取（不过滤日期，抓取最新新闻）
    print("=" * 50)
    print("📡 阶段 1: RSS 抓取")
    print("=" * 50)
    
    for feed_info in RSS_FEEDS:
        news = fetch_from_rss_latest(feed_info)
        all_news.extend(news)
    
    # 2. 从 API 抓取（过滤日期）
    print("\n" + "=" * 50)
    print("🔌 阶段 2: API 抓取")
    print("=" * 50)
    
    for source_info in API_SOURCES:
        news = fetch_from_api(source_info, target_date)
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
    
    save_daily_data(unique_news, target_date)
    
    # 5. 完成
    print("\n" + "=" * 50)
    print("✅ 采集完成！")
    print("=" * 50)
    print(f"\n📊 统计：")
    print(f"   - 共采集：{len(unique_news)} 条新闻")
    print(f"   - 日期：{target_date}")
    print(f"   - 本地预览：http://localhost:8000/docs/")


if __name__ == "__main__":
    main()
