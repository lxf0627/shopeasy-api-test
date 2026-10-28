"""购物车管理测试用例 — P0。"""

import allure
import pytest
from pages.cart_page import CartPage


@allure.epic("ShopEasy 前台")
@allure.feature("购物车管理")
class TestCart:
    """购物车功能测试集。

    ⚠️ 条件可自动化 — 需购物车中已有商品（buyer1 预置数据）。
    当 buyer1 购物车为空时，测试验证空态展示。
    """

    # ── F-TC-014: 购物车金额计算 ─────────────────────────

    @allure.story("F-TC-014: 购物车页面展示")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p0
    @pytest.mark.smoke
    def test_cart_display(
        self, logged_in_buyer1, cart_page: CartPage, base_url: str
    ):
        """购物车页面正常加载。
        ⚠️ 条件可自动化 — 如购物车为空则验证空态展示。
        """
        page = logged_in_buyer1
        cart_page.__init__(page)
        cart_page.open(base_url)
        cart_page.assert_page_loaded()

        # 检查购物车是否有商品
        rows = page.locator("table tbody tr")
        if rows.count() > 0:
            # 有商品时验证合计金额
            cart_page.assert_total_amount("¥")
        else:
            # 空购物车验证空态
            cart_page.assert_cart_empty()

    # ── F-TC-015: 购物车删除商品确认模态框 ───────────────

    @allure.story("F-TC-015: 删除商品弹出确认模态框")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p0
    def test_cart_delete_confirm_dialog(
        self, logged_in_buyer1, cart_page: CartPage, base_url: str
    ):
        """⚠️ 条件可自动化 — 需购物车中已有商品。
        删除商品时弹出确认模态框。
        """
        page = logged_in_buyer1
        cart_page.__init__(page)
        cart_page.open(base_url)
        cart_page.assert_page_loaded()

        # 检查是否有删除按钮
        delete_btn = page.get_by_role("button", name="删除").first
        if delete_btn.is_visible(timeout=3000):
            delete_btn.click()
            cart_page.assert_confirm_dialog_visible()
            cart_page.assert_confirm_dialog_text("确定删除该商品")
            page.get_by_role("dialog").get_by_role("button", name="取消").click()
            page.get_by_role("dialog").wait_for(state="hidden", timeout=3000)
        else:
            # 购物车为空，无删除按钮
            cart_page.assert_cart_empty()

    # ── F-TC-016: 购物车全选/取消全选 ────────────────────

    @allure.story("F-TC-016: 全选/全不选 checkbox 联动")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p0
    def test_cart_select_all(
        self, logged_in_buyer1, cart_page: CartPage, base_url: str
    ):
        """⚠️ 条件可自动化 — 需购物车中已有商品。
        全选/取消全选 checkbox 联动。
        """
        page = logged_in_buyer1
        cart_page.__init__(page)
        cart_page.open(base_url)
        cart_page.assert_page_loaded()

        # 检查购物车是否有商品
        rows = page.locator("table tbody tr").filter(has=page.locator("td"))
        if rows.count() > 0:
            cart_page.click_select_all()
            cart_page.assert_select_all_state(True)
            cart_page.click_select_all()
            cart_page.assert_select_all_state(False)
        else:
            # 购物车为空
            cart_page.assert_cart_empty()