#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI Daily Skill 流水线执行脚本

这个脚本实现了 SKILL.md 中定义的完整 8 步流水线：
1. Fetch（采集）- 从信息源采集内容
2. Filter（过滤）- 过滤低质量和无关内容
3. Dedup（去重）- 语义去重，合并同源报道
4. Verify（验证）- 验证信息真实性
5. Summarize（摘要）- 生成中英文摘要
6. Tag（打标签）- 自动分类打标签
7. Score（评分）- 重要性评分（1-5 分）
8. Write（写入）- 写入 JSON 文件并更新索引

使用方式：
    python3 scripts/skill_pipeline.py --date 2026-03-29
    python3 scripts/skill_pipeline.py --today
"""

import os
import sys
import json
import hashlib
import argparse
import feedparser
import requests
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup

# ==================== 配置 ====================

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DOCS_DATA_DIR = PROJECT_ROOT / "docs" / "data"

# 确保输出目录存在
DATA_DIR.mkdir(exist_ok=True)
DOCS_DATA_DIR.mkdir(exist_ok=True)

# RSS 源列表（与 sources.md 保持一致）
RSS_FEEDS = [
    {
        "name": "OpenAI Blog",
        "url": "https://openai.com/blog/rss.xml",
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
        "name": "TechCrunch AI",
        "url": "https://techcrunch.com/category/artificial-intelligence/feed/",
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

# 标签分类
TAG_CATEGORIES = [
    "模型发布", "产品更新", "融资并购", "研究论文",
    "行业合作", "政策法规", "Agent 编程", "多模态",
    "机器人", "评测基准"
]

# ==================== 工具函数 ====================

def generate_id(url):
    """从 URL 生成 8 位十六进制 ID"""
    return f"{hash(url) & 0xFFFFFFFF:08x}"

def is_same_date(date_str, target_date):
    """检查日期字符串是否与目标日期匹配"""
    try:
        clean_date = date_str.replace(' GMT', '').replace(' UTC', '').replace(' +0000', '').strip()
        date_formats = [
            "%Y-%m-%d", "%Y/%m/%d %H:%M", "%a, %d %b %Y %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S"
        ]
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(clean_date, fmt)
                return parsed_date.strftime("%Y-%m-%d") == target_date
            except (ValueError, IndexError):
                continue
        return target_date in date_str
    except Exception:
        return False

def clean_html(html):
    """清理 HTML 标签"""
    if not html:
        return ""
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(strip=True)

# ==================== 第 1 步：Fetch（采集） ====================

def step_fetch(target_date):
    """从信息源采集内容"""
    print("=" * 60)
    print("📡 第 1 步：Fetch（采集）")
    print("=" * 60)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/rss+xml, application/xml, text/xml, */*"
    }

    raw_items = []

    for feed_info in RSS_FEEDS:
        try:
            print(f"  抓取: {feed_info['name']}...")
            response = requests.get(feed_info['url'], headers=headers, timeout=10)
            feed = feedparser.parse(response.content)

            news_count = 0
            for entry in feed.entries:
                published_at = entry.get('published', datetime.now().isoformat())

                if not is_same_date(published_at, target_date):
                    continue

                content = entry.get('summary', entry.title)
                content = clean_html(content)

                news = {
                    "title": entry.title,
                    "url": entry.link,
                    "content": content,
                    "published_at": published_at,
                    "source_name": feed_info['name'],
                    "source_type": feed_info['type'],
                    "language": feed_info['language']
                }
                raw_items.append(news)
                news_count += 1

                if news_count >= 5:
                    break

            print(f"    ✅ 获取 {news_count} 条新闻")

        except Exception as e:
            print(f"    ❌ 错误: {e}")

    print(f"\n  总计: {len(raw_items)} 条原始新闻\n")
    return raw_items

# ==================== 第 2 步：Filter（过滤） ====================

def step_filter(raw_items):
    """过滤低质量和无关内容"""
    print("=" * 60)
    print("🔍 第 2 步：Filter（过滤）")
    print("=" * 60)

    filtered_items = []
    excluded_count = 0

    for item in raw_items:
        title = item['title'].lower()
        content = item['content'].lower()

        # 过滤规则 1：排除标题党
        if title.count('!') >= 3 or '震惊' in title or '惊呆' in title:
            excluded_count += 1
            continue

        # 过滤规则 2：排除广告
        if '广告' in title or '推广' in title or 'sponsored' in title:
            excluded_count += 1
            continue

        # 过滤规则 3：检查 AI 相关性
        ai_keywords = ['ai', 'artificial intelligence', '人工智能', '模型', 'model', 'llm', 'gpt', 'claude', 'gemini']
        has_ai = any(keyword in title or keyword in content for keyword in ai_keywords)

        if not has_ai and item['source_type'] not in ['official']:
            excluded_count += 1
            continue

        filtered_items.append(item)

    print(f"  原始: {len(raw_items)} 条")
    print(f"  过滤后: {len(filtered_items)} 条")
    print(f"  排除: {excluded_count} 条\n")

    return filtered_items

# ==================== 第 3 步：Dedup（去重） ====================

def step_dedup(filtered_items):
    """语义去重，合并同源报道"""
    print("=" * 60)
    print("🔄 第 3 步：Dedup（去重）")
    print("=" * 60)

    seen_urls = set()
    seen_titles = set()
    deduped_items = []

    for item in filtered_items:
        # URL 去重
        if item['url'] in seen_urls:
            continue
        seen_urls.add(item['url'])

        # 标题去重（使用前 50 个字符）
        title_key = item['title'][:50].lower()
        if title_key in seen_titles:
            continue
        seen_titles.add(title_key)

        # 添加 merged_sources 字段
        item['merged_sources'] = []
        deduped_items.append(item)

    print(f"  去重前: {len(filtered_items)} 条")
    print(f"  去重后: {len(deduped_items)} 条\n")

    return deduped_items

# ==================== 第 4 步：Verify（验证） ====================

def step_verify(deduped_items):
    """验证信息真实性"""
    print("=" * 60)
    print("✅ 第 4 步：Verify（验证）")
    print("=" * 60)

    verified_items = []

    for item in deduped_items:
        # 来源可信度评估
        source_type = item['source_type']
        if source_type == 'official':
            confidence = 'high'
        elif source_type in ['media', 'media_cn']:
            confidence = 'medium'
        else:
            confidence = 'low'

        item['confidence'] = confidence
        verified_items.append(item)

    print(f"  验证完成: {len(verified_items)} 条\n")
    return verified_items

# ==================== 第 5 步：Summarize（摘要） ====================

def step_summarize(verified_items):
    """生成中英文摘要"""
    print("=" * 60)
    print("📝 第 5 步：Summarize（摘要）")
    print("=" * 60)

    summarized_items = []

    for item in verified_items:
        title = item['title']
        content = item['content']
        source_name = item['source_name']
        language = item['language']

        # 生成摘要（使用简单的截取方式，实际可调用 AI API）
        if len(content) > 150:
            summary = content[:150] + "..."
        else:
            summary = content

        # 构建摘要格式："来源：核心内容..."
        summary_zh = f"{source_name}：{summary}"

        if language == 'en':
            # 英文条目需要双语摘要
            item['title_en'] = title
            item['title_zh'] = title  # TODO: 可调用翻译 API
            item['summary_zh'] = summary_zh
            item['summary_en'] = f"Source: {summary}"
        else:
            # 中文条目只需要中文摘要
            item['title_zh'] = title
            item['summary_zh'] = summary_zh

        summarized_items.append(item)
        print(f"  ✅ 生成摘要: {title[:30]}...")

    print(f"\n  摘要生成完成: {len(summarized_items)} 条\n")
    return summarized_items

# ==================== 第 6 步：Tag（打标签） ====================

def step_tag(summarized_items):
    """自动分类打标签"""
    print("=" * 60)
    print("🏷️ 第 6 步：Tag（打标签）")
    print("=" * 60)

    tagged_items = []

    for item in summarized_items:
        title = item['title'].lower()
        content = item['content'].lower()

        tags = [item['source_name']]  # 来源标签

        # 根据关键词自动分类
        if '发布' in title or 'release' in title or 'launch' in title:
            tags.append('产品发布')
        elif '融资' in title or 'fund' in title or 'investment' in title:
            tags.append('融资并购')
        elif '论文' in title or 'paper' in title or 'arxiv' in title:
            tags.append('研究论文')
        elif '合作' in title or 'partnership' in title:
            tags.append('行业合作')
        elif 'agent' in title:
            tags.append('Agent 编程')
        elif '多模态' in title or 'multimodal' in title:
            tags.append('多模态')
        elif '机器人' in title or 'robot' in title:
            tags.append('机器人')

        item['tags'] = tags
        tagged_items.append(item)
        print(f"  ✅ 标签: {title[:30]}... -> {tags}")

    print(f"\n  标签完成: {len(tagged_items)} 条\n")
    return tagged_items

# ==================== 第 7 步：Score（评分） ====================

def step_score(tagged_items):
    """重要性评分（1-5 分）"""
    print("=" * 60)
    print("⭐ 第 7 步：Score（评分）")
    print("=" * 60)

    scored_items = []

    for item in tagged_items:
        source_type = item['source_type']
        title = item['title'].lower()

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

        score = min(score, 5)  # 最高 5 分
        item['importance'] = score
        scored_items.append(item)
        print(f"  ✅ 评分: {title[:30]}... -> {score} 分")

    print(f"\n  评分完成: {len(scored_items)} 条\n")
    return scored_items

# ==================== 第 8 步：Write（写入） ====================

def step_write(scored_items, target_date):
    """写入 JSON 文件并更新索引"""
    print("=" * 60)
    print("💾 第 8 步：Write（写入）")
    print("=" * 60)

    collected_at = datetime.utcnow().isoformat() + "Z"

    # 构建最终的 items 数组
    final_items = []
    for item in scored_items:
        final_item = {
            "id": generate_id(item['url']),
            "lang": item['language'],
            "tags": item['tags'],
            "source_name": item['source_name'],
            "source_url": item['url'],
            "published_at": item['published_at'],
            "collected_at": collected_at,
            "importance": item['importance'],
            "merged_sources": item.get('merged_sources', [])
        }

        if item['language'] == 'en':
            final_item['title_en'] = item.get('title_en', item['title'])
            final_item['title_zh'] = item.get('title_zh', item['title'])
            final_item['summary_en'] = item.get('summary_en', '')
            final_item['summary_zh'] = item.get('summary_zh', '')
        else:
            final_item['title_zh'] = item.get('title_zh', item['title'])
            final_item['summary_zh'] = item.get('summary_zh', '')

        final_items.append(final_item)

    # 生成每日数据文件
    daily_data = {
        "date": target_date,
        "generated_at": collected_at,
        "total_items": len(final_items),
        "items": final_items
    }

    # 写入 data/YYYY-MM-DD.json
    daily_file = DATA_DIR / f"{target_date}.json"
    with open(daily_file, 'w', encoding='utf-8') as f:
        json.dump(daily_data, f, ensure_ascii=False, indent=2)
    print(f"  ✅ 写入: {daily_file}")

    # 写入 docs/data/YYYY-MM-DD.json
    docs_daily_file = DOCS_DATA_DIR / f"{target_date}.json"
    with open(docs_daily_file, 'w', encoding='utf-8') as f:
        json.dump(daily_data, f, ensure_ascii=False, indent=2)
    print(f"  ✅ 写入: {docs_daily_file}")

    # 更新索引文件
    update_index(final_items, target_date, collected_at)

    print(f"\n  写入完成！共 {len(final_items)} 条新闻\n")
    return daily_data

def update_index(items, target_date, collected_at):
    """更新索引文件"""
    # 获取已有日期列表
    existing_dates = []
    index_file = DATA_DIR / "index.json"

    if index_file.exists():
        try:
            with open(index_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
                existing_dates = existing_data.get('dates', [])
        except:
            pass

    # 更新日期列表
    if target_date not in existing_dates:
        existing_dates.append(target_date)
    existing_dates.sort(reverse=True)

    # 生成索引数据
    index_data = {
        "latest_date": existing_dates[0] if existing_dates else target_date,
        "updated_at": collected_at,
        "dates": existing_dates,
        "items": items
    }

    # 写入 data/index.json
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)
    print(f"  ✅ 更新索引: {index_file}")

    # 写入 docs/data/index.json
    docs_index_file = DOCS_DATA_DIR / "index.json"
    with open(docs_index_file, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)
    print(f"  ✅ 更新索引: {docs_index_file}")

# ==================== 完整流水线 ====================

def run_full_pipeline(target_date):
    """运行完整的 8 步流水线"""
    print("\n" + "=" * 60)
    print("🚀 AI Daily Skill 流水线启动")
    print("=" * 60)
    print(f"📅 目标日期: {target_date}\n")

    # 执行 8 步流水线
    raw_items = step_fetch(target_date)
    if not raw_items:
        print("⚠️  没有采集到新闻，流水线结束")
        return None

    filtered_items = step_filter(raw_items)
    deduped_items = step_dedup(filtered_items)
    verified_items = step_verify(deduped_items)
    summarized_items = step_summarize(verified_items)
    tagged_items = step_tag(summarized_items)
    scored_items = step_score(tagged_items)
    result = step_write(scored_items, target_date)

    print("=" * 60)
    print("🎉 流水线执行完成！")
    print("=" * 60)
    print(f"📊 统计:")
    print(f"   - 采集: {len(raw_items)} 条")
    print(f"   - 最终: {len(scored_items)} 条")
    print(f"   - 日期: {target_date}")
    print(f"\n💡 本地预览: python3 -m http.server 8000")
    print(f"   然后访问: http://localhost:8000/docs/\n")

    return result

# ==================== 主函数 ====================

def main():
    parser = argparse.ArgumentParser(description='AI Daily Skill 流水线')
    parser.add_argument('--date', '-d', type=str, default=None,
                        help='目标日期（格式：YYYY-MM-DD）')
    parser.add_argument('--today', '-t', action='store_true',
                        help='使用今天的日期')
    parser.add_argument('--fetch-only', action='store_true',
                        help='只执行 Fetch 步骤')

    args = parser.parse_args()

    # 确定目标日期
    if args.date:
        target_date = args.date
    else:
        target_date = datetime.now().strftime("%Y-%m-%d")

    if args.fetch_only:
        # 只执行 Fetch 步骤
        raw_items = step_fetch(target_date)
        print("\n采集结果:")
        print(json.dumps(raw_items, ensure_ascii=False, indent=2))
    else:
        # 运行完整流水线
        run_full_pipeline(target_date)

if __name__ == "__main__":
    main()
