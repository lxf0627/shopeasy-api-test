# -*- coding: utf-8 -*-
"""
订单状态相关测试用例
覆盖：TC-STS-001, TC-STS-002, TC-STS-003, TC-STS-004
"""
import pytest
import allure


@allure.epic("用户下单流程")
@allure.feature("订单状态")
class TestOrderStatus:
    """订单状态异常测试"""

    @allure.story("重复支付")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("非pending状态订单支付应返回400")
    @pytest.mark.p0
    @pytest.mark.order
    @pytest.mark.negative
    def test_tc_sts_001_pay_non_pending_order(self, buyer1_client, product_id, sku_id):
        """
        TC-STS-001: 非pending状态订单支付应返回400
        """
        with allure.step("准备: 创建并支付订单"):
            buyer1_client.post('/api/cart', json_data={'productId': product_id, 'skuId': sku_id, 'quantity': 1})
            address_response = buyer1_client.get('/api/addresses')
            address_id = address_response.json()['data'][0]['id']
            create_response = buyer1_client.post('/api/orders', json_data={'addressId': address_id})
            order_id = create_response.json()['data']['id']
            buyer1_client.post(f'/api/orders/{order_id}/pay', json_data={'method': 'balance'})

        with allure.step("测试: 尝试再次支付"):
            response = buyer1_client.post(f'/api/orders/{order_id}/pay', json_data={'method': 'balance'})

        with allure.step("验证: 返回400"):
            assert response.status_code == 400, f"期望状态码400，实际{response.status_code}"
            data = response.json()
            assert data['code'] == 400, f"期望code=400，实际{data['code']}"
            assert data['message'] == '订单状态不支持支付', f"期望message='订单状态不支持支付'，实际{data['message']}"

    @allure.story("取消已支付订单")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("非pending状态订单取消应返回400")
    @pytest.mark.p0
    @pytest.mark.order
    @pytest.mark.negative
    def test_tc_sts_002_cancel_non_pending_order(self, buyer1_client, product_id, sku_id):
        """
        TC-STS-002: 非pending状态订单取消应返回400
        """
        with allure.step("准备: 创建并支付订单"):
            buyer1_client.post('/api/cart', json_data={'productId': product_id, 'skuId': sku_id, 'quantity': 1})
            address_response = buyer1_client.get('/api/addresses')
            address_id = address_response.json()['data'][0]['id']
            create_response = buyer1_client.post('/api/orders', json_data={'addressId': address_id})
            order_id = create_response.json()['data']['id']
            buyer1_client.post(f'/api/orders/{order_id}/pay', json_data={'method': 'balance'})

        with allure.step("测试: 尝试取消已支付的订单"):
            response = buyer1_client.put(f'/api/orders/{order_id}/cancel')

        with allure.step("验证: 返回400"):
            assert response.status_code == 400, f"期望状态码400，实际{response.status_code}"
            data = response.json()
            assert data['message'] == '只能取消待支付的订单'

    @allure.story("发货未支付订单")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("非paid状态订单发货应返回400")
    @pytest.mark.p0
    @pytest.mark.order
    @pytest.mark.negative
    def test_tc_sts_003_ship_pending_order(self, buyer1_client, admin_client, product_id, sku_id):
        """
        TC-STS-003: 非paid状态订单发货应返回400
        """
        with allure.step("准备: 创建订单(pending状态)"):
            buyer1_client.post('/api/cart', json_data={'productId': product_id, 'skuId': sku_id, 'quantity': 1})
            address_response = buyer1_client.get('/api/addresses')
            address_id = address_response.json()['data'][0]['id']
            create_response = buyer1_client.post('/api/orders', json_data={'addressId': address_id})
            order_id = create_response.json()['data']['id']

        with allure.step("测试: 尝试发货pending状态的订单"):
            response = admin_client.put(f'/api/admin/orders/{order_id}/ship')

        with allure.step("验证: 返回400"):
            assert response.status_code == 400, f"期望状态码400，实际{response.status_code}"
            assert response.json()['message'] == '只能发货已支付的订单'

    @allure.story("确认收货未发货订单")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("非shipped状态确认收货应返回400")
    @pytest.mark.p0
    @pytest.mark.order
    @pytest.mark.negative
    def test_tc_sts_004_confirm_pending_order(self, buyer1_client, product_id, sku_id):
        """
        TC-STS-004: 非shipped状态确认收货应返回400
        """
        with allure.step("准备: 创建订单(pending状态)"):
            buyer1_client.post('/api/cart', json_data={'productId': product_id, 'skuId': sku_id, 'quantity': 1})
            address_response = buyer1_client.get('/api/addresses')
            address_id = address_response.json()['data'][0]['id']
            create_response = buyer1_client.post('/api/orders', json_data={'addressId': address_id})
            order_id = create_response.json()['data']['id']

        with allure.step("测试: 尝试确认收货pending状态的订单"):
            response = buyer1_client.put(f'/api/orders/{order_id}/confirm')

        with allure.step("验证: 返回400"):
            assert response.status_code == 400, f"期望状态码400，实际{response.status_code}"
            assert response.json()['message'] == '只能确认已发货的订单'