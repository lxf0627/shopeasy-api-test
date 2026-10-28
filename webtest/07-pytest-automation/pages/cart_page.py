"""购物车页面对象。"""

import re
import allure
from playwright.sync_api import Page, expect
from pages.base_page import BasePage


class CartPage(BasePage):
    """购物车页 /cart 的页面对象。"""

    PATH = "/cart"

    def __init__(self, page: Page):
        super().__init__(page)

    # ── 定位器 ────────────────────────────────────────────

    @property
    def select_all_checkbox(self):
        return self.page.get_by_role("checkbox", name="全选")

    @property
    def checkout_button(self):
        return self.page.get_by_role("button", name="去结算")

    @property
    def total_amount(self):
        return self.page.locator("strong")

    @property
    def empty_message(self):
        return self.page.get_by_text("购物车是空的")

    # ── 操作 ──────────────────────────────────────────────

    @allure.step("打开购物车页")
    def open(self, base_url: str):
        self.navigate(f"{base_url}{self.PATH}")
        self.page.wait_for_load_state("domcontentloaded")

    @allure.step("点击全选 checkbox")
    def click_select_all(self):
        self.click(self.select_all_checkbox)

    @allure.step("点击去结算")
    def click_checkout(self):
        self.click(self.checkout_button)

    @allure.step("点击商品删除按钮: {product_name}")
    def click_delete(self, product_name: str):
        """点击指定商品行的删除按钮。"""
        row = self.page.get_by_role("row").filter(has_text=product_name)
        row.get_by_role("button", name="删除").click()

    @allure.step("设置商品数量: {quantity}")
    def set_product_quantity(self, quantity: int, product_name: str = ""):
        """设置指定商品的数量。"""
        if product_name:
            row = self.page.get_by_role("row").filter(has_text=product_name)
            row.get_by_role("spinbutton").fill(str(quantity))
        else:
            self.page.get_by_role("spinbutton").first.fill(str(quantity))

    @allure.step("增加商品数量")
    def increase_product_quantity(self, product_name: str = ""):
        if product_name:
            row = self.page.get_by_role("row").filter(has_text=product_name)
            row.get_by_role("button", name="增加数值").click()
        else:
            self.page.get_by_role("button", name="增加数值").first.click()

    @allure.step("减少商品数量")
    def decrease_product_quantity(self, product_name: str = ""):
        if product_name:
            row = self.page.get_by_role("row").filter(has_text=product_name)
            row.get_by_role("button", name="减少数值").click()
        else:
            self.page.get_by_role("button", name="减少数值").first.click()

    @allure.step("勾选商品 checkbox: {product_name}")
    def check_product(self, product_name: str):
        row = self.page.get_by_role("row").filter(has_text=product_name)
        row.get_by_role("checkbox").check()

    @allure.step("取消勾选商品 checkbox: {product_name}")
    def uncheck_product(self, product_name: str):
        row = self.page.get_by_role("row").filter(has_text=product_name)
        row.get_by_role("checkbox").uncheck()

    # ── 断言 ──────────────────────────────────────────────

    @allure.step("断言购物车页已加载")
    def assert_page_loaded(self):
        """断言购物车页已加载 — 购物车标题可见即可。"""
        heading = self.page.get_by_role("heading", name="购物车")
        expect(heading).to_be_visible(timeout=5000)

    @allure.step("断言商品在购物车中: {product_name}")
    def assert_product_in_cart(self, product_name: str):
        cell = self.page.get_by_role("cell", name=product_name)
        expect(cell).to_be_visible(timeout=5000)

    @allure.step("断言商品不在购物车中: {product_name}")
    def assert_product_not_in_cart(self, product_name: str):
        cell = self.page.get_by_role("cell", name=product_name)
        expect(cell).not_to_be_visible(timeout=5000)

    @allure.step("断言合计金额包含: {amount_text}")
    def assert_total_amount(self, amount_text: str):
        expect(self.total_amount).to_contain_text(amount_text, timeout=5000)

    @allure.step("断言购物车为空")
    def assert_cart_empty(self):
        expect(self.empty_message).to_be_visible(timeout=5000)

    @allure.step("断言全选 checkbox 状态: checked={expected}")
    def assert_select_all_state(self, expected: bool):
        if expected:
            expect(self.select_all_checkbox).to_be_checked()
        else:
            expect(self.select_all_checkbox).not_to_be_checked()

    @allure.step("断言确认弹窗出现")
    def assert_confirm_dialog_visible(self):
        dialog = self.page.get_by_role("dialog")
        expect(dialog).to_be_visible(timeout=5000)
        return dialog

    @allure.step("断言确认弹窗内容: {text}")
    def assert_confirm_dialog_text(self, text: str):
        dialog = self.assert_confirm_dialog_visible()
        expect(dialog).to_contain_text(text)