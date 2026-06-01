"""
Skills-Recommender 配置文件

Vibe Coder 画像配置：定义筛选维度、关键词、质量门槛
"""

# ============================================================
# 筛选维度配置（按优先级排序）
# ============================================================

DIMENSIONS = [
    {
        "name": "AI 编码工具链",
        "emoji": "🤖",
        "priority": 3,
        "description": "Claude Code Skills、Cursor Rules、MCP Servers、AI Agent 框架",
        "keywords": [
            "claude-code", "mcp-server", "cursor-rules", "ai-coding",
            "agent", "mcp", "model-context-protocol", "claude",
            "ai-agent", "llm-tools", "code-generation",
        ],
        "topics": [
            "mcp-server", "model-context-protocol", "claude-code",
            "ai-agent", "llm-tools", "ai-coding",
        ],
    },
    {
        "name": "AI 协作增强",
        "emoji": "🚀",
        "priority": 3,
        "description": "Prompt 模板、上下文管理、代码审查 AI",
        "keywords": [
            "prompt-engineering", "code-review", "context-management",
            "ai-prompt", "prompt-template", "cursor",
        ],
        "topics": [
            "prompt-engineering", "cursor", "ai-prompt",
        ],
    },
    {
        "name": "全栈积木",
        "emoji": "🧱",
        "priority": 2,
        "description": "SaaS 模板、API 快速搭建、ORM、认证支付",
        "keywords": [
            "saas-template", "api", "orm", "auth", "payment",
            "boilerplate", "starter", "fullstack", "nextjs",
        ],
        "topics": [
            "saas-template", "boilerplate", "starter-template",
            "fullstack", "api", "orm",
        ],
    },
    {
        "name": "设计到代码",
        "emoji": "🎨",
        "priority": 2,
        "description": "设计稿转代码、UI 生成、原型工具",
        "keywords": [
            "design-to-code", "ui-generator", "figma",
            "prototype", "tailwind", "component-library",
        ],
        "topics": [
            "design-to-code", "ui-generator", "figma",
            "component-library",
        ],
    },
    {
        "name": "DevOps 自动化",
        "emoji": "⚙️",
        "priority": 1,
        "description": "部署、监控、日志、数据库管理",
        "keywords": [
            "deployment", "monitoring", "devops", "infrastructure",
            "docker", "kubernetes", "ci-cd", "database",
        ],
        "topics": [
            "devops", "deployment", "monitoring", "infrastructure",
        ],
    },
    {
        "name": "移动端效率",
        "emoji": "📱",
        "priority": 1,
        "description": "跨平台框架、移动开发工具",
        "keywords": [
            "react-native", "flutter", "mobile", "cross-platform",
            "expo", "ios", "android",
        ],
        "topics": [
            "react-native", "flutter", "cross-platform", "mobile",
        ],
    },
]

# ============================================================
# 搜索策略配置
# ============================================================

SEARCH_STRATEGIES = [
    {
        "name": "近期爆火新项目",
        "description": "7 天内创建的高 star 项目",
        "query": "created:>{date_7d_ago} stars:>50",
        "sort": "stars",
        "per_page": 30,
    },
    {
        "name": "MCP 生态",
        "description": "Model Context Protocol 相关项目",
        "query": "mcp server in:name,description,readme",
        "sort": "stars",
        "per_page": 30,
    },
    {
        "name": "Claude Code 生态",
        "description": "Claude Code 相关项目",
        "query": "claude-code in:name,description,readme",
        "sort": "stars",
        "per_page": 30,
    },
    {
        "name": "AI Agent 工具",
        "description": "AI Agent 和 LLM 工具",
        "query": "ai agent in:name,description stars:>100",
        "sort": "stars",
        "per_page": 30,
    },
    {
        "name": "全栈/移动模板",
        "description": "SaaS 模板和跨平台框架",
        "query": "boilerplate starter template in:name,description stars:>200",
        "sort": "stars",
        "per_page": 30,
    },
]

# ============================================================
# 质量门槛
# ============================================================

QUALITY_THRESHOLDS = {
    "min_stars": 50,            # 最低 star 数（细分领域项目 star 普遍较低）
    "max_days_since_update": 60,  # 最近 60 天内有更新
    "min_star_velocity": 5,     # 最低星速（stars/day），用于筛选爆火项目
}

# ============================================================
# 排除规则
# ============================================================

EXCLUDE_TOPICS = [
    "awesome-list",        # 排除 awesome 列表
    "tutorial",            # 排除教程
    "learning",            # 排除学习资料
    "interview",           # 排除面试题
    "cheatsheet",          # 排除速查表
]

EXCLUDE_KEYWORDS_IN_NAME = [
    "awesome-",
    "-tutorial",
    "-examples",
    "-learning",
]

# ============================================================
# AI 分析配置
# ============================================================

ANALYSIS_CONFIG = {
    "model": "mimo-v2.5-pro",
    "max_tokens": 4096,
    "batch_size": 5,  # 每批分析的项目数
    "max_projects_per_run": 20,  # 每次运行最多分析的项目数
}

# ============================================================
# 报告配置
# ============================================================

REPORT_CONFIG = {
    "output_dir": "reports",
    "date_format": "%Y-%m-%d",
    "max_projects_per_dimension": 5,  # 每个维度最多展示的项目数
}

# ============================================================
# Vibe Coder 画像（用于 AI 分析的 Prompt）
# ============================================================

VIBE_CODER_PROFILE = """
用户画像：Vibe Coder（AI 交互编程爱好者）

核心特征：
- 主要通过与 AI 交互来编程（Claude Code、Cursor 等），不手写代码
- 独立开发者 / 全栈创业者
- 多项目并行，不限语言
- 关注效率和快速迭代

需求偏好：
- 优先关注能提升 AI 编码效率的工具（⭐⭐⭐）
- 其次是全栈积木和设计到代码（⭐⭐）
- 最后是 DevOps 和移动端（⭐）

适合的项目特征：
- 开箱即用，学习成本低
- 文档完善，社区活跃
- 能被 AI 工具（Claude Code、Cursor）直接使用或集成
- 能加速从想法到产品的过程
"""
