"""
通知推送模块

支持 Server酱 微信推送。
"""

import os
import requests


def send_serverchan(title: str, content: str, sendkey: str | None = None) -> bool:
    """
    通过 Server酱 发送微信推送

    Args:
        title: 消息标题（显示在微信通知中）
        content: 消息正文（支持 Markdown）
        sendkey: Server酱 SendKey，不传则从环境变量读取

    Returns:
        是否发送成功
    """
    sendkey = sendkey or os.getenv("SERVERCHAN_SENDKEY", "")
    if not sendkey:
        print("  未设置 SERVERCHAN_SENDKEY，跳过微信推送")
        return False

    url = f"https://sctapi.ftqq.com/{sendkey}.send"
    data = {
        "title": title,
        "content": content,
    }

    try:
        resp = requests.post(url, data=data, timeout=30)
        result = resp.json()
        if result.get("code") == 0:
            print("  微信推送成功")
            return True
        else:
            print(f"  微信推送失败: {result.get('message', '未知错误')}")
            return False
    except Exception as e:
        print(f"  微信推送异常: {e}")
        return False


def send_daily_report(report_content: str, date_str: str) -> bool:
    """
    推送每日简报

    Args:
        report_content: 简报 Markdown 内容
        date_str: 日期字符串

    Returns:
        是否发送成功
    """
    title = f"Skills Daily - {date_str}"

    # Server酱 内容有长度限制，截取前 4000 字符
    content = report_content[:4000]
    if len(report_content) > 4000:
        content += "\n\n... (内容已截断，完整版见本地文件)"

    return send_serverchan(title, content)
