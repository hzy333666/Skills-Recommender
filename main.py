"""
Skills-Recommender 主入口

串联搜索 → 分析 → 生成简报的完整流程。
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加项目根目录到 path
sys.path.insert(0, str(Path(__file__).parent))

import config
from src.github_searcher import run_search
from src.analyzer import analyze_repos
from src.report_generator import generate_report, save_report
from src.notifier import send_daily_report


def save_snapshot(repos: list[dict], date_str: str):
    """
    保存当日快照数据，用于后续对比 star 增长

    Args:
        repos: 仓库列表
        date_str: 日期字符串
    """
    snapshot_dir = os.path.join("data", "snapshots")
    os.makedirs(snapshot_dir, exist_ok=True)

    filepath = os.path.join(snapshot_dir, f"{date_str}.json")
    snapshot = {
        "date": date_str,
        "repos": {
            repo["name"]: {
                "stars": repo["stars"],
                "star_velocity": repo["star_velocity"],
            }
            for repo in repos
        },
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2)

    print(f"💾 快照已保存: {filepath}")


def load_previous_snapshot(date_str: str) -> dict | None:
    """
    加载前一天的快照数据

    Args:
        date_str: 当天日期字符串

    Returns:
        前一天的快照数据，或 None
    """
    from datetime import timedelta

    snapshot_dir = os.path.join("data", "snapshots")
    prev_date = (datetime.strptime(date_str, "%Y-%m-%d") - timedelta(days=1)).strftime(
        "%Y-%m-%d"
    )
    filepath = os.path.join(snapshot_dir, f"{prev_date}.json")

    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def add_star_delta(repos: list[dict], prev_snapshot: dict | None) -> list[dict]:
    """
    添加 star 增长数据（与前一天对比）

    Args:
        repos: 当天仓库列表
        prev_snapshot: 前一天的快照数据

    Returns:
        添加了 star_delta 字段的仓库列表
    """
    if not prev_snapshot:
        return repos

    prev_repos = prev_snapshot.get("repos", {})
    for repo in repos:
        name = repo["name"]
        if name in prev_repos:
            prev_stars = prev_repos[name].get("stars", 0)
            repo["star_delta"] = repo["stars"] - prev_stars
        else:
            repo["star_delta"] = 0  # 新项目

    return repos


def main():
    """主流程"""
    print("=" * 60)
    print("🎯 Skills-Recommender — 每日 Skills 简报生成器")
    print("=" * 60)
    print()

    date_str = datetime.now().strftime("%Y-%m-%d")
    print(f"📅 日期: {date_str}")
    print()

    # Step 1: 搜索
    print("━" * 40)
    print("Step 1/5: GitHub 搜索")
    print("━" * 40)
    repos = run_search(vars(config))

    if not repos:
        print("⚠️ 未找到任何符合条件的项目，流程结束")
        return

    # Step 2: 对比历史数据
    print()
    print("━" * 40)
    print("Step 2/5: 历史数据对比")
    print("━" * 40)
    prev_snapshot = load_previous_snapshot(date_str)
    if prev_snapshot:
        repos = add_star_delta(repos, prev_snapshot)
        print(f"📈 已加载前一天快照，对比 star 增长")
    else:
        print("📭 无前一天快照，跳过对比")

    # Step 3: AI 分析
    print()
    print("━" * 40)
    print("Step 3/5: AI 分析")
    print("━" * 40)
    analyzed_repos = analyze_repos(repos, vars(config))

    # Step 4: 生成简报
    print()
    print("━" * 40)
    print("Step 4/5: 生成简报")
    print("━" * 40)
    report_content = generate_report(analyzed_repos, vars(config), date_str)
    report_path = save_report(report_content, vars(config), date_str)

    # 保存快照
    save_snapshot(repos, date_str)

    # Step 5: 微信推送
    print()
    print("━" * 40)
    print("Step 5/5: 微信推送")
    print("━" * 40)
    send_daily_report(report_content, date_str)

    print()
    print("=" * 60)
    print(f"✅ 完成！简报已生成: {report_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
