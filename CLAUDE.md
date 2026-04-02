# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI Daily (AI 日报) is a skill-driven news aggregation pipeline that collects, deduplicates, summarizes, and archives AI industry news into daily JSON files, served via a static GitHub Pages frontend.

There are no build tools, package managers, or test frameworks — the entire pipeline runs through Claude Code skill invocations.

## Running the Pipeline

Trigger the pipeline by saying phrases like:
- "帮我运行今天的 AI 日报流水线"
- "生成 2026-04-02 的日报数据"
- "run the pipeline"

The skill definition is at `skills/ai-daily/SKILL.md`. All detailed instructions, schemas, and prompts are under `skills/ai-daily/references/`.

## Pipeline Steps

1. **Fetch** — Collect from sources via curl/RSS, or web search fallback
2. **Filter** — Remove ads, job posts, off-topic content
3. **Semantic Dedup** — Merge same-event articles, keep highest-tier source as primary
4. **Time Verify** — Extract `published_at` from HTML meta/RSS; null if unverifiable
5. **Summarize** — Generate bilingual EN/ZH summaries (≤200 words/字)
6. **Tag** — Assign 1–3 tags from the taxonomy in `references/schema.md`
7. **Score** — Importance 1–5
8. **Write JSON** — Append to `data/YYYY-MM-DD.json`, sync to `docs/data/`, rebuild `index.json`

## Data Architecture

- `data/YYYY-MM-DD.json` — Primary daily archive (one file per day)
- `data/index.json` — Index with `latest_date`, `dates[]`, and copy of latest daily items
- `docs/data/` — Mirror of `data/` for GitHub Pages (must stay in sync)

## Git Workflow (Post-Pipeline)

```bash
git add data/ docs/data/
git commit -m "feat: add YYYY-MM-DD AI daily pipeline output (N items)"
git push
```
