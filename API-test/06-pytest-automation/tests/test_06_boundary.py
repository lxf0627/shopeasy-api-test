# -*- coding: utf-8 -*-
"""
边界测试和库存测试用例
覆盖：TC-BND-003, TC-BND-004, TC-EXC-005, TC-EXC-006, TC-POS-003
"""
import pytest
import allure


@allure.epic("用户下单流程")
@allure.feature("边界测试")
class TestBoundary:
    """边界测试"""

    @allure.story("不存在的资源")
    @allure.severity(allure.severity_level.MINOR)
    @allure.description("不存在的商品ID查询应返回404")
    @pytest.mark.p2
    @pytest.mark.negative
    def test_tc_bnd_003_nonexistent_product_id(self, api_client):
        """
        TC-BND-003: 不存在的商品ID查询应返回404
        """
        test_ids = [0, -1, 99999]
        for product_id in test_ids:
            with allure.step(f"查询商品ID={product_id}"):
                response = api_client.get(f'/api/products/{product_id}')
                assert response.status_code == 404, \
                    f"商品ID={product_id} 期望状态码404，实际{response.status_code}"

    @allure.story("不存在的资源")
    @allure.severity(allure.severity_level.MINOR)
    @allure.description("不存在的订单ID查询应返回404")
    @pytest.mark.p2
    @pytest.mark.negative
    def test_tc_bnd_004_nonexistent_order_id(self, buyer1_client):
        """
        TC-BND-004: 不存在的订单ID查询应返回404
        """
        with allure.step("查询不存在的订单ID=99999"):
            response = buyer1_client.get('/api/orders/99999')

        with allure.step("验证返回404"):
            assert response.status_code == 404, f"期望状态码404，实际{response.status_code}"
            assert response.json()['message'] == '订单不存在'


@allure.epic("用户下单流程")
@allure.feature("订单异常")
class TestOrderException:
    """订单异常测试"""

    @allure.story("无效地址")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("无效地址创建订单应返回400")
    @pytest.mark.p1
    @pytest.mark.order
    @pytest.mark.negative
    def test_tc_exc_005_invalid_address(self, buyer1_client, product_id, sku_id):
        """
        TC-EXC-005: 无效地址创建订单应返回400
        """
        with allure.step("添加购物车"):
            buyer1_client.post('/api/cart', json_data={
                'productId': product_id, 'skuId': sku_id, 'quantity': 1
            })

        with allure.step("使用无效地址创建订单"):
            response = buyer1_client.post('/api/orders', json_data={'addressId': 99999})

        with allure.step("验证返回400"):
            assert response.status_code == 400, f"期望状态码400，实际{response.status_code}"
            assert response.json()['message'] == '收货地址不存在'

    @allure.story("空购物车")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("购物车为空时创建订单应返回400")
    @pytest.mark.p0
    @pytest.mark.order
    @pytest.mark.negative
    def test_tc_exc_006_empty_cart_create_order(self, buyer2_client):
        """
        TC-EXC-006: 购物车为空时创建订单应返回400
        """
        with allure.step("获取地址"):
            address_response = buyer2_client.get('/api/addresses')
            address_id = address_response.json()['data'][0]['id']

        with allure.step("尝试创建订单"):
            response = buyer2_client.post('/api/orders', json_data={'addressId': address_id})

        with allure.step("验证返回400"):
            assert response.status_code == 400, f"期望状态码400，实际{response.status_code}"
            assert response.json()['message'] == '请选择商品'


@allure.epic("用户下单流程")
@allure.feature("库存管理")
class TestStockManagement:
    """库存管理测试"""

    @allure.story("库存恢复")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("取消订单后库存应恢复")
    @pytest.mark.p1
    @pytest.mark.order
    @pytest.mark.positive
    def test_tc_pos_003_cancel_order_restore_stock(self, buyer1_client, product_id, sku_id):
        """
        TC-POS-003: 取消订单后库存应恢复
        """
        with allure.step("清空购物车"):
            cart_response = buyer1_client.get('/api/cart')
            for item in cart_response.json()['data']:
                buyer1_client.delete(f'/api/cart/{item["id"]}')

        with allure.step("获取初始库存"):
            product_response = buyer1_client.get(f'/api/products/{product_id}')
            stock_before = product_response.json()['data']['stock']
            allure.attach(f"初始库存: {stock_before}", name="库存信息")

        with allure.step("添加购物车并创建订单"):
            buyer1_client.post('/api/cart', json_data={
                'productId': product_id, 'skuId': sku_id, 'quantity': 1
            })
            address_response = buyer1_client.get('/api/addresses')
            address_id = address_response.json()['data'][0]['id']
            create_response = buyer1_client.post('/api/orders', json_data={'addressId': address_id})
            order_id = create_response.json()['data']['id']

        with allure.step("验证库存扣减"):
            product_after_order = buyer1_client.get(f'/api/products/{product_id}').json()['data']
            stock_after_order = product_after_order['stock']
            assert stock_after_order == stock_before - 1, \
                f"库存应扣减1，期望{stock_before - 1}，实际{stock_after_order}"

        with allure.step("取消订单"):
            cancel_response = buyer1_client.put(f'/api/orders/{order_id}/cancel')
            assert cancel_response.status_code == 200
            assert cancel_response.json()['data']['status'] == 'cancelled'

        with allure.step("验证库存恢复"):
            product_after_cancel = buyer1_client.get(f'/api/products/{product_id}').json()['data']
            stock_after_cancel = product_after_cancel['stock']
            assert stock_after_cancel == stock_before, \
                f"库存应恢复，期望{stock_before}，实际{stock_after_cancel}"