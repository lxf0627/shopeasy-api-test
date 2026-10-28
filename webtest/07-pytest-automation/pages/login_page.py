"""登录页面对象。"""

import allure
from playwright.sync_api import Page, expect
from pages.base_page import BasePage


class LoginPage(BasePage):
    """登录页 /login 的页面对象。"""

    PATH = "/login"

    def __init__(self, page: Page):
        super().__init__(page)

    # ── 定位器 ────────────────────────────────────────────

    @property
    def username_input(self):
        return self.page.get_by_role("textbox", name="用户名")

    @property
    def password_input(self):
        return self.page.get_by_role("textbox", name="密码")

    @property
    def login_button(self):
        return self.page.get_by_role("button", name="登录")

    @property
    def register_link(self):
        return self.page.get_by_role("link", name="还没有账号？立即注册")

    # ── 操作 ──────────────────────────────────────────────

    @allure.step("打开登录页")
    def open(self, base_url: str):
        """导航到登录页。"""
        self.navigate(f"{base_url}{self.PATH}")

    @allure.step("输入用户名: {username}")
    def input_username(self, username: str):
        self.fill(self.username_input, username)

    @allure.step("输入密码")
    def input_password(self, password: str):
        self.fill(self.password_input, password)

    @allure.step("点击登录按钮")
    def click_login(self):
        self.click(self.login_button)

    @allure.step("执行登录: {username}")
    def login(self, username: str, password: str):
        """完整登录流程。"""
        self.input_username(username)
        self.input_password(password)
        self.click_login()

    # ── 断言 ──────────────────────────────────────────────

    @allure.step("断言登录页已加载")
    def assert_page_loaded(self):
        self.assert_visible(self.username_input)
        self.assert_visible(self.password_input)
        self.assert_visible(self.login_button)

    @allure.step("断言登录成功（导航栏显示: {nickname}）")
    def assert_login_success(self, nickname: str):
        """断言登录成功 — 导航栏出现用户昵称。"""
        user_btn = self.page.get_by_role("button", name=nickname)
        expect(user_btn).to_be_visible(timeout=10000)

    @allure.step("断言登录失败（仍在登录页）")
    def assert_login_failed(self):
        """断言登录失败 — URL 仍包含 /login。"""
        import re
        from playwright.sync_api import expect
        expect(self.page).to_have_url(re.compile(r"/login"), timeout=10000)

    @allure.step("断言登录失败提示: {message}")
    def assert_login_error_message(self, message: str):
        """断言页面显示错误提示。"""
        error = self.page.get_by_text(message)
        expect(error).to_be_visible(timeout=5000)