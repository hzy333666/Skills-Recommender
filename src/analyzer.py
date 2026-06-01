"""
AI 分析引擎模块

使用 OpenAI 兼容 API（如 Mimo）对 GitHub 项目进行智能分析，
基于 Vibe Coder 画像生成结构化评价。
"""

import os
import json
import time
from typing import Optional
from openai import OpenAI


def create_analysis_prompt(repos: list[dict], vibe_coder_profile: str) -> str:
    """
    创建分析 Prompt

    Args:
        repos: 仓库列表
        vibe_coder_profile: Vibe Coder 画像描述

    Returns:
        完整的 Prompt 字符串
    """
    repos_text = ""
    for i, repo in enumerate(repos, 1):
        repos_text += f"""
---
项目 {i}:
- 名称: {repo['name']}
- 描述: {repo['description']}
- 链接: {repo['url']}
- Star 数: {repo['stars']}
- 语言: {repo['language']}
- Topics: {', '.join(repo['topics']) if repo['topics'] else '无'}
- 创建时间: {repo['created_at']}
- 最近更新: {repo['updated_at']}
- Star Velocity: {repo['star_velocity']} stars/day
---
"""

    return f"""你是一个 Skills 推荐专家。请根据以下用户画像，分析每个 GitHub 项目是否适合该用户。

{vibe_coder_profile}

请对以下项目逐一分析，返回 JSON 数组。每个项目需要包含：

1. **name**: 项目名称（保持原样）
2. **category**: 最匹配的类别标签，必须是以下之一：
   - "🤖 AI 编码工具链"
   - "🚀 AI 协作增强"
   - "🧱 全栈积木"
   - "🎨 设计到代码"
   - "⚙️ DevOps 自动化"
   - "📱 移动端效率"
3. **summary**: 一句话中文简介（不超过 50 字）
4. **use_cases**: 适用场景列表（2-3 个，中文）
5. **vibe_coder_score**: 适合 Vibe Coder 的评分（1-10 分，10 分最相关）
6. **vibe_coder_reason**: 为什么适合/不适合 Vibe Coder（一句话，中文）
7. **highlight**: 最值得关注的亮点（一句话，中文）

评分标准：
- 9-10 分：Vibe Coder 必备工具，直接提升 AI 编码效率
- 7-8 分：非常相关，能加速开发流程
- 5-6 分：有一定相关性，特定场景有用
- 3-4 分：相关性较低，但可能有参考价值
- 1-2 分：不相关，不建议关注

请严格返回 JSON 数组格式，不要添加其他文字。示例：
```json
[
  {{
    "name": "owner/repo",
    "category": "🤖 AI 编码工具链",
    "summary": "一句话简介",
    "use_cases": ["场景1", "场景2"],
    "vibe_coder_score": 8.5,
    "vibe_coder_reason": "原因",
    "highlight": "亮点"
  }}
]

以下是待分析的项目：

{repos_text}
"""


def create_client() -> OpenAI:
    """
    创建 OpenAI 兼容客户端

    Returns:
        OpenAI 客户端实例
    """
    api_key = os.getenv("AI_API_KEY", "")
    base_url = os.getenv("AI_BASE_URL", "https://token-plan-cn.xiaomimimo.com/v1")

    if not api_key:
        raise ValueError("未设置 AI_API_KEY 环境变量")

    return OpenAI(api_key=api_key, base_url=base_url)


def analyze_batch(
    client: OpenAI,
    repos: list[dict],
    vibe_coder_profile: str,
    model: str = "mimo-v2.5-pro",
    max_tokens: int = 4096,
) -> list[dict]:
    """
    分析一批项目

    Args:
        client: OpenAI 客户端
        repos: 仓库列表
        vibe_coder_profile: Vibe Coder 画像
        model: 使用的模型
        max_tokens: 最大 token 数

    Returns:
        分析结果列表
    """
    prompt = create_analysis_prompt(repos, vibe_coder_profile)

    try:
        response = client.chat.completions.create(
            model=model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )

        response_text = response.choices[0].message.content

        # 提取 JSON（处理可能的 markdown 代码块）
        if "```json" in response_text:
            json_str = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            json_str = response_text.split("```")[1].split("```")[0].strip()
        else:
            json_str = response_text.strip()

        results = json.loads(json_str)
        return results if isinstance(results, list) else [results]

    except json.JSONDecodeError as e:
        print(f"JSON 解析失败: {e}")
        print(f"   原始响应: {response_text[:200]}...")
        return []
    except Exception as e:
        print(f"分析失败: {e}")
        return []


def analyze_repos(repos: list[dict], config: dict) -> list[dict]:
    """
    分析所有仓库

    Args:
        repos: 仓库列表
        config: 配置字典

    Returns:
        合并后的分析结果列表
    """
    try:
        client = create_client()
    except ValueError as e:
        print(f"  {e}")
        return []

    analysis_config = config.get("ANALYSIS_CONFIG", {})
    vibe_coder_profile = config.get("VIBE_CODER_PROFILE", "")

    model = analysis_config.get("model", "mimo-v2.5-pro")
    max_tokens = analysis_config.get("max_tokens", 4096)
    batch_size = analysis_config.get("batch_size", 5)
    max_projects = analysis_config.get("max_projects_per_run", 20)

    # 限制分析数量
    repos_to_analyze = repos[:max_projects]
    print(f"  开始 AI 分析，共 {len(repos_to_analyze)} 个项目...")

    all_results = []

    # 分批处理
    for i in range(0, len(repos_to_analyze), batch_size):
        batch = repos_to_analyze[i : i + batch_size]
        batch_num = i // batch_size + 1
        total_batches = (len(repos_to_analyze) + batch_size - 1) // batch_size

        print(f"   处理批次 {batch_num}/{total_batches} ({len(batch)} 个项目)...")

        results = analyze_batch(
            client=client,
            repos=batch,
            vibe_coder_profile=vibe_coder_profile,
            model=model,
            max_tokens=max_tokens,
        )

        all_results.extend(results)

        # 避免 API 速率限制
        if i + batch_size < len(repos_to_analyze):
            time.sleep(1)

    print(f"  分析完成，共 {len(all_results)} 个项目获得评价")

    # 合并原始数据和分析结果
    enriched_results = merge_analysis(repos_to_analyze, all_results)
    return enriched_results


def merge_analysis(repos: list[dict], analyses: list[dict]) -> list[dict]:
    """
    合并原始仓库数据和 AI 分析结果

    Args:
        repos: 原始仓库列表
        analyses: AI 分析结果列表

    Returns:
        合并后的列表
    """
    # 建立分析结果的索引（按名称）
    analysis_map = {}
    for a in analyses:
        name = a.get("name", "")
        if name:
            analysis_map[name] = a

    merged = []
    for repo in repos:
        name = repo["name"]
        analysis = analysis_map.get(name, {})

        merged_repo = {
            **repo,
            "category": analysis.get("category", "未分类"),
            "summary": analysis.get("summary", repo.get("description", "")),
            "use_cases": analysis.get("use_cases", []),
            "vibe_coder_score": analysis.get("vibe_coder_score", 0),
            "vibe_coder_reason": analysis.get("vibe_coder_reason", ""),
            "highlight": analysis.get("highlight", ""),
        }
        merged.append(merged_repo)

    # 按 vibe_coder_score 排序
    merged.sort(key=lambda r: r.get("vibe_coder_score", 0), reverse=True)
    return merged
