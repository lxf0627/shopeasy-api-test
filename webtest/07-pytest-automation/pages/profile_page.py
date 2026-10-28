"""个人中心页面对象。"""

import allure
from playwright.sync_api import Page, expect
from pages.base_page import BasePage


class ProfilePage(BasePage):
    """个人中心页 /profile 的页面对象。"""

    PATH = "/profile"

    def __init__(self, page: Page):
        super().__init__(page)

    # ── 定位器 ────────────────────────────────────────────

    @property
    def tab_personal_info(self):
        return self.page.get_by_role("tab", name="个人信息")

    @property
    def tab_address(self):
        return self.page.get_by_role("tab", name="收货地址")

    @property
    def tab_change_password(self):
        return self.page.get_by_role("tab", name="修改密码")

    @property
    def nickname_input(self):
        return self.page.get_by_role("textbox", name="昵称")

    @property
    def username_input(self):
        return self.page.get_by_role("textbox", name="用户名")

    @property
    def save_button(self):
        return self.page.get_by_role("button", name="保存修改")

    @property
    def add_address_button(self):
        return self.page.get_by_role("button", name="新增地址")

    @property
    def edit_button(self):
        return self.page.get_by_role("button", name="编辑").first

    @property
    def delete_button(self):
        return self.page.get_by_role("button", name="删除").first

    @property
    def old_password_input(self):
        return self.page.get_by_role("textbox", name="原密码")

    @property
    def new_password_input(self):
        return self.page.get_by_role("textbox", name="新密码")

    @property
    def confirm_password_input(self):
        return self.page.get_by_role("textbox", name="确认新密码")

    @property
    def change_password_button(self):
        return self.page.get_by_role("button", name="修改密码")

    # ── 操作 ──────────────────────────────────────────────

    @allure.step("打开个人中心页")
    def open(self, base_url: str):
        self.navigate(f"{base_url}{self.PATH}")
        self.page.wait_for_load_state("domcontentloaded")

    @allure.step("切换到个人信息 Tab")
    def go_to_personal_info(self):
        self.click(self.tab_personal_info)

    @allure.step("切换到收货地址 Tab")
    def go_to_address(self):
        self.click(self.tab_address)

    @allure.step("切换到修改密码 Tab")
    def go_to_change_password(self):
        self.click(self.tab_change_password)

    @allure.step("修改昵称为: {nickname}")
    def change_nickname(self, nickname: str):
        self.nickname_input.wait_for(state="visible")
        self.nickname_input.clear()
        self.fill(self.nickname_input, nickname)
        self.click(self.save_button)

    @allure.step("修改密码")
    def change_password(self, old_pwd: str, new_pwd: str):
        """修改密码流程。"""
        self.go_to_change_password()
        self.fill(self.old_password_input, old_pwd)
        self.fill(self.new_password_input, new_pwd)
        self.fill(self.confirm_password_input, new_pwd)
        self.click(self.change_password_button)

    @allure.step("点击新增地址")
    def click_add_address(self):
        self.click(self.add_address_button)

    @allure.step("点击编辑按钮")
    def click_edit(self):
        self.click(self.edit_button)

    @allure.step("点击删除按钮")
    def click_delete(self):
        self.click(self.delete_button)

    # ── 断言 ──────────────────────────────────────────────

    @allure.step("断言个人中心页已加载")
    def assert_page_loaded(self):
        self.assert_visible(self.tab_personal_info)

    @allure.step("断言用户名不可修改")
    def assert_username_disabled(self):
        self.assert_disabled(self.username_input)

    @allure.step("断言昵称为: {nickname}")
    def assert_nickname(self, nickname: str):
        expect(self.nickname_input).to_have_value(nickname, timeout=5000)

    @allure.step("断言保存成功提示")
    def assert_save_success(self):
        toast = self.page.get_by_text("保存成功")
        expect(toast).to_be_visible(timeout=5000)

    @allure.step("断言密码修改成功提示")
    def assert_password_change_success(self):
        toast = self.page.get_by_text("密码修改成功")
        expect(toast).to_be_visible(timeout=5000)

    @allure.step("断言删除确认弹窗出现")
    def assert_delete_confirm_dialog(self):
        dialog = self.page.get_by_role("dialog")
        expect(dialog).to_be_visible(timeout=5000)
        return dialog

    @allure.step("断言地址数量: {count}")
    def assert_address_count(self, count: int):
        """断言地址列表中有指定数量的地址。"""
        addresses = self.page.locator("[class*='address']")
        expect(addresses).to_have_count(count, timeout=5000)