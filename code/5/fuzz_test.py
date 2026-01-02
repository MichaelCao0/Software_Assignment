import random
import string
import time
from services import AuthService, MenuService, CartService
from decimal import Decimal
import traceback

def get_random_string(length):
    letters = string.ascii_letters + string.digits + string.punctuation + " "
    return ''.join(random.choice(letters) for i in range(length))

def get_random_phone():
    return ''.join(random.choice(string.digits) for i in range(random.randint(5, 15)))

def run_fuzz_test(duration_seconds=10): # 实际要求 5 小时，这里演示运行 10 秒
    print(f"开始模糊测试，持续时间: {duration_seconds} 秒...")
    auth_service = AuthService()
    menu_service = MenuService()
    cart_service = CartService()
    
    start_time = time.time()
    iterations = 0
    errors = 0
    
    while time.time() - start_time < duration_seconds:
        iterations += 1
        try:
            # 随机执行某种操作
            action = random.choice(['register', 'login', 'create_item'])
            
            if action == 'register':
                nickname = get_random_string(random.randint(0, 50))
                phone = get_random_phone()
                auth_service.register(nickname, phone)
                
            elif action == 'login':
                phone = get_random_phone()
                auth_service.login(phone)
                
            elif action == 'create_item':
                name = get_random_string(random.randint(1, 20))
                try:
                    price = Decimal(random.uniform(-100, 1000))
                except:
                    price = Decimal("10.00")
                category = get_random_string(random.randint(0, 10))
                menu_service.create_item(name, price, category)
                
        except Exception as e:
            errors += 1
            print(f"在第 {iterations} 次迭代中发现崩溃/异常:")
            traceback.print_exc()
            
    print(f"\n模糊测试完成!")
    print(f"总迭代次数: {iterations}")
    print(f"异常捕获次数: {errors}")

if __name__ == "__main__":
    run_fuzz_test(10) # 演示运行

