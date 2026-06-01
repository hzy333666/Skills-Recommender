"""
GitHub Search API 封装模块

实现多维度搜索策略，计算 star velocity，过滤低质量项目。
"""

import os
import time
import requests
from datetime import datetime, timedelta
from typing import Optional


class GitHubSearcher:
    """GitHub Search API 客户端"""

    BASE_URL = "https://api.github.com/search/repositories"

    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv("GITHUB_TOKEN", "")
        self.headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            self.headers["Authorization"] = f"Bearer {self.token}"
        self.rate_limit_remaining = 30
        self.rate_limit_reset = 0

    def _handle_rate_limit(self, response: requests.Response):
        """处理速率限制"""
        self.rate_limit_remaining = int(
            response.headers.get("X-RateLimit-Remaining", 30)
        )
        self.rate_limit_reset = int(response.headers.get("X-RateLimit-Reset", 0))
        if self.rate_limit_remaining <= 1:
            wait_time = max(0, self.rate_limit_reset - time.time()) + 1
            print(f"⏳ Rate limit 接近上限，等待 {wait_time:.0f} 秒...")
            time.sleep(wait_time)

    def search(self, query: str, sort: str = "stars", per_page: int = 30) -> list[dict]:
        """
        执行 GitHub Search API 查询

        Args:
            query: 搜索查询字符串
            sort: 排序方式 (stars, forks, updated)
            per_page: 每页结果数（最大 100）

        Returns:
            仓库列表
        """
        params = {
            "q": query,
            "sort": sort,
            "order": "desc",
            "per_page": min(per_page, 100),
        }

        try:
            response = self.get(self.BASE_URL, params=params)
            self._handle_rate_limit(response)
            response.raise_for_status()
            data = response.json()
            return data.get("items", [])
        except requests.RequestException as e:
            print(f"❌ GitHub API 请求失败: {e}")
            return []

    def get(self, url: str, params: dict | None = None) -> requests.Response:
        """发送 GET 请求"""
        return requests.get(url, headers=self.headers, params=params, timeout=30)

    def calculate_star_velocity(self, repo: dict) -> float:
        """
        计算 star velocity（星速）= stars / days_since_creation

        衡量项目爆火程度的指标
        """
        stars = repo.get("stargazers_count", 0)
        created_at = repo.get("created_at", "")
        if not created_at:
            return 0.0
        created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        now = datetime.now(created.tzinfo)
        days = max(1, (now - created).days)
        return round(stars / days, 2)

    def enrich_repo(self, repo: dict) -> dict:
        """
        丰富仓库数据，添加计算字段
        """
        return {
            "name": repo.get("full_name", ""),
            "description": repo.get("description", "") or "",
            "url": repo.get("html_url", ""),
            "stars": repo.get("stargazers_count", 0),
            "forks": repo.get("forks_count", 0),
            "language": repo.get("language", "") or "",
            "topics": repo.get("topics", []),
            "created_at": repo.get("created_at", ""),
            "updated_at": repo.get("updated_at", ""),
            "pushed_at": repo.get("pushed_at", ""),
            "license": (repo.get("license") or {}).get("spdx_id", ""),
            "open_issues": repo.get("open_issues_count", 0),
            "star_velocity": self.calculate_star_velocity(repo),
            "archived": repo.get("archived", False),
            "fork": repo.get("fork", False),
        }

    def is_quality_project(
        self,
        repo: dict,
        min_stars: int = 500,
        max_days_since_update: int = 30,
        exclude_topics: list[str] | None = None,
        exclude_name_patterns: list[str] | None = None,
    ) -> bool:
        """
        质量过滤器

        Args:
            repo: 仓库数据
            min_stars: 最低 star 数
            max_days_since_update: 最近更新天数上限
            exclude_topics: 排除的 topics
            exclude_name_patterns: 排除的名称模式

        Returns:
            是否通过质量检查
        """
        # 排除归档和 fork 项目
        if repo.get("archived") or repo.get("fork"):
            return False

        # star 数检查
        if repo.get("stargazers_count", 0) < min_stars:
            return False

        # 更新时间检查
        updated_at = repo.get("updated_at") or repo.get("pushed_at", "")
        if updated_at:
            updated = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
            now = datetime.now(updated.tzinfo)
            if (now - updated).days > max_days_since_update:
                return False

        # 排除特定 topics
        topics = set(repo.get("topics", []))
        if exclude_topics and topics & set(exclude_topics):
            return False

        # 排除特定名称模式
        name = repo.get("full_name", "").lower()
        if exclude_name_patterns:
            for pattern in exclude_name_patterns:
                if pattern.lower() in name:
                    return False

        return True


def prepare_search_queries(config: dict) -> list[dict]:
    """
    根据配置准备搜索查询列表

    Args:
        config: 配置字典，包含 SEARCH_STRATEGIES

    Returns:
        准备好的查询列表
    """
    today = datetime.now()
    date_7d_ago = (today - timedelta(days=7)).strftime("%Y-%m-%d")
    date_30d_ago = (today - timedelta(days=30)).strftime("%Y-%m-%d")

    queries = []
    for strategy in config.get("SEARCH_STRATEGIES", []):
        query = strategy["query"]
        # 替换日期占位符
        query = query.replace("{date_7d_ago}", date_7d_ago)
        query = query.replace("{date_30d_ago}", date_30d_ago)
        queries.append({
            "name": strategy["name"],
            "description": strategy["description"],
            "query": query,
            "sort": strategy.get("sort", "stars"),
            "per_page": strategy.get("per_page", 30),
        })
    return queries


def run_search(config: dict) -> list[dict]:
    """
    执行完整的搜索流程

    Args:
        config: 配置字典

    Returns:
        去重后的仓库列表（已丰富数据）
    """
    searcher = GitHubSearcher()
    queries = prepare_search_queries(config)

    all_repos = {}  # 用 name 去重
    quality_config = config.get("QUALITY_THRESHOLDS", {})
    exclude_topics = config.get("EXCLUDE_TOPICS", [])
    exclude_name_patterns = config.get("EXCLUDE_KEYWORDS_IN_NAME", [])

    for q in queries:
        print(f"🔍 搜索: {q['name']} - {q['description']}")
        print(f"   查询: {q['query']}")

        items = searcher.search(
            query=q["query"],
            sort=q["sort"],
            per_page=q["per_page"],
        )

        count = 0
        for repo in items:
            enriched = searcher.enrich_repo(repo)

            # 去重
            if enriched["name"] in all_repos:
                continue

            # 质量过滤（宽松模式：只检查基本条件，star_velocity 在后续分析中使用）
            if not searcher.is_quality_project(
                repo,
                min_stars=quality_config.get("min_stars", 100),
                max_days_since_update=quality_config.get("max_days_since_update", 30),
                exclude_topics=exclude_topics,
                exclude_name_patterns=exclude_name_patterns,
            ):
                continue

            all_repos[enriched["name"]] = enriched
            count += 1

        print(f"   ✅ 找到 {count} 个符合条件的项目")

        # 避免触发速率限制
        time.sleep(2)

    # 按 star_velocity 排序
    repos = sorted(
        all_repos.values(),
        key=lambda r: r["star_velocity"],
        reverse=True,
    )

    print(f"\n📊 总计找到 {len(repos)} 个不重复的高质量项目")
    return repos
