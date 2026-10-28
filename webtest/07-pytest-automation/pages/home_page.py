"""首页页面对象。"""

import re
import allure
from playwright.sync_api import Page, expect
from pages.base_page import BasePage


class HomePage(BasePage):
    """首页 / 的页面对象。"""

    PATH = "/"

    def __init__(self, page: Page):
        super().__init__(page)

    # ── 定位器 ────────────────────────────────────────────

    @property
    def search_input(self):
        return self.page.get_by_role("textbox", name="搜索商品...")

    @property
    def search_button(self):
        return self.page.locator("button").filter(has=self.page.locator("svg")).nth(0)

    @property
    def cart_button(self):
        return self.page.locator("button").filter(has=self.page.locator("sup"))

    @property
    def user_button(self):
        return self.page.get_by_role("button", name=re.compile("张三|李四|admin"))

    @property
    def sort_default(self):
        return self.page.get_by_role("radio", name="默认")

    @property
    def sort_sales(self):
        return self.page.get_by_role("radio", name="销量")

    @property
    def next_page_button(self):
        return self.page.get_by_role("button", name="下一页")

    @property
    def prev_page_button(self):
        return self.page.get_by_role("button", name="上一页")

    @property
    def login_link(self):
        return self.page.get_by_role("link", name="登录")

    @property
    def register_link(self):
        return self.page.get_by_role("link", name="注册")

    # ── 操作 ──────────────────────────────────────────────

    @allure.step("打开首页")
    def open(self, base_url: str):
        self.navigate(f"{base_url}{self.PATH}")

    @allure.step("搜索商品: {keyword}")
    def search(self, keyword: str):
        """在搜索框输入关键词并按回车搜索。"""
        self.fill(self.search_input, keyword)
        self.search_input.press("Enter")
        self.page.wait_for_load_state("domcontentloaded")

    @allure.step("点击分类: {category}")
    def click_category(self, category: str):
        """点击分类 Tab。"""
        self.click(self.page.get_by_text(category))

    @allure.step("点击商品: {product_name}")
    def click_product(self, product_name: str):
        """点击商品卡片进入详情页。"""
        self.click(self.page.get_by_text(product_name))

    @allure.step("点击购物车按钮")
    def click_cart(self):
        self.click(self.cart_button)

    @allure.step("点击用户按钮")
    def click_user_button(self):
        self.click(self.user_button)

    @allure.step("点击退出登录")
    def click_logout(self):
        self.click_user_button()
        logout_btn = self.page.get_by_role("button", name="退出登录")
        self.click(logout_btn)

    @allure.step("选择排序方式: {sort_name}")
    def select_sort(self, sort_name: str):
        self.click(self.page.get_by_role("radio", name=sort_name))

    @allure.step("点击下一页")
    def click_next_page(self):
        self.click(self.next_page_button)

    # ── 断言 ──────────────────────────────────────────────

    @allure.step("断言首页已加载")
    def assert_page_loaded(self):
        self.assert_visible(self.search_input)

    @allure.step("断言商品可见: {product_name}")
    def assert_product_visible(self, product_name: str):
        product = self.page.get_by_text(product_name)
        expect(product).to_be_visible(timeout=5000)

    @allure.step("断言商品不可见: {product_name}")
    def assert_product_not_visible(self, product_name: str):
        product = self.page.get_by_text(product_name)
        expect(product).not_to_be_visible(timeout=5000)

    @allure.step("断言搜索结果标题: {title}")
    def assert_search_result_title(self, title: str):
        heading = self.page.get_by_text(re.compile(title))
        expect(heading).to_be_visible(timeout=5000)

    @allure.step("断言未登录状态")
    def assert_not_logged_in(self):
        self.assert_visible(self.login_link)

    @allure.step("获取商品卡片数量")
    def get_product_count(self) -> int:
        """统计当前页面商品卡片数量。"""
        cards = self.page.locator("h4")
        return cards.count()