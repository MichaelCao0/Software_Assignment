"""餐饮点单系统 - 主入口"""
import tkinter as tk
from tkinter import ttk
from decimal import Decimal
import uuid

from domain.models import MenuItem
from repositories.repository import InMemoryMenuRepo, InMemoryOrderRepo
from services.services import MenuService, OrderService
from presentation.gui import CustomerGUI, AdminGUI


def init_sample_data(menu_service: MenuService):
    """初始化示例数据"""
    items = [
        MenuItem(str(uuid.uuid4()), "宫保鸡丁", Decimal("32"), "热菜", "经典川菜"),
        MenuItem(str(uuid.uuid4()), "番茄炒蛋", Decimal("18"), "热菜", "家常菜"),
        MenuItem(str(uuid.uuid4()), "扬州炒饭", Decimal("25"), "主食", "粒粒分明"),
        MenuItem(str(uuid.uuid4()), "酸辣汤", Decimal("12"), "汤品", "酸辣开胃"),
        MenuItem(str(uuid.uuid4()), "可乐", Decimal("5"), "饮料", "冰镇可乐"),
    ]
    for item in items:
        menu_service.add_menu_item(item)


def main():
    """主函数"""
    menu_repo = InMemoryMenuRepo()
    order_repo = InMemoryOrderRepo()
    menu_service = MenuService(menu_repo)
    order_service = OrderService(order_repo, menu_repo)
    init_sample_data(menu_service)
    
    root = tk.Tk()
    root.title("餐饮点单系统")
    root.geometry("400x300")
    
    frame = ttk.Frame(root, padding="50")
    frame.pack(expand=True)
    
    ttk.Label(frame, text="欢迎使用餐饮点单系统", font=("", 16, "bold")).pack(pady=20)
    
    def open_customer():
        CustomerGUI(tk.Toplevel(root), menu_service, order_service)
    
    def open_admin():
        AdminGUI(tk.Toplevel(root), menu_service, order_service)
    
    ttk.Button(frame, text="顾客端", command=open_customer, width=20).pack(pady=10)
    ttk.Button(frame, text="管理员端", command=open_admin, width=20).pack(pady=10)
    ttk.Button(frame, text="退出", command=root.quit, width=20).pack(pady=10)
    
    root.mainloop()


if __name__ == "__main__":
    main()

