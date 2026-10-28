# ShopEasy UI 自动化测试项目

基于 **Python + Playwright + Pytest + Allure** 的工业级 UI 自动化测试框架。

## 项目结构

```
07-pytest-automation/
├── conftest.py              # 全局配置与 fixtures
├── pytest.ini               # Pytest 配置
├── requirements.txt         # 依赖清单
├── pages/                   # Page Object 层
│   ├── base_page.py         # 基础页面类
│   ├── login_page.py        # 登录页
│   ├── home_page.py         # 首页
│   ├── product_page.py      # 商品详情页
│   ├── cart_page.py         # 购物车页
│   ├── checkout_page.py     # 结算页
│   ├── order_page.py        # 订单页
│   ├── profile_page.py      # 个人中心页
│   └── admin_page.py        # 后台管理页
├── tests/                   # 测试用例层
│   ├── test_login.py        # 登录测试 (P0)
│   ├── test_search.py       # 搜索测试 (P0)
│   ├── test_cart.py         # 购物车测试 (P0)
│   ├── test_checkout.py     # 结算测试 (P0)
│   ├── test_order.py        # 订单测试 (P0)
│   ├── test_bug_regression.py # Bug 回归 (P0)
│   ├── test_product.py      # 商品详情 (P1)
│   ├── test_state_machine.py # 状态机 (P1)
│   ├── test_admin.py        # 后台管理 (P1)
│   ├── test_profile.py      # 个人中心 (P2)
│   └── test_buyer2.py       # buyer2 流程 (P3)
├── utils/                   # 工具层
│   └── helpers.py           # 辅助函数
└── reports/                 # 测试报告
    └── allure-results/      # Allure 原始数据
```

## 环境准备

```bash
# 1. 安装 Python 依赖
pip install -r requirements.txt

# 2. 安装 Playwright 浏览器
python -m playwright install chromium
```

## 执行测试

```bash
# 执行全部测试
pytest tests/ -v --alluredir=reports/allure-results

# 仅执行 P0 冒烟测试
pytest tests/ -m p0 -v --alluredir=reports/allure-results

# 仅执行登录模块
pytest tests/test_login.py -v --alluredir=reports/allure-results

# 仅执行 Bug 回归
pytest tests/ -m bug_regression -v --alluredir=reports/allure-results
```

## 生成 Allure 报告

```bash
# 方式一：Allure CLI（需安装 Java + Allure）
allure serve reports/allure-results

# 方式二：纯 Python 生成器
python generate_report.py
```

## 测试账户

| 角色 | 用户名 | 密码 | 说明 |
|------|--------|------|------|
| 管理员 | admin | 123456 | 后台管理权限 |
| 买家1 | buyer1 | 123456 | 张三 |
| 买家2 | buyer2 | 123456 | 李四 |
| 禁用用户 | disabled_user | 123456 | 已禁用，登录返回 403 |

## 已知 Bug 说明

| Bug | 描述 | 影响用例 | 当前处理 |
|-----|------|----------|----------|
| Bug① | 订单详情收货信息为空 | F-TC-018/024/040d | 混合断言（API+UI） |
| Bug② | 后台订单操作列为空 | B-TC-012 | 断言操作列为空 |
| Bug③ | 前端地址对话框发送 id 字段 | F-TC-031/032 | 跳过（❌） |
| Bug④ | 零库存商品详情页崩溃 | F-TC-013 | 跳过（❌） |
| Bug⑤ | 前端分类对话框发送 id 字段 | B-TC-008/009 | API 替代 |
| Bug⑥ | 分类排序字段映射错误 | B-TC-009 | 低影响 |
| Bug⑦ | 删除有商品关联的分类 | B-TC-011 | 验证孤儿数据 |

## 跳过的用例（❌ 暂不可自动化）

- **F-TC-013**: 库存为0时加入购物车 — Bug④ 导致页面崩溃
- **F-TC-031**: 新增收货地址 — Bug③ 导致前端操作失败
- **F-TC-032**: 编辑收货地址 — Bug③ 导致前端操作失败