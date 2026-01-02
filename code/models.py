"""
奶茶点单系统 - 领域模型类
基于UML类图实现的核心领域对象
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional
from uuid import uuid4, UUID


class Sweetness(Enum):
    """甜度枚举"""
    NONE = "无糖"
    THREE = "三分糖"
    FIVE = "五分糖"
    SEVEN = "七分糖"
    FULL = "全糖"


class OrderStatus(Enum):
    """订单状态枚举"""
    PENDING = "待接单"
    PREPARING = "制作中"
    READY = "待取餐"
    COMPLETED = "已完成"
    CANCELLED = "已取消"


@dataclass
class User:
    """用户类"""
    user_id: UUID = field(default_factory=uuid4)
    nickname: str = ""
    phone: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        if isinstance(self.user_id, str):
            self.user_id = UUID(self.user_id)
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'user_id': str(self.user_id),
            'nickname': self.nickname,
            'phone': self.phone,
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建"""
        return cls(**data)


@dataclass
class Topping:
    """小料/配料类"""
    topping_id: UUID = field(default_factory=uuid4)
    name: str = ""
    extra_price: Decimal = Decimal('0.00')
    
    def __post_init__(self):
        if isinstance(self.topping_id, str):
            self.topping_id = UUID(self.topping_id)
        if not isinstance(self.extra_price, Decimal):
            self.extra_price = Decimal(str(self.extra_price))
    
    def to_dict(self):
        """转换为字典"""
        return {
            'topping_id': str(self.topping_id),
            'name': self.name,
            'extra_price': str(self.extra_price)
        }
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建"""
        return cls(**data)


@dataclass
class MenuItem:
    """菜单项类"""
    item_id: UUID = field(default_factory=uuid4)
    name: str = ""
    price: Decimal = Decimal('0.00')
    category: str = ""  # UML中定义的分类属性
    allow_toppings: bool = True
    is_sold_out: bool = False
    description: str = ""
    
    def __post_init__(self):
        if isinstance(self.item_id, str):
            self.item_id = UUID(self.item_id)
        if not isinstance(self.price, Decimal):
            self.price = Decimal(str(self.price))
    
    def to_dict(self):
        """转换为字典"""
        return {
            'item_id': str(self.item_id),
            'name': self.name,
            'price': str(self.price),
            'category': self.category,
            'allow_toppings': self.allow_toppings,
            'is_sold_out': self.is_sold_out,
            'description': self.description
        }
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建"""
        return cls(**data)


@dataclass
class Menu:
    """菜单类"""
    menu_id: UUID = field(default_factory=uuid4)
    name: str = ""
    updated_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True
    items: List[MenuItem] = field(default_factory=list)
    
    def __post_init__(self):
        if isinstance(self.menu_id, str):
            self.menu_id = UUID(self.menu_id)
        if isinstance(self.updated_at, str):
            self.updated_at = datetime.fromisoformat(self.updated_at)
    
    def add_item(self, item: MenuItem):
        """添加菜单项"""
        self.items.append(item)
        self.updated_at = datetime.now()
    
    def remove_item(self, item_id: UUID):
        """移除菜单项"""
        self.items = [item for item in self.items if item.item_id != item_id]
        self.updated_at = datetime.now()
    
    def to_dict(self):
        """转换为字典"""
        return {
            'menu_id': str(self.menu_id),
            'name': self.name,
            'updated_at': self.updated_at.isoformat(),
            'is_active': self.is_active,
            'items': [item.to_dict() for item in self.items]
        }
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建"""
        items = [MenuItem.from_dict(item) for item in data.get('items', [])]
        data_copy = data.copy()
        data_copy['items'] = items
        return cls(**data_copy)


@dataclass
class OrderItem:
    """订单项类"""
    order_item_id: UUID = field(default_factory=uuid4)
    menu_item: Optional[MenuItem] = None
    quantity: int = 1
    sweetness: Sweetness = Sweetness.FIVE
    toppings: List[Topping] = field(default_factory=list)
    remark: str = ""
    
    def __post_init__(self):
        if isinstance(self.order_item_id, str):
            self.order_item_id = UUID(self.order_item_id)
        if isinstance(self.sweetness, str):
            for s in Sweetness:
                if s.value == self.sweetness:
                    self.sweetness = s
                    break
    
    def subtotal(self) -> Decimal:
        """计算小计"""
        if not self.menu_item:
            return Decimal('0.00')
        
        base_price = self.menu_item.price
        toppings_price = sum(t.extra_price for t in self.toppings)
        return (base_price + toppings_price) * Decimal(str(self.quantity))
    
    def to_dict(self):
        """转换为字典"""
        return {
            'order_item_id': str(self.order_item_id),
            'menu_item': self.menu_item.to_dict() if self.menu_item else None,
            'quantity': self.quantity,
            'sweetness': self.sweetness.value,
            'toppings': [t.to_dict() for t in self.toppings],
            'remark': self.remark
        }
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建"""
        menu_item = MenuItem.from_dict(data['menu_item']) if data.get('menu_item') else None
        toppings = [Topping.from_dict(t) for t in data.get('toppings', [])]
        return cls(
            order_item_id=data['order_item_id'],
            menu_item=menu_item,
            quantity=data['quantity'],
            sweetness=data['sweetness'],
            toppings=toppings,
            remark=data.get('remark', '')
        )


@dataclass
class Order:
    """订单类"""
    order_id: UUID = field(default_factory=uuid4)
    user_id: UUID = None
    status: OrderStatus = OrderStatus.PENDING
    items: List[OrderItem] = field(default_factory=list)
    remark: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        if isinstance(self.order_id, str):
            self.order_id = UUID(self.order_id)
        if isinstance(self.user_id, str):
            self.user_id = UUID(self.user_id)
        if isinstance(self.status, str):
            for s in OrderStatus:
                if s.value == self.status:
                    self.status = s
                    break
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)
    
    def total_amount(self) -> Decimal:
        """计算总金额"""
        return sum(item.subtotal() for item in self.items)
    
    def add_item(self, item: OrderItem):
        """添加订单项"""
        self.items.append(item)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'order_id': str(self.order_id),
            'user_id': str(self.user_id) if self.user_id else None,
            'status': self.status.value,
            'items': [item.to_dict() for item in self.items],
            'remark': self.remark,
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建"""
        items = [OrderItem.from_dict(item) for item in data.get('items', [])]
        return cls(
            order_id=data['order_id'],
            user_id=data.get('user_id'),
            status=data['status'],
            items=items,
            remark=data.get('remark', ''),
            created_at=data['created_at']
        )


@dataclass
class Cart:
    """购物车类"""
    cart_id: UUID = field(default_factory=uuid4)
    user_id: UUID = None
    items: List[OrderItem] = field(default_factory=list)
    
    def __post_init__(self):
        if isinstance(self.cart_id, str):
            self.cart_id = UUID(self.cart_id)
        if isinstance(self.user_id, str):
            self.user_id = UUID(self.user_id)
    
    def add_item(self, menu_item: MenuItem, quantity: int = 1,
                 sweetness: Sweetness = Sweetness.FIVE,
                 toppings: List[Topping] = None,
                 remark: str = ""):
        """添加商品到购物车"""
        order_item = OrderItem(
            menu_item=menu_item,
            quantity=quantity,
            sweetness=sweetness,
            toppings=toppings or [],
            remark=remark
        )
        self.items.append(order_item)
    
    def remove_item(self, order_item_id: UUID):
        """从购物车移除商品"""
        self.items = [item for item in self.items if item.order_item_id != order_item_id]
    
    def update_quantity(self, order_item_id: UUID, quantity: int):
        """更新购物车中商品的数量（UML中定义的方法）"""
        if quantity <= 0:
            self.remove_item(order_item_id)
            return
        
        for item in self.items:
            if item.order_item_id == order_item_id:
                item.quantity = quantity
                return
    
    def clear(self):
        """清空购物车"""
        self.items = []
    
    def total(self) -> Decimal:
        """计算购物车总价"""
        return sum(item.subtotal() for item in self.items)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'cart_id': str(self.cart_id),
            'user_id': str(self.user_id) if self.user_id else None,
            'items': [item.to_dict() for item in self.items]
        }
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建"""
        items = [OrderItem.from_dict(item) for item in data.get('items', [])]
        return cls(
            cart_id=data['cart_id'],
            user_id=data.get('user_id'),
            items=items
        )


@dataclass
class Review:
    """评价类"""
    review_id: UUID = field(default_factory=uuid4)
    user_id: UUID = None
    order_id: UUID = None
    rating: int = 5
    content: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    reply: str = ""
    
    def __post_init__(self):
        if isinstance(self.review_id, str):
            self.review_id = UUID(self.review_id)
        if isinstance(self.user_id, str):
            self.user_id = UUID(self.user_id)
        if isinstance(self.order_id, str):
            self.order_id = UUID(self.order_id)
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'review_id': str(self.review_id),
            'user_id': str(self.user_id) if self.user_id else None,
            'order_id': str(self.order_id) if self.order_id else None,
            'rating': self.rating,
            'content': self.content,
            'created_at': self.created_at.isoformat(),
            'reply': self.reply
        }
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建"""
        return cls(**data)


@dataclass
class Favorite:
    """收藏类"""
    favorite_id: UUID = field(default_factory=uuid4)
    user_id: UUID = None
    item_id: UUID = None
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        if isinstance(self.favorite_id, str):
            self.favorite_id = UUID(self.favorite_id)
        if isinstance(self.user_id, str):
            self.user_id = UUID(self.user_id)
        if isinstance(self.item_id, str):
            self.item_id = UUID(self.item_id)
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'favorite_id': str(self.favorite_id),
            'user_id': str(self.user_id) if self.user_id else None,
            'item_id': str(self.item_id) if self.item_id else None,
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建"""
        return cls(**data)


@dataclass
class Promotion:
    """促销类"""
    promotion_id: UUID = field(default_factory=uuid4)
    title: str = ""
    content: str = ""
    start_at: datetime = field(default_factory=datetime.now)
    end_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True
    
    def __post_init__(self):
        if isinstance(self.promotion_id, str):
            self.promotion_id = UUID(self.promotion_id)
        if isinstance(self.start_at, str):
            self.start_at = datetime.fromisoformat(self.start_at)
        if isinstance(self.end_at, str):
            self.end_at = datetime.fromisoformat(self.end_at)
    
    def is_valid(self) -> bool:
        """检查促销是否有效"""
        now = datetime.now()
        return self.is_active and self.start_at <= now <= self.end_at
    
    def to_dict(self):
        """转换为字典"""
        return {
            'promotion_id': str(self.promotion_id),
            'title': self.title,
            'content': self.content,
            'start_at': self.start_at.isoformat(),
            'end_at': self.end_at.isoformat(),
            'is_active': self.is_active
        }
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建"""
        return cls(**data)

