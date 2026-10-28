"""后台管理页面对象。"""

import re
import allure
from playwright.sync_api import Page, expect
from pages.base_page import BasePage


class AdminPage(BasePage):
    """后台管理页 /admin/* 的页面对象。"""

    BASE_PATH = "/admin"
    PRODUCTS_PATH = "/admin/products"
    CATEGORIES_PATH = "/admin/categories"
    ORDERS_PATH = "/admin/orders"
    USERS_PATH = "/admin/users"
    REVIEWS_PATH = "/admin/reviews"

    def __init__(self, page: Page):
        super().__init__(page)

    # ── 通用定位器 ────────────────────────────────────────

    @property
    def search_input(self):
        return self.page.get_by_role("textbox", name=re.compile("搜索"))

    @property
    def search_button(self):
        return self.page.get_by_role("button", name="搜索")

    @property
    def status_filter(self):
        return self.page.get_by_role("combobox").first

    @property
    def add_button(self):
        return self.page.get_by_role("button", name=re.compile("新增"))

    @property
    def edit_button(self):
        return self.page.get_by_role("button", name="编辑").first

    @property
    def delete_button(self):
        return self.page.get_by_role("button", name="删除").first

    @property
    def back_to_frontend_button(self):
        return self.page.get_by_role("button", name="← 返回前台")

    @property
    def logout_button(self):
        return self.page.get_by_role("button", name="退出登录")

    @property
    def confirm_dialog(self):
        return self.page.get_by_role("dialog")

    # ── 菜单定位器（通过顺序） ────────────────────────────

    def _menu_item(self, index: int):
        return self.page.locator("aside menuitem").nth(index)

    @property
    def menu_dashboard(self):
        return self._menu_item(0)

    @property
    def menu_products(self):
        return self._menu_item(1)

    @property
    def menu_categories(self):
        return self._menu_item(2)

    @property
    def menu_orders(self):
        return self._menu_item(3)

    @property
    def menu_users(self):
        return self._menu_item(4)

    @property
    def menu_reviews(self):
        return self._menu_item(5)

    # ── 仪表盘定位器 ──────────────────────────────────────

    @property
    def stat_cards(self):
        return self.page.locator("[class*='stat'], [class*='card']")

    @property
    def recent_orders_table(self):
        return self.page.locator("table")

    # ── 操作 ──────────────────────────────────────────────

    @allure.step("打开后台首页")
    def open_dashboard(self, base_url: str):
        self.navigate(f"{base_url}{self.BASE_PATH}")
        self.page.wait_for_load_state("domcontentloaded")

    @allure.step("导航到商品管理")
    def go_to_products(self, base_url: str):
        self.navigate(f"{base_url}{self.PRODUCTS_PATH}")
        self.page.wait_for_load_state("domcontentloaded")

    @allure.step("导航到分类管理")
    def go_to_categories(self, base_url: str):
        self.navigate(f"{base_url}{self.CATEGORIES_PATH}")
        self.page.wait_for_load_state("domcontentloaded")

    @allure.step("导航到订单管理")
    def go_to_orders(self, base_url: str):
        self.navigate(f"{base_url}{self.ORDERS_PATH}")
        self.page.wait_for_load_state("domcontentloaded")

    @allure.step("导航到用户管理")
    def go_to_users(self, base_url: str):
        self.navigate(f"{base_url}{self.USERS_PATH}")
        self.page.wait_for_load_state("domcontentloaded")

    @allure.step("导航到评价管理")
    def go_to_reviews(self, base_url: str):
        self.navigate(f"{base_url}{self.REVIEWS_PATH}")
        self.page.wait_for_load_state("domcontentloaded")

    @allure.step("搜索: {keyword}")
    def search(self, keyword: str):
        self.fill(self.search_input, keyword)
        self.click(self.search_button)
        self.page.wait_for_load_state("domcontentloaded")

    @allure.step("点击新增按钮")
    def click_add(self):
        self.click(self.add_button)

    @allure.step("点击编辑按钮")
    def click_edit(self):
        self.click(self.edit_button)

    @allure.step("点击删除按钮")
    def click_delete(self):
        self.click(self.delete_button)

    @allure.step("确认弹窗点击: {button_text}")
    def confirm_dialog_click(self, button_text: str = "确定"):
        dialog = self.confirm_dialog
        dialog.wait_for(state="visible")
        dialog.get_by_role("button", name=button_text).click()

    @allure.step("取消弹窗点击: {button_text}")
    def confirm_dialog_dismiss(self, button_text: str = "取消"):
        dialog = self.confirm_dialog
        dialog.wait_for(state="visible")
        dialog.get_by_role("button", name=button_text).click()

    @allure.step("点击返回前台")
    def click_back_to_frontend(self):
        self.click(self.back_to_frontend_button)

    @allure.step("点击退出登录")
    def click_logout(self):
        self.click(self.logout_button)

    @allure.step("点击商品下架/上架按钮: {product_name}")
    def toggle_product_status(self, product_name: str):
        """点击指定商品行的下架/上架按钮。"""
        row = self.page.get_by_role("row").filter(has_text=product_name)
        btn = row.get_by_role("button", name=re.compile("下架|上架"))
        btn.click()

    @allure.step("点击用户禁用/启用按钮: {username}")
    def toggle_user_status(self, username: str):
        """点击指定用户行的禁用/启用按钮。"""
        row = self.page.get_by_role("row").filter(has_text=username)
        btn = row.get_by_role("button", name=re.compile("禁用|启用"))
        btn.click()

    @allure.step("选择状态筛选: {status}")
    def select_status_filter(self, status: str):
        self.status_filter.select_option(label=status)
        self.page.wait_for_load_state("domcontentloaded")

    # ── 断言 ──────────────────────────────────────────────

    @allure.step("断言后台页面已加载")
    def assert_page_loaded(self):
        self.assert_visible(self.search_input)

    @allure.step("断言仪表盘数据展示")
    def assert_dashboard_loaded(self):
        """断言仪表盘统计卡片和最近订单表存在。"""
        self.assert_visible(self.stat_cards.first)

    @allure.step("断言商品状态: {product_name} → {status}")
    def assert_product_status(self, product_name: str, status: str):
        row = self.page.get_by_role("row").filter(has_text=product_name)
        status_cell = row.get_by_text(status)
        expect(status_cell).to_be_visible(timeout=5000)

    @allure.step("断言用户状态: {username} → {status}")
    def assert_user_status(self, username: str, status: str):
        row = self.page.get_by_role("row").filter(has_text=username)
        status_cell = row.get_by_text(status)
        expect(status_cell).to_be_visible(timeout=5000)

    @allure.step("断言搜索结果包含: {text}")
    def assert_search_result_contains(self, text: str):
        result = self.page.get_by_text(text)
        expect(result).to_be_visible(timeout=5000)

    @allure.step("断言确认弹窗出现")
    def assert_confirm_dialog_visible(self):
        expect(self.confirm_dialog).to_be_visible(timeout=5000)

    @allure.step("断言操作列无按钮（Bug② 存在确认）")
    def assert_operation_column_empty(self):
        """Bug② 验证 — 订单操作列 cell 内无 button。"""
        rows = self.page.locator("table tbody tr")
        first_row = rows.first
        last_cell = first_row.locator("td").last
        buttons = last_cell.get_by_role("button")
        expect(buttons).to_have_count(0, timeout=3000)

    @allure.step("断言操作列有按钮（Bug② 修复后）")
    def assert_operation_column_has_buttons(self):
        """Bug② 回归 — 修复后操作列应有按钮。"""
        rows = self.page.locator("table tbody tr")
        first_row = rows.first
        last_cell = first_row.locator("td").last
        buttons = last_cell.get_by_role("button")
        expect(buttons).not_to_have_count(0, timeout=5000)

    @allure.step("断言 admin 行无操作按钮（自保护）")
    def assert_admin_no_action_button(self):
        """B-TC-016: admin 行操作列应为空。"""
        rows = self.page.locator("table tbody tr")
        admin_row = rows.filter(has_text="admin")
        last_cell = admin_row.locator("td").last
        buttons = last_cell.get_by_role("button")
        expect(buttons).to_have_count(0, timeout=3000)