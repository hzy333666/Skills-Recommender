# 🎯 Skills-Recommender

为 **Vibe Coder** 量身定制的每日 Skills 简报自动化工具。

自动从 GitHub 搜索当日最热门的 Skills 和项目，经过 AI 分析筛选后生成每日简报。

## 🚀 功能特点

- **多维度搜索**：AI 编码工具链、全栈积木、设计到代码、DevOps、移动端
- **智能筛选**：基于 Vibe Coder 画像的 AI 分析，只推荐真正适合你的项目
- **每日自动**：Windows Task Scheduler 定时运行，每天早上推送简报
- **结构化简报**：Markdown 格式，包含名称、简介、适用场景、Vibe Coder 评分

## 📋 前置条件

- Python 3.10+
- GitHub Personal Access Token（[生成地址](https://github.com/settings/tokens)）
- Anthropic API Key（[获取地址](https://console.anthropic.com/)）

## 🛠️ 安装

```bash
# 克隆项目
cd G:\Skills-Recommender

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入你的 Token 和 API Key
```

## 📖 使用

### 手动运行

```bash
python main.py
```

### 定时运行

```bash
# 创建 Windows 定时任务（每天 8:00 AM）
run_daily.bat
```

简报输出到 `reports/` 目录，格式为 `YYYY-MM-DD.md`。

## 📁 项目结构

```
├── config.py                 # 筛选配置（维度、关键词、门槛）
├── main.py                   # 主入口
├── src/
│   ├── github_searcher.py    # GitHub Search API 封装
│   ├── analyzer.py           # Claude API 分析引擎
│   └── report_generator.py   # Markdown 简报生成
├── reports/                  # 每日简报输出
├── data/snapshots/           # 历史数据（star 对比）
├── .env.example              # 环境变量模板
└── requirements.txt
```

## ⚙️ 配置

编辑 `config.py` 自定义：
- 筛选维度和关键词
- 质量门槛（star 数、活跃度）
- 搜索策略
- AI 分析参数
