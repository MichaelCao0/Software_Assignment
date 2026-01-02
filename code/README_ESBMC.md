# ESBMC形式化验证文档索引

## 📚 文档列表

### 1. 快速开始 ⭐ (从这里开始！)
**文件**: `ESBMC快速开始指南.md`

适合：刚接触ESBMC的用户

内容：
- ESBMC介绍
- 安装步骤（WSL/Docker）
- 第一个验证示例
- 常见问题解答

**阅读时间**: 10分钟

---

### 2. 完整分析报告 📊
**文件**: `ESBMC形式化验证报告.md`

适合：需要详细了解验证结果的用户

内容：
- 所有发现的问题（17个）
- 详细的风险评估
- 修复建议和代码示例
- ESBMC原理介绍

**阅读时间**: 30-60分钟

---

### 3. 测试代码 💻
**文件**: `esbmc_verification_tests.py`

适合：需要运行验证或了解测试细节的用户

内容：
- 10大类15个测试函数
- 详细的注释说明
- 每个测试的验证属性
- ESBMC命令示例

**代码行数**: 300+行

---

## 🚀 运行脚本

### Windows批处理脚本

#### `run_esbmc_wsl.bat` (推荐)
使用WSL运行ESBMC验证

**用法**：
```cmd
# 运行所有测试
run_esbmc_wsl.bat

# 运行单个测试
run_esbmc_wsl.bat test_price_calculation_overflow
```

---

#### `run_esbmc_docker.bat`
使用Docker运行ESBMC验证

**用法**：
```cmd
# 运行所有测试
run_esbmc_docker.bat

# 运行单个测试
run_esbmc_docker.bat test_quantity_division_by_zero
```

---

#### `run_esbmc_tests.bat`
Windows原生批处理（需要已安装ESBMC）

**用法**：
```cmd
run_esbmc_tests.bat
```

---

## 📋 快速决策树

```
你想做什么？
│
├─ 我是新手，想快速了解
│  └─► 阅读: ESBMC快速开始指南.md
│
├─ 我想运行验证
│  ├─ 已安装WSL
│  │  └─► 运行: run_esbmc_wsl.bat
│  ├─ 已安装Docker
│  │  └─► 运行: run_esbmc_docker.bat
│  └─ 都没有
│     └─► 阅读: ESBMC快速开始指南.md (安装部分)
│
├─ 我想了解发现了什么问题
│  └─► 阅读: ESBMC形式化验证报告.md
│
└─ 我想了解测试细节
   └─► 查看: esbmc_verification_tests.py
```

---

## 🎯 推荐学习路径

### 路径A: 快速体验（30分钟）
1. ✅ 安装ESBMC（使用WSL）
2. ✅ 运行第一个测试
3. ✅ 查看反例
4. ✅ 尝试修复

**文档顺序**：
1. `ESBMC快速开始指南.md` (安装部分)
2. 运行 `run_esbmc_wsl.bat test_price_calculation_overflow`
3. 查看输出

---

### 路径B: 深入理解（2小时）
1. ✅ 完整阅读快速开始指南
2. ✅ 运行所有基础测试
3. ✅ 阅读完整分析报告
4. ✅ 研究测试代码
5. ✅ 实现修复建议

**文档顺序**：
1. `ESBMC快速开始指南.md` (完整)
2. 运行 `run_esbmc_wsl.bat`
3. `ESBMC形式化验证报告.md` (完整)
4. `esbmc_verification_tests.py` (阅读)

---

### 路径C: 实战应用（半天）
1. ✅ 理解ESBMC原理
2. ✅ 分析所有测试结果
3. ✅ 修改原始代码
4. ✅ 创建新的验证测试
5. ✅ 集成到CI/CD

**文档顺序**：
1. `ESBMC形式化验证报告.md` (第2节：ESBMC工具介绍)
2. 运行所有测试并分析
3. 修改 `models.py` 和 `services.py`
4. 创建自定义测试

---

## 📊 文件关系图

```
ESBMC形式化验证
│
├── 📄 README_ESBMC.md (本文件)
│   └── 索引和导航
│
├── 📘 ESBMC快速开始指南.md
│   ├── 入门教程
│   └── 安装指南
│
├── 📊 ESBMC形式化验证报告.md
│   ├── 完整分析结果
│   ├── 17个问题详解
│   └── 修复建议
│
├── 💻 esbmc_verification_tests.py
│   ├── 15个测试函数
│   └── 验证属性定义
│
├── 🔧 运行脚本
│   ├── run_esbmc_wsl.bat (WSL)
│   ├── run_esbmc_docker.bat (Docker)
│   └── run_esbmc_tests.bat (原生)
│
└── 📦 原始代码
    ├── models.py (被验证)
    ├── services.py (被验证)
    └── ...
```

---

## 🔍 按问题类型查找

### 算术安全问题
- **测试**: `test_price_calculation_overflow`, `test_discount_overflow`
- **报告章节**: 3.1, 3.7
- **风险级别**: 高

### 边界检查问题
- **测试**: `test_quantity_update_bounds`, `test_order_items_bounds_check`
- **报告章节**: 3.2, 3.3
- **风险级别**: 中

### 除零错误
- **测试**: `test_quantity_division_by_zero`
- **报告章节**: 3.2.1
- **风险级别**: 严重

### 业务逻辑问题
- **测试**: `test_order_status_transition`, `test_rating_validation`
- **报告章节**: 3.4, 3.5
- **风险级别**: 高

### 时间逻辑问题
- **测试**: `test_promotion_validity`, `test_time_range_validation`
- **报告章节**: 3.6
- **风险级别**: 中

### 并发安全问题
- **测试**: `test_cart_concurrent_modification`
- **报告章节**: 3.8
- **风险级别**: 高

---

## 📈 验证统计

```
总测试数量: 15个
预期失败: 8个 (发现bug)
预期通过: 7个 (验证正确性)

问题分类:
├── 严重 (Critical): 3个
├── 高 (High): 5个
├── 中 (Medium): 7个
└── 低 (Low): 2个
```

---

## 🛠️ 工具要求

### 最低要求
- **操作系统**: Windows 10/11
- **内存**: 4GB+
- **磁盘**: 10GB+

### 推荐配置
- **操作系统**: Windows 11 + WSL2
- **内存**: 8GB+
- **磁盘**: 20GB+
- **处理器**: 4核心+

---

## ⚡ 快速命令参考

```bash
# 查看版本
esbmc --version

# 运行单个测试
esbmc esbmc_verification_tests.py --function test_name

# 运行并限制时间
esbmc esbmc_verification_tests.py --function test_name --timeout 30

# 多属性验证
esbmc esbmc_verification_tests.py --function test_name --multi-property

# 增加循环展开
esbmc esbmc_verification_tests.py --function test_name --unwind 10

# 使用特定求解器
esbmc esbmc_verification_tests.py --function test_name --z3
esbmc esbmc_verification_tests.py --function test_name --boolector
```

---

## 📞 获取帮助

### 在线资源
- 🌐 [ESBMC官网](https://esbmc.org)
- 💬 [ESBMC GitHub Issues](https://github.com/esbmc/esbmc/issues)
- 📖 [Python Frontend文档](https://github.com/esbmc/esbmc/blob/master/src/python-frontend/README.md)

### 本地文档
- 查看 `esbmc/README.md`
- 查看 `esbmc/BUILDING.md`
- 查看 `esbmc/src/python-frontend/README.md`

---

## ✅ 检查清单

### 开始前
- [ ] 已阅读快速开始指南
- [ ] 已安装WSL或Docker
- [ ] 已安装ESBMC
- [ ] 已验证ESBMC安装（`esbmc --version`）

### 运行验证
- [ ] 已运行基础测试（3个）
- [ ] 已查看测试输出
- [ ] 已理解反例含义
- [ ] 已阅读分析报告

### 实施改进
- [ ] 已识别需要修复的问题
- [ ] 已实施修复
- [ ] 已重新运行验证
- [ ] 已确认问题解决

---

## 🎉 开始使用

**推荐新手第一步**：
```cmd
# 1. 打开此文件所在目录
cd D:\source\course_\CN_EXP\se_code\code

# 2. 阅读快速开始指南
notepad ESBMC快速开始指南.md

# 3. 安装ESBMC（按指南操作）

# 4. 运行第一个测试
run_esbmc_wsl.bat test_price_calculation_overflow
```

**祝你验证顺利！** 🚀

---

**最后更新**: 2025年12月12日  
**维护者**: 软件工程课程团队



















