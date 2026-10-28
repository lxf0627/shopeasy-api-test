# -*- coding: utf-8 -*-
"""
购物车和数据一致性测试用例
覆盖：TC-DAT-001, TC-DAT-002, TC-EXC-003, TC-EXC-004, TC-EXP-001, TC-EXP-002, TC-EXP-003
"""
import pytest
import allure


@allure.epic("用户下单流程")
@allure.feature("购物车")
class TestCartException:
    """购物车异常测试"""

    @allure.story("缺少必填参数")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("有规格商品未选SKU应返回400")
    @pytest.mark.p0
    @pytest.mark.cart
    @pytest.mark.negative
    def test_tc_exc_003_no_sku_selected(self, buyer1_client, product_id):
        """
        TC-EXC-003: 有规格商品未选SKU应返回400
        """
        with allure.step("添加有规格商品但不传skuId"):
            response = buyer1_client.post('/api/cart', json_data={
                'productId': product_id,
                'quantity': 1
            })

        with allure.step("验证返回400"):
            assert response.status_code == 400, f"期望状态码400，实际{response.status_code}"
            data = response.json()
            assert '规格' in data['message'], f"期望message包含'规格'，实际{data['message']}"

    @allure.story("不存在的商品")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("不存在的商品加入购物车应返回404")
    @pytest.mark.p1
    @pytest.mark.cart
    @pytest.mark.negative
    def test_tc_exc_004_nonexistent_product(self, buyer1_client):
        """
        TC-EXC-004: 不存在的商品加入购物车应返回404
        """
        with allure.step("添加不存在的商品"):
            response = buyer1_client.post('/api/cart', json_data={
                'productId': 99999,
                'quantity': 1
            })

        with allure.step("验证返回404"):
            assert response.status_code == 404, f"期望状态码404，实际{response.status_code}"
            assert response.json()['message'] == '商品不存在'


@allure.epic("用户下单流程")
@allure.feature("购物车行为")
class TestCartBehavior:
    """购物车行为测试"""

    @allure.story("库存校验")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("零库存商品加入购物车应返回400")
    @pytest.mark.p1
    @pytest.mark.cart
    @pytest.mark.negative
    def test_tc_exp_001_zero_stock_product(self, buyer1_client):
        """
        TC-EXP-001: 零库存商品加入购物车应返回400
        """
        with allure.step("添加零库存商品(id=27)"):
            response = buyer1_client.post('/api/cart', json_data={
                'productId': 27,
                'quantity': 1
            })

        with allure.step("验证返回400 库存不足"):
            assert response.status_code == 400, f"期望状态码400，实际{response.status_code}"
            assert response.json()['message'] == '库存不足'

    @allure.story("数量累加")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("同一商品重复添加购物车应累加数量")
    @pytest.mark.p1
    @pytest.mark.cart
    @pytest.mark.positive
    def test_tc_exp_002_duplicate_add_to_cart(self, buyer1_client, product_id, sku_id):
        """
        TC-EXP-002: 同一商品重复添加购物车应累加数量
        """
        with allure.step("第一次添加"):
            response1 = buyer1_client.post('/api/cart', json_data={
                'productId': product_id, 'skuId': sku_id, 'quantity': 1
            })
            assert response1.status_code in [200, 201]

        with allure.step("第二次添加"):
            response2 = buyer1_client.post('/api/cart', json_data={
                'productId': product_id, 'skuId': sku_id, 'quantity': 1
            })
            assert response2.status_code == 200

        with allure.step("验证数量累加"):
            cart_response = buyer1_client.get('/api/cart')
            cart_items = cart_response.json()['data']
            for item in cart_items:
                if item['productId'] == product_id and item['skuId'] == sku_id:
                    assert item['quantity'] >= 2, f"期望数量>=2，实际{item['quantity']}"

    @allure.story("无规格商品")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("无规格商品不传skuId应能加入购物车")
    @pytest.mark.p1
    @pytest.mark.cart
    @pytest.mark.positive
    def test_tc_exp_003_no_spec_product_without_sku(self, buyer1_client):
        """
        TC-EXP-003: 无规格商品不传skuId应能加入购物车
        """
        with allure.step("添加无规格商品(AirPods Pro 2, id=3)"):
            response = buyer1_client.post('/api/cart', json_data={
                'productId': 3,
                'quantity': 1
            })

        with allure.step("验证返回201"):
            assert response.status_code == 201, f"期望状态码201，实际{response.status_code}"


@allure.epic("用户下单流程")
@allure.feature("数据一致性")
class TestDataConsistency:
    """数据一致性测试"""

    @allure.story("购物车清空")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("创建订单后购物车应清空")
    @pytest.mark.p0
    @pytest.mark.order
    @pytest.mark.positive
    def test_tc_dat_001_cart_empty_after_order(self, buyer1_client, product_id, sku_id):
        """
        TC-DAT-001: 创建订单后购物车应清空
        """
        with allure.step("添加购物车"):
            buyer1_client.post('/api/cart', json_data={
                'productId': product_id, 'skuId': sku_id, 'quantity': 1
            })

        with allure.step("查询购物车确认有商品"):
            cart_before = buyer1_client.get('/api/cart').json()['data']
            assert len(cart_before) > 0, "购物车应有商品"

        with allure.step("创建订单"):
            address_response = buyer1_client.get('/api/addresses')
            address_id = address_response.json()['data'][0]['id']
            create_response = buyer1_client.post('/api/orders', json_data={'addressId': address_id})
            assert create_response.status_code == 201, "创建订单失败"

        with allure.step("验证购物车为空"):
            cart_after = buyer1_client.get('/api/cart').json()['data']
            assert len(cart_after) == 0, f"购物车应为空，实际有{len(cart_after)}件商品"

    @allure.story("金额一致性")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("订单金额应与商品价格一致")
    @pytest.mark.p0
    @pytest.mark.order
    @pytest.mark.positive
    def test_tc_dat_002_order_amount_matches_price(self, buyer1_client, product_id, sku_id):
        """
        TC-DAT-002: 订单金额应与商品价格一致
        """
        with allure.step("获取商品价格"):
            product_response = buyer1_client.get(f'/api/products/{product_id}')
            sku_price = product_response.json()['data']['skus'][0]['price']
            allure.attach(f"SKU价格: {sku_price}", name="商品价格")

        with allure.step("添加购物车并创建订单"):
            buyer1_client.post('/api/cart', json_data={
                'productId': product_id, 'skuId': sku_id, 'quantity': 1
            })
            address_response = buyer1_client.get('/api/addresses')
            address_id = address_response.json()['data'][0]['id']
            create_response = buyer1_client.post('/api/orders', json_data={'addressId': address_id})
            order_data = create_response.json()['data']

        with allure.step("验证订单金额"):
            assert order_data['totalAmount'] == sku_price, \
                f"订单金额应为{sku_price}，实际{order_data['totalAmount']}"

        with allure.step("验证订单项价格"):
            order_id = order_data['id']
            detail_response = buyer1_client.get(f'/api/orders/{order_id}')
            order_items = detail_response.json()['data']['OrderItems']
            assert order_items[0]['price'] == sku_price, \
                f"订单项价格应为{sku_price}，实际{order_items[0]['price']}"