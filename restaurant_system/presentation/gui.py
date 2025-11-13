"""表现层 - GUI界面"""
import tkinter as tk
from tkinter import ttk, messagebox
from decimal import Decimal
import uuid

from domain.models import MenuItem, Cart, CartItem, OrderStatus
from services.services import MenuService, OrderService


class CustomerGUI:
    """顾客端界面"""
    
    def __init__(self, root: tk.Tk, menu_service: MenuService, order_service: OrderService):
        self.root = root
        self.menu_service = menu_service
        self.order_service = order_service
        self.cart = Cart()
        
        self.root.title("餐饮点单系统 - 顾客端")
        self.root.geometry("800x500")
        
        # 菜单列表
        left_frame = ttk.LabelFrame(self.root, text="菜单", padding="10")
        left_frame.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        
        self.menu_tree = ttk.Treeview(left_frame, columns=('name', 'price'), show='headings', height=18)
        self.menu_tree.heading('name', text='菜品')
        self.menu_tree.heading('price', text='价格')
        self.menu_tree.pack(fill='both', expand=True)
        ttk.Button(left_frame, text="添加到购物车", command=self.add_to_cart).pack(pady=5)
        
        # 购物车
        right_frame = ttk.LabelFrame(self.root, text="购物车", padding="10")
        right_frame.pack(side='right', fill='both', expand=True, padx=5, pady=5)
        
        self.cart_tree = ttk.Treeview(right_frame, columns=('item', 'price'), show='headings', height=15)
        self.cart_tree.heading('item', text='商品')
        self.cart_tree.heading('price', text='小计')
        self.cart_tree.pack(fill='both', expand=True)
        
        self.total_label = ttk.Label(right_frame, text="总价: ¥0.00", font=("", 12, "bold"))
        self.total_label.pack(pady=10)
        
        ttk.Button(right_frame, text="移除", command=self.remove_from_cart).pack(side='left', padx=5)
        ttk.Button(right_frame, text="结算", command=self.checkout).pack(side='right', padx=5)
        
        self.refresh_menu()
    
    def refresh_menu(self):
        for item in self.menu_tree.get_children():
            self.menu_tree.delete(item)
        for item in self.menu_service.get_available_items():
            self.menu_tree.insert('', 'end', values=(item.name, f"¥{item.base_price}"), tags=(item.id,))
    
    def add_to_cart(self):
        selection = self.menu_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请先选择菜品")
            return
        
        item_id = self.menu_tree.item(selection[0])['tags'][0]
        menu_item = self.menu_service.get_item_by_id(item_id)
        cart_item = CartItem(id=str(uuid.uuid4()), menu_item=menu_item, quantity=1)
        self.cart.add_item(cart_item)
        self.refresh_cart()
    
    def remove_from_cart(self):
        selection = self.cart_tree.selection()
        if not selection:
            return
        item_id = self.cart_tree.item(selection[0])['tags'][0]
        self.cart.remove_item(item_id)
        self.refresh_cart()
    
    def refresh_cart(self):
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)
        for item in self.cart.items:
            self.cart_tree.insert('', 'end', values=(item.menu_item.name, f"¥{item.calculate_subtotal()}"), tags=(item.id,))
        self.total_label.config(text=f"总价: ¥{self.cart.get_total_price()}")
    
    def checkout(self):
        if not self.cart.items:
            messagebox.showwarning("提示", "购物车为空")
            return
        try:
            order = self.order_service.create_order(self.cart)
            messagebox.showinfo("成功", f"订单已创建！订单号: {order.id[:8]}\n总价: ¥{order.total_price}")
            self.cart.clear()
            self.refresh_cart()
        except Exception as e:
            messagebox.showerror("错误", str(e))


class AdminGUI:
    """管理员端界面"""
    
    def __init__(self, root: tk.Tk, menu_service: MenuService, order_service: OrderService):
        self.root = root
        self.menu_service = menu_service
        self.order_service = order_service
        
        self.root.title("餐饮点单系统 - 管理员端")
        self.root.geometry("800x500")
        
        # 标签页
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 菜单管理
        menu_frame = ttk.Frame(notebook)
        notebook.add(menu_frame, text='菜单管理')
        
        self.menu_tree = ttk.Treeview(menu_frame, columns=('name', 'price', 'status'), show='headings', height=18)
        self.menu_tree.heading('name', text='菜品')
        self.menu_tree.heading('price', text='价格')
        self.menu_tree.heading('status', text='状态')
        self.menu_tree.pack(fill='both', expand=True, padx=10, pady=10)
        
        btn_frame1 = ttk.Frame(menu_frame)
        btn_frame1.pack(fill='x', padx=10, pady=5)
        ttk.Button(btn_frame1, text="添加菜品", command=self.add_menu_item).pack(side='left', padx=5)
        ttk.Button(btn_frame1, text="上/下架", command=self.toggle_item).pack(side='left', padx=5)
        ttk.Button(btn_frame1, text="刷新", command=self.refresh_menu).pack(side='left', padx=5)
        
        # 订单管理
        order_frame = ttk.Frame(notebook)
        notebook.add(order_frame, text='订单管理')
        
        self.order_tree = ttk.Treeview(order_frame, columns=('id', 'price', 'status'), show='headings', height=18)
        self.order_tree.heading('id', text='订单号')
        self.order_tree.heading('price', text='总价')
        self.order_tree.heading('status', text='状态')
        self.order_tree.pack(fill='both', expand=True, padx=10, pady=10)
        
        btn_frame2 = ttk.Frame(order_frame)
        btn_frame2.pack(fill='x', padx=10, pady=5)
        ttk.Button(btn_frame2, text="制作中", command=lambda: self.update_status(OrderStatus.PROCESSING)).pack(side='left', padx=5)
        ttk.Button(btn_frame2, text="已完成", command=lambda: self.update_status(OrderStatus.COMPLETED)).pack(side='left', padx=5)
        ttk.Button(btn_frame2, text="刷新", command=self.refresh_orders).pack(side='left', padx=5)
        
        self.refresh_menu()
        self.refresh_orders()
    
    def refresh_menu(self):
        for item in self.menu_tree.get_children():
            self.menu_tree.delete(item)
        for item in self.menu_service.get_all_items():
            status = "上架" if item.is_available else "下架"
            self.menu_tree.insert('', 'end', values=(item.name, f"¥{item.base_price}", status), tags=(item.id,))
    
    def refresh_orders(self):
        for item in self.order_tree.get_children():
            self.order_tree.delete(item)
        for order in self.order_service.get_orders():
            self.order_tree.insert('', 'end', values=(order.id[:8], f"¥{order.total_price}", order.status.value), tags=(order.id,))
    
    def add_menu_item(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("添加菜品")
        dialog.geometry("350x200")
        
        ttk.Label(dialog, text="名称:").grid(row=0, column=0, padx=10, pady=10)
        name_entry = ttk.Entry(dialog, width=20)
        name_entry.grid(row=0, column=1, padx=10, pady=10)
        
        ttk.Label(dialog, text="价格:").grid(row=1, column=0, padx=10, pady=10)
        price_entry = ttk.Entry(dialog, width=20)
        price_entry.grid(row=1, column=1, padx=10, pady=10)
        
        ttk.Label(dialog, text="分类:").grid(row=2, column=0, padx=10, pady=10)
        category_entry = ttk.Entry(dialog, width=20)
        category_entry.grid(row=2, column=1, padx=10, pady=10)
        
        def save():
            try:
                item = MenuItem(
                    id=str(uuid.uuid4()),
                    name=name_entry.get(),
                    base_price=Decimal(price_entry.get()),
                    category=category_entry.get()
                )
                self.menu_service.add_menu_item(item)
                messagebox.showinfo("成功", "菜品添加成功")
                dialog.destroy()
                self.refresh_menu()
            except Exception as e:
                messagebox.showerror("错误", str(e))
        
        ttk.Button(dialog, text="保存", command=save).grid(row=3, column=0, columnspan=2, pady=20)
    
    def toggle_item(self):
        selection = self.menu_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请先选择菜品")
            return
        item_id = self.menu_tree.item(selection[0])['tags'][0]
        self.menu_service.toggle_availability(item_id)
        self.refresh_menu()
    
    def update_status(self, status: OrderStatus):
        selection = self.order_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请先选择订单")
            return
        order_id = self.order_tree.item(selection[0])['tags'][0]
        self.order_service.update_order_status(order_id, status)
        self.refresh_orders()

