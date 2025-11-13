"""业务服务层 - 业务逻辑处理"""
from typing import List
from datetime import datetime
import uuid

from domain.models import MenuItem, Order, Cart, OrderStatus
from repositories.repository import MenuRepository, OrderRepository


class MenuService:
    """菜单管理服务"""
    def __init__(self, menu_repo: MenuRepository):
        self.menu_repo = menu_repo
    
    def get_available_items(self) -> List[MenuItem]:
        return [item for item in self.menu_repo.find_all() if item.is_available]
    
    def get_all_items(self) -> List[MenuItem]:
        return self.menu_repo.find_all()
    
    def get_item_by_id(self, item_id: str) -> MenuItem:
        return self.menu_repo.find_by_id(item_id)
    
    def add_menu_item(self, item: MenuItem) -> None:
        self.menu_repo.save(item)
    
    def toggle_availability(self, item_id: str) -> None:
        item = self.menu_repo.find_by_id(item_id)
        if item:
            item.is_available = not item.is_available
            self.menu_repo.update(item)


class OrderService:
    """订单管理服务"""
    def __init__(self, order_repo: OrderRepository, menu_repo: MenuRepository):
        self.order_repo = order_repo
        self.menu_repo = menu_repo
    
    def create_order(self, cart: Cart, remark: str = "") -> Order:
        if not cart.items:
            raise ValueError("购物车为空")
        
        order = Order(
            id=str(uuid.uuid4()),
            items=cart.items.copy(),
            status=OrderStatus.PENDING,
            total_price=cart.get_total_price(),
            created_at=datetime.now(),
            remark=remark
        )
        self.order_repo.save(order)
        return order
    
    def get_orders(self) -> List[Order]:
        return self.order_repo.find_all()
    
    def update_order_status(self, order_id: str, status: OrderStatus) -> None:
        order = self.order_repo.find_by_id(order_id)
        if order:
            order.status = status
            self.order_repo.update(order)

