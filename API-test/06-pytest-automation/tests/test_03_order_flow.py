# -*- coding: utf-8 -*-
"""
核心下单流程测试用例
覆盖：TC-POS-001, TC-POS-002
"""
import pytest
import allure


@allure.epic("用户下单流程")
@allure.feature("订单流程")
class TestOrderFlow:
    """核心下单流程测试"""

    @allure.story("完整下单流程")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.description("用户完整下单流程：登录->商品->购物车->订单")
    @pytest.mark.p0
    @pytest.mark.order
    @pytest.mark.positive
    def test_tc_pos_001_full_order_flow(self, buyer1_client, product_id, sku_id):
        """
        TC-POS-001: 用户完整下单流程（登录->商品->购物车->订单）
        来源: 用例-用户下单流程-2026-10-08.md 2.1 正向场景
        """
        with allure.step("步骤1: 获取商品详情"):
            product_response = buyer1_client.get(f'/api/products/{product_id}')
            assert product_response.status_code == 200, "获取商品详情失败"
            product_data = product_response.json()['data']
            assert product_data['hasSpec'] == True, "商品应有规格"
            sku = product_data['skus'][0]
            sku_price = sku['price']
            allure.attach(f"SKU价格: {sku_price}", name="商品价格")

        with allure.step("步骤2: 添加到购物车"):
            cart_response = buyer1_client.post('/api/cart', json_data={
                'productId': product_id,
                'skuId': sku_id,
                'quantity': 1
            })
            assert cart_response.status_code in [200, 201], f"添加购物车失败，状态码{cart_response.status_code}"

        with allure.step("步骤3: 查询购物车"):
            cart_list_response = buyer1_client.get('/api/cart')
            assert cart_list_response.status_code == 200, "查询购物车失败"
            cart_items = cart_list_response.json()['data']
            assert len(cart_items) > 0, "购物车应有商品"

        with allure.step("步骤4: 获取收货地址"):
            address_response = buyer1_client.get('/api/addresses')
            assert address_response.status_code == 200, "获取地址失败"
            addresses = address_response.json()['data']
            assert len(addresses) > 0, "应有收货地址"
            address_id = addresses[0]['id']

        with allure.step("步骤5: 创建订单"):
            order_response = buyer1_client.post('/api/orders', json_data={
                'addressId': address_id
            })
            assert order_response.status_code == 201, f"创建订单失败，状态码{order_response.status_code}"
            order_data = order_response.json()['data']
            assert order_data['status'] == 'pending', f"订单状态应为pending，实际{order_data['status']}"
            assert order_data['totalAmount'] == sku_price, \
                f"订单金额应为{sku_price}，实际{order_data['totalAmount']}"
            allure.attach(f"订单号: {order_data['orderNo']}", name="订单信息")

        with allure.step("步骤6: 查询订单详情"):
            order_id = order_data['id']
            detail_response = buyer1_client.get(f'/api/orders/{order_id}')
            assert detail_response.status_code == 200, "查询订单详情失败"
            detail_data = detail_response.json()['data']
            assert detail_data['id'] == order_id, "订单ID应一致"
            assert len(detail_data['OrderItems']) > 0, "订单应有商品项"

    @allure.story("订单状态流转")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.description("订单状态流转: pending->paid->shipped->received")
    @pytest.mark.p0
    @pytest.mark.order
    @pytest.mark.positive
    def test_tc_pos_002_order_status_flow(self, buyer1_client, admin_client, product_id, sku_id):
        """
        TC-POS-002: 订单状态流转 pending->paid->shipped->received
        来源: 用例-用户下单流程-2026-10-08.md 2.1 正向场景
        """
        with allure.step("准备: 创建测试订单"):
            buyer1_client.post('/api/cart', json_data={
                'productId': product_id,
                'skuId': sku_id,
                'quantity': 1
            })
            address_response = buyer1_client.get('/api/addresses')
            address_id = address_response.json()['data'][0]['id']
            create_response = buyer1_client.post('/api/orders', json_data={
                'addressId': address_id
            })
            assert create_response.status_code == 201, "创建订单失败"
            order_id = create_response.json()['data']['id']
            allure.attach(f"订单ID: {order_id}", name="测试订单")

        with allure.step("步骤1: 支付订单 (pending -> paid)"):
            pay_response = buyer1_client.post(f'/api/orders/{order_id}/pay', json_data={
                'method': 'balance'
            })
            assert pay_response.status_code == 200, f"支付失败，状态码{pay_response.status_code}"
            assert pay_response.json()['data']['order']['status'] == 'paid', "支付后状态应为paid"

        with allure.step("步骤2: 管理员发货 (paid -> shipped)"):
            ship_response = admin_client.put(f'/api/admin/orders/{order_id}/ship')
            assert ship_response.status_code == 200, f"发货失败，状态码{ship_response.status_code}"
            assert ship_response.json()['data']['status'] == 'shipped', "发货后状态应为shipped"

        with allure.step("步骤3: 用户确认收货 (shipped -> received)"):
            confirm_response = buyer1_client.put(f'/api/orders/{order_id}/confirm')
            assert confirm_response.status_code == 200, f"确认收货失败，状态码{confirm_response.status_code}"
            assert confirm_response.json()['data']['status'] == 'received', "确认收货后状态应为received"

        with allure.step("步骤4: 查询最终状态"):
            final_response = buyer1_client.get(f'/api/orders/{order_id}')
            assert final_response.status_code == 200, "查询订单失败"
            assert final_response.json()['data']['status'] == 'received', "最终状态应为received"