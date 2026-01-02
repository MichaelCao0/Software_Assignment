"""
奶茶点单系统 - 主入口文件
提供顾客端和管理员端的启动入口
"""

import tkinter as tk
from tkinter import ttk

from gui_customer import CustomerGUI
from gui_admin import AdminGUI


def main():
    """主函数"""
    root = tk.Tk()
    root.title("奶茶点单系统")
    root.geometry("400x300")
    
    frame = ttk.Frame(root, padding="50")
    frame.pack(expand=True)
    
    ttk.Label(frame, text="欢迎使用奶茶点单系统", 
              font=("Arial", 16, "bold")).pack(pady=20)
    
    def open_customer():
        """打开顾客端"""
        customer_window = tk.Toplevel(root)
        CustomerGUI(customer_window)
    
    def open_admin():
        """打开管理员端"""
        admin_window = tk.Toplevel(root)
        AdminGUI(admin_window)
    
    ttk.Button(frame, text="顾客端", command=open_customer, 
               width=20).pack(pady=10)
    ttk.Button(frame, text="管理员端", command=open_admin, 
               width=20).pack(pady=10)
    ttk.Button(frame, text="退出", command=root.quit, 
               width=20).pack(pady=10)
    
    root.mainloop()


if __name__ == "__main__":
    main()

