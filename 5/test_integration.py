import pytest
from decimal import Decimal
from uuid import uuid4
from pathlib import Path

from services import AuthService, MenuService, CartService, OrderService
from models import OrderStatus, Sweetness

@pytest.fixture
def clean_data_dir():
    """清理测试数据目录"""
    data_dir = Path(__file__).parent.parent / 'data'
    for filename in ['users.json', 'menu_items.json', 'carts.json', 'orders.json', 'toppings.json']:
        filepath = data_dir / filename
        if filepath.exists():
            filepath.unlink()
    yield

class TestSystemIntegration:
    """系统集成测试"""

    def test_full_order_flow(self, clean_data_dir):
        """
        测试用例 1: 完整的下单流程 (自底向上集成)
        涉及: AuthService -> MenuService -> CartService -> OrderService
        """
        # 1. 准备基础数据 (管理员操作)
        menu_service = MenuService()
        item1 = menu_service.create_item("四季春", Decimal("12.00"), "茶饮")
        item2 = menu_service.create_item("波霸奶茶", Decimal("16.00"), "经典")
        topping = menu_service.create_topping("红豆", Decimal("3.00"))

        # 2. 用户注册与登录
        auth_service = AuthService()
        success, _, user = auth_service.register("小王", "13512345678")
        assert success is True
        
        success, _, logged_user = auth_service.login("13512345678")
        assert success is True
        user_id = logged_user.user_id

        # 3. 浏览菜单并添加购物车
        cart_service = CartService()
        # 添加第一件商品：四季春，无糖，不加小料
        cart_service.add_to_cart(user_id, item1.item_id, quantity=1, sweetness=Sweetness.NONE)
        # 添加第二件商品：波霸奶茶，七分糖，加红豆
        cart_service.add_to_cart(user_id, item2.item_id, quantity=2, sweetness=Sweetness.SEVEN, topping_ids=[topping.topping_id])

        cart = cart_service.get_cart(user_id)
        assert len(cart.items) == 2
        # 总价: 12*1 + (16+3)*2 = 12 + 38 = 50
        assert cart.total() == Decimal("50.00")

        # 4. 下单结算
        order_service = OrderService()
        success, msg, order = order_service.place_order(user_id, remark="少放点红豆")
        assert success is True
        assert order.status == OrderStatus.PENDING
        assert order.total_amount() == Decimal("50.00")
        
        # 验证购物车已清空
        assert len(order_service.cart_service.get_cart(user_id).items) == 0

        # 5. 管理员更新订单状态
        success, msg = order_service.update_status(order.order_id, OrderStatus.PREPARING)
        assert success is True, f"更新状态失败: {msg}"
        
        updated_order = order_service.get_order(order.order_id)
        assert updated_order.status == OrderStatus.PREPARING

    def test_invalid_flow_handling(self, clean_data_dir):
        """
        测试用例 2: 异常流程处理集成
        """
        auth_service = AuthService()
        menu_service = MenuService()
        order_service = OrderService()
        cart_service = CartService()

        # 注册用户 (使用合法的手机号)
        success, msg, user = auth_service.register("测试员", "110110110")
        assert success is True, f"注册失败: {msg}"
        user_id = user.user_id

        # 尝试为空购物车下单
        success, msg, order = order_service.place_order(user_id)
        assert success is False
        assert len(msg) > 0 # 只要有错误消息即可

        # 添加已下架商品到购物车
        item = menu_service.create_item("过期奶茶", Decimal("5.00"))
        menu_service.mark_sold_out(item.item_id, True)
        
        success, msg = cart_service.add_to_cart(user_id, item.item_id)
        assert success is False
        assert len(msg) > 0 # 只要有错误消息即可
        
        # 验证购物车仍然为空
        cart = cart_service.get_cart(user_id)
        assert cart is None or len(cart.items) == 0

