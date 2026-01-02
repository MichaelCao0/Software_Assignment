"""
生成Python代码的AST JSON文件
用于ESBMC Python Frontend的前端处理
"""

import ast
import json
import sys
from pathlib import Path

try:
    import ast2json
except ImportError:
    print("[错误] 未安装 ast2json 模块")
    print("请运行: pip install ast2json")
    sys.exit(1)


def generate_ast_json(python_file: str, output_file: str = None):
    """
    生成Python文件的AST JSON表示
    
    Args:
        python_file: Python源文件路径
        output_file: 输出JSON文件路径（可选）
    """
    # 读取Python源码
    with open(python_file, 'r', encoding='utf-8') as f:
        source_code = f.read()
    
    # 解析为AST
    try:
        tree = ast.parse(source_code, filename=python_file)
    except SyntaxError as e:
        print(f"[错误] 语法错误: {e}")
        return None
    
    # 转换为JSON
    ast_json = ast2json.ast2json(tree)
    
    # 确定输出文件名
    if output_file is None:
        output_file = Path(python_file).stem + "_ast.json"
    
    # 写入JSON文件
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(ast_json, f, indent=2, ensure_ascii=False)
    
    print(f"✓ AST JSON已生成: {output_file}")
    print(f"  - 源文件: {python_file}")
    print(f"  - JSON大小: {len(json.dumps(ast_json))} 字节")
    
    return ast_json


def generate_type_annotated_json(python_file: str, output_file: str = None):
    """
    生成带类型注解的AST JSON
    这是ESBMC的第二个JSON（类型标注后的）
    
    注意: 这里只是简单示例，实际的类型推断由ESBMC内部完成
    """
    # 首先生成基本AST
    ast_json = generate_ast_json(python_file, None)
    
    if ast_json is None:
        return None
    
    # 确定输出文件名
    if output_file is None:
        output_file = Path(python_file).stem + "_typed_ast.json"
    
    # 添加类型信息的占位符（实际类型推断由ESBMC完成）
    typed_ast = {
        "original_ast": ast_json,
        "type_annotations": {
            "note": "实际类型推断由ESBMC内部完成",
            "method": "基于PEP 484类型注解和类型推断"
        }
    }
    
    # 写入JSON文件
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(typed_ast, f, indent=2, ensure_ascii=False)
    
    print(f"✓ 类型标注JSON已生成: {output_file}")
    
    return typed_ast


def analyze_ast_structure(ast_json: dict):
    """分析AST结构"""
    def count_nodes(node, node_type_counts):
        if isinstance(node, dict):
            node_type = node.get('_type', 'Unknown')
            node_type_counts[node_type] = node_type_counts.get(node_type, 0) + 1
            for value in node.values():
                count_nodes(value, node_type_counts)
        elif isinstance(node, list):
            for item in node:
                count_nodes(item, node_type_counts)
    
    node_counts = {}
    count_nodes(ast_json, node_counts)
    
    print("\n📊 AST结构分析:")
    print(f"  - 节点类型总数: {len(node_counts)}")
    print(f"  - 节点总数: {sum(node_counts.values())}")
    print("\n  主要节点类型:")
    for node_type, count in sorted(node_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"    • {node_type}: {count}个")


def batch_generate(file_pattern: str = "*.py"):
    """批量生成JSON文件"""
    from glob import glob
    
    files = glob(file_pattern)
    
    # 排除生成的文件本身
    files = [f for f in files if not f.startswith('generate_ast')]
    
    print(f"找到 {len(files)} 个Python文件")
    print("=" * 60)
    
    for py_file in files:
        print(f"\n处理: {py_file}")
        print("-" * 60)
        try:
            ast_json = generate_ast_json(py_file)
            if ast_json:
                analyze_ast_structure(ast_json)
        except Exception as e:
            print(f"[错误] 处理失败: {e}")


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("=" * 60)
        print("ESBMC AST JSON生成工具")
        print("=" * 60)
        print("\n用法:")
        print("  python generate_ast_json.py <python_file>")
        print("  python generate_ast_json.py --batch [pattern]")
        print("\n示例:")
        print("  # 单个文件")
        print("  python generate_ast_json.py esbmc_verification_tests.py")
        print("\n  # 批量处理")
        print("  python generate_ast_json.py --batch")
        print("  python generate_ast_json.py --batch \"test_*.py\"")
        print("\n输出:")
        print("  • <filename>_ast.json - AST的JSON表示")
        print("  • <filename>_typed_ast.json - 类型标注的JSON")
        print("\n说明:")
        print("  ESBMC Python Frontend工作流程:")
        print("  1. Python源码 → AST → JSON (第一个JSON)")
        print("  2. 类型标注 → 带类型的AST → JSON (第二个JSON)")
        print("  3. 符号表生成 → GOTO程序 → 验证")
        print("=" * 60)
        sys.exit(1)
    
    if sys.argv[1] == '--batch':
        pattern = sys.argv[2] if len(sys.argv) > 2 else "*.py"
        batch_generate(pattern)
    else:
        python_file = sys.argv[1]
        if not Path(python_file).exists():
            print(f"[错误] 文件不存在: {python_file}")
            sys.exit(1)
        
        print("=" * 60)
        print(f"处理文件: {python_file}")
        print("=" * 60)
        
        # 生成两个JSON文件
        ast_json = generate_ast_json(python_file)
        if ast_json:
            analyze_ast_structure(ast_json)
            print("\n" + "=" * 60)
            generate_type_annotated_json(python_file)
            print("=" * 60)
            print("\n✅ 完成！")
            print("\n💡 提示:")
            print("  这些JSON文件展示了ESBMC Python Frontend的中间处理步骤")
            print("  实际使用ESBMC时，这些步骤是自动完成的")


if __name__ == "__main__":
    main()



















