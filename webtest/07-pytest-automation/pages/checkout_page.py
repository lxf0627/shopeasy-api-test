"""结算页面对象。"""

import re
import allure
from playwright.sync_api import Page, expect
from pages.base_page import BasePage


class CheckoutPage(BasePage):
    """结算页 /checkout 的页面对象。"""

    PATH = "/checkout"

    def __init__(self, page: Page):
        super().__init__(page)

    # ── 定位器 ────────────────────────────────────────────

    @property
    def address_radio(self):
        return self.page.get_by_role("radio").first

    @property
    def order_note_input(self):
        return self.page.get_by_role("textbox", name="选填")

    @property
    def submit_button(self):
        return self.page.get_by_role("button", name="提交订单")

    @property
    def total_text(self):
        return self.page.get_by_text(re.compile("合计:"))

    @property
    def page_title(self):
        return self.page.get_by_role("heading", level=2)

    # ── 操作 ──────────────────────────────────────────────

    @allure.step("打开结算页")
    def open(self, base_url: str):
        self.navigate(f"{base_url}{self.PATH}")
        self.page.wait_for_load_state("domcontentloaded")

    @allure.step("选择收货地址")
    def select_address(self):
        """选择第一个收货地址。"""
        self.click(self.address_radio)

    @allure.step("选择第 {index} 个收货地址")
    def select_address_by_index(self, index: int):
        """选择指定索引的收货地址。"""
        radio = self.page.get_by_role("radio").nth(index)
        self.click(radio)

    @allure.step("输入订单备注: {note}")
    def enter_order_note(self, note: str):
        self.fill(self.order_note_input, note)

    @allure.step("点击提交订单")
    def click_submit_order(self):
        self.click(self.submit_button)

    @allure.step("完整结算流程")
    def checkout(self, note: str = ""):
        """完整结算流程：选地址 → 输入备注 → 提交。"""
        self.select_address()
        if note:
            self.enter_order_note(note)
        self.click_submit_order()

    # ── 断言 ──────────────────────────────────────────────

    @allure.step("断言结算页已加载")
    def assert_page_loaded(self):
        self.assert_visible(self.submit_button)

    @allure.step("断言收货地址可见")
    def assert_address_visible(self):
        expect(self.address_radio).to_be_visible(timeout=5000)

    @allure.step("断言商品在结算清单中: {product_name}")
    def assert_product_in_list(self, product_name: str):
        product = self.page.get_by_text(product_name)
        expect(product).to_be_visible(timeout=5000)

    @allure.step("断言合计金额: {amount_text}")
    def assert_total_amount(self, amount_text: str):
        expect(self.total_text).to_contain_text(amount_text, timeout=5000)

    @allure.step("断言提交按钮禁用")
    def assert_submit_disabled(self):
        self.assert_disabled(self.submit_button)

    @allure.step("断言提交按钮启用")
    def assert_submit_enabled(self):
        self.assert_enabled(self.submit_button)