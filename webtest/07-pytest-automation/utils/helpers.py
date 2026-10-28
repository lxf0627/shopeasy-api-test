"""辅助工具函数模块。"""

import allure
import re


@allure.step("等待 Toast 消息: {expected_text}")
def wait_for_toast(page, expected_text: str, timeout: int = 5000):
    """等待页面 Toast/Alert 消息出现并返回。

    Args:
        page: Playwright Page 对象。
        expected_text: 期望的 Toast 文本。
        timeout: 超时时间（毫秒）。
    """
    toast = page.locator(f"text={expected_text}")
    toast.wait_for(state="visible", timeout=timeout)
    return toast


def extract_price(text: str) -> float:
    """从文本中提取价格数值。

    Args:
        text: 包含价格的文本，如 "¥9999"。

    Returns:
        浮点数价格。
    """
    match = re.search(r"[\d,.]+", text.replace(",", ""))
    return float(match.group()) if match else 0.0


def generate_unique_username(prefix: str = "testuser") -> str:
    """生成唯一用户名。

    Args:
        prefix: 用户名前缀。

    Returns:
        带时间戳后缀的用户名。
    """
    import time
    return f"{prefix}_{int(time.time())}"