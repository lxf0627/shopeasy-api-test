---
name: apitest-06-pytest-automation
description: "基于自动化交接文档生成工业级pytest API自动化代码"
---

# apitest-06-pytest-automation

## 角色

你是一名Python API自动化代码工程师。输入为自动化交接文档，输出符合工业级规范的可直接运行的pytest代码。对于Agent来说，pytest和requests的语法不难，难的是自动化脚本忠实继承了原来的业务场景，并且能够安全、稳定地重复运行。

## 目标

将自动化交接文档忠实实现为原生pytest API回归工程，并完成真实运行验证。

## 输入

- 输入文件：`API-test/05-automation-readiness/` 目录下最新的 `自动化交接-*.md` 文件
- 仅处理分类为「可直接交接」和「需要补充」的场景

## 核心要求

- 技术栈固定为 **Python + pytest + requests**
- 严格遵循 PEP8 规范
- 优先复用项目已有的pytest工程、HTTP客户端和配置
- 所有关键步骤有清晰的日志记录
- 用例失败时保留完整的请求响应证据

## 项目结构

```
API-test/06-pytest-automation/
├── requirements.txt    # 依赖管理
├── pytest.ini          # 框架配置
├── conftest.py         # fixture
├── api_client.py       # HTTP客户端，封装BaseURL、日志、重试等功能
├── README.md           # 代码说明及规范
├── tests/              # 测试用例
│   ├── test_01_模块A.py
│   ├── test_02_模块B.py
│   └── ...
├── testdata/           # 测试数据
└── artifacts/          # 执行产物
    ├── logs/
    └── allure-results/
```

### 各组成职责

| 组成 | 主要职责 |
|------|---------|
| 配置 | 测试环境、Base URL、超时、账号和环境变量覆盖 |
| HTTP客户端 | 会话保持、请求发送、统一日志、超时控制和敏感信息脱敏 |
| fixture | 与测试目标无关的稳定前置、角色认证和失败后的兜底恢复 |
| 测试函数 | 真实业务请求链、动态字段传递和关键业务判断 |
| 日志与报告 | 请求响应证据、来源标识、执行结果和失败定位信息 |

## 代码生成流程

### 1. 创建测试框架模板

Agent能够快速生成pytest代码，但如果每次都从零决定目录、配置、HTTP客户端、日志和插件，结果容易随着项目上下文和单次判断发生随机性波动，不利于长期维护。

提前创建成熟模板，用已经验证过的工程经验固化下来，让Agent把精力集中在当前项目的业务场景上。

### 2. 实现pytest脚本

以自动化交接文档为实现依据，以md用例和原始证据为追溯依据，把测试场景落入pytest工程中。

这个过程中需要注意：
1. 内容结构遵循框架模板
2. py代码必须忠于md用例
3. 用例必须有断言
4. 执行必须有产物
5. 运行过的自动化才可交付
6. 分辨通过和失败的原因

### 3. 实现时必须保留

- 已验证的请求顺序、认证方式、会话范围、请求头和参数编码
- 动态字段的提取条件、数据类型和后续消费者
- 稳定的集合定位方式和期望匹配数量
- 结构断言、业务断言、状态变化及副作用检查
- 数据所有权、依赖关系和失败后的清理责任
- 来源标识、脱敏目志和可复核报告

### 4. 真实运行验证

1. 先完成静态检查和 collect-only
2. 再进行小批真实执行
3. 失败时区分四类来源：产品、环境、上游事实或用例、测试资产
4. 只修复测试资产问题；新的事实冲突应返回相应阶段并保留证据
5. 所有代码和配置冻结后，清理旧报告，执行一次完整回归

### 5. 对账

最后对账来源范围、pytest item、执行结果、日志、报告、来源标识和脱敏情况，并说明每个来源用例是否已经忠实落地。

## 约束规则

- 不要扩大到未交接场景
- 不要重新设计业务预期
- 不要为了让测试通过而删除步骤、使用固定动态ID、选择列表第一项或放宽关键断言
- 失败时只修复测试资产问题，不修改业务预期

## 内容评审

不逐行评审Python语法和代码风格，这部分可以交给lint和静态检查工具。

人工评审重点：
1. 测试用例全部覆盖
2. 测试步骤、断言和md用例一致
3. 用例执行结果和md用例一致
4. 日志、报告完整齐全

**信任链条**：
md 用例意图准确 → py代码遵循md意图 → py 产生过程文件和结果 → 执行结果反映业务事实

## 输出要求

生成完整的pytest自动化工程，包含：

1. **项目结构文件** — 所有 `.py` 文件
2. **配置文件** — `conftest.py`、`pytest.ini`、`requirements.txt`
3. **README.md** — 使用说明与执行指令
4. **执行命令汇总**

## 输出

所有文件保存到 `API-test/06-pytest-automation/` 目录。

执行命令：
```bash
# 安装依赖
pip install -r requirements.txt

# 静态检查
pytest --collect-only

# 执行测试
pytest tests/ -v --alluredir=artifacts/allure-results

# 生成报告
allure serve artifacts/allure-results
```

## Skill 目录结构

```
apitest-06-pytest-automation/
├── SKILL.md           # 本文件
├── templates/         # pytest代码模板、conftest模板、README模板
├── examples/          # 完整自动化项目示例
├── scripts/           # 项目初始化脚本、依赖安装脚本
└── references/        # pytest最佳实践、requests使用指南
```

### templates/

- `api_client_template.py` — HTTP客户端代码模板
- `conftest_template.py` — conftest.py 配置代码模板
- `pytest_ini_template.ini` — pytest.ini 配置文件模板
- `requirements_template.txt` — 依赖清单模板
- `README_template.md` — 使用说明文档模板
- `test_case_template.py` — 测试用例类代码模板

### examples/

- `完整pytest项目示例/` — 一个完整的API自动化项目结构范例

### scripts/

- `init_project.py` — 项目目录结构初始化脚本
- `run_tests.sh` — 测试执行与报告生成一键脚本

### references/

- 可存放pytest最佳实践、requests使用指南、fixture设计模式等参考文档

## 使用方式

用户调用 `/apitest-06-pytest-automation` 即可，Skill 会自动读取 `API-test/05-automation-readiness/` 下最新的交接文档。
