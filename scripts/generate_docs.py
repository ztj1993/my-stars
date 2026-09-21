#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate Markdown documentation and an interactive HTML web dashboard
from data/enriched_stars.json.
"""

import os
import sys
import json
import collections
from datetime import datetime

# Ensure UTF-8 output on Windows terminal
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENRICHED_FILE = os.path.join(BASE_DIR, "data", "enriched_stars.json")
DOCS_DIR = os.path.join(BASE_DIR, "docs")
CAT_DOCS_DIR = os.path.join(DOCS_DIR, "categories")
LANG_DOCS_DIR = os.path.join(DOCS_DIR, "languages")
README_FILE = os.path.join(BASE_DIR, "README.md")
HTML_FILE = os.path.join(BASE_DIR, "index.html")

CATEGORY_SLUGS = {
    "AI 与大模型": "ai-llm",
    "前端与跨端开发": "frontend",
    "后端架构与微服务": "backend",
    "DevOps 与云原生": "devops",
    "效率工具与 CLI": "cli-tools",
    "数据处理与爬虫": "data-scraping",
    "数据库与存储": "database",
    "网络安全与逆向": "security",
    "影音多媒体与图形": "media",
    "资源精选与学习指南": "learning-resources"
}


def load_data():
    with open(ENRICHED_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def render_project_markdown_item(item: dict, index: int) -> str:
    name = item["name"]
    full_name = item["full_name"]
    url = item["html_url"]
    stars = item["stars"]
    lang = item["language"] or "Unknown"
    summary = item["summary_zh"]
    tags = item["tags"]
    features = item["features_zh"]
    tag_badges = " ".join([f"`{t}`" for t in tags])

    features_md = "\n".join([f"  - {f}" for f in features])

    md = f"""### {index}. [{full_name}]({url})
- **⭐ Stars**: `{stars:,}` | **语言**: `{lang}` | **标签**: {tag_badges}
- **📝 中文介绍**: {summary}
- **✨ 核心功能与亮点**:
{features_md}
"""
    return md


def generate_category_docs(stars: list):
    os.makedirs(CAT_DOCS_DIR, exist_ok=True)
    cats_grouped = collections.defaultdict(list)
    for s in stars:
        cats_grouped[s["category"]].append(s)

    for cat_name, items in cats_grouped.items():
        slug = CATEGORY_SLUGS.get(cat_name, "misc")
        icon = items[0]["category_icon"] if items else "📦"
        filename = os.path.join(CAT_DOCS_DIR, f"{slug}.md")
        
        # Sort by stars descending
        sorted_items = sorted(items, key=lambda x: x["stars"], reverse=True)

        lines = [
            f"# {icon} {cat_name} ({len(items)} 个项目)",
            "",
            f"> 本文档收录了 `ztj1993` 在 **{cat_name}** 领域的精选 Star 项目，按 Star 数量降序排列。",
            "",
            "[← 返回项目总览](../../README.md)",
            "",
            "---",
            ""
        ]

        for i, item in enumerate(sorted_items, 1):
            lines.append(render_project_markdown_item(item, i))

        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(f"Generated category doc: {filename} ({len(items)} projects)")


def generate_main_readme(stars: list):
    total_stars = len(stars)
    update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Category stats
    cat_counts = collections.Counter(s["category"] for s in stars)
    lang_counts = collections.Counter(s["language"] for s in stars)

    # Top 15 high star projects
    top_starred = sorted(stars, key=lambda x: x["stars"], reverse=True)[:15]

    lines = [
        "# 🌟 My GitHub Stars 知识库",
        "",
        f"[![Total Stars](https://img.shields.io/badge/Total_Stars-{total_stars}-blue.svg?style=for-the-badge&logo=github)](https://github.com/ztj1993?tab=stars)",
        f"[![Categories](https://img.shields.io/badge/Categories-10_Domains-brightgreen.svg?style=for-the-badge)](./docs/categories/)",
        f"[![Last Updated](https://img.shields.io/badge/Updated-{update_time[:10]}-orange.svg?style=for-the-badge)](#)",
        f"[![Interactive Web UI](https://img.shields.io/badge/Web_Dashboard-Open_HTML-purple.svg?style=for-the-badge)](./index.html)",
        "",
        "> 💡 本仓库为 GitHub 用户 [`ztj1993`](https://github.com/ztj1993) 的全部 Star 仓库精选知识库。包含 **全量数据提取、10 大功能领域智能归类、技术栈多维标签标注与中文核心功能深度介绍**。",
        "",
        "🔗 **快速入口**：",
        "- 🖥️ **[打开交互式 Web 搜索看板 (index.html)](./index.html)**（支持全局实时秒搜、多标签组合过滤、图表统计、卡片/表格双视图）",
        "- 📁 **[浏览各领域分册文档目录](./docs/categories/)**",
        "",
        "---",
        "",
        "## 📊 领域分类导航 (Categories)",
        "",
        "| 分类领域 | 项目数量 | 占比 | 专题文档入口 |",
        "| :--- | :---: | :---: | :--- |"
    ]

    for cat_name, slug in CATEGORY_SLUGS.items():
        count = cat_counts.get(cat_name, 0)
        pct = (count / total_stars * 100) if total_stars else 0
        icon = next((s["category_icon"] for s in stars if s["category"] == cat_name), "📦")
        lines.append(f"| {icon} **{cat_name}** | `{count}` 个 | `{pct:.1f}%` | [📖 查看《{cat_name}》专题文档](./docs/categories/{slug}.md) |")

    lines.extend([
        "",
        "---",
        "",
        "## 💻 主要编程语言分布 (Top Languages)",
        "",
        "| 编程语言 | 项目数量 | 占比 |",
        "| :--- | :---: | :---: |"
    ])

    for lang, count in lang_counts.most_common(10):
        pct = (count / total_stars * 100) if total_stars else 0
        lines.append(f"| **{lang}** | `{count}` 个 | `{pct:.1f}%` |")

    lines.extend([
        "",
        "---",
        "",
        "## 🏆 热门高星标杆项目精选 (Top Starred Projects)",
        ""
    ])

    for i, item in enumerate(top_starred, 1):
        lines.append(render_project_markdown_item(item, i))

    lines.extend([
        "",
        "---",
        "",
        "## 🛠️ 项目自动化与更新机制",
        "",
        "- 本知识库基于 Python 自动化流水线构建：",
        "  - 数据抓取：`scripts/fetch_stars.py`",
        "  - 智能解析与中文摘要：`scripts/enrich_stars.py`",
        "  - 知识库与 Web 看板生成：`scripts/generate_docs.py`",
        "- 支持通过 GitHub Actions（`.github/workflows/update-stars.yml`）定时或手动一键同步最新 Stars。",
        "",
        f"<sub>*知识库构建时间: {update_time}*</sub>"
    ])

    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Generated main README.md: {README_FILE}")


def generate_web_dashboard(stars: list):
    """Generate a single-file interactive Web UI dashboard with real-time search, filters, and stats."""
    json_payload = json.dumps(stars, ensure_ascii=False)
    
    html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ztj1993 - GitHub Stars 知识库看板</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <script>
    tailwind.config = {{
      darkMode: 'class',
      theme: {{
        extend: {{
          colors: {{
            brand: {{
              50: '#f0f9ff',
              100: '#e0f2fe',
              500: '#0ea5e9',
              600: '#0284c7',
              700: '#0369a1',
            }}
          }}
        }}
      }}
    }}
  </script>
  <style>
    [x-cloak] {{ display: none !important; }}
    ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
    ::-webkit-scrollbar-thumb {{ background: #cbd5e1; border-radius: 3px; }}
    .dark ::-webkit-scrollbar-thumb {{ background: #475569; }}
  </style>
</head>
<body class="bg-slate-50 dark:bg-slate-900 text-slate-800 dark:text-slate-100 min-h-screen transition-colors duration-200"
      x-data="starsApp()" x-cloak>

  <!-- Navigation Header -->
  <header class="sticky top-0 z-30 backdrop-blur-md bg-white/80 dark:bg-slate-900/80 border-b border-slate-200 dark:border-slate-800 transition-colors">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
      <div class="flex items-center justify-between gap-4">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-sky-500 to-indigo-600 flex items-center justify-center text-white shadow-lg shadow-sky-500/20 font-bold text-lg">
            ★
          </div>
          <div>
            <h1 class="text-lg font-bold tracking-tight bg-gradient-to-r from-slate-900 to-slate-700 dark:from-white dark:to-slate-300 bg-clip-text text-transparent">
              GitHub Stars 知识库
            </h1>
            <p class="text-xs text-slate-500 dark:text-slate-400">
              User: <span class="font-semibold text-sky-600 dark:text-sky-400">ztj1993</span> • <span x-text="allStars.length"></span> 个项目
            </p>
          </div>
        </div>

        <!-- Global Search Bar -->
        <div class="flex-1 max-w-xl relative">
          <i class="fa-solid fa-magnifying-glass absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 text-sm"></i>
          <input 
            type="text" 
            x-model="searchQuery" 
            placeholder="搜索项目名称、中文功能概括、亮点特性、标签、语言..."
            class="w-full pl-10 pr-10 py-2 text-sm bg-slate-100 dark:bg-slate-800 border-none rounded-xl focus:ring-2 focus:ring-sky-500 outline-none transition-all placeholder-slate-400 text-slate-900 dark:text-white"
          >
          <button 
            x-show="searchQuery" 
            @click="searchQuery = ''"
            class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200">
            <i class="fa-solid fa-xmark text-sm"></i>
          </button>
        </div>

        <!-- Controls -->
        <div class="flex items-center gap-2">
          <!-- View Toggle -->
          <div class="flex bg-slate-100 dark:bg-slate-800 p-1 rounded-xl">
            <button 
              @click="viewMode = 'grid'" 
              :class="viewMode === 'grid' ? 'bg-white dark:bg-slate-700 shadow-sm text-sky-600 dark:text-sky-400' : 'text-slate-500 hover:text-slate-700'"
              class="px-2.5 py-1 text-xs rounded-lg font-medium transition-all"
              title="卡片视图">
              <i class="fa-solid fa-grip"></i>
            </button>
            <button 
              @click="viewMode = 'table'" 
              :class="viewMode === 'table' ? 'bg-white dark:bg-slate-700 shadow-sm text-sky-600 dark:text-sky-400' : 'text-slate-500 hover:text-slate-700'"
              class="px-2.5 py-1 text-xs rounded-lg font-medium transition-all"
              title="表格视图">
              <i class="fa-solid fa-list"></i>
            </button>
          </div>

          <!-- Theme Toggle -->
          <button 
            @click="toggleTheme()" 
            class="p-2 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors">
            <i :class="isDark ? 'fa-solid fa-sun text-amber-400' : 'fa-solid fa-moon text-indigo-500'"></i>
          </button>

          <!-- GitHub Link -->
          <a href="https://github.com/ztj1993?tab=stars" target="_blank" 
             class="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-900 text-white dark:bg-white dark:text-slate-900 text-xs font-semibold hover:opacity-90 transition-opacity">
            <i class="fa-brands fa-github text-sm"></i>
            <span>GitHub</span>
          </a>
        </div>
      </div>
    </div>

    <!-- Category Filter Bar -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-3 overflow-x-auto no-scrollbar">
      <div class="flex items-center gap-1.5 min-w-max">
        <button 
          @click="selectedCategory = 'all'"
          :class="selectedCategory === 'all' ? 'bg-sky-600 text-white shadow-md shadow-sky-500/20' : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700'"
          class="px-3 py-1.5 rounded-lg text-xs font-medium transition-all flex items-center gap-1.5">
          <span>🌟 全部</span>
          <span class="px-1.5 py-0.2 rounded-full text-[10px]" :class="selectedCategory === 'all' ? 'bg-white/20 text-white' : 'bg-slate-200 dark:bg-slate-700 text-slate-500'" x-text="allStars.length"></span>
        </button>

        <template x-for="cat in categoryList" :key="cat.name">
          <button 
            @click="selectedCategory = cat.name"
            :class="selectedCategory === cat.name ? 'bg-sky-600 text-white shadow-md shadow-sky-500/20' : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700'"
            class="px-3 py-1.5 rounded-lg text-xs font-medium transition-all flex items-center gap-1.5">
            <span x-text="cat.icon + ' ' + cat.name"></span>
            <span class="px-1.5 py-0.2 rounded-full text-[10px]" :class="selectedCategory === cat.name ? 'bg-white/20 text-white' : 'bg-slate-200 dark:bg-slate-700 text-slate-500'" x-text="cat.count"></span>
          </button>
        </template>
      </div>
    </div>
  </header>

  <!-- Main Container -->
  <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">

    <!-- Secondary Filters & Sort Bar -->
    <div class="bg-white dark:bg-slate-800/80 rounded-2xl p-4 border border-slate-200/80 dark:border-slate-800 shadow-sm mb-6 space-y-3">
      <div class="flex flex-wrap items-center justify-between gap-4">
        <!-- Languages Filter -->
        <div class="flex flex-wrap items-center gap-1.5">
          <span class="text-xs font-medium text-slate-400 mr-1"><i class="fa-solid fa-code mr-1"></i>编程语言:</span>
          <button 
            @click="selectedLanguage = 'all'"
            :class="selectedLanguage === 'all' ? 'bg-slate-900 text-white dark:bg-white dark:text-slate-900' : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200'"
            class="px-2.5 py-1 rounded-md text-xs font-medium transition-all">
            全部
          </button>
          <template x-for="lang in topLanguages" :key="lang.name">
            <button 
              @click="selectedLanguage = lang.name"
              :class="selectedLanguage === lang.name ? 'bg-slate-900 text-white dark:bg-white dark:text-slate-900' : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200'"
              class="px-2.5 py-1 rounded-md text-xs font-medium transition-all flex items-center gap-1">
              <span x-text="lang.name"></span>
              <span class="text-[10px] opacity-70" x-text="'(' + lang.count + ')'"></span>
            </button>
          </template>
        </div>

        <!-- Sort Select -->
        <div class="flex items-center gap-2 ml-auto">
          <span class="text-xs text-slate-400 font-medium"><i class="fa-solid fa-arrow-down-short-wide mr-1"></i>排序:</span>
          <select 
            x-model="sortBy"
            class="bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-200 text-xs rounded-lg px-2.5 py-1.5 border-none outline-none focus:ring-1 focus:ring-sky-500 font-medium cursor-pointer">
            <option value="stars_desc">⭐ Star 数 (从高到低)</option>
            <option value="stars_asc">⭐ Star 数 (从低到高)</option>
            <option value="starred_desc">🕒 Star 时间 (最新优先)</option>
            <option value="updated_desc">🔄 仓库更新 (最新优先)</option>
            <option value="name_asc">🔤 项目名称 (A-Z)</option>
          </select>
        </div>
      </div>

      <!-- Result Count Info -->
      <div class="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400 border-t border-slate-100 dark:border-slate-700/50 pt-2.5">
        <div>
          共匹配到 <span class="font-bold text-sky-600 dark:text-sky-400" x-text="filteredStars.length"></span> 个项目
          <span x-show="selectedCategory !== 'all'" x-text="' / 所选分类: ' + selectedCategory"></span>
          <span x-show="selectedLanguage !== 'all'" x-text="' / 所选语言: ' + selectedLanguage"></span>
          <span x-show="searchQuery" x-text="' / 包含搜索词: \\'' + searchQuery + '\\''"></span>
        </div>
        <button 
          x-show="selectedCategory !== 'all' || selectedLanguage !== 'all' || searchQuery"
          @click="resetFilters()"
          class="text-sky-600 dark:text-sky-400 hover:underline font-medium">
          <i class="fa-solid fa-rotate-left mr-1"></i>重置所有筛选
        </button>
      </div>
    </div>

    <!-- Empty State -->
    <div x-show="filteredStars.length === 0" class="text-center py-16 bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700">
      <i class="fa-regular fa-folder-open text-5xl text-slate-300 dark:text-slate-600 mb-3"></i>
      <h3 class="text-base font-semibold text-slate-700 dark:text-slate-300">没有找到匹配的项目</h3>
      <p class="text-xs text-slate-400 mt-1">请尝试更换关键词或重置筛选条件</p>
      <button @click="resetFilters()" class="mt-4 px-4 py-2 bg-sky-600 text-white text-xs font-semibold rounded-xl hover:bg-sky-700 transition-colors">
        重置筛选
      </button>
    </div>

    <!-- Grid View -->
    <div x-show="viewMode === 'grid' && filteredStars.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
      <template x-for="item in pagedStars" :key="item.id">
        <div class="bg-white dark:bg-slate-800/90 rounded-2xl p-5 border border-slate-200/80 dark:border-slate-700/70 hover:border-sky-400 dark:hover:border-sky-500 shadow-sm hover:shadow-lg hover:shadow-sky-500/5 transition-all flex flex-col justify-between group">
          
          <div>
            <!-- Card Header -->
            <div class="flex items-start justify-between gap-3 mb-2.5">
              <div class="flex items-center gap-2 flex-1 min-w-0">
                <span class="text-lg" x-text="item.category_icon"></span>
                <a :href="item.html_url" target="_blank" 
                   class="text-sm font-bold text-slate-900 dark:text-white hover:text-sky-600 dark:hover:text-sky-400 truncate transition-colors"
                   :title="item.full_name"
                   x-text="item.full_name">
                </a>
              </div>
              <div class="flex items-center gap-1 text-amber-500 font-bold text-xs bg-amber-50 dark:bg-amber-950/40 px-2 py-0.5 rounded-full border border-amber-200 dark:border-amber-800">
                <i class="fa-solid fa-star text-[10px]"></i>
                <span x-text="formatStars(item.stars)"></span>
              </div>
            </div>

            <!-- Chinese Summary -->
            <p class="text-xs text-slate-600 dark:text-slate-300 line-clamp-2 leading-relaxed mb-3 font-normal" x-text="item.summary_zh"></p>

            <!-- Key Features Collapsible / Highlights -->
            <div class="bg-slate-50 dark:bg-slate-900/60 rounded-xl p-2.5 mb-3 border border-slate-100 dark:border-slate-800 text-[11px] space-y-1.5">
              <template x-for="(feat, idx) in item.features_zh" :key="idx">
                <div class="flex items-start gap-1.5 text-slate-600 dark:text-slate-300">
                  <span class="text-sky-500 mt-0.5">•</span>
                  <span class="leading-tight" x-text="feat"></span>
                </div>
              </template>
            </div>
          </div>

          <!-- Card Footer (Tags & Meta) -->
          <div>
            <!-- Tags -->
            <div class="flex flex-wrap gap-1 mb-3">
              <span class="px-2 py-0.5 bg-sky-50 dark:bg-sky-950/60 text-sky-600 dark:text-sky-300 rounded-md text-[10px] font-semibold border border-sky-100 dark:border-sky-900" x-text="item.language || 'Unknown'"></span>
              <template x-for="tag in item.tags.slice(1, 4)" :key="tag">
                <span class="px-1.5 py-0.5 bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 rounded text-[10px]" x-text="tag"></span>
              </template>
            </div>

            <div class="flex items-center justify-between pt-2 border-t border-slate-100 dark:border-slate-700/60 text-[11px] text-slate-400">
              <span class="text-[10px]" x-text="'分类: ' + item.category"></span>
              <div class="flex items-center gap-2">
                <a x-show="item.homepage" :href="item.homepage" target="_blank" class="hover:text-sky-500 transition-colors" title="官网/Demo">
                  <i class="fa-solid fa-link"></i>
                </a>
                <a :href="item.html_url" target="_blank" class="hover:text-sky-500 transition-colors" title="打开 GitHub">
                  <i class="fa-brands fa-github text-xs"></i>
                </a>
              </div>
            </div>
          </div>

        </div>
      </template>
    </div>

    <!-- Table View -->
    <div x-show="viewMode === 'table' && filteredStars.length > 0" class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200/80 dark:border-slate-700 overflow-hidden shadow-sm">
      <div class="overflow-x-auto">
        <table class="w-full text-left text-xs text-slate-600 dark:text-slate-300">
          <thead class="bg-slate-50 dark:bg-slate-900/60 text-slate-700 dark:text-slate-200 font-semibold border-b border-slate-200 dark:border-slate-700">
            <tr>
              <th class="py-3 px-4">项目仓库</th>
              <th class="py-3 px-3">领域分类</th>
              <th class="py-3 px-3">主要语言</th>
              <th class="py-3 px-3">Star 数</th>
              <th class="py-3 px-4">中文定位与功能亮点</th>
              <th class="py-3 px-3 text-right">操作</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 dark:divide-slate-700/50">
            <template x-for="item in pagedStars" :key="item.id">
              <tr class="hover:bg-slate-50/80 dark:hover:bg-slate-700/40 transition-colors">
                <td class="py-3 px-4 font-bold text-slate-900 dark:text-white whitespace-nowrap">
                  <div class="flex items-center gap-1.5">
                    <span x-text="item.category_icon"></span>
                    <a :href="item.html_url" target="_blank" class="hover:text-sky-500 transition-colors" x-text="item.full_name"></a>
                  </div>
                </td>
                <td class="py-3 px-3 whitespace-nowrap">
                  <span class="px-2 py-0.5 rounded-full text-[10px] bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 font-medium" x-text="item.category"></span>
                </td>
                <td class="py-3 px-3 whitespace-nowrap">
                  <span class="font-semibold text-sky-600 dark:text-sky-400" x-text="item.language || '-'"></span>
                </td>
                <td class="py-3 px-3 whitespace-nowrap font-bold text-amber-500">
                  ★ <span x-text="item.stars.toLocaleString()"></span>
                </td>
                <td class="py-3 px-4 max-w-md">
                  <div class="font-medium text-slate-800 dark:text-slate-200 line-clamp-1 mb-1" x-text="item.summary_zh"></div>
                  <div class="text-[10px] text-slate-400 line-clamp-1" x-text="item.features_zh.join('；')"></div>
                </td>
                <td class="py-3 px-3 text-right whitespace-nowrap">
                  <a :href="item.html_url" target="_blank" class="p-1.5 rounded-lg bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 hover:text-sky-500 transition-colors inline-block">
                    <i class="fa-brands fa-github"></i>
                  </a>
                </td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Pagination Controls -->
    <div x-show="totalPages > 1" class="mt-8 flex items-center justify-between border-t border-slate-200 dark:border-slate-800 pt-4">
      <div class="text-xs text-slate-500 dark:text-slate-400">
        显示第 <span class="font-semibold" x-text="(currentPage - 1) * pageSize + 1"></span> 到 <span class="font-semibold" x-text="Math.min(currentPage * pageSize, filteredStars.length)"></span> 条，共 <span class="font-semibold" x-text="filteredStars.length"></span> 条
      </div>
      <div class="flex items-center gap-1.5">
        <button 
          @click="currentPage = Math.max(1, currentPage - 1)" 
          :disabled="currentPage === 1"
          class="px-3 py-1.5 rounded-lg bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-xs font-semibold disabled:opacity-40 hover:bg-slate-50 transition-all">
          <i class="fa-solid fa-chevron-left mr-1"></i>上一页
        </button>
        <span class="px-3 py-1.5 text-xs font-semibold text-slate-600 dark:text-slate-300" x-text="currentPage + ' / ' + totalPages"></span>
        <button 
          @click="currentPage = Math.min(totalPages, currentPage + 1)" 
          :disabled="currentPage === totalPages"
          class="px-3 py-1.5 rounded-lg bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-xs font-semibold disabled:opacity-40 hover:bg-slate-50 transition-all">
          下一页<i class="fa-solid fa-chevron-right ml-1"></i>
        </button>
      </div>
    </div>

  </main>

  <footer class="mt-12 py-6 border-t border-slate-200 dark:border-slate-800 text-center text-xs text-slate-400">
    <p>Generated for <a href="https://github.com/ztj1993" target="_blank" class="text-sky-500 font-semibold hover:underline">@ztj1993</a> • Powered by Antigravity Python Pipeline</p>
  </footer>

  <script>
    const RAW_STARS_DATA = {json_payload};

    function starsApp() {{
      return {{
        allStars: RAW_STARS_DATA,
        searchQuery: '',
        selectedCategory: 'all',
        selectedLanguage: 'all',
        sortBy: 'stars_desc',
        viewMode: 'grid',
        currentPage: 1,
        pageSize: 48,
        isDark: window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches,

        init() {{
          if (this.isDark) {{
            document.documentElement.classList.add('dark');
          }}
          this.$watch('searchQuery', () => {{ this.currentPage = 1; }});
          this.$watch('selectedCategory', () => {{ this.currentPage = 1; }});
          this.$watch('selectedLanguage', () => {{ this.currentPage = 1; }});
          this.$watch('sortBy', () => {{ this.currentPage = 1; }});
        }},

        toggleTheme() {{
          this.isDark = !this.isDark;
          if (this.isDark) {{
            document.documentElement.classList.add('dark');
          }} else {{
            document.documentElement.classList.remove('dark');
          }}
        }},

        resetFilters() {{
          this.searchQuery = '';
          this.selectedCategory = 'all';
          this.selectedLanguage = 'all';
          this.sortBy = 'stars_desc';
          this.currentPage = 1;
        }},

        formatStars(num) {{
          if (num >= 1000) {{
            return (num / 1000).toFixed(1) + 'k';
          }}
          return num;
        }},

        get categoryList() {{
          const counts = {{}};
          const icons = {{}};
          this.allStars.forEach(s => {{
            counts[s.category] = (counts[s.category] || 0) + 1;
            icons[s.category] = s.category_icon;
          }});
          return Object.keys(counts).map(name => ({{
            name: name,
            count: counts[name],
            icon: icons[name] || '📦'
          }})).sort((a, b) => b.count - a.count);
        }},

        get topLanguages() {{
          const counts = {{}};
          this.allStars.forEach(s => {{
            const l = s.language || 'Unknown';
            counts[l] = (counts[l] || 0) + 1;
          }});
          return Object.keys(counts)
            .map(name => ({{ name, count: counts[name] }}))
            .sort((a, b) => b.count - a.count)
            .slice(0, 10);
        }},

        get filteredStars() {{
          let result = this.allStars;

          // Category filter
          if (this.selectedCategory !== 'all') {{
            result = result.filter(s => s.category === this.selectedCategory);
          }}

          // Language filter
          if (this.selectedLanguage !== 'all') {{
            result = result.filter(s => (s.language || 'Unknown') === this.selectedLanguage);
          }}

          // Search query filter
          if (this.searchQuery.trim()) {{
            const q = this.searchQuery.toLowerCase().trim();
            result = result.filter(s => {{
              return (
                (s.full_name && s.full_name.toLowerCase().includes(q)) ||
                (s.summary_zh && s.summary_zh.toLowerCase().includes(q)) ||
                (s.language && s.language.toLowerCase().includes(q)) ||
                (s.tags && s.tags.some(t => t.toLowerCase().includes(q))) ||
                (s.features_zh && s.features_zh.some(f => f.toLowerCase().includes(q))) ||
                (s.raw_description && s.raw_description.toLowerCase().includes(q))
              );
            }});
          }}

          // Sorting
          if (this.sortBy === 'stars_desc') {{
            result = result.slice().sort((a, b) => (b.stars || 0) - (a.stars || 0));
          }} else if (this.sortBy === 'stars_asc') {{
            result = result.slice().sort((a, b) => (a.stars || 0) - (b.stars || 0));
          }} else if (this.sortBy === 'starred_desc') {{
            result = result.slice().sort((a, b) => (b.starred_at || '').localeCompare(a.starred_at || ''));
          }} else if (this.sortBy === 'updated_desc') {{
            result = result.slice().sort((a, b) => (b.updated_at || '').localeCompare(a.updated_at || ''));
          }} else if (this.sortBy === 'name_asc') {{
            result = result.slice().sort((a, b) => a.name.localeCompare(b.name));
          }}

          return result;
        }},

        get totalPages() {{
          return Math.ceil(this.filteredStars.length / this.pageSize) || 1;
        }},

        get pagedStars() {{
          const start = (this.currentPage - 1) * this.pageSize;
          return this.filteredStars.slice(start, start + this.pageSize);
        }}
      }};
    }}
  </script>
</body>
</html>
"""
    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Generated interactive web dashboard: {HTML_FILE}")


def main():
    stars = load_data()
    print(f"Loaded {len(stars)} enriched star items.")
    generate_category_docs(stars)
    generate_main_readme(stars)
    generate_web_dashboard(stars)
    print("\nAll documentation and Web UI generated successfully!")


if __name__ == "__main__":
    main()
