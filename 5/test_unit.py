import pytest
import os
import shutil
from pathlib import Path
from decimal import Decimal
from uuid import uuid4

# 导入被测组件
from models import Sweetness, OrderStatus
from services import AuthService, CartService, MenuService
from repositories import UserRepository, MenuItemRepository, CartRepository, ToppingRepository

@pytest.fixture
def clean_data_dir():
    """清理并准备测试数据目录"""
    data_dir = Path(__file__).parent.parent / 'data'
    if data_dir.exists():
        # 备份原数据（可选，这里为了简单直接删除，实际环境需小心）
        # shutil.move(str(data_dir), str(data_dir) + "_bak")
        pass
    
    # 确保 repos 重新加载数据，这里通过重新实例化或清理文件实现
    for filename in ['users.json', 'menu_items.json', 'carts.json', 'toppings.json']:
        filepath = data_dir / filename
        if filepath.exists():
            filepath.unlink()
    
    yield
    
    # 测试后清理
    # for filename in ['users.json', 'menu_items.json', 'carts.json', 'toppings.json']:
    #     filepath = data_dir / filename
    #     if filepath.exists():
    #         filepath.unlink()

class TestAuthService:
    """AuthService 单元测试 (子功能 1)"""
    
    def test_register_success(self, clean_data_dir):
        service = AuthService()
        success, msg, user = service.register("张三", "13800138000")
        assert success is True
        assert msg == "注册成功"
        assert user.nickname == "张三"
        assert user.phone == "13800138000"

    def test_register_duplicate_phone(self, clean_data_dir):
        service = AuthService()
        service.register("张三", "13800138000")
        success, msg, user = service.register("李四", "13800138000")
        assert success is False
        assert msg == "该手机号已注册"
        assert user is None

    def test_login_success(self, clean_data_dir):
        service = AuthService()
        service.register("张三", "13800138000")
        success, msg, user = service.login("13800138000")
        assert success is True
        assert msg == "登录成功"
        assert user.nickname == "张三"
        assert service.get_current_user() == user

    def test_login_fail(self, clean_data_dir):
        service = AuthService()
        success, msg, user = service.login("13999999999")
        assert success is False
        assert msg == "用户不存在"
        assert user is None

    def test_logout(self, clean_data_dir):
        service = AuthService()
        service.register("张三", "13800138000")
        service.login("13800138000")
        service.logout()
        assert service.get_current_user() is None

class TestCartService:
    """CartService 单元测试 (子功能 2)"""
    
    @pytest.fixture
    def setup_menu(self):
        menu_service = MenuService()
        # 创建一个测试商品
        item = menu_service.create_item("珍珠奶茶", Decimal("15.00"), "经典")
        # 创建一个小料
        topping = menu_service.create_topping("珍珠", Decimal("2.00"))
        return item, topping

    def test_get_or_create_cart(self, clean_data_dir):
        service = CartService()
        user_id = uuid4()
        cart = service.get_or_create_cart(user_id)
        assert cart.user_id == user_id
        assert len(cart.items) == 0

    def test_add_to_cart_success(self, clean_data_dir, setup_menu):
        item, topping = setup_menu
        service = CartService()
        user_id = uuid4()
        
        success, msg = service.add_to_cart(
            user_id, item.item_id, quantity=2,
            sweetness=Sweetness.FULL,
            topping_ids=[topping.topping_id],
            remark="多加冰"
        )
        
        assert success is True
        assert msg == "已添加到购物车"
        
        cart = service.get_cart(user_id)
        assert len(cart.items) == 1
        assert cart.items[0].menu_item.name == "珍珠奶茶"
        assert cart.items[0].quantity == 2
        assert cart.items[0].sweetness == Sweetness.FULL
        assert cart.items[0].toppings[0].name == "珍珠"
        assert cart.items[0].remark == "多加冰"
        # 总价计算: (15 + 2) * 2 = 34
        assert cart.total() == Decimal("34.00")

    def test_add_non_existent_item(self, clean_data_dir):
        service = CartService()
        user_id = uuid4()
        success, msg = service.add_to_cart(user_id, uuid4())
        assert success is False
        assert msg == "商品不存在"

    def test_add_sold_out_item(self, clean_data_dir):
        menu_service = MenuService()
        item = menu_service.create_item("缺货奶茶", Decimal("10.00"))
        menu_service.mark_sold_out(item.item_id, True)
        
        service = CartService()
        user_id = uuid4()
        success, msg = service.add_to_cart(user_id, item.item_id)
        assert success is False
        assert msg == "商品已售罄"

    def test_remove_from_cart(self, clean_data_dir, setup_menu):
        item, _ = setup_menu
        service = CartService()
        user_id = uuid4()
        service.add_to_cart(user_id, item.item_id)
        
        cart = service.get_cart(user_id)
        order_item_id = cart.items[0].order_item_id
        
        success = service.remove_from_cart(user_id, order_item_id)
        assert success is True
        assert len(service.get_cart(user_id).items) == 0

    def test_clear_cart(self, clean_data_dir, setup_menu):
        item, _ = setup_menu
        service = CartService()
        user_id = uuid4()
        service.add_to_cart(user_id, item.item_id)
        service.add_to_cart(user_id, item.item_id)
        
        assert len(service.get_cart(user_id).items) == 2
        service.clear_cart(user_id)
        assert len(service.get_cart(user_id).items) == 0

