"""领域模型层 - 核心业务对象"""
from dataclasses import dataclass, field
from typing import List
from decimal import Decimal
from enum import Enum
from datetime import datetime
import uuid


class OrderStatus(Enum):
    """订单状态枚举"""
    PENDING = "待处理"
    PROCESSING = "制作中"
    COMPLETED = "已完成"
    CANCELLED = "已取消"


@dataclass
class MenuItem:
    """菜单项"""
    id: str
    name: str
    base_price: Decimal
    category: str
    description: str = ""
    is_available: bool = True
    
    def __post_init__(self):
        if isinstance(self.base_price, (int, float)):
            self.base_price = Decimal(str(self.base_price))


@dataclass
class CartItem:
    """购物车项目"""
    id: str
    menu_item: MenuItem
    quantity: int
    remark: str = ""
    
    def calculate_subtotal(self) -> Decimal:
        """计算小计价格"""
        return self.menu_item.base_price * self.quantity


class Cart:
    """购物车"""
    def __init__(self):
        self.id: str = str(uuid.uuid4())
        self.items: List[CartItem] = []
    
    def add_item(self, item: CartItem):
        """添加商品到购物车"""
        self.items.append(item)
    
    def remove_item(self, item_id: str):
        """从购物车移除商品"""
        self.items = [item for item in self.items if item.id != item_id]
    
    def update_quantity(self, item_id: str, quantity: int):
        """更新商品数量"""
        for item in self.items:
            if item.id == item_id:
                item.quantity = quantity
                break
    
    def clear(self):
        """清空购物车"""
        self.items.clear()
    
    def get_total_price(self) -> Decimal:
        """计算总价"""
        return sum(item.calculate_subtotal() for item in self.items)


@dataclass
class Order:
    """订单"""
    id: str
    items: List[CartItem]
    status: OrderStatus
    total_price: Decimal
    created_at: datetime
    remark: str = ""
    
    def __post_init__(self):
        if isinstance(self.total_price, (int, float)):
            self.total_price = Decimal(str(self.total_price))

