# 实验 5：测试与持续集成 - 使用指南

本目录包含“奶茶点单系统”的自动化测试套件、模糊测试工具以及持续集成配置。

## 📂 目录结构

- `test_unit.py`: **单元测试**。针对 `AuthService` 和 `CartService` 的核心功能测试。
- `test_integration.py`: **集成测试**。模拟从注册到下单的完整业务链路。
- `fuzz_test.py`: **模糊测试**。对系统接口进行随机压力测试，检测健壮性。
- `实验报告.md`: 本次实验的详细技术报告，包含测试用例及修复记录。

---

## 🛠️ 环境准备

在执行测试前，请确保已安装 `pytest` 及其覆盖率插件：

```bash
pip install pytest pytest-cov
```

---

## 🧪 执行测试

所有的测试脚本都需要在 `se_code/code` 目录下运行，以便正确导入模块。请先切换目录：

```bash
cd se_code/code
```

### 1. 运行单元测试 (Unit Testing)
执行以下命令运行所有单元测试：

```bash
# 设置 PYTHONPATH 以确保 pytest 能找到源码
$env:PYTHONPATH = "."
python -m pytest 5/test_unit.py
```

### 2. 运行集成测试 (Integration Testing)
验证多个服务模块之间的协作：

```bash
$env:PYTHONPATH = "."
python -m pytest 5/test_integration.py
```

### 3. 查看测试覆盖率
您可以同时运行所有测试并生成代码覆盖率报告：

```bash
$env:PYTHONPATH = "."
python -m pytest 5/test_unit.py 5/test_integration.py --cov=. --cov-report=term-missing
```

---

## ⚡ 运行模糊测试 (Fuzz Testing)

模糊测试脚本通过随机数据模拟高频并发调用。直接使用 Python 运行：

```bash
$env:PYTHONPATH = "."
python 5/fuzz_test.py
```
*注：该脚本会捕获并打印预期的业务异常（如负数价格拦截），若出现 `Traceback` 属正常拦截现象。*

---

## 🚀 持续集成 (CI)

本项目已配置 GitHub Actions 工作流。配置文件位于根目录的 `.github/workflows/ci.yml`。

**工作流流程：**
1. 自动检测代码推送（Push）或拉取请求（PR）。
2. 在 Ubuntu 环境下安装 Python 3.10。
3. 自动安装依赖并执行全量 `pytest` 测试。
4. 若任何测试失败，CI 状态将显示为红色，提醒开发者修复。

---
**实验完成人**：曹喆 (231220100)
**日期**：2026-01-02

