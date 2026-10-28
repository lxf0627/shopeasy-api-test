# -*- coding: utf-8 -*-
"""
权限相关测试用例
覆盖：TC-AUTH-001, TC-AUTH-002, TC-AUTH-003
"""
import pytest
import allure


@allure.epic("用户下单流程")
@allure.feature("权限控制")
class TestAuth:
    """权限控制测试"""

    @allure.story("未认证访问")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("未登录访问需认证接口应返回401")
    @pytest.mark.p0
    @pytest.mark.auth
    @pytest.mark.negative
    def test_tc_auth_001_unauthenticated_access(self, api_client):
        """
        TC-AUTH-001: 未登录访问需认证接口应返回401
        来源: 用例-用户下单流程-2026-10-08.md 2.4 权限场景
        """
        # 确保没有token
        api_client.clear_token()

        # 测试多个需认证接口
        endpoints = [
            ('GET', '/api/addresses'),
            ('GET', '/api/cart'),
            ('POST', '/api/orders'),
        ]

        for method, path in endpoints:
            with allure.step(f"测试 {method} {path}"):
                response = api_client.request(method, path, json_data={'addressId': 1} if method == 'POST' else None)
                assert response.status_code == 401, \
                    f"{method} {path} 期望状态码401，实际{response.status_code}"
                data = response.json()
                assert data['code'] == 401, \
                    f"{method} {path} 期望code=401，实际{data['code']}"

    @allure.story("无效凭证")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("无效token访问接口应返回401")
    @pytest.mark.p1
    @pytest.mark.auth
    @pytest.mark.negative
    def test_tc_auth_002_invalid_token(self, api_client):
        """
        TC-AUTH-002: 无效token访问接口应返回401
        来源: 用例-用户下单流程-2026-10-08.md 2.4 权限场景
        """
        with allure.step("设置伪造的token"):
            fake_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6OTk5LCJyb2xlIjoidXNlciIsImlhdCI6MTcxMDAwMDAwMH0.FAKE_SIGNATURE"
            api_client.set_token(fake_token)

        with allure.step("测试访问接口"):
            response = api_client.get('/api/addresses')

        with allure.step("验证返回401"):
            assert response.status_code == 401, f"期望状态码401，实际{response.status_code}"
            data = response.json()
            assert data['code'] == 401, f"期望code=401，实际{data['code']}"

    @allure.story("权限越级")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("普通用户访问管理员接口应返回403")
    @pytest.mark.p0
    @pytest.mark.auth
    @pytest.mark.negative
    def test_tc_auth_003_normal_user_admin_api(self, buyer1_client):
        """
        TC-AUTH-003: 普通用户访问管理员接口应返回403
        来源: 用例-用户下单流程-2026-10-08.md 2.4 权限场景
        """
        with allure.step("尝试访问管理员发货接口"):
            response = buyer1_client.put('/api/admin/orders/1/ship')

        with allure.step("验证返回403"):
            assert response.status_code == 403, f"期望状态码403，实际{response.status_code}"
            data = response.json()
            assert data['code'] == 403, f"期望code=403，实际{data['code']}"
            assert data['message'] == '无权限访问', f"期望message='无权限访问'，实际{data['message']}"