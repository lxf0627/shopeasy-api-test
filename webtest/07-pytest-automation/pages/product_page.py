"""商品详情页页面对象。"""

import re
import allure
from playwright.sync_api import Page, expect
from pages.base_page import BasePage


class ProductPage(BasePage):
    """商品详情页 /product/{id} 的页面对象。"""

    PATH_TEMPLATE = "/product/{product_id}"

    def __init__(self, page: Page):
        super().__init__(page)

    # ── 定位器 ────────────────────────────────────────────

    @property
    def product_name(self):
        return self.page.get_by_role("heading", level=1)

    @property
    def price_display(self):
        return self.page.locator("text=/¥\\d/").first

    @property
    def stock_display(self):
        return self.page.get_by_text(re.compile("库存:"))

    @property
    def quantity_input(self):
        return self.page.get_by_role("spinbutton")

    @property
    def increase_button(self):
        return self.page.get_by_role("button", name="增加数值")

    @property
    def decrease_button(self):
        return self.page.get_by_role("button", name="减少数值")

    @property
    def add_to_cart_button(self):
        return self.page.get_by_role("button", name="加入购物车")

    @property
    def favorite_button(self):
        return self.page.get_by_role("button", name=re.compile("收藏|已收藏"))

    @property
    def selected_spec_text(self):
        return self.page.get_by_text(re.compile("已选:"))

    @property
    def main_content(self):
        return self.page.locator("main")

    # ── 操作 ──────────────────────────────────────────────

    @allure.step("打开商品详情页: product_id={product_id}")
    def open(self, base_url: str, product_id: int):
        path = self.PATH_TEMPLATE.format(product_id=product_id)
        self.navigate(f"{base_url}{path}")
        self.page.wait_for_load_state("domcontentloaded")

    @allure.step("选择规格: {spec_text}")
    def select_spec(self, spec_text: str):
        self.click(self.page.get_by_text(spec_text))

    @allure.step("设置数量: {quantity}")
    def set_quantity(self, quantity: int):
        self.quantity_input.wait_for(state="visible")
        self.quantity_input.fill(str(quantity))

    @allure.step("增加数量")
    def increase_quantity(self):
        self.click(self.increase_button)

    @allure.step("减少数量")
    def decrease_quantity(self):
        self.click(self.decrease_button)

    @allure.step("点击加入购物车")
    def click_add_to_cart(self):
        self.click(self.add_to_cart_button)

    @allure.step("点击收藏按钮")
    def click_favorite(self):
        self.click(self.favorite_button)

    # ── 断言 ──────────────────────────────────────────────

    @allure.step("断言商品详情页已加载")
    def assert_page_loaded(self):
        self.assert_visible(self.product_name)

    @allure.step("断言价格为: {price_text}")
    def assert_price(self, price_text: str):
        price = self.page.get_by_text(price_text)
        expect(price).to_be_visible(timeout=5000)

    @allure.step("断言库存为: {stock}")
    def assert_stock(self, stock: int):
        stock_text = self.page.get_by_text(re.compile(f"库存:\\s*{stock}"))
        expect(stock_text).to_be_visible(timeout=5000)

    @allure.step("断言已选规格: {spec_text}")
    def assert_selected_spec(self, spec_text: str):
        spec = self.page.get_by_text(re.compile(f"已选:.*{spec_text}"))
        expect(spec).to_be_visible(timeout=5000)

    @allure.step("断言加入购物车按钮禁用")
    def assert_add_to_cart_disabled(self):
        self.assert_disabled(self.add_to_cart_button)

    @allure.step("断言加入购物车按钮启用")
    def assert_add_to_cart_enabled(self):
        self.assert_enabled(self.add_to_cart_button)

    @allure.step("断言收藏状态: {is_favorited}")
    def assert_favorite_state(self, is_favorited: bool):
        if is_favorited:
            expect(self.favorite_button).to_contain_text("已收藏")
        else:
            expect(self.favorite_button).to_contain_text("收藏")

    @allure.step("断言页面崩溃（main 区域为空）")
    def assert_page_crashed(self):
        """用于 Bug④ 验证 — 零库存商品页面崩溃。"""
        main = self.main_content
        expect(main).to_be_visible(timeout=5000)
        # 崩溃时 main 区域内容为空或 spinbutton 不存在
        expect(self.quantity_input).not_to_be_visible(timeout=3000)