"""登录模块测试用例 — P0。"""

import re
import allure
import pytest
from pages.login_page import LoginPage


@allure.epic("ShopEasy 前台")
@allure.feature("用户认证")
class TestLogin:
    """登录功能测试集。"""

    # ── F-TC-001: 新用户注册成功 ─────────────────────────
    # ⚠️ 条件可自动化 — 需动态用户名，注册页输入框需确认

    # ── F-TC-002: buyer1 正常登录 ─────────────────────────

    @allure.story("F-TC-002: buyer1 正常登录成功")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p0
    @pytest.mark.smoke
    def test_buyer1_login_success(self, login_page: LoginPage, base_url: str):
        """buyer1 登录成功，导航栏显示"张三"。"""
        login_page.open(base_url)
        login_page.assert_page_loaded()
        login_page.login("buyer1", "123456")
        login_page.assert_login_success("张三")

    # ── F-TC-003: 禁用用户登录拦截 ───────────────────────

    @allure.story("F-TC-003: 禁用用户登录返回 403")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p0
    def test_disabled_user_login_blocked(self, login_page: LoginPage, base_url: str):
        """⚠️ 条件可自动化 — 方案 A：URL 未变化间接验证登录失败。"""
        login_page.open(base_url)
        login_page.assert_page_loaded()
        login_page.login("disabled_user", "123456")
        login_page.assert_login_failed()

    # ── F-TC-004: 错误密码登录失败 ───────────────────────

    @allure.story("F-TC-004: 错误密码登录失败")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p0
    @pytest.mark.smoke
    def test_wrong_password_login_fail(self, login_page: LoginPage, base_url: str):
        """错误密码登录失败，URL 仍在 /login。"""
        login_page.open(base_url)
        login_page.assert_page_loaded()
        login_page.login("buyer1", "wrong_password")
        login_page.assert_login_failed()

    # ── F-TC-005: buyer2 正常登录 ─────────────────────────

    @allure.story("F-TC-005: buyer2 正常登录成功")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p0
    @pytest.mark.smoke
    def test_buyer2_login_success(self, login_page: LoginPage, base_url: str):
        """buyer2 登录成功，导航栏显示"李四"。"""
        login_page.open(base_url)
        login_page.assert_page_loaded()
        login_page.login("buyer2", "123456")
        login_page.assert_login_success("李四")