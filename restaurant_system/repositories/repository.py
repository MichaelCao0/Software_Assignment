"""仓储层 - 数据访问抽象"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict
from domain.models import MenuItem, Order


class MenuRepository(ABC):
    """菜单仓储接口"""
    @abstractmethod
    def save(self, item: MenuItem) -> None: pass
    
    @abstractmethod
    def find_by_id(self, item_id: str) -> Optional[MenuItem]: pass
    
    @abstractmethod
    def find_all(self) -> List[MenuItem]: pass
    
    @abstractmethod
    def update(self, item: MenuItem) -> None: pass
    
    @abstractmethod
    def delete(self, item_id: str) -> None: pass


class OrderRepository(ABC):
    """订单仓储接口"""
    @abstractmethod
    def save(self, order: Order) -> None: pass
    
    @abstractmethod
    def find_by_id(self, order_id: str) -> Optional[Order]: pass
    
    @abstractmethod
    def find_all(self) -> List[Order]: pass
    
    @abstractmethod
    def update(self, order: Order) -> None: pass


class InMemoryMenuRepo(MenuRepository):
    """内存实现的菜单仓储"""
    def __init__(self):
        self._storage: Dict[str, MenuItem] = {}
    
    def save(self, item: MenuItem) -> None:
        self._storage[item.id] = item
    
    def find_by_id(self, item_id: str) -> Optional[MenuItem]:
        return self._storage.get(item_id)
    
    def find_all(self) -> List[MenuItem]:
        return list(self._storage.values())
    
    def update(self, item: MenuItem) -> None:
        if item.id in self._storage:
            self._storage[item.id] = item
    
    def delete(self, item_id: str) -> None:
        if item_id in self._storage:
            del self._storage[item_id]


class InMemoryOrderRepo(OrderRepository):
    """内存实现的订单仓储"""
    def __init__(self):
        self._storage: Dict[str, Order] = {}
    
    def save(self, order: Order) -> None:
        self._storage[order.id] = order
    
    def find_by_id(self, order_id: str) -> Optional[Order]:
        return self._storage.get(order_id)
    
    def find_all(self) -> List[Order]:
        return list(self._storage.values())
    
    def update(self, order: Order) -> None:
        if order.id in self._storage:
            self._storage[order.id] = order

