# 餐饮点单系统

基于UML设计实现的餐饮点单系统，采用Python + Tkinter开发。

## 系统架构

采用四层架构设计：
- **领域模型层**（domain/）：核心业务对象
- **仓储层**（repositories/）：数据访问抽象
- **业务服务层**（services/）：业务逻辑处理
- **表现层**（presentation/）：用户界面

## 功能特性

### 顾客端
- 浏览可用菜单
- 商品自定义（口味、份量、加料）
- 购物车管理（添加、删除、修改数量）
- 结算下单

### 管理员端
- 菜单管理（增删改查）
- 商品上下架管理
- 订单列表查看
- 订单状态处理（待处理→制作中→已完成）

## 运行环境

- Python 3.8+
- 无需额外安装第三方包（使用Python内置库）

## 运行方式

```bash
# 进入项目目录
cd restaurant_system

# 运行主程序
python main.py
```

## 目录结构

```
restaurant_system/
├── domain/
│   └── models.py          # 领域模型（MenuItem, Order, Cart等）
├── repositories/
│   └── repository.py      # 仓储接口和内存实现
├── services/
│   └── services.py        # 业务服务（MenuService, OrderService）
├── presentation/
│   └── gui.py             # GUI界面（CustomerGUI, AdminGUI）
├── main.py                # 应用入口
├── requirements.txt       # 依赖说明
└── README.md              # 项目说明
```

## 设计模式

- Repository模式：数据访问抽象
- Service层模式：业务逻辑封装
- 依赖注入：服务依赖仓储接口
- 状态模式：订单状态管理

## 核心类说明

### 领域模型
- `MenuItem`：菜单项
- `CustomizationOption`：自定义选项
- `Cart`：购物车
- `CartItem`：购物车项
- `Order`：订单
- `OrderStatus`：订单状态枚举

### 服务层
- `MenuService`：菜单管理服务
- `OrderService`：订单管理服务

### 仓储层
- `MenuRepository`：菜单仓储接口
- `OrderRepository`：订单仓储接口
- `InMemoryMenuRepo`：内存实现
- `InMemoryOrderRepo`：内存实现

## 使用说明

1. 启动程序后选择"顾客端"或"管理员端"
2. 顾客端可浏览菜单、添加商品到购物车并下单
3. 管理员端可管理菜品、查看和处理订单
4. 系统使用内存存储，重启后数据清空

## 扩展说明

如需持久化存储，可：
1. 实现新的Repository类（如SQLiteMenuRepo）
2. 在main.py中替换InMemoryRepo为数据库实现
3. 无需修改服务层和表现层代码（依赖倒置原则）


