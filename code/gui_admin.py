"""
奶茶点单系统 - 管理员端GUI界面
使用tkinter实现管理员图形用户界面
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from decimal import Decimal
from uuid import UUID

from models import MenuItem, OrderStatus
from services import MenuService, OrderService


class AdminGUI:
    """管理员端GUI主类"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("奶茶点单系统 - 管理员端")
        self.root.geometry("900x600")
        
        # 初始化服务
        self.menu_service = MenuService()
        self.order_service = OrderService()
        
        # 创建主界面
        self.create_widgets()
    
    def create_widgets(self):
        """创建主界面组件"""
        # 创建标签页
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 菜单管理页
        self.menu_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.menu_frame, text="菜单管理")
        self.create_menu_tab()
        
        # 订单管理页
        self.order_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.order_frame, text="订单管理")
        self.create_order_tab()
        
        # 自动加载数据
        self.refresh_menu()
        self.refresh_orders()
    
    def create_menu_tab(self):
        """创建菜单管理标签页"""
        # 菜单列表
        list_frame = ttk.Frame(self.menu_frame)
        list_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        tk.Label(list_frame, text="菜单列表", font=('Arial', 14, 'bold')).pack()
        
        # 创建表格
        columns = ('名称', '价格', '分类', '状态')
        self.menu_tree = ttk.Treeview(list_frame, columns=columns, show='tree headings', height=15)
        
        self.menu_tree.heading('#0', text='ID')
        self.menu_tree.column('#0', width=0, stretch=False)
        
        for col in columns:
            self.menu_tree.heading(col, text=col)
            self.menu_tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.menu_tree.yview)
        self.menu_tree.configure(yscrollcommand=scrollbar.set)
        
        self.menu_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # 底部：按钮
        bottom_frame = ttk.Frame(self.menu_frame)
        bottom_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Button(bottom_frame, text="添加菜品", command=self.add_menu_item,
                 bg='#4CAF50', fg='white', width=15).pack(side='left', padx=5)
        tk.Button(bottom_frame, text="编辑菜品", command=self.edit_menu_item,
                 bg='#2196F3', fg='white', width=15).pack(side='left', padx=5)
        tk.Button(bottom_frame, text="上/下架", command=self.toggle_item,
                 bg='#FF9800', fg='white', width=15).pack(side='left', padx=5)
        tk.Button(bottom_frame, text="删除菜品", command=self.delete_menu_item,
                 bg='#F44336', fg='white', width=15).pack(side='left', padx=5)
        tk.Button(bottom_frame, text="刷新", command=self.refresh_menu,
                 bg='#9E9E9E', fg='white', width=10).pack(side='left', padx=5)
    
    def create_order_tab(self):
        """创建订单管理标签页"""
        # 订单列表
        list_frame = ttk.Frame(self.order_frame)
        list_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        tk.Label(list_frame, text="订单列表", font=('Arial', 14, 'bold')).pack()
        
        # 创建表格
        columns = ('订单号', '状态', '金额', '时间')
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
        
        tk.Button(bottom_frame, text="待接单", command=lambda: self.update_order_status(OrderStatus.PENDING),
                 bg='#9E9E9E', fg='white', width=12).pack(side='left', padx=5)
        tk.Button(bottom_frame, text="制作中", command=lambda: self.update_order_status(OrderStatus.PREPARING),
                 bg='#2196F3', fg='white', width=12).pack(side='left', padx=5)
        tk.Button(bottom_frame, text="待取餐", command=lambda: self.update_order_status(OrderStatus.READY),
                 bg='#FF9800', fg='white', width=12).pack(side='left', padx=5)
        tk.Button(bottom_frame, text="已完成", command=lambda: self.update_order_status(OrderStatus.COMPLETED),
                 bg='#4CAF50', fg='white', width=12).pack(side='left', padx=5)
        tk.Button(bottom_frame, text="查看详情", command=self.view_order_detail,
                 bg='#9C27B0', fg='white', width=12).pack(side='left', padx=5)
        tk.Button(bottom_frame, text="刷新", command=self.refresh_orders,
                 bg='#9E9E9E', fg='white', width=10).pack(side='left', padx=5)
    
    def refresh_menu(self):
        """刷新菜单列表"""
        # 清空树
        for item in self.menu_tree.get_children():
            self.menu_tree.delete(item)
        
        items = self.menu_service.list_all_items()
        for item in items:
            status = "售罄" if item.is_sold_out else "在售"
            values = (
                item.name,
                f"¥{item.price}",
                item.category or "未分类",
                status
            )
            self.menu_tree.insert('', 'end', text=str(item.item_id), values=values)
    
    def add_menu_item(self):
        """添加菜品"""
        dialog = tk.Toplevel(self.root)
        dialog.title("添加菜品")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 名称
        tk.Label(dialog, text="名称:").grid(row=0, column=0, sticky='e', padx=10, pady=10)
        name_entry = tk.Entry(dialog, width=30)
        name_entry.grid(row=0, column=1, padx=10, pady=10)
        
        # 价格
        tk.Label(dialog, text="价格:").grid(row=1, column=0, sticky='e', padx=10, pady=10)
        price_entry = tk.Entry(dialog, width=30)
        price_entry.grid(row=1, column=1, padx=10, pady=10)
        
        # 分类
        tk.Label(dialog, text="分类:").grid(row=2, column=0, sticky='e', padx=10, pady=10)
        category_entry = tk.Entry(dialog, width=30)
        category_entry.grid(row=2, column=1, padx=10, pady=10)
        
        # 描述
        tk.Label(dialog, text="描述:").grid(row=3, column=0, sticky='ne', padx=10, pady=10)
        description_text = tk.Text(dialog, width=30, height=4)
        description_text.grid(row=3, column=1, padx=10, pady=10)
        
        def save():
            try:
                name = name_entry.get().strip()
                price_str = price_entry.get().strip()
                category = category_entry.get().strip()
                description = description_text.get('1.0', 'end').strip()
                
                if not name or not price_str:
                    messagebox.showwarning("警告", "请填写名称和价格")
                    return
                
                price = Decimal(price_str)
                if price < 0:
                    messagebox.showwarning("警告", "价格不能为负数")
                    return
                
                item = self.menu_service.create_item(
                    name=name,
                    price=price,
                    category=category,
                    description=description
                )
                
                messagebox.showinfo("成功", f"菜品 '{item.name}' 添加成功")
                dialog.destroy()
                self.refresh_menu()
            except ValueError:
                messagebox.showerror("错误", "价格格式不正确")
            except Exception as e:
                messagebox.showerror("错误", str(e))
        
        tk.Button(dialog, text="保存", command=save,
                 bg='#4CAF50', fg='white', width=15).grid(row=4, column=0, columnspan=2, pady=20)
    
    def edit_menu_item(self):
        """编辑菜品"""
        selection = self.menu_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请选择要编辑的菜品")
            return
        
        item_id = UUID(self.menu_tree.item(selection[0])['text'])
        item = self.menu_service.get_item(item_id)
        if not item:
            messagebox.showerror("错误", "菜品不存在")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("编辑菜品")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 名称
        tk.Label(dialog, text="名称:").grid(row=0, column=0, sticky='e', padx=10, pady=10)
        name_entry = tk.Entry(dialog, width=30)
        name_entry.insert(0, item.name)
        name_entry.grid(row=0, column=1, padx=10, pady=10)
        
        # 价格
        tk.Label(dialog, text="价格:").grid(row=1, column=0, sticky='e', padx=10, pady=10)
        price_entry = tk.Entry(dialog, width=30)
        price_entry.insert(0, str(item.price))
        price_entry.grid(row=1, column=1, padx=10, pady=10)
        
        # 分类
        tk.Label(dialog, text="分类:").grid(row=2, column=0, sticky='e', padx=10, pady=10)
        category_entry = tk.Entry(dialog, width=30)
        category_entry.insert(0, item.category)
        category_entry.grid(row=2, column=1, padx=10, pady=10)
        
        # 描述
        tk.Label(dialog, text="描述:").grid(row=3, column=0, sticky='ne', padx=10, pady=10)
        description_text = tk.Text(dialog, width=30, height=4)
        description_text.insert('1.0', item.description)
        description_text.grid(row=3, column=1, padx=10, pady=10)
        
        def save():
            try:
                name = name_entry.get().strip()
                price_str = price_entry.get().strip()
                category = category_entry.get().strip()
                description = description_text.get('1.0', 'end').strip()
                
                if not name or not price_str:
                    messagebox.showwarning("警告", "请填写名称和价格")
                    return
                
                price = Decimal(price_str)
                if price < 0:
                    messagebox.showwarning("警告", "价格不能为负数")
                    return
                
                updated_item = self.menu_service.update_item(
                    item_id=item_id,
                    name=name,
                    price=price,
                    category=category,
                    description=description
                )
                
                if updated_item:
                    messagebox.showinfo("成功", f"菜品 '{updated_item.name}' 更新成功")
                    dialog.destroy()
                    self.refresh_menu()
            except ValueError:
                messagebox.showerror("错误", "价格格式不正确")
            except Exception as e:
                messagebox.showerror("错误", str(e))
        
        tk.Button(dialog, text="保存", command=save,
                 bg='#4CAF50', fg='white', width=15).grid(row=4, column=0, columnspan=2, pady=20)
    
    def toggle_item(self):
        """切换商品上下架状态"""
        selection = self.menu_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请选择要操作的菜品")
            return
        
        item_id = UUID(self.menu_tree.item(selection[0])['text'])
        item = self.menu_service.get_item(item_id)
        if not item:
            messagebox.showerror("错误", "菜品不存在")
            return
        
        # 切换售罄状态（下架=售罄，上架=在售）
        new_status = not item.is_sold_out
        success = self.menu_service.mark_sold_out(item_id, new_status)
        
        if success:
            status_text = "下架" if new_status else "上架"
            messagebox.showinfo("成功", f"菜品已{status_text}")
            self.refresh_menu()
        else:
            messagebox.showerror("错误", "操作失败")
    
    def delete_menu_item(self):
        """删除菜品"""
        selection = self.menu_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请选择要删除的菜品")
            return
        
        item_id = UUID(self.menu_tree.item(selection[0])['text'])
        item = self.menu_service.get_item(item_id)
        if not item:
            messagebox.showerror("错误", "菜品不存在")
            return
        
        if messagebox.askyesno("确认", f"确定要删除菜品 '{item.name}' 吗？"):
            success = self.menu_service.delete_item(item_id)
            if success:
                messagebox.showinfo("成功", "菜品已删除")
                self.refresh_menu()
            else:
                messagebox.showerror("错误", "删除失败")
    
    def refresh_orders(self):
        """刷新订单列表"""
        # 清空树
        for item in self.order_tree.get_children():
            self.order_tree.delete(item)
        
        orders = self.order_service.list_orders()
        for order in orders:
            values = (
                str(order.order_id)[:8],
                order.status.value,
                f"¥{order.total_amount()}",
                order.created_at.strftime("%Y-%m-%d %H:%M")
            )
            self.order_tree.insert('', 'end', text=str(order.order_id), values=values)
    
    def update_order_status(self, status: OrderStatus):
        """更新订单状态"""
        selection = self.order_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请选择要处理的订单")
            return
        
        order_id = UUID(self.order_tree.item(selection[0])['text'])
        success, message = self.order_service.update_status(order_id, status)
        
        if success:
            messagebox.showinfo("成功", message)
            self.refresh_orders()
        else:
            messagebox.showerror("错误", message)
    
    def view_order_detail(self):
        """查看订单详情"""
        selection = self.order_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请选择订单")
            return
        
        order_id = UUID(self.order_tree.item(selection[0])['text'])
        order = self.order_service.get_order(order_id)
        
        if not order:
            messagebox.showerror("错误", "订单不存在")
            return
        
        # 创建详情窗口
        detail_window = tk.Toplevel(self.root)
        detail_window.title("订单详情")
        detail_window.geometry("500x400")
        
        from tkinter import scrolledtext
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


def run_admin_app():
    """运行管理员端应用"""
    root = tk.Tk()
    app = AdminGUI(root)
    root.mainloop()


if __name__ == '__main__':
    run_admin_app()

