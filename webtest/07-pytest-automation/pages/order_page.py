"""订单页面对象。"""

import re
import allure
from playwright.sync_api import Page, expect
from pages.base_page import BasePage


class OrderPage(BasePage):
    """订单列表页 /orders 和订单详情页 /order/{id} 的页面对象。"""

    LIST_PATH = "/orders"
    DETAIL_PATH_TEMPLATE = "/order/{order_id}"

    def __init__(self, page: Page):
        super().__init__(page)

    # ── 列表页定位器 ──────────────────────────────────────

    @property
    def tab_all(self):
        return self.page.get_by_role("tab", name="全部")

    @property
    def tab_pending(self):
        return self.page.get_by_role("tab", name="待支付")

    @property
    def tab_paid(self):
        return self.page.get_by_role("tab", name="已支付")

    @property
    def tab_shipped(self):
        return self.page.get_by_role("tab", name="已发货")

    @property
    def tab_completed(self):
        return self.page.get_by_role("tab", name="已完成")

    @property
    def tab_cancelled(self):
        return self.page.get_by_role("tab", name="已取消")

    @property
    def empty_message(self):
        return self.page.get_by_text("暂无订单")

    # ── 详情页定位器 ──────────────────────────────────────

    @property
    def order_number(self):
        return self.page.get_by_role("cell", name=re.compile("ORD"))

    @property
    def recipient_name(self):
        return self.page.locator("table tr:nth-child(2) td:nth-child(2)")

    @property
    def recipient_phone(self):
        return self.page.locator("table tr:nth-child(2) td:nth-child(4)")

    @property
    def shipping_address(self):
        return self.page.locator("table tr:nth-child(3) td:nth-child(2)")

    @property
    def cancel_button(self):
        return self.page.get_by_role("button", name="取消订单")

    @property
    def pay_button(self):
        return self.page.get_by_role("button", name="去支付")

    @property
    def confirm_dialog(self):
        return self.page.get_by_role("dialog")

    # ── 列表页操作 ────────────────────────────────────────

    @allure.step("打开订单列表页")
    def open_list(self, base_url: str):
        self.navigate(f"{base_url}{self.LIST_PATH}")
        self.page.wait_for_load_state("domcontentloaded")

    @allure.step("点击状态 Tab: {tab_name}")
    def click_tab(self, tab_name: str):
        self.click(self.page.get_by_role("tab", name=tab_name))

    @allure.step("点击订单: {order_id}")
    def click_order(self, order_id: str):
        self.click(self.page.get_by_text(order_id))

    # ── 详情页操作 ────────────────────────────────────────

    @allure.step("打开订单详情页: order_id={order_id}")
    def open_detail(self, base_url: str, order_id: str):
        path = self.DETAIL_PATH_TEMPLATE.format(order_id=order_id)
        self.navigate(f"{base_url}{path}")
        self.page.wait_for_load_state("domcontentloaded")

    @allure.step("点击取消订单")
    def click_cancel(self):
        self.click(self.cancel_button)

    @allure.step("点击去支付")
    def click_pay(self):
        self.click(self.pay_button)

    @allure.step("确认弹窗点击: {button_text}")
    def confirm_dialog_click(self, button_text: str = "确定"):
        dialog = self.confirm_dialog
        dialog.wait_for(state="visible")
        dialog.get_by_role("button", name=button_text).click()

    # ── 列表页断言 ────────────────────────────────────────

    @allure.step("断言订单列表页已加载")
    def assert_list_page_loaded(self):
        self.assert_visible(self.tab_all)

    @allure.step("断言订单存在: {order_text}")
    def assert_order_exists(self, order_text: str):
        order = self.page.get_by_text(re.compile(order_text))
        expect(order).to_be_visible(timeout=5000)

    @allure.step("断言订单状态: {status}")
    def assert_order_status(self, status: str):
        status_text = self.page.get_by_text(status)
        expect(status_text).to_be_visible(timeout=5000)

    @allure.step("断言订单列表为空")
    def assert_orders_empty(self):
        expect(self.empty_message).to_be_visible(timeout=5000)

    @allure.step("获取当前 Tab 下订单数量")
    def get_order_count(self) -> int:
        """统计当前页面订单卡片/行数量。"""
        orders = self.page.locator("[class*='order']")
        return orders.count()

    # ── 详情页断言 ────────────────────────────────────────

    @allure.step("断言订单详情页已加载")
    def assert_detail_page_loaded(self):
        self.assert_visible(self.order_number)

    @allure.step("断言订单号: {order_id}")
    def assert_order_number(self, order_id: str):
        expect(self.order_number).to_contain_text(order_id)

    @allure.step("断言收货人信息非空（Bug① 回归）")
    def assert_recipient_not_empty(self):
        """Bug① 回归验证 — 修复后收货人字段应非空。"""
        expect(self.recipient_name).not_to_be_empty(timeout=5000)

    @allure.step("断言收货人信息为空（Bug① 存在确认）")
    def assert_recipient_empty(self):
        """Bug① 验证 — 当前收货人字段为空。"""
        text = self.recipient_name.inner_text()
        assert text.strip() == "", f"收货人字段预期为空，实际为: '{text}'"

    @allure.step("断言手机号信息非空（Bug① 回归）")
    def assert_phone_not_empty(self):
        expect(self.recipient_phone).not_to_be_empty(timeout=5000)

    @allure.step("断言收货地址非空（Bug① 回归）")
    def assert_address_not_empty(self):
        expect(self.shipping_address).not_to_be_empty(timeout=5000)

    @allure.step("断言取消订单按钮可见")
    def assert_cancel_button_visible(self):
        self.assert_visible(self.cancel_button)

    @allure.step("断言去支付按钮可见")
    def assert_pay_button_visible(self):
        self.assert_visible(self.pay_button)

    @allure.step("断言确认弹窗出现")
    def assert_confirm_dialog_visible(self):
        expect(self.confirm_dialog).to_be_visible(timeout=5000)