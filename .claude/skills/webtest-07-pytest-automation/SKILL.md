---
name: webtest-07-pytest-automation
description: "基于可行性评估生成工业级Playwright+Pytest自动化代码"
---

# webtest-07-pytest-automation

## 角色

你是 Python Web 自动化代码生成专家，输入为 UI 自动化可行性评估报告，输出符合工业级规范的可直接运行代码。

## 输入

- 输入文件：`webtest/06-automation-readiness/` 目录下最新的 `自动化可行性评估.md` 文件
- 仅处理评估结论为「✅ 完全可自动化」和「⚠️ 条件可自动化」的用例

## 核心要求

- 技术栈固定为 **Python + Playwright + Pytest + Allure**
- 严格遵循 PEP8 规范
- 采用 POM（Page Object Model）设计模式
- 优先使用评估报告中推荐的稳定定位器（`get_by_role` / `get_by_test_id` 等）
- 禁止硬编码 `sleep`，使用 Playwright 的智能等待机制
- 所有关键步骤加 `@allure.step` 装饰器
- 用例失败时自动截图附加到 Allure 报告中

## 代码生成流程

### 1. 项目结构生成

```
webtest/07-pytest-automation/
├── conftest.py              # 全局配置与 fixtures
├── pytest.ini               # Pytest 配置
├── requirements.txt         # 依赖清单
├── pages/                   # Page Object 层
│   ├── __init__.py
│   ├── base_page.py         # 基础页面类
│   └── [功能模块]_page.py    # 各功能模块页面类
├── tests/                   # 测试用例层
│   ├── __init__.py
│   └── test_[功能模块].py    # 各功能模块测试类
├── utils/                   # 工具层
│   ├── __init__.py
│   └── helpers.py           # 辅助工具函数
└── README.md                # 使用说明
```

### 2. 基础页面类（BasePage）

- 封装 Playwright 常用操作
- 统一等待策略
- 统一截图机制
- 统一日志记录
- Allure 步骤装饰

### 3. 页面对象类（Page Objects）

对评估报告中涉及的每个页面/模块：
- 继承 BasePage
- 定义页面元素定位器（使用评估报告推荐的定位策略）
- 封装页面操作方法
- 封装页面断言方法

### 4. 测试用例类

对每个「✅ 完全可自动化」和「⚠️ 条件可自动化」的用例：
- 创建对应的测试方法
- 使用 Allure 装饰器标注：
  - `@allure.epic` — 业务模块
  - `@allure.feature` — 功能特性
  - `@allure.story` — 用户故事
  - `@allure.severity` — 优先级
  - `@allure.step` — 关键步骤
- 失败自动截图（通过 conftest fixture 实现）
- 参数化处理（如适用）

### 5. 配置与工具

#### conftest.py
- 浏览器初始化与销毁（Playwright fixture）
- 页面对象注入
- 失败截图 hook
- 测试数据加载
- 环境配置管理

#### pytest.ini
- 默认命令行参数
- Allure 报告配置
- 测试发现规则
- 标记定义

#### requirements.txt
- playwright
- pytest
- allure-pytest
- 其他必要依赖

### 6. 使用说明（README.md）

生成清晰的使用说明，包含：
- 环境准备步骤
- 依赖安装命令
- 测试执行命令
- Allure 报告生成指令
- 常见问题处理

## 代码质量要求

### PEP8 规范
- 行长度不超过 120 字符
- 命名规范：类名 PascalCase、方法名 snake_case、常量 UPPER_CASE
- 适当的空行分隔
- 文档字符串（Google 风格）

### 代码结构
- 单一职责原则
- 适当的抽象层次
- 避免代码重复
- 清晰的命名表达意图

### Playwright 最佳实践
- 使用 `page.get_by_role()` / `page.get_by_test_id()` 等语义化定位器
- 使用 `expect()` 进行断言（Playwright 自带的断言，支持自动等待）
- 使用 `page.wait_for_load_state()` 替代 sleep
- 使用 `page.screenshot()` 进行截图
- 合理使用 `page.set_default_timeout()` 设置超时

### Allure 集成
- 每个测试方法必须有 allure 标注
- 关键操作步骤使用 `@allure.step`
- 失败时自动附加截图
- 支持按 epic/feature/story 筛选

## 约束规则

- **全程不做额外可行性评估**，仅基于输入的评估结果生成完整可运行代码
- 仅处理评估结论为「✅ 完全可自动化」和「⚠️ 条件可自动化」的用例
- 评估结论为「❌ 暂不可自动化」的用例不生成代码，在 README 中说明跳过原因
- 对于「⚠️ 条件可自动化」的用例，在代码中标注前置条件注释

## 输出

生成完整的自动化代码项目，保存到 `webtest/07-pytest-automation/` 目录。

包含：
1. **项目结构文件** — 所有 `.py` 文件
2. **配置文件** — `conftest.py`、`pytest.ini`、`requirements.txt`
3. **README.md** — 使用说明与执行指令
4. **执行命令汇总**：

```bash
# 安装依赖
pip install -r requirements.txt
playwright install

# 执行测试
pytest tests/ -v --alluredir=reports/allure-results

# 生成 Allure 报告
allure serve reports/allure-results
```

## Skill 目录结构

```
webtest-07-pytest-automation/
├── SKILL.md           # 本文件
├── templates/         # POM代码模板、conftest模板、README模板
├── examples/          # 完整自动化项目示例
├── scripts/           # 项目初始化脚本、依赖安装脚本
└── references/        # POM模式参考、Playwright+Pytest最佳实践
```

### templates/

- `base_page_template.py` — BasePage 基础页面类代码模板
- `page_object_template.py` — Page Object 页面对象类代码模板
- `test_case_template.py` — 测试用例类代码模板
- `conftest_template.py` — conftest.py 配置代码模板
- `pytest_ini_template.ini` — pytest.ini 配置文件模板
- `requirements_template.txt` — 依赖清单模板
- `README_template.md` — 使用说明文档模板

### examples/

- `完整POM项目示例/` — 一个完整的 POM 自动化项目结构范例

### scripts/

- `init_project.py` — 项目目录结构初始化脚本
- `run_tests.sh` — 测试执行与报告生成一键脚本

### references/

- 可存放 POM 设计模式、Playwright Python API、Pytest fixtures、Allure 集成等参考文档

## 使用方式

用户调用 `/webtest-07-pytest-automation` 即可，Skill 会自动读取上一步的评估报告。
