"""Page Object 层 — 导出所有页面类。"""

from pages.base_page import BasePage
from pages.login_page import LoginPage
from pages.home_page import HomePage
from pages.product_page import ProductPage
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.order_page import OrderPage
from pages.profile_page import ProfilePage
from pages.admin_page import AdminPage

__all__ = [
    "BasePage",
    "LoginPage",
    "HomePage",
    "ProductPage",
    "CartPage",
    "CheckoutPage",
    "OrderPage",
    "ProfilePage",
    "AdminPage",
]