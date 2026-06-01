"""
简报生成模块（精简版）

将 AI 分析结果格式化为紧凑的 Markdown 每日简报。
"""

import os
from datetime import datetime
from collections import defaultdict


def generate_report(
    repos: list[dict],
    config: dict,
    date_str: str | None = None,
) -> str:
    """
    生成精简版 Markdown 每日简报

    Args:
        repos: 已分析的仓库列表
        config: 配置字典
        date_str: 日期字符串（默认今天）

    Returns:
        Markdown 格式的简报内容
    """
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")

    report_config = config.get("REPORT_CONFIG", {})
    max_per_dimension = report_config.get("max_projects_per_dimension", 5)
    dimensions = config.get("DIMENSIONS", [])

    # 按类别分组
    categorized = defaultdict(list)
    for repo in repos:
        category = repo.get("category", "未分类")
        categorized[category].append(repo)

    # 构建简报
    lines = []

    # 标题
    lines.append(f"# Skills Daily — {date_str}")
    lines.append("")

    # 统计概览
    total = len(repos)
    category_stats = []
    for dim in dimensions:
        emoji = dim["emoji"]
        name = dim["name"]
        full_name = f"{emoji} {name}"
        count = len(categorized.get(full_name, []))
        if count > 0:
            category_stats.append(f"{emoji}{count}")

    lines.append(f"共 {total} 个项目 | {' '.join(category_stats)}")
    lines.append("")

    # 按维度优先级输出
    for dim in dimensions:
        emoji = dim["emoji"]
        name = dim["name"]
        full_name = f"{emoji} {name}"
        dim_repos = categorized.get(full_name, [])

        if not dim_repos:
            continue

        lines.append(f"## {emoji} {name}")
        lines.append("")

        # 每个维度取 top N
        for repo in dim_repos[:max_per_dimension]:
            score = repo.get("vibe_coder_score", 0)
            stars = repo.get("stars", 0)
            velocity = repo.get("star_velocity", 0)
            summary = repo.get("summary", "")
            highlight = repo.get("highlight", "")

            # 评分标记
            if score >= 9:
                mark = "🔥"
            elif score >= 7:
                mark = "⭐"
            else:
                mark = "·"

            # 名称 + 评分
            lines.append(f"{mark} [{repo['name']}]({repo['url']})  `{score}/10`")

            # 一行信息：star + 速度 + 简介
            info = f"⭐{stars:,}"
            if velocity > 0:
                info += f" (+{velocity:.0f}/d)"
            if summary:
                info += f" — {summary}"
            lines.append(info)

            # 亮点（如有）
            if highlight:
                lines.append(f"  💡 {highlight}")

            lines.append("")

    # 尾部
    lines.append(f"*Skills-Recommender · {datetime.now().strftime('%H:%M')}*")

    return "\n".join(lines)


def save_report(content: str, config: dict, date_str: str | None = None) -> str:
    """
    保存简报到文件

    Args:
        content: 简报内容
        config: 配置字典
        date_str: 日期字符串

    Returns:
        保存的文件路径
    """
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")

    report_config = config.get("REPORT_CONFIG", {})
    output_dir = report_config.get("output_dir", "reports")

    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    filename = f"{date_str}.md"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"📄 简报已保存: {filepath}")
    return filepath
