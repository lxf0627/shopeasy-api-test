"""全局 Pytest 配置 — Fixtures 与 Hooks。"""

import os
import pytest
import allure
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page

from pages.login_page import LoginPage
from pages.home_page import HomePage
from pages.product_page import ProductPage
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.order_page import OrderPage
from pages.profile_page import ProfilePage
from pages.admin_page import AdminPage

BASE_URL = os.getenv("BASE_URL", "http://localhost:5173")
ADMIN_CREDENTIALS = {"username": "admin", "password": "123456"}
BUYER1_CREDENTIALS = {"username": "buyer1", "password": "123456"}
BUYER2_CREDENTIALS = {"username": "buyer2", "password": "123456"}


# ── 浏览器 Fixtures ──────────────────────────────────────

@pytest.fixture(scope="session")
def playwright_instance():
    """Session 级 Playwright 实例。"""
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="session")
def browser(playwright_instance) -> Browser:
    """Session 级浏览器实例（Chromium）。"""
    browser = playwright_instance.chromium.launch(headless=True)
    yield browser
    browser.close()


@pytest.fixture(scope="function")
def context(browser) -> BrowserContext:
    """Function 级浏览器上下文（每个测试独立）。"""
    ctx = browser.new_context(
        viewport={"width": 1280, "height": 720},
        locale="zh-CN",
    )
    yield ctx
    ctx.close()


@pytest.fixture(scope="function")
def page(context) -> Page:
    """Function 级页面对象。"""
    pg = context.new_page()
    yield pg
    pg.close()


# ── 登录态 Fixtures ──────────────────────────────────────

@pytest.fixture(scope="function")
def logged_in_buyer1(page: Page) -> Page:
    """以 buyer1 身份登录后的页面。"""
    login = LoginPage(page)
    login.open(BASE_URL)
    login.login(BUYER1_CREDENTIALS["username"], BUYER1_CREDENTIALS["password"])
    login.assert_login_success("张三")
    return page


@pytest.fixture(scope="function")
def logged_in_buyer2(page: Page) -> Page:
    """以 buyer2 身份登录后的页面。"""
    login = LoginPage(page)
    login.open(BASE_URL)
    login.login(BUYER2_CREDENTIALS["username"], BUYER2_CREDENTIALS["password"])
    login.assert_login_success("李四")
    return page


@pytest.fixture(scope="function")
def logged_in_admin(page: Page) -> Page:
    """以 admin 身份登录后的页面。"""
    login = LoginPage(page)
    login.open(BASE_URL)
    login.login(ADMIN_CREDENTIALS["username"], ADMIN_CREDENTIALS["password"])
    login.assert_login_success("管理")
    return page


# ── Page Object Fixtures ─────────────────────────────────

@pytest.fixture
def login_page(page) -> LoginPage:
    return LoginPage(page)


@pytest.fixture
def home_page(page) -> HomePage:
    return HomePage(page)


@pytest.fixture
def product_page(page) -> ProductPage:
    return ProductPage(page)


@pytest.fixture
def cart_page(page) -> CartPage:
    return CartPage(page)


@pytest.fixture
def checkout_page(page) -> CheckoutPage:
    return CheckoutPage(page)


@pytest.fixture
def order_page(page) -> OrderPage:
    return OrderPage(page)


@pytest.fixture
def profile_page(page) -> ProfilePage:
    return ProfilePage(page)


@pytest.fixture
def admin_page(page) -> AdminPage:
    return AdminPage(page)


# ── 测试数据 Fixtures ────────────────────────────────────

@pytest.fixture
def base_url() -> str:
    return BASE_URL


# ── Hooks ────────────────────────────────────────────────

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """测试失败时自动截图并附加到 Allure 报告。"""
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        page = item.funcargs.get("page") or item.funcargs.get("logged_in_buyer1")
        if page:
            try:
                screenshot = page.screenshot()
                allure.attach(
                    screenshot,
                    name=f"failure_{item.nodeid}",
                    attachment_type=allure.attachment_type.PNG,
                )
            except Exception:
                pass