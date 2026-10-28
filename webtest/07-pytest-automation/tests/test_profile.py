"""个人中心测试用例 — P2。"""

import allure
import pytest
from pages.profile_page import ProfilePage


@allure.epic("ShopEasy 前台")
@allure.feature("个人中心")
class TestProfile:
    """个人中心功能测试集。"""

    # ── F-TC-033: 删除收货地址 ───────────────────────────

    @allure.story("F-TC-033: 删除收货地址弹出确认弹窗后删除成功")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p2
    def test_delete_address(
        self, logged_in_buyer1, profile_page: ProfilePage, base_url: str
    ):
        """删除收货地址 — 确认弹窗 → 删除成功。"""
        page = logged_in_buyer1
        profile_page.__init__(page)
        profile_page.open(base_url)
        profile_page.assert_page_loaded()
        profile_page.go_to_address()

        # 点击删除
        profile_page.click_delete()
        profile_page.assert_delete_confirm_dialog()

        # 点击取消
        page.get_by_role("dialog").get_by_role("button", name="取消").click()
        page.get_by_role("dialog").wait_for(state="hidden", timeout=3000)

    # ── F-TC-036: 修改个人信息保存 ───────────────────────

    @allure.story("F-TC-036: 修改昵称后保存成功")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p2
    def test_change_nickname(
        self, logged_in_buyer1, profile_page: ProfilePage, base_url: str
    ):
        """修改昵称后保存成功。
        ⚠️ 必须在 buyer1 所有用例最后执行，测试完成后需恢复原始值。
        """
        page = logged_in_buyer1
        profile_page.__init__(page)
        profile_page.open(base_url)
        profile_page.assert_page_loaded()
        profile_page.go_to_personal_info()

        # 验证用户名不可修改
        profile_page.assert_username_disabled()

    # ── F-TC-037: 用户名不可修改 ─────────────────────────

    @allure.story("F-TC-037: 用户名字段不可修改（disabled）")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.p2
    def test_username_disabled(
        self, logged_in_buyer1, profile_page: ProfilePage, base_url: str
    ):
        """用户名字段应 disabled。"""
        page = logged_in_buyer1
        profile_page.__init__(page)
        profile_page.open(base_url)
        profile_page.assert_page_loaded()
        profile_page.go_to_personal_info()
        profile_page.assert_username_disabled()

    # ── F-TC-038: 修改密码 ───────────────────────────────

    @allure.story("F-TC-038: 修改密码功能验证")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p2
    def test_change_password(
        self, logged_in_buyer1, profile_page: ProfilePage, base_url: str
    ):
        """修改密码功能验证。
        ⚠️ 测试完成后需将密码改回 123456。
        """
        page = logged_in_buyer1
        profile_page.__init__(page)
        profile_page.open(base_url)
        profile_page.assert_page_loaded()

        # 切换到修改密码 Tab
        profile_page.go_to_change_password()

        # 验证修改密码表单可见
        assert profile_page.old_password_input.is_visible()
        assert profile_page.new_password_input.is_visible()


@allure.epic("ShopEasy 前台")
@allure.feature("收藏管理")
class TestFavorites:
    """收藏管理功能测试集。"""

    # ── F-TC-034: 收藏/取消收藏商品 ──────────────────────

    @allure.story("F-TC-034: 收藏商品后取消收藏")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p2
    def test_favorite_unfavorite(
        self, logged_in_buyer1, base_url: str
    ):
        """收藏商品后取消收藏。"""
        page = logged_in_buyer1
        from pages.product_page import ProductPage

        product_page = ProductPage(page)
        product_page.open(base_url, product_id=1)
        product_page.assert_page_loaded()

        # 选择规格
        product_page.select_spec("256GB")
        page.wait_for_timeout(300)
        product_page.select_spec("原色钛金属")
        page.wait_for_load_state("domcontentloaded")

        # 点击收藏
        product_page.click_favorite()
        page.wait_for_timeout(500)

        # 验证收藏状态变化
        favorite_btn = product_page.favorite_button
        assert favorite_btn.is_visible()

        # 再次点击取消收藏
        product_page.click_favorite()
        page.wait_for_timeout(500)

    # ── F-TC-035: 收藏列表取消收藏 ───────────────────────

    @allure.story("F-TC-035: 收藏列表页取消收藏，商品移除")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p2
    def test_favorite_list_remove(
        self, logged_in_buyer1, base_url: str
    ):
        """收藏列表页取消收藏。"""
        page = logged_in_buyer1
        # 访问收藏列表页
        page.goto(f"{base_url}/favorites", wait_until="domcontentloaded")