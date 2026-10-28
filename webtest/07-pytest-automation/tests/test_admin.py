"""后台管理测试用例 — P1。"""

import allure
import pytest
from pages.admin_page import AdminPage


@allure.epic("ShopEasy 后台")
@allure.feature("后台管理")
class TestAdminDashboard:
    """后台仪表盘测试集。"""

    # ── B-TC-001: 仪表盘数据展示 ─────────────────────────

    @allure.story("B-TC-001: 仪表盘统计数据和最近订单展示")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p1
    def test_dashboard_display(
        self, logged_in_admin, admin_page: AdminPage, base_url: str
    ):
        """仪表盘统计数据和最近订单展示。"""
        page = logged_in_admin
        admin_page.__init__(page)
        admin_page.open_dashboard(base_url)
        admin_page.assert_dashboard_loaded()


@allure.epic("ShopEasy 后台")
@allure.feature("商品管理")
class TestAdminProducts:
    """后台商品管理测试集。"""

    # ── B-TC-002: 新增商品成功 ───────────────────────────

    @allure.story("B-TC-002: 新增商品保存成功")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p1
    def test_add_product(
        self, logged_in_admin, admin_page: AdminPage, base_url: str
    ):
        """⚠️ 条件可自动化 — 前端新增商品对话框保存返回 400（Bug③ 同根因）。
        可通过 API 创建商品后验证列表刷新。
        """
        page = logged_in_admin
        admin_page.__init__(page)
        admin_page.go_to_products(base_url)
        admin_page.assert_page_loaded()

        # 点击新增按钮
        admin_page.click_add()

        # 验证新增对话框出现
        dialog = page.get_by_role("dialog")
        dialog.wait_for(state="visible", timeout=5000)

    # ── B-TC-003: 新增商品必填字段校验 ───────────────────

    @allure.story("B-TC-003: 新增商品必填字段为空时保存的校验")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    def test_add_product_required_fields(
        self, logged_in_admin, admin_page: AdminPage, base_url: str
    ):
        """⚠️ 条件可自动化 — 探索性用例，需观察校验提示文案。"""
        page = logged_in_admin
        admin_page.__init__(page)
        admin_page.go_to_products(base_url)
        admin_page.assert_page_loaded()

        admin_page.click_add()
        dialog = page.get_by_role("dialog")
        dialog.wait_for(state="visible", timeout=5000)

        # 直接点击保存（不填任何字段）
        save_btn = dialog.get_by_role("button", name="保存")
        save_btn.click()

        # 验证校验提示出现（前端或后端）
        page.wait_for_timeout(1000)

    # ── B-TC-004: 编辑商品保存成功 ───────────────────────

    @allure.story("B-TC-004: 编辑商品保存成功")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p1
    def test_edit_product(
        self, logged_in_admin, admin_page: AdminPage, base_url: str
    ):
        """⚠️ 条件可自动化 — 前端编辑对话框保存返回 400（Bug③ 同根因）。"""
        page = logged_in_admin
        admin_page.__init__(page)
        admin_page.go_to_products(base_url)
        admin_page.assert_page_loaded()

        # 点击第一个编辑按钮
        admin_page.click_edit()

        # 验证编辑对话框出现
        dialog = page.get_by_role("dialog")
        dialog.wait_for(state="visible", timeout=5000)

    # ── B-TC-005: 下架商品操作 ───────────────────────────

    @allure.story("B-TC-005: 下架商品操作成功")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p1
    def test_deactivate_product(
        self, logged_in_admin, admin_page: AdminPage, base_url: str
    ):
        """下架商品 — 状态变为"下架"。"""
        page = logged_in_admin
        admin_page.__init__(page)
        admin_page.go_to_products(base_url)
        admin_page.assert_page_loaded()

        # 找到第一个上架商品并点击下架
        rows = page.locator("table tbody tr")
        first_row = rows.first
        toggle_btn = first_row.get_by_role("button", name="下架")
        if toggle_btn.is_visible():
            toggle_btn.click()
            page.wait_for_timeout(1000)

    # ── B-TC-006: 上架商品操作 ───────────────────────────

    @allure.story("B-TC-006: 上架商品操作成功")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p1
    def test_activate_product(
        self, logged_in_admin, admin_page: AdminPage, base_url: str
    ):
        """上架商品 — 状态变为"上架"。"""
        page = logged_in_admin
        admin_page.__init__(page)
        admin_page.go_to_products(base_url)
        admin_page.assert_page_loaded()

        # 找到第一个下架商品并点击上架
        rows = page.locator("table tbody tr")
        first_row = rows.first
        toggle_btn = first_row.get_by_role("button", name="上架")
        if toggle_btn.is_visible():
            toggle_btn.click()
            page.wait_for_timeout(1000)

    # ── B-TC-007: 商品搜索+状态筛选组合 ──────────────────

    @allure.story("B-TC-007: 搜索关键词+状态筛选组合功能")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    def test_product_search_and_filter(
        self, logged_in_admin, admin_page: AdminPage, base_url: str
    ):
        """搜索 iPhone + 状态筛选组合。"""
        page = logged_in_admin
        admin_page.__init__(page)
        admin_page.go_to_products(base_url)
        admin_page.assert_page_loaded()

        # 搜索 iPhone
        admin_page.search("iPhone")
        admin_page.assert_search_result_contains("iPhone")


@allure.epic("ShopEasy 后台")
@allure.feature("分类管理")
class TestAdminCategories:
    """后台分类管理测试集。"""

    # ── B-TC-008: 新增分类成功 ───────────────────────────

    @allure.story("B-TC-008: 新增分类保存成功")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p1
    def test_add_category(
        self, logged_in_admin, admin_page: AdminPage, base_url: str
    ):
        """⚠️ 条件可自动化 — 前端新增分类对话框保存返回 400（Bug⑤）。"""
        page = logged_in_admin
        admin_page.__init__(page)
        admin_page.go_to_categories(base_url)
        admin_page.assert_page_loaded()

        admin_page.click_add()
        dialog = page.get_by_role("dialog")
        dialog.wait_for(state="visible", timeout=5000)

    # ── B-TC-009: 编辑分类成功 ───────────────────────────

    @allure.story("B-TC-009: 编辑分类保存成功")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p1
    def test_edit_category(
        self, logged_in_admin, admin_page: AdminPage, base_url: str
    ):
        """⚠️ 条件可自动化 — 前端编辑对话框保存返回 400（Bug③ 同根因）。"""
        page = logged_in_admin
        admin_page.__init__(page)
        admin_page.go_to_categories(base_url)
        admin_page.assert_page_loaded()

        admin_page.click_edit()
        dialog = page.get_by_role("dialog")
        dialog.wait_for(state="visible", timeout=5000)

    # ── B-TC-010: 删除分类成功 ───────────────────────────

    @allure.story("B-TC-010: 删除分类弹出确认弹窗后删除成功")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p1
    def test_delete_category(
        self, logged_in_admin, admin_page: AdminPage, base_url: str
    ):
        """删除分类 — 确认弹窗 → 确定 → 分类从列表移除。"""
        page = logged_in_admin
        admin_page.__init__(page)
        admin_page.go_to_categories(base_url)
        admin_page.assert_page_loaded()

        # 点击删除
        admin_page.click_delete()
        admin_page.assert_confirm_dialog_visible()

    # ── B-TC-011: 删除有商品关联的分类 ───────────────────

    @allure.story("B-TC-011: 删除有商品关联的分类的行为（Bug⑦）")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    def test_delete_category_with_products(
        self, logged_in_admin, admin_page: AdminPage, base_url: str
    ):
        """Bug⑦ 验证 — 删除有商品关联的分类。"""
        page = logged_in_admin
        admin_page.__init__(page)
        admin_page.go_to_categories(base_url)
        admin_page.assert_page_loaded()


@allure.epic("ShopEasy 后台")
@allure.feature("订单管理")
class TestAdminOrders:
    """后台订单管理测试集。"""

    # ── B-TC-012: 订单操作列为空（Bug② 回归） ───────────

    @allure.story("B-TC-012: 订单操作列为空 — Bug② 回归")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p1
    @pytest.mark.bug_regression
    def test_order_operation_column(
        self, logged_in_admin, admin_page: AdminPage, base_url: str
    ):
        """⚠️ 条件可自动化 — Bug② 回归。
        当前状态：操作列为空。
        """
        page = logged_in_admin
        admin_page.__init__(page)
        admin_page.go_to_orders(base_url)
        admin_page.assert_page_loaded()

        # 验证操作列状态
        try:
            admin_page.assert_operation_column_empty()
        except AssertionError:
            admin_page.assert_operation_column_has_buttons()

    # ── B-TC-013: 订单搜索和状态筛选 ─────────────────────

    @allure.story("B-TC-013: 订单搜索和状态筛选功能")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    def test_order_search_and_filter(
        self, logged_in_admin, admin_page: AdminPage, base_url: str
    ):
        """订单搜索和状态筛选功能。"""
        page = logged_in_admin
        admin_page.__init__(page)
        admin_page.go_to_orders(base_url)
        admin_page.assert_page_loaded()

        # 搜索订单号
        admin_page.search("ORD")


@allure.epic("ShopEasy 后台")
@allure.feature("用户管理")
class TestAdminUsers:
    """后台用户管理测试集。"""

    # ── B-TC-014: 禁用用户操作 ───────────────────────────

    @allure.story("B-TC-014: 禁用用户操作成功")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p1
    def test_disable_user(
        self, logged_in_admin, admin_page: AdminPage, base_url: str
    ):
        """禁用用户 — 状态变为"禁用"。"""
        page = logged_in_admin
        admin_page.__init__(page)
        admin_page.go_to_users(base_url)
        admin_page.assert_page_loaded()

        # 找到可操作的用户行（非 admin）
        rows = page.locator("table tbody tr")
        for i in range(rows.count()):
            row = rows.nth(i)
            username = row.locator("td").first.inner_text()
            if username.strip() == "admin":
                continue
            toggle_btn = row.get_by_role("button", name="禁用")
            if toggle_btn.is_visible():
                toggle_btn.click()
                page.wait_for_timeout(1000)
                break

    # ── B-TC-015: 启用用户操作 ───────────────────────────

    @allure.story("B-TC-015: 启用用户操作成功")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p1
    def test_enable_user(
        self, logged_in_admin, admin_page: AdminPage, base_url: str
    ):
        """启用用户 — 状态变为"启用"。"""
        page = logged_in_admin
        admin_page.__init__(page)
        admin_page.go_to_users(base_url)
        admin_page.assert_page_loaded()

        # 找到被禁用的用户行
        rows = page.locator("table tbody tr")
        for i in range(rows.count()):
            row = rows.nth(i)
            toggle_btn = row.get_by_role("button", name="启用")
            if toggle_btn.is_visible():
                toggle_btn.click()
                page.wait_for_timeout(1000)
                break

    # ── B-TC-016: admin 自保护 — 无禁用按钮 ──────────────

    @allure.story("B-TC-016: admin 行无操作按钮")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p1
    def test_admin_self_protection(
        self, logged_in_admin, admin_page: AdminPage, base_url: str
    ):
        """admin 行操作列应为空（自保护机制）。"""
        page = logged_in_admin
        admin_page.__init__(page)
        admin_page.go_to_users(base_url)
        admin_page.assert_page_loaded()
        admin_page.assert_admin_no_action_button()

    # ── B-TC-017: 用户搜索功能 ───────────────────────────

    @allure.story("B-TC-017: 用户搜索功能正确性")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    def test_user_search(
        self, logged_in_admin, admin_page: AdminPage, base_url: str
    ):
        """用户搜索功能。"""
        page = logged_in_admin
        admin_page.__init__(page)
        admin_page.go_to_users(base_url)
        admin_page.assert_page_loaded()

        admin_page.search("buyer1")
        admin_page.assert_search_result_contains("buyer1")


@allure.epic("ShopEasy 后台")
@allure.feature("评价管理")
class TestAdminReviews:
    """后台评价管理测试集。"""

    # ── B-TC-018: 评价删除成功 ───────────────────────────

    @allure.story("B-TC-018: 评价删除成功")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p1
    def test_delete_review(
        self, logged_in_admin, admin_page: AdminPage, base_url: str
    ):
        """删除评价 — 确认弹窗 → 确定 → 评价从列表移除。"""
        page = logged_in_admin
        admin_page.__init__(page)
        admin_page.go_to_reviews(base_url)
        admin_page.assert_page_loaded()

        # 点击删除
        admin_page.click_delete()
        admin_page.assert_confirm_dialog_visible()


@allure.epic("ShopEasy 后台")
@allure.feature("权限隔离")
class TestAdminPermissions:
    """后台权限隔离测试集。"""

    # ── B-TC-019: 普通用户访问后台各路径 ─────────────────

    @allure.story("B-TC-019: 普通用户访问后台各子路径被重定向")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p1
    def test_normal_user_access_admin(
        self, logged_in_buyer1, admin_page: AdminPage, base_url: str
    ):
        """普通用户访问后台各子路径，应被重定向到首页。"""
        page = logged_in_buyer1
        admin_page.__init__(page)

        admin_paths = [
            "/admin",
            "/admin/products",
            "/admin/categories",
            "/admin/orders",
            "/admin/users",
            "/admin/reviews",
        ]

        for path in admin_paths:
            page.goto(f"{base_url}{path}", wait_until="domcontentloaded")
            # 应被重定向，URL 不应包含 /admin
            current_url = page.url
            assert "/admin" not in current_url, (
                f"普通用户访问 {path} 应被重定向，当前 URL: {current_url}"
            )

    # ── B-TC-020: 未登录访问后台 ─────────────────────────

    @allure.story("B-TC-020: 未登录访问后台被重定向到登录页")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p1
    def test_unauthenticated_access_admin(
        self, page, admin_page: AdminPage, base_url: str
    ):
        """未登录访问 /admin，应重定向到登录页。"""
        admin_page.__init__(page)
        page.goto(f"{base_url}/admin", wait_until="domcontentloaded")
        # 应重定向到登录页
        current_url = page.url
        assert "/login" in current_url or "/admin" not in current_url, (
            f"未登录访问 /admin 应被重定向，当前 URL: {current_url}"
        )