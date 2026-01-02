"""
故意植入的缺陷代码 - 用于测试工具检测能力
包含常见的安全和质量问题
"""

from typing import Optional, List
import os


# ==================== 缺陷1: Memory Leak (资源未释放) ====================
class DatabaseConnection:
    """数据库连接类 - 存在资源泄漏"""
    
    def __init__(self, host: str):
        self.host = host
        self.file = open(f"log_{host}.txt", "w")  # 缺陷：文件未关闭
        print(f"Connected to {host}")
    
    def query(self, sql: str):
        """执行查询"""
        self.file.write(f"Query: {sql}\n")
        return []
    
    # 缺陷：缺少 __del__ 或 close() 方法来关闭文件


def test_memory_leak():
    """测试内存泄漏 - 文件句柄未释放"""
    conn = DatabaseConnection("localhost")
    conn.query("SELECT * FROM users")
    # 缺陷：conn被丢弃，文件未关闭


# ==================== 缺陷2: NULL Pointer Dereference ====================
def get_user_name(user_id: int) -> Optional[str]:
    """获取用户名 - 可能返回None"""
    if user_id < 0:
        return None
    return f"User_{user_id}"


def test_null_pointer_dereference():
    """测试空指针引用"""
    user_name = get_user_name(-1)  # 返回None
    # 缺陷：未检查None就使用
    name_length = len(user_name)  # TypeError: object of type 'NoneType' has no len()
    print(f"Name length: {name_length}")


# ==================== 缺陷3: Division by Zero ====================
def calculate_average(total: int, count: int) -> float:
    """计算平均值 - 可能除零"""
    # 缺陷：未检查count是否为0
    return total / count  # ZeroDivisionError


def test_division_by_zero():
    """测试除零错误"""
    result = calculate_average(100, 0)  # 缺陷：count=0
    print(f"Average: {result}")


# ==================== 缺陷4: Array Index Out of Bounds ====================
def get_first_item(items: List[int]) -> int:
    """获取第一个元素 - 可能越界"""
    # 缺陷：未检查列表是否为空
    return items[0]  # IndexError: list index out of range


def test_array_out_of_bounds():
    """测试数组越界"""
    empty_list = []
    first = get_first_item(empty_list)  # 缺陷：空列表
    print(f"First item: {first}")


# ==================== 缺陷5: Resource Double Close ====================
class FileHandler:
    """文件处理器 - 双重关闭"""
    
    def __init__(self, filename: str):
        self.file = open(filename, "w")
        self.closed = False
    
    def write(self, data: str):
        """写入数据"""
        if not self.closed:
            self.file.write(data)
    
    def close(self):
        """关闭文件"""
        self.file.close()
        self.closed = True
    
    def __del__(self):
        """析构函数"""
        # 缺陷：可能导致双重关闭
        self.file.close()  # 如果已经调用close()，这里会再次关闭


def test_double_close():
    """测试双重关闭"""
    handler = FileHandler("test.txt")
    handler.write("Hello")
    handler.close()  # 第一次关闭
    # handler被销毁时，__del__会再次关闭（双重关闭）


# ==================== 缺陷6: Integer Overflow ====================
def calculate_total_price(price: int, quantity: int) -> int:
    """计算总价 - 可能溢出"""
    # 缺陷：未检查溢出
    return price * quantity  # 如果price和quantity很大，可能溢出


def test_integer_overflow():
    """测试整数溢出"""
    # 在Python中整数不会溢出，但在其他语言或使用numpy时可能
    max_int = 2147483647  # int32最大值
    result = calculate_total_price(max_int, 2)  # 缺陷：溢出
    print(f"Total: {result}")


# ==================== 缺陷7: SQL Injection (模拟) ====================
def unsafe_query(username: str) -> str:
    """不安全的查询 - SQL注入"""
    # 缺陷：直接拼接SQL，未过滤输入
    sql = f"SELECT * FROM users WHERE username = '{username}'"
    return sql


def test_sql_injection():
    """测试SQL注入"""
    # 恶意输入
    malicious_input = "admin' OR '1'='1"
    query = unsafe_query(malicious_input)
    # 缺陷：生成的SQL: SELECT * FROM users WHERE username = 'admin' OR '1'='1'
    print(f"Query: {query}")


# ==================== 缺陷8: Uninitialized Variable ====================
def process_data(flag: bool) -> int:
    """处理数据 - 变量未初始化"""
    # 缺陷：result可能未初始化
    if flag:
        result = 100
    # 如果flag为False，result未定义
    return result  # NameError: name 'result' is not defined


def test_uninitialized_variable():
    """测试未初始化变量"""
    value = process_data(False)  # 缺陷：result未初始化
    print(f"Value: {value}")


# ==================== 缺陷9: Race Condition (并发问题) ====================
class Counter:
    """计数器 - 存在竞态条件"""
    
    def __init__(self):
        self.count = 0
    
    def increment(self):
        """增加计数 - 非线程安全"""
        # 缺陷：读取-修改-写入不是原子操作
        temp = self.count
        temp = temp + 1
        self.count = temp


def test_race_condition():
    """测试竞态条件"""
    import threading
    
    counter = Counter()
    
    def worker():
        for _ in range(1000):
            counter.increment()
    
    # 创建多个线程
    threads = [threading.Thread(target=worker) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    # 缺陷：预期10000，但由于竞态条件，实际值可能小于10000
    print(f"Count: {counter.count}")


# ==================== 缺陷10: Path Traversal ====================
def read_user_file(filename: str) -> str:
    """读取用户文件 - 路径遍历漏洞"""
    # 缺陷：未验证文件路径，可能访问任意文件
    base_dir = "/var/www/uploads/"
    filepath = base_dir + filename  # 简单拼接，不安全
    
    # 恶意输入如 "../../etc/passwd" 可以访问系统文件
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return f.read()
    return ""


def test_path_traversal():
    """测试路径遍历"""
    # 缺陷：恶意文件名
    malicious_file = "../../../etc/passwd"
    content = read_user_file(malicious_file)
    print(f"Content: {content[:100]}")


# ==================== 缺陷11: Use After Free (模拟) ====================
class Resource:
    """资源类"""
    def __init__(self, name: str):
        self.name = name
        self.data = [1, 2, 3, 4, 5]
    
    def get_data(self):
        """获取数据"""
        return self.data


def test_use_after_free():
    """测试释放后使用"""
    resource = Resource("test")
    data_ref = resource.data  # 获取引用
    
    # 模拟释放
    resource = None
    
    # 缺陷：继续使用已"释放"的资源
    # 在Python中由于垃圾回收，这通常不会出错，但在C/C++中是严重问题
    print(f"Data: {data_ref}")  # 在Python中仍然有效，但在其他语言可能崩溃


# ==================== 缺陷12: Type Confusion ====================
def process_value(value):
    """处理值 - 类型混淆"""
    # 缺陷：假设value是字符串，但未验证
    return value.upper()  # 如果value不是字符串，AttributeError


def test_type_confusion():
    """测试类型混淆"""
    # 传入错误类型
    result = process_value(12345)  # 缺陷：传入int而非str
    print(f"Result: {result}")


# ==================== 主测试函数 ====================
if __name__ == "__main__":
    print("警告：此文件包含故意植入的缺陷，仅用于测试工具检测能力")
    print("请勿在生产环境中运行！")
    print()
    
    # 注意：这些测试会导致各种错误，仅用于演示
    # 取消注释以运行特定测试
    
    # test_memory_leak()
    # test_null_pointer_dereference()  # TypeError
    # test_division_by_zero()  # ZeroDivisionError
    # test_array_out_of_bounds()  # IndexError
    # test_double_close()
    # test_integer_overflow()
    # test_sql_injection()
    # test_uninitialized_variable()  # NameError
    # test_race_condition()
    # test_path_traversal()
    # test_use_after_free()
    # test_type_confusion()  # AttributeError
    
    print("缺陷代码准备完成，请使用分析工具检测")



















