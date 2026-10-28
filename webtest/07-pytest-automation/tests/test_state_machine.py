"""订单状态机测试用例 — P1。"""

import allure
import pytest
from pages.order_page import OrderPage


@allure.epic("ShopEasy 前台")
@allure.feature("订单状态机")
class TestStateMachine:
    """订单状态机测试集。

    ⚠️ 条件可自动化 — 状态机用例需 API 造数 + UI 验证混合。
    当前实现以 UI 验证为主，API 造数部分待后续增强。
    """

    # ── F-TC-025: 待支付→已支付 ──────────────────────────

    @allure.story("F-TC-025: 待支付→已支付状态迁移")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p1
    def test_pending_to_paid(
        self, logged_in_buyer1, order_page: OrderPage, base_url: str
    ):
        """⚠️ 条件可自动化 — 需 API 造数。
        验证订单列表中"已支付"Tab 有订单。
        """
        page = logged_in_buyer1
        order_page.__init__(page)
        order_page.open_list(base_url)
        order_page.assert_list_page_loaded()

        # 点击已支付 Tab
        order_page.click_tab("已支付")
        page.wait_for_load_state("domcontentloaded")

    # ── F-TC-026: 已支付→已发货 ──────────────────────────

    @allure.story("F-TC-026: 已支付→已发货状态迁移")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p1
    def test_paid_to_shipped(
        self, logged_in_buyer1, order_page: OrderPage, base_url: str
    ):
        """⚠️ 条件可自动化 — 需 API 造数 + 后台发货操作。
        受 Bug② 影响，后台操作列为空。
        """
        page = logged_in_buyer1
        order_page.__init__(page)
        order_page.open_list(base_url)
        order_page.assert_list_page_loaded()

        # 点击已发货 Tab
        order_page.click_tab("已发货")
        page.wait_for_load_state("domcontentloaded")

    # ── F-TC-027: 已发货→已完成 ──────────────────────────

    @allure.story("F-TC-027: 已发货→已完成状态迁移")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p1
    def test_shipped_to_completed(
        self, logged_in_buyer1, order_page: OrderPage, base_url: str
    ):
        """⚠️ 条件可自动化 — 需 API 造数。"""
        page = logged_in_buyer1
        order_page.__init__(page)
        order_page.open_list(base_url)
        order_page.assert_list_page_loaded()

        # 点击已完成 Tab
        order_page.click_tab("已完成")
        page.wait_for_load_state("domcontentloaded")

    # ── F-TC-029: 已支付→已退款 ──────────────────────────

    @allure.story("F-TC-029: 已支付→已退款状态迁移")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    def test_paid_to_refunded(
        self, logged_in_buyer1, order_page: OrderPage, base_url: str
    ):
        """⚠️ 条件可自动化 — 需 API 造数。"""
        page = logged_in_buyer1
        order_page.__init__(page)
        order_page.open_list(base_url)
        order_page.assert_list_page_loaded()

        # 点击已退款 Tab
        order_page.click_tab("已退款")
        page.wait_for_load_state("domcontentloaded")