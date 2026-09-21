#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enrich raw stars data with categorization, Chinese summary, features, and tags.
Saves the enriched metadata to data/enriched_stars.json.
"""

import os
import sys
import re
import json
import collections

# Ensure UTF-8 output on Windows terminal
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_FILE = os.path.join(BASE_DIR, "data", "raw_stars.json")
ENRICHED_FILE = os.path.join(BASE_DIR, "data", "enriched_stars.json")

# Category definitions
CATEGORIES = {
    "AI 与大模型": {
        "icon": "🤖",
        "keywords": [
            "ai", "llm", "gpt", "agent", "prompt", "rag", "openai", "claude", "ollama",
            "whisper", "deepseek", "langchain", "huggingface", "pytorch", "tensorflow",
            "diffusion", "embedding", "nlp", "cv", "vision", "speech", "tts", "stt",
            "short-drama", "drama", "genai", "chatgpt", "chatbot", "transformer",
            "lora", "vllm", "llama", "stable-diffusion", "midjourney", "comfyui",
            "neural", "machine-learning", "deep-learning", "text-to-speech", "model",
            "voice", "asr", "ocr", "multimodal", "fine-tuning", "vector", "ai-art"
        ]
    },
    "前端与跨端开发": {
        "icon": "🎨",
        "keywords": [
            "vue", "react", "frontend", "ui", "components", "web", "electron", "flutter",
            "android", "ios", "react-native", "tailwind", "vite", "webpack", "uniapp",
            "taro", "mobile", "ui-kit", "ant-design", "element-ui", "css", "html5",
            "chrome-extension", "extension", "svelte", "solidjs", "nextjs", "nuxt",
            "typescript", "javascript", "canvas", "wasm", "webassembly", "astro",
            "theme", "widget", "layout", "responsive"
        ]
    },
    "后端架构与微服务": {
        "icon": "⚙️",
        "keywords": [
            "fastapi", "flask", "django", "gin", "echo", "spring", "nestjs", "microservice",
            "rpc", "grpc", "gateway", "middleware", "rest-api", "backend", "framework",
            "fiber", "swoole", "workerman", "thinkphp", "laravel", "hyperf", "express",
            "koa", "jwt", "oauth", "auth", "session", "websocket", "http", "api-gateway",
            "serverless", "grpc-go", "gin-gonic", "actix", "axum", "rocket", "routing"
        ]
    },
    "DevOps 与云原生": {
        "icon": "☁️",
        "keywords": [
            "docker", "k8s", "kubernetes", "helm", "terraform", "ci/cd", "ci", "cd",
            "github-actions", "prometheus", "grafana", "openwrt", "vpn", "proxy", "clash",
            "v2ray", "shadowsocks", "nginx", "traefik", "caddy", "cloudflare", "devops",
            "deploy", "cloud", "linux", "passwall", "sing-box", "xray", "trojan",
            "ansible", "container", "podman", "consul", "etcd", "mesh", "istio",
            "tunnel", "frp", "wireguard", "dns", "ddns", "server", "router", "homelab"
        ]
    },
    "效率工具与 CLI": {
        "icon": "🛠️",
        "keywords": [
            "cli", "terminal", "tui", "tool", "utility", "automation", "workflow",
            "productivity", "git", "downloader", "youtube-dl", "aria2", "editor",
            "neovim", "vim", "alfred", "raycast", "script", "powershell", "zsh",
            "bash", "shell", "tmux", "fzf", "grep", "ripgrep", "cheat", "sync",
            "compress", "backup", "manager", "desktop", "mac", "windows", "clipboard",
            "quick-look", "launcher", "shortcut"
        ]
    },
    "数据处理与爬虫": {
        "icon": "🕷️",
        "keywords": [
            "scraper", "scraping", "crawler", "spider", "scrapy", "selenium", "playwright",
            "puppeteer", "etl", "pandas", "polars", "spark", "data-analysis",
            "visualization", "echarts", "d3", "pdf", "parsing", "data-extraction",
            "feed", "rss", "feedparser", "charts", "table", "excel", "csv", "json-parser",
            "beautifulsoup", "headless", "stealth"
        ]
    },
    "数据库与存储": {
        "icon": "🗄️",
        "keywords": [
            "database", "db", "mysql", "postgresql", "postgres", "sqlite", "redis",
            "mongodb", "clickhouse", "minio", "storage", "s3", "orm", "gorm", "prisma",
            "sql", "nosql", "vector-database", "milvus", "chroma", "qdrant", "duckdb",
            "kv", "cache", "memcached", "rocksdb", "dbt", "elastic", "elasticsearch",
            "meilisearch", "typesense", "dbx", "dbeaver", "datagrip", "backup-tool"
        ]
    },
    "网络安全与逆向": {
        "icon": "🛡️",
        "keywords": [
            "security", "pentest", "vulnerability", "ctf", "exploit", "reverse-engineering",
            "frida", "ida", "ghidra", "decompiler", "xss", "sqli", "scanner", "audit",
            "cryptography", "bypass", "wifite", "nmap", "wireshark", "pwn", "burp",
            "honeypot", "fuzzing", "malware", "sandbox", "antivirus", "sniffer"
        ]
    },
    "影音多媒体与图形": {
        "icon": "🎬",
        "keywords": [
            "ffmpeg", "video", "audio", "media", "player", "stream", "webrtc", "rtmp",
            "3d", "opengl", "webgl", "canvas", "rendering", "game", "graphics",
            "image-processing", "blender", "shaders", "music", "mp4", "mp3", "subtitles",
            "live", "obs", "sound", "vlc", "encoder", "decoder", "transcoder"
        ]
    },
    "资源精选与学习指南": {
        "icon": "📚",
        "keywords": [
            "awesome", "tutorial", "roadmap", "book", "interview", "guide", "learning",
            "cheat-sheet", "leetcode", "collection", "list", "paper", "algorithm-patterns",
            "curated", "resources", "cheatsheet", "notes", "handbook", "awesome-list",
            "learn", "study", "docs", "documentation", "tips"
        ]
    }
}

KNOWN_PROJECTS = {
    "openai/whisper": "OpenAI 开源的高鲁棒性多语种语音识别与语音转文本模型系统。",
    "punkpeye/awesome-mcp-servers": "精选的模型上下文协议（MCP）服务端与生态工具资源大合集。",
    "jamesmurdza/awesome-ai-devtools": "精选的 AI 驱动开发者工具、辅助编程与研发提效资源列表。",
    "strapi/strapi": "业界领先的开源 Headless CMS 框架，完全基于 TypeScript/JavaScript 打造，高度可定制。",
    "iamkun/dayjs": "极简高效的现代化日期时间处理库（仅 2KB），拥有与 Moment.js 兼容的 API 规范。",
    "jazzband/tablib": "用于表格数据集处理格式化库，支持 XLS、CSV、JSON、YAML 等多种格式自由互转。",
    "t8y2/dbx": "轻量级跨平台现代数据库客户端，支持 90+ 数据库并内置 AI 助手与 MCP Server。",
    "jlcodes99/cockpit-tools": "通用 AI IDE 账号管理工具，支持 Antigravity/Cursor/Copilot 多账号无缝切换与配额监控。",
    "lbjlaq/Antigravity-Manager": "专业 Antigravity 账号管理与一键无缝切换桌面客户端（基于 Tauri v2 + React）。",
    "getnora-io/nora": "极轻量级多格式制品仓库管理服务，单二进制文件支持 Docker/npm/PyPI 等 15 种格式制品存储。",
    "backube/volsync": "面向 Kubernetes 存储卷（PVC）的高性能异步数据复制与跨集群容灾迁移利器。",
    "lisaac/openwrt-in-docker": "基于 Docker 容器化一键部署与运行的 OpenWrt 软路由及主旁路由网关方案。",
    "samyk/pwnat": "无需第三方代理或服务器介入的 NAT/防火墙内网双向穿透技术与实用工具。",
    "hackerschoice/gsocket": "突破防火墙与 NAT 限制的高安全性端到端加密通信与网络穿透利器。"
}

TRANSLATION_DICT = {
    "a curated list of": "精选合集：",
    "curated list of": "精选合集：",
    "a collection of": "精选合集：",
    "collection of": "精选合集：",
    "all-in-one": "一站式",
    "lightweight": "轻量级",
    "high-performance": "高性能",
    "high performance": "高性能",
    "cross-platform": "跨平台",
    "asynchronous": "异步",
    "distributed": "分布式",
    "real-time": "实时",
    "open-source": "开源",
    "open source": "开源",
    "command-line": "命令行",
    "command line": "命令行",
    "framework": "框架",
    "library": "库",
    "toolkit": "工具包",
    "plugin": "插件",
    "extension": "扩展",
    "dashboard": "仪表盘",
    "microservice": "微服务",
    "full-stack": "全栈",
    "reverse proxy": "反向代理",
    "load balancer": "负载均衡器",
    "monitoring": "监控",
    "caching": "缓存",
    "automation": "自动化",
    "crawler": "爬虫",
    "scraper": "抓取工具",
    "orchestration": "编排",
    "container": "容器",
    "kubernetes": "Kubernetes",
    "docker": "Docker",
    "database": "数据库",
    "storage": "存储",
    "client": "客户端",
    "server": "服务端",
    "generator": "生成器",
    "manager": "管理器",
    "workflow": "工作流",
    "pipeline": "流水线",
    "assistant": "助手",
    "interface": "界面",
    "frontend": "前端",
    "backend": "后端",
    "middleware": "中间件",
    "gateway": "网关",
    "package manager": "包管理器",
    "registry": "制品/包注册表",
    "replication": "数据复制",
    "migration": "数据迁移",
    "backup": "备份",
    "recovery": "恢复",
    "visualization": "可视化",
    "template": "模板",
    "boilerplate": "脚手架/模板",
    "starter": "启动器",
    "scaffold": "脚手架",
    "benchmark": "基准测试",
    "testing": "测试",
    "security": "安全",
    "vulnerability": "漏洞",
    "scanner": "扫描器",
    "analyzer": "分析器",
    "parser": "解析器",
    "compiler": "编译器",
    "interpreter": "解释器",
    "runtime": "运行时",
    "engine": "引擎",
    "sdk": "SDK",
    "api": "API",
    "cli": "命令行工具",
    "gui": "图形界面",
    "tui": "终端界面",
    "web ui": "Web 界面",
    "desktop app": "桌面应用",
    "mobile app": "移动应用",
    "best practices": "最佳实践",
    "cheat sheet": "速查表",
    "cheatsheet": "速查表",
    "headless cms": "Headless CMS 内容管理系统"
}

def clean_text(text: str) -> str:
    if not text:
        return ""
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    return text

def has_chinese(text: str) -> bool:
    if not text:
        return False
    return bool(re.search(r"[\u4e00-\u9fa5]", text))

def extract_chinese_part(text: str) -> str:
    """Extracts Chinese portion if bilingual text is present."""
    if not text or not has_chinese(text):
        return ""
    
    parts = re.split(r"[|｜\n—–—]", text)
    zh_candidates = [p.strip() for p in parts if has_chinese(p)]
    if zh_candidates:
        # Choose the most descriptive Chinese segment
        longest_zh = max(zh_candidates, key=len)
        if len(longest_zh) >= 10:
            return longest_zh
            
    # Or return text with cleaned punctuation
    return text.strip()

def translate_english_desc(desc: str, repo: dict) -> str:
    full_name = repo.get("full_name", "")
    if full_name in KNOWN_PROJECTS:
        return KNOWN_PROJECTS[full_name]
        
    if not desc:
        name = repo.get("name", "")
        lang = repo.get("language") or "开源"
        topics = repo.get("topics") or []
        t_str = f"（涵盖 {', '.join(topics[:3])}）" if topics else ""
        return f"基于 {lang} 开发的实用开源项目与工具 {name}{t_str}。"
    
    text = desc.strip()
    lower = text.lower()
    
    # Common prefix cleanups
    if lower.startswith("a "):
        text = text[2:].strip()
    elif lower.startswith("an "):
        text = text[3:].strip()
    elif lower.startswith("the "):
        text = text[4:].strip()

    # Dictionary translation
    sorted_dict = sorted(TRANSLATION_DICT.items(), key=lambda x: len(x[0]), reverse=True)
    res = text
    for en, zh in sorted_dict:
        pattern = re.compile(r"\b" + re.escape(en) + r"\b", re.IGNORECASE)
        res = pattern.sub(zh, res)
        
    # Heuristic translations for common structures
    if not has_chinese(res):
        lang = repo.get("language") or "多语言"
        topics = repo.get("topics") or []
        t_str = f"（技术标签: {', '.join(topics[:3])}）" if topics else ""
        return f"基于 {lang} 构建：{text} {t_str}"
        
    return res

def determine_category(repo: dict) -> str:
    name = (repo.get("name") or "").lower()
    full_name = (repo.get("full_name") or "").lower()
    desc = (repo.get("description") or "").lower()
    topics = [t.lower() for t in (repo.get("topics") or [])]
    lang = (repo.get("language") or "").lower()
    
    all_text = f"{name} {full_name} {desc} {' '.join(topics)}"
    scores = collections.defaultdict(int)
    
    # Rule weights
    if any(k in all_text for k in ["whisper", "llm", "gpt", "agent", "prompt", "openai", "claude", "ollama", "stable-diffusion", "midjourney", "comfyui", "vllm", "short-drama", "huobao-drama", "toonflow", "deepseek", "langchain"]):
        scores["AI 与大模型"] += 15
    if any(k in all_text for k in ["awesome-", "learn-", "tutorial", "interview", "roadmap", "cheatsheet", "guide", "cheatsheet"]):
        scores["资源精选与学习指南"] += 12
    if any(k in all_text for k in ["docker", "k8s", "kubernetes", "openwrt", "passwall", "clash", "v2ray", "shadowsocks", "sing-box", "xray", "trojan", "helm", "terraform", "wireguard"]):
        scores["DevOps 与云原生"] += 10
    if any(k in all_text for k in ["mysql", "postgresql", "postgres", "sqlite", "redis", "mongodb", "clickhouse", "minio", "duckdb", "dbx", "database", "vector-database"]):
        scores["数据库与存储"] += 10
    if any(k in all_text for k in ["pentest", "vulnerability", "exploit", "reverse-engineering", "frida", "ida", "ghidra", "decompiler", "xss", "sqli", "ctf"]):
        scores["网络安全与逆向"] += 10
    if any(k in all_text for k in ["ffmpeg", "video", "audio", "player", "webrtc", "rtmp", "3d", "opengl", "webgl", "blender"]):
        scores["影音多媒体与图形"] += 10
    if any(k in all_text for k in ["scraper", "scraping", "crawler", "spider", "scrapy", "selenium", "playwright", "puppeteer"]):
        scores["数据处理与爬虫"] += 10
    if any(k in all_text for k in ["cli", "terminal", "tui", "downloader", "youtube-dl", "aria2", "neovim", "alfred", "raycast", "workflow"]):
        scores["效率工具与 CLI"] += 8
    if any(k in all_text for k in ["vue", "react", "frontend", "ui", "tailwind", "vite", "webpack", "uniapp", "taro", "chrome-extension"]):
        scores["前端与跨端开发"] += 8
    if any(k in all_text for k in ["fastapi", "flask", "django", "gin", "echo", "spring", "nestjs", "microservice", "rpc", "grpc", "swoole", "workerman", "hyperf"]):
        scores["后端架构与微服务"] += 8

    # Keyword match
    for cat, data in CATEGORIES.items():
        for kw in data["keywords"]:
            if kw in topics:
                scores[cat] += 4
            if re.search(r"\b" + re.escape(kw) + r"\b", name):
                scores[cat] += 3
            if kw in desc:
                scores[cat] += 1
                
    if not scores or max(scores.values()) == 0:
        if lang in ["vue", "html", "css", "javascript", "typescript"]:
            scores["前端与跨端开发"] += 2
        elif lang in ["php", "go", "java", "c#"]:
            scores["后端架构与微服务"] += 2
        elif lang in ["python"]:
            scores["效率工具与 CLI"] += 2
        elif lang in ["shell", "dockerfile"]:
            scores["DevOps 与云原生"] += 2
        elif lang in ["c", "c++", "rust"]:
            scores["效率工具与 CLI"] += 2
        else:
            scores["效率工具与 CLI"] += 1
            
    return max(scores.items(), key=lambda x: x[1])[0]

def extract_tags(repo: dict, category: str) -> list:
    tags = []
    lang = repo.get("language")
    if lang:
        tags.append(lang)
        
    topics = repo.get("topics") or []
    for t in topics:
        clean_t = t.strip()
        if clean_t and clean_t.lower() not in [tag.lower() for tag in tags]:
            if len(tags) < 6:
                tags.append(clean_t)
                
    name = (repo.get("name") or "").lower()
    desc = (repo.get("description") or "").lower()
    full_text = f"{name} {desc} {' '.join(topics)}"
    
    if any(k in full_text for k in ["cli", "command-line", "terminal", "tui"]):
        if "CLI" not in tags: tags.append("CLI")
    if any(k in full_text for k in ["framework", "框架"]):
        if "框架" not in tags: tags.append("框架")
    if any(k in full_text for k in ["docker", "container", "dockerfile"]):
        if "Docker" not in tags: tags.append("Docker")
    if any(k in full_text for k in ["k8s", "kubernetes"]):
        if "Kubernetes" not in tags: tags.append("Kubernetes")
    if any(k in full_text for k in ["llm", "large language model", "agent", "gpt"]):
        if "LLM" not in tags: tags.append("LLM")
    if any(k in full_text for k in ["web ui", "gui", "web-ui", "desktop"]):
        if "GUI/WebUI" not in tags: tags.append("GUI/WebUI")
    if any(k in full_text for k in ["api", "rest-api", "grpc"]):
        if "API" not in tags: tags.append("API")
        
    return tags[:6]

def generate_summary_and_features(repo: dict, category: str):
    full_name = repo.get("full_name") or ""
    raw_desc = repo.get("description") or ""
    name = repo.get("name") or ""
    lang = repo.get("language") or "多语言"
    topics = repo.get("topics") or []
    stars = repo.get("stargazers_count", 0)
    
    if full_name in KNOWN_PROJECTS:
        summary_zh = KNOWN_PROJECTS[full_name]
    elif has_chinese(raw_desc):
        zh_part = extract_chinese_part(raw_desc)
        summary_zh = zh_part if len(zh_part) >= 8 else raw_desc
    else:
        summary_zh = translate_english_desc(raw_desc, repo)
    
    summary_zh = clean_text(summary_zh)
    if not summary_zh.endswith("。") and not summary_zh.endswith(".") and not summary_zh.endswith("！"):
        summary_zh += "。"
        
    features = []
    
    # Feature 1: Core purpose / architecture
    if category == "AI 与大模型":
        features.append("智能化驱动：深度整合大语言模型、智能体或计算机视觉能力，赋能自动化与生成式场景")
    elif category == "前端与跨端开发":
        features.append(f"现代 UI 体验：基于 {lang} 与现代前端工程化架构，提供响应式、组件化交互界面")
    elif category == "后端架构与微服务":
        features.append(f"高并发与高可用：采用 {lang} 构建，具备优异的吞吐性能、模块化服务拆分与 API 路由治理")
    elif category == "DevOps 与云原生":
        features.append("容器与自动化部署：深度支持 Docker/K8s/CI-CD，提供开箱即用的运维管理与网络代理方案")
    elif category == "效率工具与 CLI":
        features.append("极速命令行交互：提供简洁高效的 CLI/TUI 操作体验，大幅简化开发者日常繁琐操作")
    elif category == "数据处理与爬虫":
        features.append("数据采集与结构化：具备强大的网络请求、反反爬策略以及海量数据清洗与解析能力")
    elif category == "数据库与存储":
        features.append("多源数据统一管理：提供高效的存取、查询优化、数据同步复制与跨数据源兼容支持")
    elif category == "网络安全与逆向":
        features.append("安全检测与逆向分析：包含自动化脆弱性扫描、流量抓取检测及代码审计调试能力")
    elif category == "影音多媒体与图形":
        features.append("多媒体渲染与转码：支持音视频多流处理、硬件加速解码、图形渲染与实时传输")
    elif category == "资源精选与学习指南":
        features.append("全景知识体系与精选：汇集行业最佳实践、面试指南、高频技术架构与实用资源合集")
    else:
        features.append(f"开箱即用：基于 {lang} 构建，工程结构清晰，依赖轻量易维护")

    # Feature 2: Language & Performance
    if lang in ["Go", "Rust", "C", "C++"]:
        features.append(f"极致性能：使用 {lang} 原生编写，单二进制分发，内存占用低且启动迅速")
    elif lang in ["Python"]:
        features.append("生态丰富：依托完善的 Python 开源生态，API 接口设计简洁且易于二次扩展")
    elif lang in ["TypeScript", "JavaScript", "Vue"]:
        features.append(f"类型安全与组件生态：基于 {lang} 打造，代码规范健壮，支持热重载与模块化组装")
    elif lang in ["PHP"]:
        features.append("快速开发与交付：基于成熟 PHP 生态框架，适合敏捷业务迭代与高性价比部署")
    elif lang in ["Java"]:
        features.append("企业级稳健架构：基于 Java 企业级生态，具备成熟的依赖生态与严谨的类型系统")
    elif lang in ["Shell", "PowerShell"]:
        features.append("脚本化一键执行：跨环境无缝适配，免复杂安装配置，支持一键自动化脚本部署")
    else:
        features.append("技术栈友好：灵活适配多种技术环境，支持容器化与多平台部署")

    # Feature 3: Specific capability from topics / desc
    if any(t in topics for t in ["docker", "kubernetes", "k8s"]):
        features.append("容器化就绪：内置 Dockerfile 与容器编排模板，方便一键部署上线与集群扩容")
    elif any(t in topics for t in ["cli", "terminal"]):
        features.append("CLI 命令行交互：支持丰富参数配置与管道输入输出，易于集成进脚本与 CI/CD 流水线")
    elif any(t in topics for t in ["api", "rest-api", "fastapi", "grpc"]):
        features.append("标准化 API 支持：提供完善的 RESTful / gRPC 接口与清晰的接口文档规范")
    elif any(t in topics for t in ["ai", "llm", "agent"]):
        features.append("AI 智能体集成：支持多模型对接（OpenAI、Claude、本地模型等）与灵活 Prompt 编排")
    else:
        features.append("社区活跃与高星支持：在 GitHub 拥有良好社区口碑，持续维护并拥有完整文档")

    # Feature 4: Open source / Popularity badge
    if stars >= 10000:
        features.append(f"超高人气（★ {stars:,}）：业界知名标杆项目，拥有庞大社区活跃度与广泛生产实战检验")
    elif stars >= 1000:
        features.append(f"热门高星（★ {stars:,}）：经过广泛社区验证的优秀开源方案，文档完善且维护活跃")
    else:
        features.append(f"精选实用工具（★ {stars:,}）：针对特定垂直场景设计，解决痛点需求，小巧精悍")

    return summary_zh, features

def process_all_stars():
    print(f"Loading raw stars from {RAW_FILE}...")
    with open(RAW_FILE, "r", encoding="utf-8") as f:
        raw_stars = json.load(f)
    print(f"Loaded {len(raw_stars)} repositories.")

    enriched_stars = []
    category_counts = collections.Counter()
    language_counts = collections.Counter()

    for idx, repo in enumerate(raw_stars):
        category = determine_category(repo)
        category_counts[category] += 1
        
        lang = repo.get("language") or "Unknown"
        language_counts[lang] += 1
        
        tags = extract_tags(repo, category)
        summary_zh, features_zh = generate_summary_and_features(repo, category)
        
        enriched_item = {
            "id": repo.get("id"),
            "name": repo.get("name"),
            "full_name": repo.get("full_name"),
            "owner": repo.get("owner", {}).get("login"),
            "owner_avatar": repo.get("owner", {}).get("avatar_url"),
            "html_url": repo.get("html_url"),
            "homepage": repo.get("homepage"),
            "raw_description": repo.get("description"),
            "summary_zh": summary_zh,
            "features_zh": features_zh,
            "category": category,
            "category_icon": CATEGORIES.get(category, {}).get("icon", "📦"),
            "language": repo.get("language") or "Unknown",
            "tags": tags,
            "topics": repo.get("topics") or [],
            "stars": repo.get("stargazers_count", 0),
            "forks": repo.get("forks_count", 0),
            "open_issues": repo.get("open_issues_count", 0),
            "license": repo.get("license", {}).get("spdx_id") if repo.get("license") else None,
            "created_at": repo.get("created_at"),
            "updated_at": repo.get("updated_at"),
            "starred_at": repo.get("starred_at")
        }
        enriched_stars.append(enriched_item)

    print("\n--- 分类统计概览 ---")
    for cat, count in category_counts.most_common():
        icon = CATEGORIES.get(cat, {}).get("icon", "")
        print(f"{icon} {cat}: {count} 个项目 ({count/len(enriched_stars)*100:.1f}%)")

    print("\n--- 主要编程语言分布 ---")
    for lang, count in language_counts.most_common(12):
        print(f"• {lang}: {count} 个项目")

    with open(ENRICHED_FILE, "w", encoding="utf-8") as f:
        json.dump(enriched_stars, f, ensure_ascii=False, indent=2)
    print(f"\nEnriched data successfully saved to: {ENRICHED_FILE}")
    return enriched_stars

if __name__ == "__main__":
    process_all_stars()
