# API Test Automation - 用户下单流程

## 技术栈

- **Python 3.8+**
- **pytest** - 测试框架
- **requests** - HTTP客户端
- **allure-python-commons** - 测试报告

## 项目结构

```
06-pytest-automation/
├── requirements.txt        # 依赖管理
├── pytest.ini              # pytest配置
├── conftest.py             # fixtures
├── api_client.py           # HTTP客户端
├── generate_report.py      # 报告生成器（无需Java）
├── run_tests.py            # 测试执行脚本
├── README.md               # 本文档
├── tests/                  # 测试用例
│   ├── test_01_login.py    # 登录测试
│   ├── test_02_auth.py     # 权限测试
│   ├── test_03_order_flow.py  # 下单流程
│   ├── test_04_order_status.py # 订单状态
│   ├── test_05_cart.py     # 购物车测试
│   └── test_06_boundary.py # 边界测试
└── artifacts/              # 执行产物
    ├── allure-results/     # Allure原始数据
    └── report.html         # HTML测试报告
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行测试

```bash
# 方式1: 使用脚本（推荐）
python run_tests.py

# 方式2: 手动执行
# 执行测试并生成allure数据
python -m pytest tests/ -v --alluredir=artifacts/allure-results

# 生成HTML报告
python generate_report.py
```

### 3. 查看报告

报告会自动打开，或手动打开: `artifacts/report.html`

## 测试用例清单

| 编号 | 场景 | 优先级 | 文件 |
|------|------|--------|------|
| TC-EXC-001 | 禁用用户登录 | P0 | test_01_login.py |
| TC-EXC-002 | 错误密码登录 | P0 | test_01_login.py |
| TC-EXC-003 | 有规格商品未选SKU | P0 | test_05_cart.py |
| TC-AUTH-001 | 未登录访问需认证接口 | P0 | test_02_auth.py |
| TC-AUTH-002 | 无效token访问接口 | P1 | test_02_auth.py |
| TC-AUTH-003 | 普通用户访问管理员接口 | P0 | test_02_auth.py |
| TC-POS-001 | 用户完整下单流程 | P0 | test_03_order_flow.py |
| TC-POS-002 | 完整订单状态流转 | P0 | test_03_order_flow.py |
| TC-POS-003 | 取消订单并恢复库存 | P1 | test_06_boundary.py |
| TC-STS-001 | 非pending状态订单支付 | P0 | test_04_order_status.py |
| TC-STS-002 | 非pending状态订单取消 | P0 | test_04_order_status.py |
| TC-STS-003 | 非paid状态订单发货 | P0 | test_04_order_status.py |
| TC-STS-004 | 非shipped状态确认收货 | P0 | test_04_order_status.py |
| TC-DAT-001 | 创建订单后购物车清空 | P0 | test_05_cart.py |
| TC-DAT-002 | 订单金额与商品价格一致 | P0 | test_05_cart.py |
| TC-EXC-004 | 不存在的商品加入购物车 | P1 | test_05_cart.py |
| TC-EXC-005 | 无效地址创建订单 | P1 | test_06_boundary.py |
| TC-EXC-006 | 购物车为空创建订单 | P0 | test_06_boundary.py |
| TC-BND-003 | 不存在的商品ID查询 | P2 | test_06_boundary.py |
| TC-BND-004 | 不存在的订单ID查询 | P2 | test_06_boundary.py |
| TC-EXP-001 | 零库存商品加入购物车 | P1 | test_05_cart.py |
| TC-EXP-002 | 同一商品重复添加购物车 | P1 | test_05_cart.py |
| TC-EXP-003 | 无规格商品不传skuId | P1 | test_05_cart.py |

**测试用例总数: 24**

## 测试环境

- **Base URL:** http://localhost:3000（可用环境变量 `BASE_URL` 覆盖）
- **Web前台:** http://localhost:5173

## 测试账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 普通用户 | buyer1 | 123456 |
| 普通用户 | buyer2 | 123456 |
| 管理员 | admin | 123456 |
| 禁用用户 | disabled_user | 123456 |

> 账号密码支持环境变量注入：`TEST_BUYER1_USER` / `TEST_BUYER1_PASSWORD` 等，详见 `conftest.py`

## CI/CD（GitHub Actions）

代码推送后自动执行 API 测试，工作流定义见 `.github/workflows/api-test.yml`。

**触发时机：** push / PR 到 main、master · 手动触发 · 每日定时回归（UTC 02:17）

**执行流程：**
1. 拉取测试代码 + 被测服务端仓库（单独仓库）
2. 启动 ShopEasy API 服务（npm install + seed + 后台启动 + 健康检查）
3. 执行 pytest 测试并生成 HTML 报告
4. 上传测试报告产物（测试失败也会上传，便于排查）

**首次使用需配置：**

| 配置项 | 位置 | 说明 |
|--------|------|------|
| `SERVER_REPO` | `api-test.yml` 顶部 env | 已设为 `lxf0627/shopeasy-server` |
| `SERVER_REPO_TOKEN` | 仓库 Settings → Secrets → Actions | 服务端仓库为 **Private** 时必配（PAT，勾选 repo 权限）；Public 仓库无需配置 |
| 测试账号密码（可选） | 仓库 Secrets | 如需脱敏，配置 `TEST_BUYER1_PASSWORD` 等变量 |

**查看测试报告：** Actions 运行记录 → Artifacts → 下载 `api-test-report`