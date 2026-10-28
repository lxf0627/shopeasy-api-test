"""商品浏览与搜索测试用例 — P0。"""

import allure
import pytest
from playwright.sync_api import expect
from pages.home_page import HomePage


@allure.epic("ShopEasy 前台")
@allure.feature("商品浏览")
class TestSearch:
    """商品浏览与搜索功能测试集。"""

    # ── F-TC-006: 首页分类筛选 ───────────────────────────

    @allure.story("F-TC-006: 首页分类Tab筛选商品")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p0
    def test_category_filter(self, home_page: HomePage, base_url: str):
        """点击分类 Tab 后商品列表过滤。"""
        home_page.open(base_url)
        home_page.assert_page_loaded()
        home_page.click_category("手机数码")
        # 分类筛选后，手机数码类商品应可见
        home_page.assert_product_visible("iPhone 15 Pro Max")

    # ── F-TC-007: 商品搜索 ───────────────────────────────

    @allure.story("F-TC-007: 关键词搜索商品")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p0
    @pytest.mark.smoke
    def test_search_product(self, home_page: HomePage, base_url: str):
        """搜索 iPhone 后跳转搜索结果页。"""
        home_page.open(base_url)
        home_page.assert_page_loaded()
        home_page.search("iPhone")
        home_page.assert_url_contains("/search")
        # 验证搜索结果标题
        result_title = home_page.page.get_by_role("heading", name='搜索结果: "iPhone"')
        expect(result_title).to_be_visible(timeout=5000)
        # 验证商品卡片可见
        home_page.assert_product_visible("iPhone 15 Pro Max")

    # ── F-TC-008: 搜索无结果 ─────────────────────────────

    @allure.story("F-TC-008: 搜索无结果时的页面展示")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.p0
    def test_search_no_result(self, home_page: HomePage, base_url: str):
        """搜索不存在的商品，页面显示空态。"""
        home_page.open(base_url)
        home_page.assert_page_loaded()
        home_page.search("不存在的商品XYZ123")
        home_page.assert_url_contains("/search")
        # 验证搜索结果标题包含关键词
        result_title = home_page.page.get_by_role(
            "heading", name='搜索结果: "不存在的商品XYZ123"'
        )
        expect(result_title).to_be_visible(timeout=5000)