#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate Markdown documentation and an interactive HTML web dashboard
with modern Sidebar Tree navigation from data/enriched_stars.json.
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
    full_name = item["full_name"]
    url = item["html_url"]
    stars = item["stars"]
    lang = item["language"] or "Unknown"
    summary = item["summary_zh"]
    tags = item["tags"]
    features = item["features_zh"]
    subcat = item.get("subcategory", "")
    subcat_icon = item.get("subcategory_icon", "📦")
    tag_badges = " ".join([f"`{t}`" for t in tags])

    features_md = "\n".join([f"  - {f}" for f in features])

    md = f"""### {index}. [{full_name}]({url})
- **⭐ Stars**: `{stars:,}` | **二级分类**: {subcat_icon} `{subcat}` | **语言**: `{lang}`
- **🏷️ 标签**: {tag_badges}
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

        subcats = collections.defaultdict(list)
        for it in items:
            subcats[it.get("subcategory", "其他")].append(it)

        lines = [
            f"# {icon} {cat_name} ({len(items)} 个项目)",
            "",
            f"> 本文档收录了 `ztj1993` 在 **{cat_name}** 领域的精选 Star 项目，共划分 **{len(subcats)}** 个二级细分子分类。",
            "",
            "[← 返回知识库总览](../../README.md)",
            "",
            "## 📑 本专题二级分类导航",
            ""
        ]

        subcat_order = sorted(subcats.keys(), key=lambda k: len(subcats[k]), reverse=True)
        for idx, sub_name in enumerate(subcat_order, 1):
            sub_icon = subcats[sub_name][0].get("subcategory_icon", "•")
            sub_count = len(subcats[sub_name])
            lines.append(f"- [{sub_icon} **{sub_name}** ({sub_count} 个项目)](#{idx}-{sub_name})")

        lines.extend(["", "---", ""])

        for idx, sub_name in enumerate(subcat_order, 1):
            sub_items = sorted(subcats[sub_name], key=lambda x: x["stars"], reverse=True)
            sub_icon = sub_items[0].get("subcategory_icon", "📦")
            lines.extend([
                f"## {idx}. {sub_icon} {sub_name} ({len(sub_items)} 个项目)",
                ""
            ])
            for i, item in enumerate(sub_items, 1):
                lines.append(render_project_markdown_item(item, i))
            lines.append("")

        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(f"Generated category doc: {filename} ({len(items)} projects, {len(subcats)} subcategories)")


def generate_main_readme(stars: list):
    total_stars = len(stars)
    update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cat_sub_map = collections.defaultdict(lambda: collections.defaultdict(int))
    cat_counts = collections.Counter()
    lang_counts = collections.Counter()

    for s in stars:
        c = s["category"]
        sub = s.get("subcategory", "其他")
        cat_counts[c] += 1
        cat_sub_map[c][sub] += 1
        lang_counts[s["language"]] += 1

    top_starred = sorted(stars, key=lambda x: x["stars"], reverse=True)[:15]

    lines = [
        "# 🌟 My GitHub Stars 知识库",
        "",
        f"[![Total Stars](https://img.shields.io/badge/Total_Stars-{total_stars}-blue.svg?style=for-the-badge&logo=github)](https://github.com/ztj1993?tab=stars)",
        f"[![Primary Categories](https://img.shields.io/badge/Primary_Categories-10_Domains-brightgreen.svg?style=for-the-badge)](./docs/categories/)",
        f"[![Subcategories](https://img.shields.io/badge/Subcategories-35+_Classes-blueviolet.svg?style=for-the-badge)](./docs/categories/)",
        f"[![Interactive Web UI](https://img.shields.io/badge/Web_Dashboard-Open_HTML-purple.svg?style=for-the-badge)](./index.html)",
        "",
        "> 💡 本仓库为 GitHub 用户 [`ztj1993`](https://github.com/ztj1993) 的全部 Star 仓库精选知识库。包含 **全量数据提取、10 大功能领域智能归类、35+ 二级细分子类体系、技术栈多维标签标注与中文核心功能深度解析**。",
        "",
        "🔗 **快速入口**：",
        "- 🖥️ **[打开交互式 Web 搜索看板 (index.html)](./index.html)**（采用现代化左侧分栏层级树、全局实时秒搜、多标签组合筛选、卡片/表格双视图）",
        "- 📁 **[浏览各领域分册文档目录](./docs/categories/)**",
        "",
        "---",
        "",
        "## 📊 领域分类与二级细分子类大盘",
        "",
        "| 一级领域 | 项目总数 | 占比 | 包含二级细分子类 (Subcategories) | 专题文档入口 |",
        "| :--- | :---: | :---: | :--- | :--- |"
    ]

    for cat_name, slug in CATEGORY_SLUGS.items():
        count = cat_counts.get(cat_name, 0)
        pct = (count / total_stars * 100) if total_stars else 0
        icon = next((s["category_icon"] for s in stars if s["category"] == cat_name), "📦")
        
        sub_list = cat_sub_map[cat_name]
        sorted_subs = sorted(sub_list.items(), key=lambda x: x[1], reverse=True)
        sub_text = "<br>".join([f"• {sub} (`{sc}`)" for sub, sc in sorted_subs])
        
        lines.append(f"| {icon} **{cat_name}** | `{count}` 个 | `{pct:.1f}%` | {sub_text} | [📖 查看专题文档](./docs/categories/{slug}.md) |")

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
        "  - 智能一二级分类与中文摘要：`scripts/enrich_stars.py`",
        "  - 知识库与 Web 看板生成：`scripts/generate_docs.py`",
        "- 支持通过 GitHub Actions（`.github/workflows/update-stars.yml`）定时或手动一键同步最新 Stars。",
        "",
        f"<sub>*知识库构建时间: {update_time}*</sub>"
    ])

    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Generated main README.md: {README_FILE}")


def generate_web_dashboard(stars: list):
    """Generate an enhanced modern single-file Web UI dashboard with a Sidebar Tree layout."""
    json_payload = json.dumps(stars, ensure_ascii=False)

    html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ztj1993 - GitHub Stars 知识库</title>
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
    ::-webkit-scrollbar {{ width: 5px; height: 5px; }}
    ::-webkit-scrollbar-thumb {{ background: #cbd5e1; border-radius: 4px; }}
    .dark ::-webkit-scrollbar-thumb {{ background: #334155; }}
    .sidebar-scroll {{ max-height: calc(100vh - 65px); }}
  </style>
</head>
<body class="bg-slate-50 dark:bg-slate-950 text-slate-800 dark:text-slate-100 min-h-screen transition-colors duration-200 antialiased"
      x-data="starsApp()" x-cloak>

  <!-- Sticky Top Header -->
  <header class="sticky top-0 z-40 bg-white/90 dark:bg-slate-900/90 backdrop-blur-md border-b border-slate-200 dark:border-slate-800 px-4 lg:px-6 py-2.5 transition-colors">
    <div class="flex items-center justify-between gap-4">
      
      <!-- Brand & Mobile Toggle -->
      <div class="flex items-center gap-3">
        <button 
          @click="sidebarOpen = !sidebarOpen" 
          class="lg:hidden p-2 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200">
          <i class="fa-solid fa-bars"></i>
        </button>
        <div class="w-9 h-9 rounded-xl bg-gradient-to-tr from-sky-500 to-indigo-600 flex items-center justify-center text-white shadow-md shadow-sky-500/20 font-bold text-base">
          ★
        </div>
        <div>
          <div class="flex items-center gap-2">
            <h1 class="text-base font-bold tracking-tight text-slate-900 dark:text-white">
              GitHub Stars 知识库
            </h1>
            <span class="hidden sm:inline-block px-2 py-0.5 rounded-full text-[10px] font-semibold bg-sky-100 dark:bg-sky-950 text-sky-700 dark:text-sky-300">
              ztj1993
            </span>
          </div>
          <p class="text-[11px] text-slate-400">共 <span class="font-semibold text-slate-700 dark:text-slate-300" x-text="allStars.length"></span> 个精选仓库 • 10 大领域 35+ 子分类</p>
        </div>
      </div>

      <!-- Global Search Bar (Focused & Clean) -->
      <div class="flex-1 max-w-2xl relative mx-2">
        <i class="fa-solid fa-magnifying-glass absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 text-sm"></i>
        <input 
          type="text" 
          x-model="searchQuery" 
          placeholder="快速搜索项目名、中文介绍、子分类、亮点、标签..."
          class="w-full pl-10 pr-9 py-2 text-xs md:text-sm bg-slate-100 dark:bg-slate-800/80 border border-slate-200/60 dark:border-slate-700/60 focus:border-sky-500 focus:bg-white dark:focus:bg-slate-800 rounded-xl focus:ring-2 focus:ring-sky-500/20 outline-none transition-all placeholder-slate-400 text-slate-900 dark:text-white"
        >
        <button 
          x-show="searchQuery" 
          @click="searchQuery = ''"
          class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200">
          <i class="fa-solid fa-xmark text-sm"></i>
        </button>
      </div>

      <!-- Right Actions -->
      <div class="flex items-center gap-2">
        <!-- View Mode Switch -->
        <div class="flex bg-slate-100 dark:bg-slate-800 p-1 rounded-xl">
          <button 
            @click="viewMode = 'grid'" 
            :class="viewMode === 'grid' ? 'bg-white dark:bg-slate-700 shadow-sm text-sky-600 dark:text-sky-400' : 'text-slate-500 hover:text-slate-700 dark:hover:text-slate-300'"
            class="px-2.5 py-1 text-xs rounded-lg font-medium transition-all"
            title="网格卡片视图">
            <i class="fa-solid fa-grip"></i>
          </button>
          <button 
            @click="viewMode = 'table'" 
            :class="viewMode === 'table' ? 'bg-white dark:bg-slate-700 shadow-sm text-sky-600 dark:text-sky-400' : 'text-slate-500 hover:text-slate-700 dark:hover:text-slate-300'"
            class="px-2.5 py-1 text-xs rounded-lg font-medium transition-all"
            title="紧凑表格视图">
            <i class="fa-solid fa-list"></i>
          </button>
        </div>

        <!-- Dark/Light Theme -->
        <button 
          @click="toggleTheme()" 
          class="p-2 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors"
          title="切换明暗主题">
          <i :class="isDark ? 'fa-solid fa-sun text-amber-400' : 'fa-solid fa-moon text-indigo-500'"></i>
        </button>

        <!-- GitHub Profile -->
        <a href="https://github.com/ztj1993?tab=stars" target="_blank" 
           class="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-900 text-white dark:bg-white dark:text-slate-900 text-xs font-semibold hover:opacity-90 transition-opacity">
          <i class="fa-brands fa-github text-sm"></i>
          <span>GitHub</span>
        </a>
      </div>
    </div>
  </header>

  <!-- Two-Column Layout (Sidebar Tree + Content Area) -->
  <div class="max-w-[1600px] mx-auto flex min-h-[calc(100vh-65px)]">

    <!-- Mobile Backdrop -->
    <div 
      x-show="sidebarOpen" 
      @click="sidebarOpen = false" 
      class="fixed inset-0 z-30 bg-slate-900/50 backdrop-blur-sm lg:hidden"
      x-transition.opacity>
    </div>

    <!-- Left Sidebar (Hierarchical Category Tree) -->
    <aside 
      :class="sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'"
      class="fixed lg:sticky top-[57px] z-30 w-72 lg:w-80 h-[calc(100vh-57px)] bg-white dark:bg-slate-900 border-r border-slate-200/80 dark:border-slate-800/80 flex flex-col transition-transform duration-200 ease-in-out shrink-0">
      
      <!-- Sidebar Header / Reset -->
      <div class="p-3 border-b border-slate-100 dark:border-slate-800/60 flex items-center justify-between">
        <span class="text-xs font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500 flex items-center gap-1.5">
          <i class="fa-solid fa-folder-tree text-sky-500"></i>
          <span>分类与领域导航</span>
        </span>
        <button 
          x-show="selectedCategory !== 'all' || selectedSubcategory !== 'all' || selectedLanguage !== 'all' || searchQuery"
          @click="resetFilters()" 
          class="text-[11px] text-sky-600 dark:text-sky-400 hover:underline font-medium flex items-center gap-1">
          <i class="fa-solid fa-rotate-left"></i>
          <span>重置</span>
        </button>
      </div>

      <!-- Categories Tree Scroll Area -->
      <div class="flex-1 overflow-y-auto sidebar-scroll p-3 space-y-1">
        
        <!-- All Repos Item -->
        <button 
          @click="selectCategory('all')"
          :class="selectedCategory === 'all' ? 'bg-sky-600 text-white shadow-md shadow-sky-600/20 font-semibold' : 'text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800'"
          class="w-full text-left px-3 py-2 rounded-xl text-xs flex items-center justify-between transition-all group">
          <div class="flex items-center gap-2.5">
            <span class="text-sm">🌟</span>
            <span>全部项目</span>
          </div>
          <span 
            :class="selectedCategory === 'all' ? 'bg-white/25 text-white' : 'bg-slate-100 dark:bg-slate-800 text-slate-500 group-hover:bg-slate-200 dark:group-hover:bg-slate-700'"
            class="px-2 py-0.5 rounded-full text-[10px] font-medium" 
            x-text="allStars.length">
          </span>
        </button>

        <div class="pt-2 pb-1 px-1">
          <span class="text-[10px] font-bold uppercase text-slate-400 dark:text-slate-500">核心领域分类</span>
        </div>

        <!-- Primary Categories with Accordion Subcategories -->
        <template x-for="cat in categoryTree" :key="cat.name">
          <div class="rounded-xl overflow-hidden mb-1">
            
            <!-- Category Header -->
            <div 
              @click="toggleCategoryAccordion(cat.name)"
              :class="selectedCategory === cat.name ? 'bg-sky-50 text-sky-800 dark:bg-sky-950/60 dark:text-sky-200 font-bold border-l-4 border-sky-500 pl-2' : 'text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800/80'"
              class="px-3 py-2 text-xs flex items-center justify-between cursor-pointer transition-all select-none group">
              <div class="flex items-center gap-2 truncate">
                <span class="text-sm shrink-0" x-text="cat.icon"></span>
                <span class="truncate text-xs font-semibold" x-text="cat.name"></span>
              </div>
              <div class="flex items-center gap-1.5 shrink-0">
                <span 
                  :class="selectedCategory === cat.name ? 'bg-sky-200/70 text-sky-800 dark:bg-sky-900/80 dark:text-sky-200' : 'bg-slate-100 dark:bg-slate-800 text-slate-400 group-hover:bg-slate-200 dark:group-hover:bg-slate-700'"
                  class="px-1.5 py-0.2 rounded-md text-[10px] font-medium" 
                  x-text="cat.count">
                </span>
                <i 
                  :class="expandedCategories[cat.name] ? 'rotate-90' : ''"
                  class="fa-solid fa-chevron-right text-[9px] text-slate-400 transition-transform duration-200 w-3 text-center">
                </i>
              </div>
            </div>

            <!-- Subcategories Sub-tree -->
            <div 
              x-show="expandedCategories[cat.name]" 
              x-collapse
              class="pl-4 pr-1 py-1 space-y-0.5 border-l border-slate-200/80 dark:border-slate-800 ml-4 my-1">
              
              <!-- Subcategory "All" under this parent -->
              <button 
                @click="selectSubcategory(cat.name, 'all')"
                :class="(selectedCategory === cat.name && selectedSubcategory === 'all') ? 'bg-sky-500 text-white font-semibold' : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'"
                class="w-full text-left px-2.5 py-1.5 rounded-lg text-[11px] flex items-center justify-between transition-all">
                <span x-text="'全部 ' + cat.name"></span>
                <span class="text-[10px] opacity-70" x-text="cat.count"></span>
              </button>

              <!-- Specific Subcategories -->
              <template x-for="sub in cat.subcategories" :key="sub.name">
                <button 
                  @click="selectSubcategory(cat.name, sub.name)"
                  :class="(selectedCategory === cat.name && selectedSubcategory === sub.name) ? 'bg-sky-600 text-white font-semibold shadow-sm' : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-slate-900 dark:hover:text-slate-200'"
                  class="w-full text-left px-2.5 py-1.5 rounded-lg text-[11px] flex items-center justify-between transition-all group">
                  <div class="flex items-center gap-1.5 truncate">
                    <span class="text-xs" x-text="sub.icon"></span>
                    <span class="truncate" x-text="sub.name"></span>
                  </div>
                  <span 
                    :class="(selectedCategory === cat.name && selectedSubcategory === sub.name) ? 'bg-white/20 text-white' : 'text-slate-400'"
                    class="px-1.5 py-0.2 rounded text-[10px]" 
                    x-text="sub.count">
                  </span>
                </button>
              </template>
            </div>

          </div>
        </template>
      </div>

      <!-- Sidebar Footer Info -->
      <div class="p-3 border-t border-slate-100 dark:border-slate-800/80 text-[11px] text-slate-400 flex items-center justify-between">
        <span>已收录 710 个开源库</span>
        <span class="text-sky-500 font-medium">Auto-Sync</span>
      </div>
    </aside>

    <!-- Main Content Area -->
    <main class="flex-1 min-w-0 p-4 lg:p-6 space-y-4">
      
      <!-- Top Status & Secondary Filter Toolbar -->
      <div class="bg-white dark:bg-slate-900 rounded-2xl p-4 border border-slate-200/80 dark:border-slate-800/80 shadow-sm space-y-3">
        
        <!-- Breadcrumb & Stats -->
        <div class="flex flex-wrap items-center justify-between gap-3">
          <div class="flex items-center gap-2 flex-wrap">
            <span class="text-xs font-semibold text-slate-400">当前筛选:</span>
            <div class="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg bg-sky-50 dark:bg-sky-950/60 text-sky-800 dark:text-sky-300 text-xs font-bold border border-sky-100 dark:border-sky-900">
              <span x-text="currentBreadcrumbIcon"></span>
              <span x-text="currentBreadcrumbText"></span>
            </div>
            <span class="text-xs text-slate-400">
              (匹配到 <span class="font-bold text-sky-600 dark:text-sky-400" x-text="filteredStars.length"></span> 个项目)
            </span>
          </div>

          <!-- Sort Select -->
          <div class="flex items-center gap-2 ml-auto">
            <span class="text-xs text-slate-400 font-medium"><i class="fa-solid fa-arrow-down-short-wide mr-1"></i>排序:</span>
            <select 
              x-model="sortBy"
              class="bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-200 text-xs rounded-lg px-2.5 py-1.5 border border-slate-200/60 dark:border-slate-700 outline-none focus:ring-1 focus:ring-sky-500 font-medium cursor-pointer">
              <option value="stars_desc">⭐ Star 数量 (从高到低)</option>
              <option value="stars_asc">⭐ Star 数量 (从低到高)</option>
              <option value="starred_desc">🕒 Star 时间 (最新优先)</option>
              <option value="updated_desc">🔄 仓库更新 (最新优先)</option>
              <option value="name_asc">🔤 项目名称 (A-Z)</option>
            </select>
          </div>
        </div>

        <!-- Horizontal Language Filter Pills -->
        <div class="flex flex-wrap items-center gap-1.5 pt-2 border-t border-slate-100 dark:border-slate-800/80">
          <span class="text-xs font-medium text-slate-400 mr-1"><i class="fa-solid fa-code mr-1"></i>语言过滤:</span>
          <button 
            @click="selectedLanguage = 'all'"
            :class="selectedLanguage === 'all' ? 'bg-slate-900 text-white dark:bg-white dark:text-slate-900 shadow-sm' : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700'"
            class="px-2.5 py-1 rounded-lg text-xs font-medium transition-all">
            全部
          </button>
          <template x-for="lang in topLanguages" :key="lang.name">
            <button 
              @click="selectedLanguage = lang.name"
              :class="selectedLanguage === lang.name ? 'bg-slate-900 text-white dark:bg-white dark:text-slate-900 shadow-sm font-semibold' : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700'"
              class="px-2.5 py-1 rounded-lg text-xs font-medium transition-all flex items-center gap-1">
              <span x-text="lang.name"></span>
              <span class="text-[10px] opacity-70" x-text="'(' + lang.count + ')'"></span>
            </button>
          </template>
        </div>

      </div>

      <!-- Empty State -->
      <div x-show="filteredStars.length === 0" class="text-center py-20 bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800">
        <i class="fa-regular fa-folder-open text-5xl text-slate-300 dark:text-slate-600 mb-3"></i>
        <h3 class="text-base font-semibold text-slate-700 dark:text-slate-300">没有找到匹配的项目</h3>
        <p class="text-xs text-slate-400 mt-1">请尝试更换搜索词或在左侧选择其他分类</p>
        <button @click="resetFilters()" class="mt-4 px-4 py-2 bg-sky-600 text-white text-xs font-semibold rounded-xl hover:bg-sky-700 transition-colors">
          重置全部筛选
        </button>
      </div>

      <!-- Grid View Mode -->
      <div x-show="viewMode === 'grid' && filteredStars.length > 0" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        <template x-for="item in pagedStars" :key="item.id">
          <div class="bg-white dark:bg-slate-900 rounded-2xl p-5 border border-slate-200/80 dark:border-slate-800/80 hover:border-sky-400 dark:hover:border-sky-500 shadow-sm hover:shadow-lg hover:shadow-sky-500/5 transition-all flex flex-col justify-between group">
            
            <div>
              <!-- Compact Breadcrumb Chip & Star Badge (Single Line, Never Wrap) -->
              <div class="flex items-center justify-between gap-2 mb-2.5">
                <div class="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-slate-100 dark:bg-slate-800 text-[11px] font-medium text-slate-600 dark:text-slate-300 max-w-[200px] truncate border border-slate-200/50 dark:border-slate-700/60" :title="item.category + ' › ' + item.subcategory">
                  <span x-text="item.category_icon"></span>
                  <span class="truncate" x-text="item.category"></span>
                  <span class="text-slate-400">·</span>
                  <span class="text-sky-600 dark:text-sky-400 font-semibold truncate" x-text="item.subcategory"></span>
                </div>
                <div class="flex items-center gap-1 text-amber-500 font-bold text-xs bg-amber-50 dark:bg-amber-950/40 px-2 py-0.5 rounded-full border border-amber-200/70 dark:border-amber-800 shrink-0">
                  <i class="fa-solid fa-star text-[10px]"></i>
                  <span x-text="formatStars(item.stars)"></span>
                </div>
              </div>

              <!-- Repo Full Name -->
              <div class="mb-2">
                <a :href="item.html_url" target="_blank" 
                   class="text-sm font-bold text-slate-900 dark:text-white hover:text-sky-600 dark:hover:text-sky-400 transition-colors inline-block leading-snug break-all"
                   x-text="item.full_name">
                </a>
              </div>

              <!-- Chinese Summary -->
              <p class="text-xs text-slate-600 dark:text-slate-300 line-clamp-2 leading-relaxed mb-3 font-normal" x-text="item.summary_zh"></p>

              <!-- Feature Highlights Box -->
              <div class="bg-slate-50 dark:bg-slate-950/50 rounded-xl p-2.5 mb-3 border border-slate-100 dark:border-slate-800 text-[11px] space-y-1.5">
                <template x-for="(feat, idx) in item.features_zh" :key="idx">
                  <div class="flex items-start gap-1.5 text-slate-600 dark:text-slate-300">
                    <span class="text-sky-500 mt-0.5 shrink-0">•</span>
                    <span class="leading-tight" x-text="feat"></span>
                  </div>
                </template>
              </div>
            </div>

            <!-- Card Footer -->
            <div>
              <!-- Tags -->
              <div class="flex flex-wrap gap-1 mb-2.5">
                <span class="px-2 py-0.5 bg-sky-50 dark:bg-sky-950/60 text-sky-600 dark:text-sky-300 rounded-md text-[10px] font-semibold border border-sky-100 dark:border-sky-900" x-text="item.language || 'Unknown'"></span>
                <template x-for="tag in item.tags.slice(1, 4)" :key="tag">
                  <span class="px-1.5 py-0.5 bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 rounded text-[10px]" x-text="tag"></span>
                </template>
              </div>

              <div class="flex items-center justify-between pt-2 border-t border-slate-100 dark:border-slate-800 text-[11px] text-slate-400">
                <span class="text-[10px]" x-text="item.starred_at ? 'Star于: ' + item.starred_at.slice(0, 10) : ''"></span>
                <div class="flex items-center gap-2">
                  <a x-show="item.homepage" :href="item.homepage" target="_blank" class="hover:text-sky-500 transition-colors p-1" title="访问官网/Demo">
                    <i class="fa-solid fa-link text-xs"></i>
                  </a>
                  <a :href="item.html_url" target="_blank" class="hover:text-sky-500 transition-colors p-1" title="在 GitHub 查看">
                    <i class="fa-brands fa-github text-sm"></i>
                  </a>
                </div>
              </div>
            </div>

          </div>
        </template>
      </div>

      <!-- Table View Mode -->
      <div x-show="viewMode === 'table' && filteredStars.length > 0" class="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200/80 dark:border-slate-800 overflow-hidden shadow-sm">
        <div class="overflow-x-auto">
          <table class="w-full text-left text-xs text-slate-600 dark:text-slate-300">
            <thead class="bg-slate-50 dark:bg-slate-800/70 text-slate-700 dark:text-slate-200 font-semibold border-b border-slate-200 dark:border-slate-800">
              <tr>
                <th class="py-3 px-4">项目仓库</th>
                <th class="py-3 px-3">所属领域与分类</th>
                <th class="py-3 px-3">主要语言</th>
                <th class="py-3 px-3">Star 数</th>
                <th class="py-3 px-4">中文定位与功能亮点</th>
                <th class="py-3 px-3 text-right">操作</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100 dark:divide-slate-800">
              <template x-for="item in pagedStars" :key="item.id">
                <tr class="hover:bg-slate-50/80 dark:hover:bg-slate-800/40 transition-colors">
                  <td class="py-3 px-4 font-bold text-slate-900 dark:text-white whitespace-nowrap">
                    <div class="flex items-center gap-1.5">
                      <span x-text="item.category_icon"></span>
                      <a :href="item.html_url" target="_blank" class="hover:text-sky-500 transition-colors" x-text="item.full_name"></a>
                    </div>
                  </td>
                  <td class="py-3 px-3 whitespace-nowrap">
                    <span class="px-2 py-0.5 rounded-md text-[10px] bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 font-medium" x-text="item.category + ' · ' + item.subcategory"></span>
                  </td>
                  <td class="py-3 px-3 whitespace-nowrap">
                    <span class="font-semibold text-sky-600 dark:text-sky-400" x-text="item.language || '-'"></span>
                  </td>
                  <td class="py-3 px-3 whitespace-nowrap font-bold text-amber-500">
                    ★ <span x-text="item.stars.toLocaleString()"></span>
                  </td>
                  <td class="py-3 px-4 max-w-md">
                    <div class="font-medium text-slate-800 dark:text-slate-200 line-clamp-1 mb-0.5" x-text="item.summary_zh"></div>
                    <div class="text-[10px] text-slate-400 line-clamp-1" x-text="item.features_zh.join('；')"></div>
                  </td>
                  <td class="py-3 px-3 text-right whitespace-nowrap">
                    <a :href="item.html_url" target="_blank" class="p-1.5 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:text-sky-500 transition-colors inline-block">
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
      <div x-show="totalPages > 1" class="mt-6 flex items-center justify-between border-t border-slate-200 dark:border-slate-800 pt-4">
        <div class="text-xs text-slate-400">
          第 <span class="font-semibold text-slate-700 dark:text-slate-300" x-text="(currentPage - 1) * pageSize + 1"></span> - <span class="font-semibold text-slate-700 dark:text-slate-300" x-text="Math.min(currentPage * pageSize, filteredStars.length)"></span> 条 (共 <span class="font-semibold" x-text="filteredStars.length"></span> 条)
        </div>
        <div class="flex items-center gap-1.5">
          <button 
            @click="currentPage = Math.max(1, currentPage - 1)" 
            :disabled="currentPage === 1"
            class="px-3 py-1.5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-xs font-semibold disabled:opacity-30 hover:bg-slate-50 dark:hover:bg-slate-800 transition-all">
            <i class="fa-solid fa-chevron-left mr-1"></i>上一页
          </button>
          <span class="px-3 py-1.5 text-xs font-semibold text-slate-600 dark:text-slate-300" x-text="currentPage + ' / ' + totalPages"></span>
          <button 
            @click="currentPage = Math.min(totalPages, currentPage + 1)" 
            :disabled="currentPage === totalPages"
            class="px-3 py-1.5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-xs font-semibold disabled:opacity-30 hover:bg-slate-50 dark:hover:bg-slate-800 transition-all">
            下一页<i class="fa-solid fa-chevron-right ml-1"></i>
          </button>
        </div>
      </div>

    </main>

  </div>

  <script>
    const RAW_STARS_DATA = {json_payload};

    function starsApp() {{
      return {{
        allStars: RAW_STARS_DATA,
        searchQuery: '',
        selectedCategory: 'all',
        selectedSubcategory: 'all',
        selectedLanguage: 'all',
        sortBy: 'stars_desc',
        viewMode: 'grid',
        currentPage: 1,
        pageSize: 48,
        sidebarOpen: false,
        expandedCategories: {{}},
        isDark: window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches,

        init() {{
          if (this.isDark) {{
            document.documentElement.classList.add('dark');
          }}
          // Auto-expand all categories in accordion by default
          this.categoryTree.forEach(c => {{
            this.expandedCategories[c.name] = true;
          }});

          this.$watch('searchQuery', () => {{ this.currentPage = 1; }});
          this.$watch('selectedCategory', () => {{ this.currentPage = 1; }});
          this.$watch('selectedSubcategory', () => {{ this.currentPage = 1; }});
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

        toggleCategoryAccordion(catName) {{
          this.expandedCategories[catName] = !this.expandedCategories[catName];
        }},

        selectCategory(catName) {{
          this.selectedCategory = catName;
          this.selectedSubcategory = 'all';
          if (catName !== 'all') {{
            this.expandedCategories[catName] = true;
          }}
          this.currentPage = 1;
        }},

        selectSubcategory(catName, subName) {{
          this.selectedCategory = catName;
          this.selectedSubcategory = subName;
          this.currentPage = 1;
          if (window.innerWidth < 1024) {{
            this.sidebarOpen = false;
          }}
        }},

        resetFilters() {{
          this.searchQuery = '';
          this.selectedCategory = 'all';
          this.selectedSubcategory = 'all';
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

        get currentBreadcrumbIcon() {{
          if (this.selectedCategory === 'all') return '🌟';
          const match = this.categoryTree.find(c => c.name === this.selectedCategory);
          return match ? match.icon : '📦';
        }},

        get currentBreadcrumbText() {{
          if (this.selectedCategory === 'all') return '全部项目';
          if (this.selectedSubcategory === 'all') return this.selectedCategory;
          return this.selectedCategory + ' › ' + this.selectedSubcategory;
        }},

        get categoryTree() {{
          const treeMap = {{}};
          this.allStars.forEach(s => {{
            const cName = s.category;
            const subName = s.subcategory || '通用';
            const subIcon = s.subcategory_icon || '•';

            if (!treeMap[cName]) {{
              treeMap[cName] = {{
                name: cName,
                icon: s.category_icon || '📦',
                count: 0,
                subMap: {{}}
              }};
            }}
            treeMap[cName].count += 1;
            if (!treeMap[cName].subMap[subName]) {{
              treeMap[cName].subMap[subName] = {{
                name: subName,
                icon: subIcon,
                count: 0
              }};
            }}
            treeMap[cName].subMap[subName].count += 1;
          }});

          return Object.values(treeMap).map(cat => ({{
            name: cat.name,
            icon: cat.icon,
            count: cat.count,
            subcategories: Object.values(cat.subMap).sort((a, b) => b.count - a.count)
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

          // Primary category filter
          if (this.selectedCategory !== 'all') {{
            result = result.filter(s => s.category === this.selectedCategory);
          }}

          // Secondary subcategory filter
          if (this.selectedSubcategory !== 'all') {{
            result = result.filter(s => s.subcategory === this.selectedSubcategory);
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
                (s.subcategory && s.subcategory.toLowerCase().includes(q)) ||
                (s.category && s.category.toLowerCase().includes(q)) ||
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
    print(f"Generated modern Sidebar Tree interactive web dashboard: {HTML_FILE}")


def main():
    stars = load_data()
    print(f"Loaded {len(stars)} enriched star items.")
    generate_category_docs(stars)
    generate_main_readme(stars)
    generate_web_dashboard(stars)
    print("\nAll hierarchical documentation and modern Web UI generated successfully!")


if __name__ == "__main__":
    main()
