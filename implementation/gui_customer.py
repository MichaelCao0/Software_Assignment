"""
奶茶点单系统 - 顾客端GUI界面
使用tkinter实现图形用户界面
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from decimal import Decimal
from typing import Optional

from models import User, MenuItem, Sweetness, OrderStatus
from services import (
    AuthService, MenuService, CartService, OrderService,
    ReviewService, FavoriteService, PromotionService
)


class CustomerGUI:
    """顾客端GUI主类"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("奶茶点单系统 - 顾客端")
        self.root.geometry("1000x700")
        
        # 初始化服务
        self.auth_service = AuthService()
        self.menu_service = MenuService()
        self.cart_service = CartService()
        self.order_service = OrderService()
        self.review_service = ReviewService()
        self.favorite_service = FavoriteService()
        self.promotion_service = PromotionService()
        
        # 当前用户
        self.current_user: Optional[User] = None
        
        # 创建主界面
        self.create_widgets()
    
    def create_widgets(self):
        """创建主界面组件"""
        # 顶部标题栏
        self.create_header()
        
        # 创建标签页
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=5)
        
        # 登录/注册页
        self.login_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.login_frame, text="登录/注册")
        self.create_login_tab()
        
        # 菜单浏览页
        self.menu_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.menu_frame, text="菜单浏览", state='disabled')
        self.create_menu_tab()
        
        # 购物车页
        self.cart_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.cart_frame, text="购物车", state='disabled')
        self.create_cart_tab()
        
        # 订单页
        self.order_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.order_frame, text="我的订单", state='disabled')
        self.create_order_tab()
        
        # 收藏页
        self.favorite_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.favorite_frame, text="我的收藏", state='disabled')
        self.create_favorite_tab()
        
        # 促销页
        self.promotion_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.promotion_frame, text="促销活动")
        self.create_promotion_tab()
    
    def create_header(self):
        """创建头部"""
        header = tk.Frame(self.root, bg='#FF6B9D', height=60)
        header.pack(fill='x')
        
        title = tk.Label(header, text="🧋 奶茶点单系统", 
                        font=('Arial', 20, 'bold'),
                        bg='#FF6B9D', fg='white')
        title.pack(side='left', padx=20, pady=15)
        
        self.user_label = tk.Label(header, text="未登录",
                                   font=('Arial', 12),
                                   bg='#FF6B9D', fg='white')
        self.user_label.pack(side='right', padx=20)
    
    def create_login_tab(self):
        """创建登录/注册标签页"""
        # 登录区域
        login_frame = ttk.LabelFrame(self.login_frame, text="登录", padding=20)
        login_frame.pack(side='left', fill='both', expand=True, padx=20, pady=20)
        
        tk.Label(login_frame, text="手机号:").grid(row=0, column=0, sticky='e', pady=10)
        self.login_phone = tk.Entry(login_frame, width=30)
        self.login_phone.grid(row=0, column=1, pady=10)
        
        tk.Button(login_frame, text="登录", command=self.do_login,
                 bg='#FF6B9D', fg='white', width=20).grid(row=1, column=0, columnspan=2, pady=20)
        
        # 注册区域
        register_frame = ttk.LabelFrame(self.login_frame, text="注册", padding=20)
        register_frame.pack(side='right', fill='both', expand=True, padx=20, pady=20)
        
        tk.Label(register_frame, text="昵称:").grid(row=0, column=0, sticky='e', pady=10)
        self.register_nickname = tk.Entry(register_frame, width=30)
        self.register_nickname.grid(row=0, column=1, pady=10)
        
        tk.Label(register_frame, text="手机号:").grid(row=1, column=0, sticky='e', pady=10)
        self.register_phone = tk.Entry(register_frame, width=30)
        self.register_phone.grid(row=1, column=1, pady=10)
        
        tk.Button(register_frame, text="注册", command=self.do_register,
                 bg='#4CAF50', fg='white', width=20).grid(row=2, column=0, columnspan=2, pady=20)
    
    def create_menu_tab(self):
        """创建菜单浏览标签页"""
        # 左侧：菜单列表
        left_frame = ttk.Frame(self.menu_frame)
        left_frame.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        
        tk.Label(left_frame, text="菜单列表", font=('Arial', 14, 'bold')).pack()
        
        # 菜单列表
        menu_list_frame = ttk.Frame(left_frame)
        menu_list_frame.pack(fill='both', expand=True, pady=10)
        
        scrollbar = ttk.Scrollbar(menu_list_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.menu_listbox = tk.Listbox(menu_list_frame, yscrollcommand=scrollbar.set,
                                       font=('Arial', 11))
        self.menu_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.menu_listbox.yscroll)
        
        self.menu_listbox.bind('<<ListboxSelect>>', self.on_menu_item_select)
        
        tk.Button(left_frame, text="刷新菜单", command=self.load_menu,
                 bg='#2196F3', fg='white').pack(fill='x', pady=5)
        
        # 右侧：商品详情和定制
        right_frame = ttk.Frame(self.menu_frame)
        right_frame.pack(side='right', fill='both', expand=True, padx=10, pady=10)
        
        tk.Label(right_frame, text="商品详情", font=('Arial', 14, 'bold')).pack()
        
        detail_frame = ttk.LabelFrame(right_frame, text="选择定制", padding=10)
        detail_frame.pack(fill='both', expand=True, pady=10)
        
        # 甜度选择
        tk.Label(detail_frame, text="甜度:").grid(row=0, column=0, sticky='w', pady=5)
        self.sweetness_var = tk.StringVar(value=Sweetness.FIVE.value)
        sweetness_frame = ttk.Frame(detail_frame)
        sweetness_frame.grid(row=0, column=1, sticky='w', pady=5)
        
        for sweetness in Sweetness:
            tk.Radiobutton(sweetness_frame, text=sweetness.value,
                          variable=self.sweetness_var, value=sweetness.value).pack(side='left')
        
        # 数量选择
        tk.Label(detail_frame, text="数量:").grid(row=1, column=0, sticky='w', pady=5)
        self.quantity_var = tk.IntVar(value=1)
        tk.Spinbox(detail_frame, from_=1, to=99, textvariable=self.quantity_var,
                  width=10).grid(row=1, column=1, sticky='w', pady=5)
        
        # 小料选择
        tk.Label(detail_frame, text="小料:").grid(row=2, column=0, sticky='w', pady=5)
        self.topping_listbox = tk.Listbox(detail_frame, selectmode='multiple', height=5)
        self.topping_listbox.grid(row=2, column=1, sticky='w', pady=5)
        
        # 备注
        tk.Label(detail_frame, text="备注:").grid(row=3, column=0, sticky='w', pady=5)
        self.remark_entry = tk.Entry(detail_frame, width=30)
        self.remark_entry.grid(row=3, column=1, sticky='w', pady=5)
        
        # 按钮区
        button_frame = ttk.Frame(detail_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        tk.Button(button_frame, text="加入购物车", command=self.add_to_cart,
                 bg='#FF6B9D', fg='white', width=15).pack(side='left', padx=5)
        tk.Button(button_frame, text="收藏", command=self.toggle_favorite,
                 bg='#FFC107', width=10).pack(side='left', padx=5)
    
    def create_cart_tab(self):
        """创建购物车标签页"""
        # 购物车列表
        list_frame = ttk.Frame(self.cart_frame)
        list_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        tk.Label(list_frame, text="购物车", font=('Arial', 14, 'bold')).pack()
        
        # 创建表格
        columns = ('商品', '甜度', '小料', '数量', '单价', '小计')
        self.cart_tree = ttk.Treeview(list_frame, columns=columns, show='tree headings', height=15)
        
        self.cart_tree.heading('#0', text='ID')
        self.cart_tree.column('#0', width=0, stretch=False)
        
        for col in columns:
            self.cart_tree.heading(col, text=col)
            self.cart_tree.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.cart_tree.yview)
        self.cart_tree.configure(yscrollcommand=scrollbar.set)
        
        self.cart_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # 底部：总计和按钮
        bottom_frame = ttk.Frame(self.cart_frame)
        bottom_frame.pack(fill='x', padx=10, pady=10)
        
        self.cart_total_label = tk.Label(bottom_frame, text="总计: ¥0.00",
                                         font=('Arial', 14, 'bold'))
        self.cart_total_label.pack(side='left', padx=20)
        
        tk.Button(bottom_frame, text="清空购物车", command=self.clear_cart,
                 bg='#F44336', fg='white', width=15).pack(side='right', padx=5)
        tk.Button(bottom_frame, text="移除选中", command=self.remove_from_cart,
                 bg='#FF9800', fg='white', width=15).pack(side='right', padx=5)
        tk.Button(bottom_frame, text="结算", command=self.checkout,
                 bg='#4CAF50', fg='white', width=15).pack(side='right', padx=5)
        tk.Button(bottom_frame, text="刷新", command=self.load_cart,
                 bg='#2196F3', fg='white', width=10).pack(side='right', padx=5)
    
    def create_order_tab(self):
        """创建订单标签页"""
        # 订单列表
        list_frame = ttk.Frame(self.order_frame)
        list_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        tk.Label(list_frame, text="我的订单", font=('Arial', 14, 'bold')).pack()
        
        # 创建表格
        columns = ('订单号', '状态', '金额', '时间', '备注')
        self.order_tree = ttk.Treeview(list_frame, columns=columns, show='tree headings', height=15)
        
        self.order_tree.heading('#0', text='ID')
        self.order_tree.column('#0', width=0, stretch=False)
        
        for col in columns:
            self.order_tree.heading(col, text=col)
            self.order_tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.order_tree.yview)
        self.order_tree.configure(yscrollcommand=scrollbar.set)
        
        self.order_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # 底部：按钮
        bottom_frame = ttk.Frame(self.order_frame)
        bottom_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Button(bottom_frame, text="刷新订单", command=self.load_orders,
                 bg='#2196F3', fg='white', width=15).pack(side='left', padx=5)
        tk.Button(bottom_frame, text="查看详情", command=self.view_order_detail,
                 bg='#9C27B0', fg='white', width=15).pack(side='left', padx=5)
        tk.Button(bottom_frame, text="评价订单", command=self.review_order,
                 bg='#FF6B9D', fg='white', width=15).pack(side='left', padx=5)
    
    def create_favorite_tab(self):
        """创建收藏标签页"""
        tk.Label(self.favorite_frame, text="我的收藏", 
                font=('Arial', 14, 'bold')).pack(pady=10)
        
        # 收藏列表
        scrollbar = ttk.Scrollbar(self.favorite_frame)
        scrollbar.pack(side='right', fill='y', padx=10, pady=10)
        
        self.favorite_listbox = tk.Listbox(self.favorite_frame, 
                                           yscrollcommand=scrollbar.set,
                                           font=('Arial', 11))
        self.favorite_listbox.pack(fill='both', expand=True, padx=10, pady=10)
        scrollbar.config(command=self.favorite_listbox.yscroll)
        
        # 按钮
        button_frame = ttk.Frame(self.favorite_frame)
        button_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Button(button_frame, text="刷新", command=self.load_favorites,
                 bg='#2196F3', fg='white', width=15).pack(side='left', padx=5)
        tk.Button(button_frame, text="取消收藏", command=self.remove_favorite,
                 bg='#F44336', fg='white', width=15).pack(side='left', padx=5)
    
    def create_promotion_tab(self):
        """创建促销活动标签页"""
        tk.Label(self.promotion_frame, text="促销活动", 
                font=('Arial', 14, 'bold')).pack(pady=10)
        
        # 促销列表
        self.promotion_text = scrolledtext.ScrolledText(self.promotion_frame, 
                                                        font=('Arial', 11),
                                                        wrap='word')
        self.promotion_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 按钮
        tk.Button(self.promotion_frame, text="刷新", command=self.load_promotions,
                 bg='#2196F3', fg='white', width=15).pack(pady=10)
        
        # 自动加载促销
        self.load_promotions()
    
    # 事件处理方法
    
    def do_login(self):
        """执行登录"""
        phone = self.login_phone.get().strip()
        if not phone:
            messagebox.showwarning("警告", "请输入手机号")
            return
        
        success, message, user = self.auth_service.login(phone)
        if success:
            self.current_user = user
            self.user_label.config(text=f"欢迎，{user.nickname}")
            messagebox.showinfo("成功", message)
            
            # 启用其他标签页
            for i in range(1, 5):
                self.notebook.tab(i, state='normal')
            
            # 切换到菜单页
            self.notebook.select(1)
            self.load_menu()
        else:
            messagebox.showerror("错误", message)
    
    def do_register(self):
        """执行注册"""
        nickname = self.register_nickname.get().strip()
        phone = self.register_phone.get().strip()
        
        if not nickname or not phone:
            messagebox.showwarning("警告", "请填写所有字段")
            return
        
        success, message, user = self.auth_service.register(nickname, phone)
        if success:
            messagebox.showinfo("成功", message)
            self.register_nickname.delete(0, 'end')
            self.register_phone.delete(0, 'end')
        else:
            messagebox.showerror("错误", message)
    
    def load_menu(self):
        """加载菜单"""
        self.menu_listbox.delete(0, 'end')
        items = self.menu_service.list_items()
        
        for item in items:
            status = "【售罄】" if item.is_sold_out else ""
            self.menu_listbox.insert('end', 
                                    f"{status}{item.name} - ¥{item.price}")
        
        # 加载小料
        self.topping_listbox.delete(0, 'end')
        toppings = self.menu_service.list_toppings()
        for topping in toppings:
            self.topping_listbox.insert('end', 
                                       f"{topping.name} +¥{topping.extra_price}")
    
    def on_menu_item_select(self, event):
        """菜单项选择事件"""
        # 这里可以显示更多商品详情
        pass
    
    def add_to_cart(self):
        """添加到购物车"""
        if not self.current_user:
            messagebox.showwarning("警告", "请先登录")
            return
        
        selection = self.menu_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请选择商品")
            return
        
        # 获取选中的商品
        items = self.menu_service.list_items()
        item = items[selection[0]]
        
        # 获取甜度
        sweetness_value = self.sweetness_var.get()
        sweetness = next(s for s in Sweetness if s.value == sweetness_value)
        
        # 获取数量
        quantity = self.quantity_var.get()
        
        # 获取小料
        topping_indices = self.topping_listbox.curselection()
        toppings = self.menu_service.list_toppings()
        topping_ids = [toppings[i].topping_id for i in topping_indices]
        
        # 获取备注
        remark = self.remark_entry.get()
        
        # 添加到购物车
        success, message = self.cart_service.add_to_cart(
            self.current_user.user_id, item.item_id, quantity,
            sweetness, topping_ids, remark
        )
        
        if success:
            messagebox.showinfo("成功", message)
        else:
            messagebox.showerror("错误", message)
    
    def toggle_favorite(self):
        """切换收藏状态"""
        if not self.current_user:
            messagebox.showwarning("警告", "请先登录")
            return
        
        selection = self.menu_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请选择商品")
            return
        
        items = self.menu_service.list_items()
        item = items[selection[0]]
        
        # 检查是否已收藏
        if self.favorite_service.is_favorited(self.current_user.user_id, item.item_id):
            success, message = self.favorite_service.remove_favorite(
                self.current_user.user_id, item.item_id)
        else:
            success, message = self.favorite_service.add_favorite(
                self.current_user.user_id, item.item_id)
        
        if success:
            messagebox.showinfo("成功", message)
        else:
            messagebox.showwarning("提示", message)
    
    def load_cart(self):
        """加载购物车"""
        if not self.current_user:
            return
        
        # 清空树
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)
        
        cart = self.cart_service.get_cart(self.current_user.user_id)
        if not cart:
            self.cart_total_label.config(text="总计: ¥0.00")
            return
        
        # 添加项目
        for order_item in cart.items:
            toppings_str = ", ".join(t.name for t in order_item.toppings)
            values = (
                order_item.menu_item.name,
                order_item.sweetness.value,
                toppings_str or "无",
                order_item.quantity,
                f"¥{order_item.menu_item.price}",
                f"¥{order_item.subtotal()}"
            )
            self.cart_tree.insert('', 'end', text=str(order_item.order_item_id), values=values)
        
        # 更新总计
        self.cart_total_label.config(text=f"总计: ¥{cart.total()}")
    
    def remove_from_cart(self):
        """从购物车移除"""
        if not self.current_user:
            return
        
        selection = self.cart_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请选择要移除的商品")
            return
        
        item_id = self.cart_tree.item(selection[0])['text']
        from uuid import UUID
        self.cart_service.remove_from_cart(self.current_user.user_id, UUID(item_id))
        self.load_cart()
    
    def clear_cart(self):
        """清空购物车"""
        if not self.current_user:
            return
        
        if messagebox.askyesno("确认", "确定要清空购物车吗？"):
            self.cart_service.clear_cart(self.current_user.user_id)
            self.load_cart()
    
    def checkout(self):
        """结算"""
        if not self.current_user:
            return
        
        cart = self.cart_service.get_cart(self.current_user.user_id)
        if not cart or not cart.items:
            messagebox.showwarning("警告", "购物车为空")
            return
        
        # 询问备注
        remark = tk.simpledialog.askstring("备注", "请输入订单备注（可选）:")
        
        success, message, order = self.order_service.place_order(
            self.current_user.user_id, remark or "")
        
        if success:
            messagebox.showinfo("成功", message)
            self.load_cart()
        else:
            messagebox.showerror("错误", message)
    
    def load_orders(self):
        """加载订单"""
        if not self.current_user:
            return
        
        # 清空树
        for item in self.order_tree.get_children():
            self.order_tree.delete(item)
        
        orders = self.order_service.list_orders(self.current_user.user_id)
        
        for order in orders:
            values = (
                str(order.order_id)[:8],
                order.status.value,
                f"¥{order.total_amount()}",
                order.created_at.strftime("%Y-%m-%d %H:%M"),
                order.remark or "无"
            )
            self.order_tree.insert('', 'end', text=str(order.order_id), values=values)
    
    def view_order_detail(self):
        """查看订单详情"""
        selection = self.order_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请选择订单")
            return
        
        order_id = self.order_tree.item(selection[0])['text']
        from uuid import UUID
        order = self.order_service.get_order(UUID(order_id))
        
        if not order:
            return
        
        # 创建详情窗口
        detail_window = tk.Toplevel(self.root)
        detail_window.title("订单详情")
        detail_window.geometry("500x400")
        
        text = scrolledtext.ScrolledText(detail_window, wrap='word', font=('Arial', 11))
        text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 显示订单信息
        text.insert('end', f"订单号: {str(order.order_id)[:8]}\n")
        text.insert('end', f"状态: {order.status.value}\n")
        text.insert('end', f"时间: {order.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n")
        text.insert('end', f"备注: {order.remark or '无'}\n")
        text.insert('end', "\n商品列表:\n")
        text.insert('end', "-" * 50 + "\n")
        
        for item in order.items:
            text.insert('end', f"\n{item.menu_item.name} x{item.quantity}\n")
            text.insert('end', f"  甜度: {item.sweetness.value}\n")
            if item.toppings:
                text.insert('end', f"  小料: {', '.join(t.name for t in item.toppings)}\n")
            if item.remark:
                text.insert('end', f"  备注: {item.remark}\n")
            text.insert('end', f"  小计: ¥{item.subtotal()}\n")
        
        text.insert('end', "\n" + "-" * 50 + "\n")
        text.insert('end', f"总计: ¥{order.total_amount()}\n")
        
        text.config(state='disabled')
    
    def review_order(self):
        """评价订单"""
        if not self.current_user:
            return
        
        selection = self.order_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请选择订单")
            return
        
        order_id = self.order_tree.item(selection[0])['text']
        from uuid import UUID
        
        # 创建评价窗口
        review_window = tk.Toplevel(self.root)
        review_window.title("评价订单")
        review_window.geometry("400x300")
        
        tk.Label(review_window, text="评分 (1-5星):", font=('Arial', 12)).pack(pady=10)
        rating_var = tk.IntVar(value=5)
        tk.Spinbox(review_window, from_=1, to=5, textvariable=rating_var,
                  font=('Arial', 12), width=10).pack()
        
        tk.Label(review_window, text="评价内容:", font=('Arial', 12)).pack(pady=10)
        content_text = scrolledtext.ScrolledText(review_window, height=8, wrap='word')
        content_text.pack(fill='both', expand=True, padx=10)
        
        def submit_review():
            rating = rating_var.get()
            content = content_text.get('1.0', 'end').strip()
            
            success, message, review = self.review_service.create_review(
                self.current_user.user_id, UUID(order_id), rating, content)
            
            if success:
                messagebox.showinfo("成功", message)
                review_window.destroy()
            else:
                messagebox.showerror("错误", message)
        
        tk.Button(review_window, text="提交评价", command=submit_review,
                 bg='#FF6B9D', fg='white', width=20).pack(pady=10)
    
    def load_favorites(self):
        """加载收藏"""
        if not self.current_user:
            return
        
        self.favorite_listbox.delete(0, 'end')
        favorites = self.favorite_service.list_favorites(self.current_user.user_id)
        
        for fav in favorites:
            item = self.menu_service.get_item(fav.item_id)
            if item:
                self.favorite_listbox.insert('end', 
                                            f"{item.name} - ¥{item.price}")
    
    def remove_favorite(self):
        """移除收藏"""
        if not self.current_user:
            return
        
        selection = self.favorite_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请选择要取消的收藏")
            return
        
        favorites = self.favorite_service.list_favorites(self.current_user.user_id)
        fav = favorites[selection[0]]
        
        success, message = self.favorite_service.remove_favorite(
            self.current_user.user_id, fav.item_id)
        
        if success:
            messagebox.showinfo("成功", message)
            self.load_favorites()
    
    def load_promotions(self):
        """加载促销活动"""
        self.promotion_text.delete('1.0', 'end')
        promotions = self.promotion_service.list_active_promotions()
        
        if not promotions:
            self.promotion_text.insert('end', "暂无促销活动\n")
        else:
            for promo in promotions:
                self.promotion_text.insert('end', f"🎉 {promo.title}\n", 'title')
                self.promotion_text.insert('end', f"{promo.content}\n\n")
                self.promotion_text.insert('end', 
                    f"活动时间: {promo.start_at.strftime('%Y-%m-%d')} 至 "
                    f"{promo.end_at.strftime('%Y-%m-%d')}\n")
                self.promotion_text.insert('end', "-" * 50 + "\n\n")
        
        self.promotion_text.tag_config('title', font=('Arial', 12, 'bold'))


def run_customer_app():
    """运行顾客端应用"""
    root = tk.Tk()
    app = CustomerGUI(root)
    root.mainloop()


if __name__ == '__main__':
    run_customer_app()

