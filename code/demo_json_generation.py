"""
演示ESBMC的两个JSON生成过程
简化版示例，帮助理解ESBMC Python Frontend的工作原理
"""

import ast
import json
from typing import Dict, Any


def demo_json1_ast_generation():
    """
    演示 JSON 1: AST JSON 的生成
    这是ESBMC处理Python代码的第一步
    """
    print("=" * 70)
    print("JSON 1: AST (抽象语法树) JSON生成演示")
    print("=" * 70)
    print()
    
    # 示例Python代码
    source_code = '''
def calculate_price(base: int, quantity: int) -> int:
    """计算总价"""
    total: int = base * quantity
    assert total >= 0, "Price must be non-negative"
    return total

# 测试
price: int = calculate_price(15, 2)
assert price == 30
'''
    
    print("原始Python代码:")
    print("-" * 70)
    print(source_code)
    print("-" * 70)
    print()
    
    # 解析为AST
    tree = ast.parse(source_code)
    
    print("AST结构（简化表示）:")
    print("-" * 70)
    print(ast.dump(tree, indent=2)[:500] + "...")
    print("-" * 70)
    print()
    
    # 手动构建JSON表示（简化版）
    ast_json = {
        "_type": "Module",
        "body": [
            {
                "_type": "FunctionDef",
                "name": "calculate_price",
                "line": 2,
                "args": {
                    "_type": "arguments",
                    "args": [
                        {"arg": "base", "annotation": "int"},
                        {"arg": "quantity", "annotation": "int"}
                    ]
                },
                "returns": "int",
                "body": [
                    {
                        "_type": "AnnAssign",
                        "target": "total",
                        "annotation": "int",
                        "value": {"_type": "BinOp", "op": "Mult"}
                    },
                    {
                        "_type": "Assert",
                        "test": {"_type": "Compare", "op": "GtE"}
                    },
                    {
                        "_type": "Return",
                        "value": "total"
                    }
                ]
            }
        ]
    }
    
    print("AST JSON表示（简化版）:")
    print("-" * 70)
    print(json.dumps(ast_json, indent=2, ensure_ascii=False))
    print("-" * 70)
    print()
    
    print("✓ JSON 1 说明:")
    print("  • 保留了代码的完整结构")
    print("  • 包含了类型注解信息 (base: int)")
    print("  • 记录了每个节点的类型 (_type字段)")
    print("  • 这是ESBMC类型推断的输入")
    print()
    
    return ast_json


def demo_json2_type_annotation():
    """
    演示 JSON 2: 类型标注JSON
    这是ESBMC在AST基础上添加类型信息的过程
    """
    print()
    print("=" * 70)
    print("JSON 2: 类型标注JSON演示")
    print("=" * 70)
    print()
    
    print("类型推断过程:")
    print("-" * 70)
    
    # 示例：从显式注解推断
    print("1. 显式类型注解:")
    print("   代码: x: int = 5")
    print("   推断: x的类型是int（来自注解）")
    print()
    
    print("2. 常量类型推断:")
    print("   代码: y = 10")
    print("   推断: y的类型是int（从字面量10推断）")
    print()
    
    print("3. 表达式类型推断:")
    print("   代码: z = x + y")
    print("   推断: z的类型是int（因为x和y都是int）")
    print()
    
    print("4. 函数返回类型:")
    print("   代码: def foo(x: int) -> int: return x * 2")
    print("   推断: foo返回int（显式注解）")
    print("         x * 2的类型是int（int * int = int）")
    print()
    print("-" * 70)
    print()
    
    # 类型标注后的JSON（概念性示例）
    typed_ast_json = {
        "_type": "Module",
        "body": [
            {
                "_type": "FunctionDef",
                "name": "calculate_price",
                "line": 2,
                "return_type": {
                    "inferred": "int",
                    "source": "annotation"
                },
                "args": [
                    {
                        "arg": "base",
                        "type": {
                            "name": "int",
                            "source": "annotation",
                            "size": 32,  # bits
                            "signed": True
                        }
                    },
                    {
                        "arg": "quantity",
                        "type": {
                            "name": "int",
                            "source": "annotation",
                            "size": 32,
                            "signed": True
                        }
                    }
                ],
                "body": [
                    {
                        "_type": "AnnAssign",
                        "target": {
                            "name": "total",
                            "type": {
                                "name": "int",
                                "source": "annotation"
                            }
                        },
                        "value": {
                            "_type": "BinOp",
                            "op": "Mult",
                            "left_type": "int",
                            "right_type": "int",
                            "result_type": "int",
                            "overflow_check": True  # ESBMC会检查溢出
                        }
                    },
                    {
                        "_type": "Assert",
                        "test": {
                            "_type": "Compare",
                            "op": "GtE",
                            "left_type": "int",
                            "right_type": "int",
                            "result_type": "bool"
                        },
                        "property": "user_assertion"
                    },
                    {
                        "_type": "Return",
                        "value": {
                            "name": "total",
                            "type": "int"
                        }
                    }
                ]
            }
        ],
        "type_inference_info": {
            "method": "PEP 484 + automatic inference",
            "total_variables": 3,
            "explicitly_typed": 3,
            "inferred": 0
        }
    }
    
    print("类型标注JSON（概念性示例）:")
    print("-" * 70)
    print(json.dumps(typed_ast_json, indent=2, ensure_ascii=False))
    print("-" * 70)
    print()
    
    print("✓ JSON 2 说明:")
    print("  • 每个变量都有明确的类型信息")
    print("  • 每个表达式的类型都已推断")
    print("  • 标记了需要检查的属性（如溢出检查）")
    print("  • 这是符号执行的输入")
    print()
    
    return typed_ast_json


def demo_verification_properties():
    """
    演示ESBMC如何从类型信息生成验证属性
    """
    print()
    print("=" * 70)
    print("从类型信息到验证属性")
    print("=" * 70)
    print()
    
    examples = [
        {
            "code": "total: int = base * quantity",
            "type_info": "int * int -> int",
            "properties": [
                "算术溢出检查: !(base * quantity > INT_MAX)",
                "算术下溢检查: !(base * quantity < INT_MIN)"
            ]
        },
        {
            "code": "average: int = total // count",
            "type_info": "int // int -> int",
            "properties": [
                "除零检查: count != 0"
            ]
        },
        {
            "code": "items[index]",
            "type_info": "list[int], index: int",
            "properties": [
                "数组上界: index < len(items)",
                "数组下界: index >= 0"
            ]
        },
        {
            "code": "assert rating >= 1 and rating <= 5",
            "type_info": "bool",
            "properties": [
                "用户断言: rating >= 1 && rating <= 5"
            ]
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"示例 {i}:")
        print(f"  代码: {example['code']}")
        print(f"  类型: {example['type_info']}")
        print(f"  生成的验证属性:")
        for prop in example['properties']:
            print(f"    - {prop}")
        print()
    
    print("-" * 70)
    print()


def demo_comparison():
    """
    对比有无类型注解的区别
    """
    print()
    print("=" * 70)
    print("有类型注解 vs 无类型注解")
    print("=" * 70)
    print()
    
    print("示例1: 有类型注解 ✓ 推荐")
    print("-" * 70)
    code_typed = '''
def calculate(x: int, y: int) -> int:
    result: int = x + y
    return result
'''
    print(code_typed)
    print("优点:")
    print("  ✓ ESBMC可以精确验证")
    print("  ✓ 可以检查整数溢出")
    print("  ✓ 可以生成更强的验证属性")
    print("  ✓ 类型信息明确")
    print()
    
    print("示例2: 无类型注解 ⚠ 不推荐")
    print("-" * 70)
    code_untyped = '''
def calculate(x, y):
    result = x + y
    return result
'''
    print(code_untyped)
    print("缺点:")
    print("  ⚠ ESBMC只能进行有限的类型推断")
    print("  ⚠ 可能假设为float类型")
    print("  ⚠ 验证精度降低")
    print("  ⚠ 难以检查类型相关的错误")
    print()
    
    print("建议:")
    print("  → 始终使用类型注解（PEP 484）")
    print("  → 特别是函数参数和返回值")
    print("  → 关键变量也应该添加类型注解")
    print()


def main():
    """主演示函数"""
    print()
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 20 + "ESBMC Python Frontend" + " " * 27 + "║")
    print("║" + " " * 22 + "两个JSON演示程序" + " " * 28 + "║")
    print("╚" + "═" * 68 + "╝")
    print()
    
    print("这个演示程序展示ESBMC如何处理Python代码：")
    print("  第1步: Python源码 → AST → JSON 1")
    print("  第2步: 类型推断 → 带类型的AST → JSON 2")
    print("  第3步: JSON 2 → 符号表 → GOTO程序 → 验证")
    print()
    input("按Enter键开始演示...")
    
    # 演示JSON 1
    ast_json = demo_json1_ast_generation()
    input("\n按Enter键继续...")
    
    # 演示JSON 2
    typed_json = demo_json2_type_annotation()
    input("\n按Enter键继续...")
    
    # 演示验证属性
    demo_verification_properties()
    input("\n按Enter键继续...")
    
    # 对比说明
    demo_comparison()
    
    print()
    print("=" * 70)
    print("演示完成！")
    print("=" * 70)
    print()
    print("实际使用时:")
    print("  • 安装: pip install ast2json")
    print("  • 生成: python generate_ast_json.py your_code.py")
    print("  • 验证: esbmc your_code.py --function test_function")
    print()
    print("注意:")
    print("  • 这两个JSON在ESBMC内部自动生成")
    print("  • 通常不需要手动生成")
    print("  • generate_ast_json.py用于学习和调试")
    print()
    print("相关文档:")
    print("  • ESBMC_JSON处理说明.md - 详细说明")
    print("  • ESBMC形式化验证报告.md - 完整报告")
    print("  • ESBMC快速开始指南.md - 使用指南")
    print()


if __name__ == "__main__":
    main()



















