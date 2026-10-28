"""
Pytest配置和Fixtures
提供测试环境、API客户端、测试账号等公共fixture
支持通过环境变量切换配置（CI中通过env/secrets注入）
"""
import os
import pytest
from api_client import APIClient


# 测试环境配置（BASE_URL 可通过环境变量覆盖，便于CI/多环境切换）
BASE_URL = os.getenv('BASE_URL', 'http://localhost:3000')
TIMEOUT = 30

# 测试账号（用户名/密码可通过环境变量注入，避免敏感信息硬编码）
TEST_ACCOUNTS = {
    'buyer1': {
        'username': os.getenv('TEST_BUYER1_USER', 'buyer1'),
        'password': os.getenv('TEST_BUYER1_PASSWORD', '123456'),
    },
    'buyer2': {
        'username': os.getenv('TEST_BUYER2_USER', 'buyer2'),
        'password': os.getenv('TEST_BUYER2_PASSWORD', '123456'),
    },
    'admin': {
        'username': os.getenv('TEST_ADMIN_USER', 'admin'),
        'password': os.getenv('TEST_ADMIN_PASSWORD', '123456'),
    },
    'disabled_user': {
        'username': os.getenv('TEST_DISABLED_USER', 'disabled_user'),
        'password': os.getenv('TEST_DISABLED_PASSWORD', '123456'),
    },
}


@pytest.fixture(scope="session")
def base_url():
    """Base URL fixture"""
    return BASE_URL


@pytest.fixture(scope="session")
def test_accounts():
    """测试账号配置（支持环境变量注入）"""
    return TEST_ACCOUNTS


@pytest.fixture(scope="session")
def api_client(base_url):
    """API客户端fixture（会话级别）"""
    client = APIClient(base_url, TIMEOUT)
    yield client
    client.close()


@pytest.fixture
def buyer1_client(api_client):
    """已登录的buyer1客户端"""
    client = APIClient(BASE_URL, TIMEOUT)
    client.login(TEST_ACCOUNTS['buyer1']['username'], TEST_ACCOUNTS['buyer1']['password'])
    yield client
    client.close()


@pytest.fixture
def buyer2_client(api_client):
    """已登录的buyer2客户端"""
    client = APIClient(BASE_URL, TIMEOUT)
    client.login(TEST_ACCOUNTS['buyer2']['username'], TEST_ACCOUNTS['buyer2']['password'])
    yield client
    client.close()


@pytest.fixture
def admin_client(api_client):
    """已登录的admin客户端"""
    client = APIClient(BASE_URL, TIMEOUT)
    client.login(TEST_ACCOUNTS['admin']['username'], TEST_ACCOUNTS['admin']['password'])
    yield client
    client.close()


@pytest.fixture
def product_id():
    """测试商品ID（iPhone 15 Pro Max）"""
    return 1


@pytest.fixture
def sku_id():
    """测试SKU ID（256GB / 原色钛金属）"""
    return 1


@pytest.fixture
def address_id():
    """测试收货地址ID"""
    return 1


@pytest.fixture(autouse=True)
def log_test_name(request):
    """自动记录测试名称"""
    print(f"\n{'='*60}")
    print(f"开始测试: {request.node.name}")
    print(f"{'='*60}")
    yield
    print(f"{'='*60}")
    print(f"结束测试: {request.node.name}")
    print(f"{'='*60}\n")
