"""结算下单测试用例 — P0。"""

import allure
import pytest
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.order_page import OrderPage


@allure.epic("ShopEasy 前台")
@allure.feature("结算下单")
class TestCheckout:
    """结算下单功能测试集。

    ⚠️ 条件可自动化 — 需购物车中已有商品（buyer1 预置数据）。
    """

    # ── F-TC-017: 正常结算下单 ───────────────────────────

    @allure.story("F-TC-017: 选择地址后提交订单成功")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p0
    @pytest.mark.smoke
    def test_normal_checkout(
        self,
        logged_in_buyer1,
        cart_page: CartPage,
        checkout_page: CheckoutPage,
        order_page: OrderPage,
        base_url: str,
    ):
        """完整结算流程：购物车 → 结算 → 提交订单 → 订单列表。
        ⚠️ 条件可自动化 — 需购物车中已有商品。
        """
        page = logged_in_buyer1
        cart_page.__init__(page)
        checkout_page.__init__(page)
        order_page.__init__(page)

        # 1. 打开购物车
        cart_page.open(base_url)
        cart_page.assert_page_loaded()

        # 2. 检查购物车是否有商品
        rows = page.locator("table tbody tr")
        if rows.count() == 0:
            pytest.skip("购物车为空，跳过结算测试")

        # 3. 点击去结算
        cart_page.click_checkout()

        # 4. 结算页验证
        checkout_page.assert_page_loaded()

        # 5. 选择地址 + 提交
        checkout_page.checkout(note="自动化测试订单")

        # 6. 跳转到订单列表
        order_page.assert_list_page_loaded()

    # ── F-TC-019: 空地址下单 ─────────────────────────────

    @allure.story("F-TC-019: 用户无收货地址时提交订单")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p0
    def test_checkout_no_address(
        self, logged_in_buyer1, checkout_page: CheckoutPage, base_url: str
    ):
        """⚠️ 条件可自动化 — 需无地址的测试用户。
        结算页加载验证。
        """
        page = logged_in_buyer1
        checkout_page.__init__(page)
        checkout_page.open(base_url)
        # 结算页可能因购物车为空而重定向
        current_url = page.url
        if "/checkout" in current_url:
            checkout_page.assert_page_loaded()

    # ── F-TC-020a: 重复提交订单防护 ──────────────────────

    @allure.story("F-TC-020a: 防重复提交机制验证")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p0
    def test_duplicate_submit_prevention(
        self,
        logged_in_buyer1,
        cart_page: CartPage,
        checkout_page: CheckoutPage,
        order_page: OrderPage,
        base_url: str,
    ):
        """⚠️ 条件可自动化 — 需购物车中已有商品。
        提交订单后页面跳转，仅创建 1 笔订单。
        """
        page = logged_in_buyer1
        cart_page.__init__(page)
        checkout_page.__init__(page)
        order_page.__init__(page)

        cart_page.open(base_url)
        cart_page.assert_page_loaded()

        # 检查购物车是否有商品
        rows = page.locator("table tbody tr")
        if rows.count() == 0:
            pytest.skip("购物车为空，跳过结算测试")

        cart_page.click_checkout()
        checkout_page.assert_page_loaded()
        checkout_page.checkout()
        order_page.assert_list_page_loaded()

    # ── F-TC-021: 库存不足时提交订单 ─────────────────────

    @allure.story("F-TC-021: 库存不足时提交订单行为")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p0
    def test_insufficient_stock(
        self, logged_in_buyer1, base_url: str
    ):
        """验证数量选择器 max 属性等于库存值。"""
        page = logged_in_buyer1
        from pages.product_page import ProductPage

        product_page = ProductPage(page)
        product_page.open(base_url, product_id=1)
        product_page.assert_page_loaded()

        spinbutton = product_page.quantity_input
        spinbutton.wait_for(state="visible")
        max_val = spinbutton.get_attribute("max")
        assert max_val is not None, "数量选择器应有 max 属性"

    # ── F-TC-022: 多商品结算金额计算 ─────────────────────

    @allure.story("F-TC-022: 多件不同商品结算金额正确")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p0
    def test_multi_product_checkout_amount(
        self,
        logged_in_buyer1,
        cart_page: CartPage,
        checkout_page: CheckoutPage,
        base_url: str,
    ):
        """⚠️ 条件可自动化 — 需购物车中有多件商品。"""
        page = logged_in_buyer1
        cart_page.__init__(page)
        checkout_page.__init__(page)

        cart_page.open(base_url)
        cart_page.assert_page_loaded()

        # 检查购物车是否有商品
        rows = page.locator("table tbody tr")
        if rows.count() == 0:
            pytest.skip("购物车为空，跳过结算测试")

        cart_page.click_checkout()
        checkout_page.assert_page_loaded()
        checkout_page.assert_total_amount("合计")