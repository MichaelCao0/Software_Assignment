# ESBMC快速开始指南

## 🚀 快速导航

1. [什么是ESBMC](#什么是esbmc)
2. [安装ESBMC](#安装esbmc)
3. [运行第一个验证](#运行第一个验证)
4. [查看结果](#查看结果)
5. [常见问题](#常见问题)

---

## 什么是ESBMC？

ESBMC (Efficient SMT-based Context-Bounded Model Checker) 是一个强大的形式化验证工具，可以：

- ✅ 自动检测代码中的bug（除零、溢出、数组越界等）
- ✅ 验证业务逻辑的正确性
- ✅ 探索所有可能的执行路径
- ✅ 生成反例帮助调试

**简单说**：它比普通测试更彻底，能发现隐藏的深层bug！

---

## 安装ESBMC

### 方法1: 使用WSL (推荐 - 最简单) ⭐

#### 步骤1: 安装WSL
```powershell
# 在PowerShell（管理员模式）中运行：
wsl --install -d Ubuntu-22.04
```

安装完成后，**重启电脑**。

#### 步骤2: 在WSL中安装ESBMC
```bash
# 打开WSL终端（搜索"Ubuntu"）
wsl

# 在WSL中运行以下命令：
sudo add-apt-repository ppa:esbmc/esbmc
sudo apt update
sudo apt install esbmc

# 安装Python依赖
pip install ast2json

# 验证安装
esbmc --version
```

#### 步骤3: 测试安装
```bash
# 应该看到版本信息，如：ESBMC version 7.6
```

✅ **完成！** 你现在可以使用ESBMC了。

---

### 方法2: 使用Docker

#### 步骤1: 安装Docker Desktop
从 https://www.docker.com/products/docker-desktop 下载并安装

#### 步骤2: 拉取ESBMC镜像
```powershell
docker pull esbmc/esbmc:latest
```

#### 步骤3: 验证安装
```powershell
docker run esbmc/esbmc:latest esbmc --version
```

✅ **完成！**

---

## 运行第一个验证

### 使用WSL运行

#### 方法A: 使用我们提供的脚本（最简单）
```powershell
# 在code目录下，双击运行：
run_esbmc_wsl.bat

# 或在命令行运行单个测试：
run_esbmc_wsl.bat test_price_calculation_overflow
```

#### 方法B: 手动在WSL中运行
```bash
# 1. 在WSL中导航到代码目录
cd /mnt/d/source/course_/CN_EXP/se_code/code

# 2. 运行测试
esbmc esbmc_verification_tests.py --function test_price_calculation_overflow
```

---

### 使用Docker运行

```powershell
# 在code目录下，双击运行：
run_esbmc_docker.bat

# 或运行单个测试：
run_esbmc_docker.bat test_price_calculation_overflow
```

---

## 查看结果

### 验证通过 ✅
```
VERIFICATION SUCCESSFUL
```
**含义**：代码在这个测试场景下是正确的！

### 验证失败 ❌
```
[Counterexample]

State 1 file esbmc_verification_tests.py line 16
----------------------------------------------------
  base_price = 2147483647
  quantity = 2

Violated property:
  file esbmc_verification_tests.py line 18
  arithmetic overflow on multiply
  !overflow("*", 2147483647, 2)

VERIFICATION FAILED
```

**含义**：找到了一个bug！

**如何解读**：
1. **Counterexample**: 触发bug的具体输入值
2. **State**: 程序执行到哪一行
3. **Violated property**: 违反了什么属性（这里是算术溢出）

---

## 所有可用测试

### 基础测试（推荐从这些开始）

| 测试名称 | 检测内容 | 难度 |
|---------|---------|-----|
| `test_price_calculation_overflow` | 价格计算溢出 | ⭐ |
| `test_quantity_division_by_zero` | 除零错误 | ⭐ |
| `test_rating_validation` | 评分范围检查 | ⭐ |
| `test_subtotal_calculation` | 小计计算正确性 | ⭐⭐ |
| `test_order_items_bounds_check` | 数组越界 | ⭐⭐ |

### 高级测试

| 测试名称 | 检测内容 | 难度 |
|---------|---------|-----|
| `test_order_status_transition` | 状态转换逻辑 | ⭐⭐⭐ |
| `test_promotion_validity` | 时间逻辑验证 | ⭐⭐⭐ |
| `test_discount_overflow` | 折扣计算溢出 | ⭐⭐⭐ |
| `test_cart_concurrent_modification` | 并发安全 | ⭐⭐⭐⭐ |
| `test_order_invariant` | 业务不变量 | ⭐⭐⭐⭐ |

---

## 运行示例

### 示例1: 检测价格溢出

```bash
esbmc esbmc_verification_tests.py --function test_price_calculation_overflow
```

**期望输出**：
```
[Counterexample]
  base_price = 2147483647
  quantity = 2
  
Violated property:
  arithmetic overflow on multiply

VERIFICATION FAILED
```

**解释**：当价格非常大时，乘以数量会导致整数溢出！

---

### 示例2: 检测除零错误

```bash
esbmc esbmc_verification_tests.py --function test_quantity_division_by_zero
```

**期望输出**：
```
[Counterexample]
  total_price = 100
  item_count = 0

Violated property:
  division by zero
  item_count != 0

VERIFICATION FAILED
```

**解释**：当商品数量为0时，计算平均价格会导致除零错误！

---

### 示例3: 检测数组越界

```bash
esbmc esbmc_verification_tests.py --function test_order_items_bounds_check
```

**期望输出**：
```
[Counterexample]
  index = 10
  
Violated property:
  array bounds violated: array 'items' upper bound
  index < 5

VERIFICATION FAILED
```

**解释**：访问超出数组范围的索引会导致错误！

---

## 常用命令参数

```bash
# 基本用法
esbmc file.py --function function_name

# 增加超时时间（秒）
esbmc file.py --function function_name --timeout 60

# 多属性验证（检查所有断言）
esbmc file.py --function function_name --multi-property

# 增加循环展开深度
esbmc file.py --function function_name --unwind 10

# 使用特定求解器
esbmc file.py --function function_name --z3

# 查看详细输出
esbmc file.py --function function_name --show-vcc

# 生成反例轨迹
esbmc file.py --function function_name --no-slice
```

---

## 常见问题

### Q1: ESBMC运行很慢怎么办？

**A**: 
- 使用 `--timeout 30` 限制时间
- 简化测试函数
- 减少循环次数
- 使用更快的求解器（如 `--boolector`）

### Q2: 提示"找不到esbmc命令"？

**A**: 
- 确认已正确安装ESBMC
- 在WSL中运行 `which esbmc` 检查
- 在Docker中使用完整命令

### Q3: Python类型注解错误？

**A**: 
- ESBMC需要类型注解（如 `x: int = 5`）
- 查看 `esbmc_verification_tests.py` 的示例
- 参考ESBMC Python文档

### Q4: 验证失败是代码有bug吗？

**A**: 
不一定！可能是：
- ✅ 真的发现了bug（好事！）
- ⚠️ 测试场景不现实（如价格=21亿）
- ⚠️ 断言太严格
- ⚠️ 需要添加前置条件

### Q5: 如何修复发现的bug？

**A**: 
1. 查看Counterexample找到触发条件
2. 在原代码中添加检查
3. 重新运行验证确认修复

**示例**：
```python
# 修复前
def calculate_average(total, count):
    return total / count  # 可能除零

# 修复后
def calculate_average(total, count):
    if count == 0:
        return 0
    return total / count
```

---

## 下一步

### 1. 运行基础测试
```bash
run_esbmc_wsl.bat test_price_calculation_overflow
run_esbmc_wsl.bat test_quantity_division_by_zero
run_esbmc_wsl.bat test_rating_validation
```

### 2. 阅读完整报告
查看 `ESBMC形式化验证报告.md` 了解所有发现的问题

### 3. 修复问题
根据报告中的修复建议改进代码

### 4. 重新验证
确认修复后问题已解决

---

## 参考资料

### 本项目文档
- 📄 `ESBMC形式化验证报告.md` - 完整分析报告
- 📄 `esbmc_verification_tests.py` - 所有测试代码
- 📄 `run_esbmc_wsl.bat` - WSL运行脚本
- 📄 `run_esbmc_docker.bat` - Docker运行脚本

### 官方资源
- 🌐 [ESBMC官网](https://esbmc.org)
- 📚 [ESBMC GitHub](https://github.com/esbmc/esbmc)
- 📖 [Python Frontend文档](https://github.com/esbmc/esbmc/blob/master/src/python-frontend/README.md)

---

## 快速命令速查表

```bash
# WSL环境
wsl                                    # 进入WSL
cd /mnt/d/source/course_/CN_EXP/se_code/code  # 导航到代码目录
esbmc --version                        # 检查版本
esbmc esbmc_verification_tests.py --function test_name  # 运行测试

# Windows环境
run_esbmc_wsl.bat                      # 运行所有测试
run_esbmc_wsl.bat test_name            # 运行单个测试
run_esbmc_docker.bat test_name         # 使用Docker运行
```

---

## 🎯 开始你的第一次验证！

```bash
# 1. 打开PowerShell或命令提示符
# 2. 导航到代码目录
cd D:\source\course_\CN_EXP\se_code\code

# 3. 运行第一个测试
run_esbmc_wsl.bat test_price_calculation_overflow

# 4. 查看结果并庆祝！🎉
```

祝你验证愉快！如有问题，请查看完整报告或访问ESBMC官网。



















