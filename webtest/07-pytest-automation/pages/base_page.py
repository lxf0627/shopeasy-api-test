"""基础页面类 — 封装 Playwright 常用操作。"""

import re
import allure
from playwright.sync_api import Page, expect


class BasePage:
    """所有 Page Object 的基类。"""

    def __init__(self, page: Page):
        self.page = page
        self.page.set_default_timeout(10000)

    # ── 导航 ──────────────────────────────────────────────

    @allure.step("导航到 {url}")
    def navigate(self, url: str):
        """打开指定 URL 并等待页面加载完成。"""
        self.page.goto(url, wait_until="domcontentloaded")
        self.page.wait_for_load_state("domcontentloaded")

    @allure.step("等待页面加载")
    def wait_for_load(self):
        """等待页面 DOM 内容加载完成。"""
        self.page.wait_for_load_state("domcontentloaded")

    # ── 元素操作 ──────────────────────────────────────────

    @allure.step("点击元素: {description}")
    def click(self, locator, description: str = ""):
        """点击元素并等待其可见。"""
        locator.wait_for(state="visible")
        locator.click()

    @allure.step("填写文本: {text}")
    def fill(self, locator, text: str, description: str = ""):
        """清空输入框并填写文本。"""
        locator.wait_for(state="visible")
        locator.fill(text)

    @allure.step("选择下拉选项: {value}")
    def select_option(self, locator, value: str):
        """在下拉框中选择指定值。"""
        locator.wait_for(state="visible")
        locator.select_option(value)

    # ── 断言 ──────────────────────────────────────────────

    @allure.step("断言元素可见")
    def assert_visible(self, locator, timeout: int = 5000):
        """断言元素在页面上可见。"""
        expect(locator).to_be_visible(timeout=timeout)

    @allure.step("断言元素不可见")
    def assert_not_visible(self, locator, timeout: int = 5000):
        """断言元素在页面上不可见。"""
        expect(locator).not_to_be_visible(timeout=timeout)

    @allure.step("断言元素文本包含: {text}")
    def assert_contains_text(self, locator, text: str, timeout: int = 5000):
        """断言元素包含指定文本。"""
        expect(locator).to_contain_text(text, timeout=timeout)

    @allure.step("断言元素文本为: {text}")
    def assert_text(self, locator, text: str, timeout: int = 5000):
        """断言元素文本完全匹配。"""
        expect(locator).to_have_text(text, timeout=timeout)

    @allure.step("断言元素被禁用")
    def assert_disabled(self, locator, timeout: int = 5000):
        """断言元素处于禁用状态。"""
        expect(locator).to_be_disabled(timeout=timeout)

    @allure.step("断言元素启用")
    def assert_enabled(self, locator, timeout: int = 5000):
        """断言元素处于启用状态。"""
        expect(locator).to_be_enabled(timeout=timeout)

    @allure.step("断言 URL 包含: {url_part}")
    def assert_url_contains(self, url_part: str, timeout: int = 10000):
        """断言当前 URL 包含指定片段。"""
        expect(self.page).to_have_url(re.compile(re.escape(url_part)), timeout=timeout)

    @allure.step("断言 URL 为: {url}")
    def assert_url(self, url: str, timeout: int = 10000):
        """断言当前 URL 完全匹配。"""
        expect(self.page).to_have_url(url, timeout=timeout)

    @allure.step("断言页面标题包含: {title}")
    def assert_title_contains(self, title: str):
        """断言页面标题包含指定文本。"""
        expect(self.page).to_have_title(f"*{title}*")

    # ── 截图 ──────────────────────────────────────────────

    def take_screenshot(self, name: str = "screenshot"):
        """截图并附加到 Allure 报告。"""
        screenshot = self.page.screenshot()
        allure.attach(
            screenshot,
            name=name,
            attachment_type=allure.attachment_type.PNG,
        )
        return screenshot

    # ── 弹窗处理 ──────────────────────────────────────────

    @allure.step("处理确认弹窗: 点击 {accept_text}")
    def handle_dialog(self, accept: bool = True, accept_text: str = "确定"):
        """处理系统弹窗（alert/confirm/prompt）。"""
        self.page.on("dialog", lambda dialog: (
            dialog.accept() if accept else dialog.dismiss()
        ))

    @allure.step("点击弹窗中的 {button_text}")
    def click_dialog_button(self, button_text: str):
        """点击模态对话框中的指定按钮。"""
        dialog = self.page.get_by_role("dialog")
        dialog.wait_for(state="visible")
        dialog.get_by_role("button", name=button_text).click()

    # ── 等待 ──────────────────────────────────────────────

    @allure.step("等待元素消失")
    def wait_for_disappear(self, locator, timeout: int = 10000):
        """等待元素从页面消失。"""
        locator.wait_for(state="hidden", timeout=timeout)

    @allure.step("等待 URL 变化")
    def wait_for_url_change(self, url_part: str, timeout: int = 10000):
        """等待 URL 包含指定片段。"""
        self.page.wait_for_url(f"**{url_part}**", timeout=timeout)