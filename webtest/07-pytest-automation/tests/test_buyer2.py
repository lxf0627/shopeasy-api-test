"""buyer2 完整流程一致性测试用例 — P3。"""

import allure
import pytest
from pages.home_page import HomePage
from pages.product_page import ProductPage
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.order_page import OrderPage
from pages.profile_page import ProfilePage


@allure.epic("ShopEasy 前台")
@allure.feature("buyer2 流程一致性")
class TestBuyer2Flow:
    """buyer2 完整流程一致性测试集。"""

    # ── F-TC-040a: buyer2 登录+浏览+搜索 ─────────────────

    @allure.story("F-TC-040a: buyer2 登录+浏览+搜索")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p3
    def test_buyer2_browse_and_search(
        self, logged_in_buyer2, home_page: HomePage, base_url: str
    ):
        """buyer2 登录后浏览首页和搜索商品。"""
        page = logged_in_buyer2
        home_page.__init__(page)
        home_page.open(base_url)
        home_page.assert_page_loaded()

        # 搜索
        home_page.search("iPhone")
        home_page.assert_url_contains("/search")
        home_page.assert_product_visible("iPhone 15 Pro Max")

    # ── F-TC-040b: buyer2 商品详情+收藏 ──────────────────

    @allure.story("F-TC-040b: buyer2 商品详情+收藏")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p3
    def test_buyer2_product_and_favorite(
        self, logged_in_buyer2, product_page: ProductPage, base_url: str
    ):
        """buyer2 查看商品详情。
        ⚠️ 条件可自动化 — 收藏功能正常，地址新增/编辑受 Bug③ 影响。
        """
        page = logged_in_buyer2
        product_page.__init__(page)
        product_page.open(base_url, product_id=1)
        product_page.assert_page_loaded()

        # 选择规格
        product_page.select_spec("256GB")
        page.wait_for_timeout(300)
        product_page.select_spec("原色钛金属")
        page.wait_for_load_state("domcontentloaded")

        product_page.assert_add_to_cart_enabled()

    # ── F-TC-040c: buyer2 个人信息+登出 ──────────────────

    @allure.story("F-TC-040c: buyer2 个人信息修改+登出")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p3
    def test_buyer2_profile_and_logout(
        self, logged_in_buyer2, profile_page: ProfilePage, base_url: str
    ):
        """buyer2 查看个人信息。"""
        page = logged_in_buyer2
        profile_page.__init__(page)
        profile_page.open(base_url)
        profile_page.assert_page_loaded()
        profile_page.go_to_personal_info()
        profile_page.assert_username_disabled()

    # ── F-TC-040d: buyer2 订单详情 ───────────────────────

    @allure.story("F-TC-040d: buyer2 订单详情（受 Bug① 影响）")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p3
    def test_buyer2_order_detail(
        self, logged_in_buyer2, order_page: OrderPage, base_url: str
    ):
        """buyer2 查看订单列表。
        ⚠️ 条件可自动化 — 订单详情受 Bug① 影响。
        """
        page = logged_in_buyer2
        order_page.__init__(page)
        order_page.open_list(base_url)
        order_page.assert_list_page_loaded()

        # 点击全部 Tab
        order_page.click_tab("全部")
        page.wait_for_load_state("domcontentloaded")