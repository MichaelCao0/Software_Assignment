"""
奶茶点单系统 - 数据持久化层
使用JSON文件作为简单的数据存储
"""

import json
import os
from pathlib import Path
from typing import List, Optional, TypeVar, Generic, Type
from uuid import UUID

from models import (
    User, Menu, MenuItem, Order, Cart, Review, 
    Favorite, Promotion, Topping
)


T = TypeVar('T')


class Repository(Generic[T]):
    """通用仓储接口"""
    
    def __init__(self, filename: str, model_class: Type[T]):
        """初始化仓储"""
        self.data_dir = Path(__file__).parent / 'data'
        self.data_dir.mkdir(exist_ok=True)
        self.filepath = self.data_dir / filename
        self.model_class = model_class
        self._data: List[T] = []
        self._load()
    
    def _load(self):
        """从文件加载数据"""
        if self.filepath.exists():
            try:
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._data = [self.model_class.from_dict(item) for item in data]
            except (json.JSONDecodeError, IOError, ValueError) as e:
                print(f"加载数据失败 {self.filepath}: {e}")
                self._data = []
        else:
            self._data = []
    
    def _save(self):
        """保存数据到文件"""
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                data = [item.to_dict() for item in self._data]
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存数据失败 {self.filepath}: {e}")
    
    def save(self, item: T) -> T:
        """保存实体"""
        # 检查是否已存在
        existing = self.find_by_id(self._get_id(item))
        if existing:
            # 更新
            index = self._data.index(existing)
            self._data[index] = item
        else:
            # 新增
            self._data.append(item)
        self._save()
        return item
    
    def find_by_id(self, entity_id: UUID) -> Optional[T]:
        """根据ID查找实体"""
        for item in self._data:
            if self._get_id(item) == entity_id:
                return item
        return None
    
    def find_all(self) -> List[T]:
        """查找所有实体"""
        return self._data.copy()
    
    def delete(self, entity_id: UUID) -> bool:
        """删除实体"""
        item = self.find_by_id(entity_id)
        if item:
            self._data.remove(item)
            self._save()
            return True
        return False
    
    def _get_id(self, item: T) -> UUID:
        """获取实体ID"""
        # 优先获取最具体、唯一的实体 ID
        if hasattr(item, 'favorite_id'):
            return item.favorite_id
        elif hasattr(item, 'review_id'):
            return item.review_id
        elif hasattr(item, 'order_id'):
            return item.order_id
        elif hasattr(item, 'cart_id'):
            return item.cart_id
        elif hasattr(item, 'user_id'):
            return item.user_id
        elif hasattr(item, 'item_id'):
            return item.item_id
        elif hasattr(item, 'menu_id'):
            return item.menu_id
        elif hasattr(item, 'promotion_id'):
            return item.promotion_id
        elif hasattr(item, 'topping_id'):
            return item.topping_id
        else:
            raise ValueError(f"无法获取实体ID: {type(item)}")


class UserRepository(Repository[User]):
    """用户仓储"""
    
    def __init__(self):
        super().__init__('users.json', User)
    
    def find_by_phone(self, phone: str) -> Optional[User]:
        """根据手机号查找用户"""
        for user in self._data:
            if user.phone == phone:
                return user
        return None


class MenuRepository(Repository[Menu]):
    """菜单仓储"""
    
    def __init__(self):
        super().__init__('menus.json', Menu)
    
    def find_active(self) -> Optional[Menu]:
        """查找激活的菜单"""
        for menu in self._data:
            if menu.is_active:
                return menu
        return None


class MenuItemRepository(Repository[MenuItem]):
    """菜单项仓储"""
    
    def __init__(self):
        super().__init__('menu_items.json', MenuItem)
    
    def find_available(self) -> List[MenuItem]:
        """查找可用的菜单项（未售罄）"""
        return [item for item in self._data if not item.is_sold_out]


class OrderRepository(Repository[Order]):
    """订单仓储"""
    
    def __init__(self):
        super().__init__('orders.json', Order)
    
    def find_by_user(self, user_id: UUID) -> List[Order]:
        """查找用户的所有订单"""
        return [order for order in self._data if order.user_id == user_id]
    
    def find_by_status(self, status) -> List[Order]:
        """根据状态查找订单"""
        return [order for order in self._data if order.status == status]
    
    def find_all_sorted_by_time(self) -> List[Order]:
        """查找所有订单并按时间排序"""
        return sorted(self._data, key=lambda x: x.created_at, reverse=True)


class CartRepository(Repository[Cart]):
    """购物车仓储"""
    
    def __init__(self):
        super().__init__('carts.json', Cart)
    
    def find_by_user(self, user_id: UUID) -> Optional[Cart]:
        """查找用户的购物车"""
        for cart in self._data:
            if cart.user_id == user_id:
                return cart
        return None


class ReviewRepository(Repository[Review]):
    """评价仓储"""
    
    def __init__(self):
        super().__init__('reviews.json', Review)
    
    def find_by_user(self, user_id: UUID) -> List[Review]:
        """查找用户的所有评价"""
        return [review for review in self._data if review.user_id == user_id]
    
    def find_by_order(self, order_id: UUID) -> List[Review]:
        """查找订单的所有评价"""
        return [review for review in self._data if review.order_id == order_id]
    
    def find_all_sorted(self) -> List[Review]:
        """查找所有评价并按时间排序"""
        return sorted(self._data, key=lambda x: x.created_at, reverse=True)


class FavoriteRepository(Repository[Favorite]):
    """收藏仓储"""
    
    def __init__(self):
        super().__init__('favorites.json', Favorite)
    
    def find_by_user(self, user_id: UUID) -> List[Favorite]:
        """查找用户的所有收藏"""
        return [fav for fav in self._data if fav.user_id == user_id]
    
    def find_by_user_and_item(self, user_id: UUID, item_id: UUID) -> Optional[Favorite]:
        """查找用户对特定商品的收藏"""
        for fav in self._data:
            if fav.user_id == user_id and fav.item_id == item_id:
                return fav
        return None


class PromotionRepository(Repository[Promotion]):
    """促销仓储"""
    
    def __init__(self):
        super().__init__('promotions.json', Promotion)
    
    def find_active(self) -> List[Promotion]:
        """查找所有有效的促销"""
        return [promo for promo in self._data if promo.is_valid()]


class ToppingRepository(Repository[Topping]):
    """小料仓储"""
    
    def __init__(self):
        super().__init__('toppings.json', Topping)

