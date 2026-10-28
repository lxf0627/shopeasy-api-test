# -*- coding: utf-8 -*-
"""
登录相关测试用例
覆盖：TC-EXC-001, TC-EXC-002
"""
import pytest
import allure


@allure.epic("用户下单流程")
@allure.feature("登录模块")
class TestLogin:
    """登录异常测试"""

    @allure.story("异常登录")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("禁用用户登录应返回403")
    @pytest.mark.p0
    @pytest.mark.login
    @pytest.mark.negative
    def test_tc_exc_001_disabled_user_login(self, api_client, test_accounts):
        """
        TC-EXC-001: 禁用用户登录应返回403
        来源: 用例-用户下单流程-2026-10-08.md 2.2 异常场景
        """
        with allure.step("执行禁用用户登录"):
            response = api_client.post('/api/auth/login', json_data={
                'username': test_accounts['disabled_user']['username'],
                'password': test_accounts['disabled_user']['password']
            })

        with allure.step("验证响应状态码为403"):
            assert response.status_code == 403, f"期望状态码403，实际{response.status_code}"

        with allure.step("验证业务错误码和消息"):
            data = response.json()
            assert data['code'] == 403, f"期望code=403，实际{data['code']}"
            assert data['message'] == '账号已被禁用', f"期望message='账号已被禁用'，实际{data['message']}"

    @allure.story("异常登录")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("错误密码登录应返回401")
    @pytest.mark.p0
    @pytest.mark.login
    @pytest.mark.negative
    def test_tc_exc_002_wrong_password_login(self, api_client):
        """
        TC-EXC-002: 错误密码登录应返回401
        来源: 用例-用户下单流程-2026-10-08.md 2.2 异常场景
        """
        with allure.step("执行错误密码登录"):
            response = api_client.post('/api/auth/login', json_data={
                'username': 'buyer1',
                'password': 'wrong_password'
            })

        with allure.step("验证响应状态码为401"):
            assert response.status_code == 401, f"期望状态码401，实际{response.status_code}"

        with allure.step("验证业务错误码和消息"):
            data = response.json()
            assert data['code'] == 401, f"期望code=401，实际{data['code']}"
            assert data['message'] == '用户名或密码错误', f"期望message='用户名或密码错误'，实际{data['message']}"

    @allure.story("正常登录")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("正常用户登录成功")
    @pytest.mark.p0
    @pytest.mark.login
    @pytest.mark.positive
    def test_login_success(self, api_client, test_accounts):
        """
        正向测试: 正常用户登录成功
        """
        with allure.step("执行正常用户登录"):
            response = api_client.post('/api/auth/login', json_data={
                'username': test_accounts['buyer1']['username'],
                'password': test_accounts['buyer1']['password']
            })

        with allure.step("验证响应状态码为200"):
            assert response.status_code == 200, f"期望状态码200，实际{response.status_code}"

        with allure.step("验证返回数据包含token和用户信息"):
            data = response.json()
            assert data['code'] == 200, f"期望code=200，实际{data['code']}"
            assert 'token' in data['data'], "响应中应包含token"
            assert data['data']['user']['username'] == 'buyer1', "用户名应为buyer1"