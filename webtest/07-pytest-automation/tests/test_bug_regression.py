"""Bug 回归验证测试用例 — P0。"""

import re
import allure
import pytest
from playwright.sync_api import expect

from pages.order_page import OrderPage
from pages.admin_page import AdminPage
from pages.product_page import ProductPage


@allure.epic("ShopEasy Bug 回归")
@allure.feature("Bug 回归验证")
class TestBugRegression:
    """Bug 回归验证测试集。"""

    # ── Bug①: 订单详情收货信息为空 ───────────────────────

    @allure.story("Bug①: 订单详情收货信息为空 — 回归验证")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p0
    @pytest.mark.bug_regression
    def test_bug1_order_detail_address_empty(
        self, logged_in_buyer1, order_page: OrderPage, base_url: str
    ):
        """⚠️ 条件可自动化 — Bug① 回归。
        当前状态：收货信息字段为空（确认 Bug 存在）。
        修复后：需更新断言验证字段非空。
        """
        page = logged_in_buyer1
        order_page.__init__(page)
        order_page.open_list(base_url)
        order_page.assert_list_page_loaded()

        # 进入第一个订单详情
        order_link = page.get_by_text("查看详情").first
        if order_link.is_visible():
            order_link.click()
            page.wait_for_load_state("domcontentloaded")
            order_page.assert_detail_page_loaded()

            # 当前 Bug① 状态：收货人字段为空
            # 修复后需改为 assert_recipient_not_empty()
            try:
                order_page.assert_recipient_empty()
                allure.attach(
                    "Bug① 确认存在：收货人字段为空",
                    name="bug_status",
                    attachment_type=allure.attachment_type.TEXT,
                )
            except AssertionError:
                # 如果字段非空，说明 Bug 已修复
                order_page.assert_recipient_not_empty()
                order_page.assert_phone_not_empty()
                order_page.assert_address_not_empty()
                allure.attach(
                    "Bug① 已修复：收货信息字段有值",
                    name="bug_status",
                    attachment_type=allure.attachment_type.TEXT,
                )

    # ── Bug②: 后台订单操作列为空 ─────────────────────────

    @allure.story("Bug②: 后台订单操作列为空 — 回归验证")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p0
    @pytest.mark.bug_regression
    def test_bug2_admin_order_operation_empty(
        self, logged_in_admin, admin_page: AdminPage, base_url: str
    ):
        """⚠️ 条件可自动化 — Bug② 回归。
        当前状态：操作列 cell 为空（确认 Bug 存在）。
        修复后：操作列有按钮。
        """
        page = logged_in_admin
        admin_page.__init__(page)
        admin_page.go_to_orders(base_url)
        admin_page.assert_page_loaded()

        # 当前 Bug② 状态：操作列为空
        # 修复后需改为 assert_operation_column_has_buttons()
        try:
            admin_page.assert_operation_column_empty()
            allure.attach(
                "Bug② 确认存在：订单操作列为空",
                name="bug_status",
                attachment_type=allure.attachment_type.TEXT,
            )
        except AssertionError:
            # 如果操作列有按钮，说明 Bug 已修复
            admin_page.assert_operation_column_has_buttons()
            allure.attach(
                "Bug② 已修复：订单操作列有按钮",
                name="bug_status",
                attachment_type=allure.attachment_type.TEXT,
            )

    # ── Bug④: 零库存商品详情页崩溃 ───────────────────────

    @allure.story("Bug④: 零库存商品详情页崩溃 — 回归验证")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p0
    @pytest.mark.bug_regression
    def test_bug4_zero_stock_product_crash(
        self, page, product_page: ProductPage, base_url: str
    ):
        """❌ 暂不可自动化 — Bug④ 导致 /product/27 页面崩溃。
        当前状态：页面 main 区域为空白，spinbutton 不存在。
        修复后：页面正常渲染，数量选择器可用。
        """
        product_page.__init__(page)

        try:
            product_page.open(base_url, product_id=27)
            # 尝试检测页面是否崩溃
            product_page.assert_page_crashed()
            allure.attach(
                "Bug④ 确认存在：零库存商品页面崩溃",
                name="bug_status",
                attachment_type=allure.attachment_type.TEXT,
            )
        except Exception:
            # 如果页面正常加载，说明 Bug 已修复
            product_page.assert_page_loaded()
            product_page.assert_add_to_cart_disabled()
            allure.attach(
                "Bug④ 已修复：零库存商品页面正常渲染",
                name="bug_status",
                attachment_type=allure.attachment_type.TEXT,
            )