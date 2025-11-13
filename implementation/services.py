"""
奶茶点单系统 - 服务层
实现业务逻辑和操作
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Tuple
from uuid import UUID

from models import (
    User, Menu, MenuItem, Order, OrderItem, Cart, Review,
    Favorite, Promotion, Topping, OrderStatus, Sweetness
)
from repositories import (
    UserRepository, MenuRepository, MenuItemRepository,
    OrderRepository, CartRepository, ReviewRepository,
    FavoriteRepository, PromotionRepository, ToppingRepository
)


class AuthService:
    """用户认证服务"""
    
    def __init__(self):
        self.user_repo = UserRepository()
        self.current_user: Optional[User] = None
    
    def register(self, nickname: str, phone: str) -> Tuple[bool, str, Optional[User]]:
        """
        注册新用户
        返回: (是否成功, 消息, 用户对象)
        """
        # 检查手机号是否已注册
        existing = self.user_repo.find_by_phone(phone)
        if existing:
            return False, "该手机号已注册", None
        
        # 创建新用户
        user = User(nickname=nickname, phone=phone)
        self.user_repo.save(user)
        return True, "注册成功", user
    
    def login(self, phone: str) -> Tuple[bool, str, Optional[User]]:
        """
        登录（简化版，实际应该有验证码）
        返回: (是否成功, 消息, 用户对象)
        """
        user = self.user_repo.find_by_phone(phone)
        if not user:
            return False, "用户不存在", None
        
        self.current_user = user
        return True, "登录成功", user
    
    def logout(self):
        """登出"""
        self.current_user = None
    
    def get_current_user(self) -> Optional[User]:
        """获取当前登录用户"""
        return self.current_user


class MenuService:
    """菜单管理服务"""
    
    def __init__(self):
        self.menu_repo = MenuRepository()
        self.item_repo = MenuItemRepository()
        self.topping_repo = ToppingRepository()
    
    def list_items(self) -> List[MenuItem]:
        """列出所有可用菜单项"""
        return self.item_repo.find_available()
    
    def list_all_items(self) -> List[MenuItem]:
        """列出所有菜单项（包括售罄的）"""
        return self.item_repo.find_all()
    
    def get_item(self, item_id: UUID) -> Optional[MenuItem]:
        """获取菜单项"""
        return self.item_repo.find_by_id(item_id)
    
    def create_item(self, name: str, price: Decimal, category: str = "",
                   allow_toppings: bool = True, description: str = "") -> MenuItem:
        """创建菜单项"""
        item = MenuItem(
            name=name,
            price=price,
            category=category,
            allow_toppings=allow_toppings,
            description=description
        )
        return self.item_repo.save(item)
    
    def update_item(self, item_id: UUID, name: str = None, price: Decimal = None,
                   category: str = None, allow_toppings: bool = None, 
                   description: str = None) -> Optional[MenuItem]:
        """更新菜单项"""
        item = self.item_repo.find_by_id(item_id)
        if not item:
            return None
        
        if name is not None:
            item.name = name
        if price is not None:
            item.price = price
        if category is not None:
            item.category = category
        if allow_toppings is not None:
            item.allow_toppings = allow_toppings
        if description is not None:
            item.description = description
        
        return self.item_repo.save(item)
    
    def mark_sold_out(self, item_id: UUID, is_sold_out: bool = True) -> bool:
        """标记菜单项售罄状态"""
        item = self.item_repo.find_by_id(item_id)
        if not item:
            return False
        
        item.is_sold_out = is_sold_out
        self.item_repo.save(item)
        return True
    
    def delete_item(self, item_id: UUID) -> bool:
        """删除菜单项"""
        return self.item_repo.delete(item_id)
    
    def list_toppings(self) -> List[Topping]:
        """列出所有小料"""
        return self.topping_repo.find_all()
    
    def get_topping(self, topping_id: UUID) -> Optional[Topping]:
        """获取小料"""
        return self.topping_repo.find_by_id(topping_id)
    
    def create_topping(self, name: str, extra_price: Decimal) -> Topping:
        """创建小料"""
        topping = Topping(name=name, extra_price=extra_price)
        return self.topping_repo.save(topping)
    
    def delete_topping(self, topping_id: UUID) -> bool:
        """删除小料"""
        return self.topping_repo.delete(topping_id)


class CartService:
    """购物车服务"""
    
    def __init__(self):
        self.cart_repo = CartRepository()
        self.item_repo = MenuItemRepository()
        self.topping_repo = ToppingRepository()
    
    def get_or_create_cart(self, user_id: UUID) -> Cart:
        """获取或创建购物车"""
        cart = self.cart_repo.find_by_user(user_id)
        if not cart:
            cart = Cart(user_id=user_id)
            self.cart_repo.save(cart)
        return cart
    
    def add_to_cart(self, user_id: UUID, item_id: UUID, quantity: int = 1,
                   sweetness: Sweetness = Sweetness.FIVE,
                   topping_ids: List[UUID] = None,
                   remark: str = "") -> Tuple[bool, str]:
        """
        添加商品到购物车
        返回: (是否成功, 消息)
        """
        # 获取菜单项
        menu_item = self.item_repo.find_by_id(item_id)
        if not menu_item:
            return False, "商品不存在"
        
        if menu_item.is_sold_out:
            return False, "商品已售罄"
        
        # 获取小料
        toppings = []
        if topping_ids:
            for tid in topping_ids:
                topping = self.topping_repo.find_by_id(tid)
                if topping:
                    toppings.append(topping)
        
        # 添加到购物车
        cart = self.get_or_create_cart(user_id)
        cart.add_item(menu_item, quantity, sweetness, toppings, remark)
        self.cart_repo.save(cart)
        
        return True, "已添加到购物车"
    
    def remove_from_cart(self, user_id: UUID, order_item_id: UUID) -> bool:
        """从购物车移除商品"""
        cart = self.cart_repo.find_by_user(user_id)
        if not cart:
            return False
        
        cart.remove_item(order_item_id)
        self.cart_repo.save(cart)
        return True
    
    def clear_cart(self, user_id: UUID):
        """清空购物车"""
        cart = self.cart_repo.find_by_user(user_id)
        if cart:
            cart.clear()
            self.cart_repo.save(cart)
    
    def get_cart(self, user_id: UUID) -> Optional[Cart]:
        """获取购物车"""
        return self.cart_repo.find_by_user(user_id)


class OrderService:
    """订单服务"""
    
    def __init__(self):
        self.order_repo = OrderRepository()
        self.cart_service = CartService()
        self.reminder_service = ReminderService()
    
    def place_order(self, user_id: UUID, remark: str = "") -> Tuple[bool, str, Optional[Order]]:
        """
        下单
        返回: (是否成功, 消息, 订单对象)
        """
        # 获取购物车
        cart = self.cart_service.get_cart(user_id)
        if not cart or not cart.items:
            return False, "购物车为空", None
        
        # 创建订单
        order = Order(
            user_id=user_id,
            status=OrderStatus.PENDING,
            remark=remark
        )
        
        # 复制购物车项到订单
        for item in cart.items:
            order.add_item(item)
        
        # 保存订单
        self.order_repo.save(order)
        
        # 清空购物车
        self.cart_service.clear_cart(user_id)
        
        # 发送提醒（模拟）
        self.reminder_service.send_order_confirmation(order)
        
        return True, f"下单成功！订单号：{str(order.order_id)[:8]}", order
    
    def list_orders(self, user_id: UUID = None, sort_by_time: bool = True) -> List[Order]:
        """
        列出订单
        如果提供user_id，则只返回该用户的订单
        """
        if user_id:
            orders = self.order_repo.find_by_user(user_id)
            if sort_by_time:
                orders = sorted(orders, key=lambda x: x.created_at, reverse=True)
            return orders
        else:
            return self.order_repo.find_all_sorted_by_time()
    
    def get_order(self, order_id: UUID) -> Optional[Order]:
        """获取订单"""
        return self.order_repo.find_by_id(order_id)
    
    def update_status(self, order_id: UUID, status: OrderStatus) -> Tuple[bool, str]:
        """
        更新订单状态
        返回: (是否成功, 消息)
        """
        order = self.order_repo.find_by_id(order_id)
        if not order:
            return False, "订单不存在"
        
        order.status = status
        self.order_repo.save(order)
        
        # 如果订单状态变为待取餐，发送提醒
        if status == OrderStatus.READY:
            self.reminder_service.send_pickup_reminder(order)
        
        # 如果订单完成，邀请评价
        if status == OrderStatus.COMPLETED:
            self.reminder_service.invite_review(order)
        
        return True, f"订单状态已更新为：{status.value}"
    
    def cancel_order(self, order_id: UUID) -> Tuple[bool, str]:
        """取消订单"""
        return self.update_status(order_id, OrderStatus.CANCELLED)


class ReviewService:
    """评价服务"""
    
    def __init__(self):
        self.review_repo = ReviewRepository()
    
    def create_review(self, user_id: UUID, order_id: UUID, rating: int,
                     content: str = "") -> Tuple[bool, str, Optional[Review]]:
        """
        创建评价
        返回: (是否成功, 消息, 评价对象)
        """
        if not 1 <= rating <= 5:
            return False, "评分必须在1-5之间", None
        
        review = Review(
            user_id=user_id,
            order_id=order_id,
            rating=rating,
            content=content
        )
        
        self.review_repo.save(review)
        return True, "评价成功", review
    
    def list_reviews(self, user_id: UUID = None) -> List[Review]:
        """列出评价"""
        if user_id:
            return self.review_repo.find_by_user(user_id)
        return self.review_repo.find_all_sorted()
    
    def reply_review(self, review_id: UUID, reply_content: str) -> Tuple[bool, str]:
        """
        回复评价
        返回: (是否成功, 消息)
        """
        review = self.review_repo.find_by_id(review_id)
        if not review:
            return False, "评价不存在"
        
        review.reply = reply_content
        self.review_repo.save(review)
        return True, "回复成功"
    
    def get_review_by_order(self, order_id: UUID) -> Optional[Review]:
        """获取订单的评价"""
        reviews = self.review_repo.find_by_order(order_id)
        return reviews[0] if reviews else None


class FavoriteService:
    """收藏服务"""
    
    def __init__(self):
        self.favorite_repo = FavoriteRepository()
    
    def add_favorite(self, user_id: UUID, item_id: UUID) -> Tuple[bool, str]:
        """
        添加收藏
        返回: (是否成功, 消息)
        """
        # 检查是否已收藏
        existing = self.favorite_repo.find_by_user_and_item(user_id, item_id)
        if existing:
            return False, "已经收藏过了"
        
        favorite = Favorite(user_id=user_id, item_id=item_id)
        self.favorite_repo.save(favorite)
        return True, "收藏成功"
    
    def remove_favorite(self, user_id: UUID, item_id: UUID) -> Tuple[bool, str]:
        """
        取消收藏
        返回: (是否成功, 消息)
        """
        favorite = self.favorite_repo.find_by_user_and_item(user_id, item_id)
        if not favorite:
            return False, "未收藏该商品"
        
        self.favorite_repo.delete(favorite.favorite_id)
        return True, "已取消收藏"
    
    def list_favorites(self, user_id: UUID) -> List[Favorite]:
        """列出用户的所有收藏"""
        return self.favorite_repo.find_by_user(user_id)
    
    def is_favorited(self, user_id: UUID, item_id: UUID) -> bool:
        """检查是否已收藏"""
        return self.favorite_repo.find_by_user_and_item(user_id, item_id) is not None


class PromotionService:
    """促销服务"""
    
    def __init__(self):
        self.promotion_repo = PromotionRepository()
    
    def create_promotion(self, title: str, content: str,
                        start_at: datetime, end_at: datetime) -> Promotion:
        """创建促销"""
        promotion = Promotion(
            title=title,
            content=content,
            start_at=start_at,
            end_at=end_at
        )
        return self.promotion_repo.save(promotion)
    
    def list_active_promotions(self) -> List[Promotion]:
        """列出所有有效的促销"""
        return self.promotion_repo.find_active()
    
    def list_all_promotions(self) -> List[Promotion]:
        """列出所有促销"""
        return self.promotion_repo.find_all()
    
    def update_promotion(self, promotion_id: UUID, title: str = None,
                        content: str = None, is_active: bool = None) -> Optional[Promotion]:
        """更新促销"""
        promotion = self.promotion_repo.find_by_id(promotion_id)
        if not promotion:
            return None
        
        if title is not None:
            promotion.title = title
        if content is not None:
            promotion.content = content
        if is_active is not None:
            promotion.is_active = is_active
        
        return self.promotion_repo.save(promotion)
    
    def delete_promotion(self, promotion_id: UUID) -> bool:
        """删除促销"""
        return self.promotion_repo.delete(promotion_id)


class ReminderService:
    """提醒服务（模拟）"""
    
    def send_order_confirmation(self, order: Order):
        """发送订单确认（模拟）"""
        print(f"[提醒] 订单 {str(order.order_id)[:8]} 已确认，总金额：¥{order.total_amount()}")
    
    def send_pickup_reminder(self, order: Order):
        """发送取餐提醒（模拟）"""
        print(f"[提醒] 订单 {str(order.order_id)[:8]} 已准备好，请来取餐！")
    
    def invite_review(self, order: Order):
        """邀请评价（模拟）"""
        print(f"[提醒] 感谢您的光临！欢迎为订单 {str(order.order_id)[:8]} 评价")


class NotificationGateway:
    """通知网关接口（模拟）"""
    
    def send_sms(self, phone: str, text: str):
        """发送短信（模拟）"""
        print(f"[短信] 发送到 {phone}: {text}")
    
    def push(self, user_id: UUID, payload: dict):
        """推送通知（模拟）"""
        print(f"[推送] 发送到用户 {str(user_id)[:8]}: {payload}")

