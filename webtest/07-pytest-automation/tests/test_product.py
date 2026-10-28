"""商品详情测试用例 — P1。"""

import re
import allure
import pytest
from playwright.sync_api import expect

from pages.product_page import ProductPage
from pages.login_page import LoginPage


@allure.epic("ShopEasy 前台")
@allure.feature("商品详情")
class TestProduct:
    """商品详情功能测试集。"""

    # ── F-TC-009: 规格-价格-库存联动 ─────────────────────

    @allure.story("F-TC-009: 选择全部规格后价格/库存联动更新")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p1
    def test_spec_price_stock联动(self, page, product_page: ProductPage, base_url: str):
        """选择规格后价格/库存联动更新。"""
        product_page.__init__(page)
        product_page.open(base_url, product_id=1)
        product_page.assert_page_loaded()

        # 初始状态 — 加入购物车按钮 disabled（未选全规格）
        product_page.assert_add_to_cart_disabled()

        # 选择第一个规格
        product_page.select_spec("256GB")
        page.wait_for_timeout(500)

        # 选择第二个规格
        product_page.select_spec("原色钛金属")
        page.wait_for_load_state("domcontentloaded")

        # 选择全部规格后按钮应启用
        product_page.assert_add_to_cart_enabled()
        product_page.assert_selected_spec("256GB")

    # ── F-TC-010: 未选全规格加入购物车 disabled ──────────

    @allure.story("F-TC-010: 未选全规格时加入购物车按钮 disabled")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p1
    def test_add_to_cart_disabled_without_full_spec(
        self, page, product_page: ProductPage, base_url: str
    ):
        """未选全规格时加入购物车按钮应 disabled。"""
        product_page.__init__(page)
        product_page.open(base_url, product_id=1)
        product_page.assert_page_loaded()
        product_page.assert_add_to_cart_disabled()

    # ── F-TC-011: 未登录加入购物车重定向 ─────────────────

    @allure.story("F-TC-011: 未登录点击加入购物车重定向到登录页")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p1
    def test_add_to_cart_redirect_to_login(
        self, page, product_page: ProductPage, base_url: str
    ):
        """未登录点击加入购物车，重定向到登录页。"""
        product_page.__init__(page)
        product_page.open(base_url, product_id=1)
        product_page.assert_page_loaded()

        # 选择全部规格
        product_page.select_spec("256GB")
        page.wait_for_timeout(300)
        product_page.select_spec("原色钛金属")
        page.wait_for_load_state("domcontentloaded")

        # 点击加入购物车
        product_page.click_add_to_cart()

        # 应重定向到登录页
        product_page.assert_url_contains("/login")

    # ── F-TC-012: 已登录加入购物车成功 ───────────────────

    @allure.story("F-TC-012: 已登录+已选规格，加入购物车成功")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p1
    def test_add_to_cart_success(
        self, logged_in_buyer1, product_page: ProductPage, base_url: str
    ):
        """已登录且已选规格，加入购物车成功。"""
        page = logged_in_buyer1
        product_page.__init__(page)
        product_page.open(base_url, product_id=1)
        product_page.assert_page_loaded()

        # 选择全部规格
        product_page.select_spec("256GB")
        page.wait_for_timeout(300)
        product_page.select_spec("原色钛金属")
        page.wait_for_load_state("domcontentloaded")

        # 点击加入购物车
        product_page.click_add_to_cart()

        # 验证 Toast 提示
        toast = page.get_by_text("已加入购物车")
        expect(toast).to_be_visible(timeout=5000)

    # ── F-TC-021 补充: 库存限制验证 ──────────────────────

    @allure.story("F-TC-021: 库存限制 — 数量选择器 max 属性")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p1
    def test_stock_limit_spinbutton_max(
        self, page, product_page: ProductPage, base_url: str
    ):
        """数量选择器 max 属性应等于库存值。"""
        product_page.__init__(page)
        product_page.open(base_url, product_id=1)
        product_page.assert_page_loaded()

        # 选择规格后验证 max 属性
        product_page.select_spec("256GB")
        page.wait_for_timeout(300)
        product_page.select_spec("原色钛金属")
        page.wait_for_load_state("domcontentloaded")

        spinbutton = product_page.quantity_input
        spinbutton.wait_for(state="visible")
        max_val = spinbutton.get_attribute("max")
        assert max_val is not None, "数量选择器应有 max 属性"
        assert int(max_val) > 0, "max 属性值应大于 0"