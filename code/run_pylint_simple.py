#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""运行 Pylint 并生成报告"""
import subprocess
import sys
import os

def main():
    """主函数"""
    # 要检查的文件列表
    files_to_check = [
        'main.py',
        'models.py',
        'services.py',
        'repositories.py',
        'gui_customer.py',
        'gui_admin.py'
    ]
    
    # 检查文件是否存在
    existing_files = []
    for f in files_to_check:
        if os.path.exists(f):
            existing_files.append(f)
        else:
            print(f"警告: 文件 {f} 不存在", file=sys.stderr)
    
    if not existing_files:
        print("错误: 没有找到要检查的文件", file=sys.stderr)
        sys.exit(1)
    
    # 构建命令
    cmd = [sys.executable, '-m', 'pylint'] + existing_files + ['--rcfile=.pylintrc']
    
    # 运行命令
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            check=False
        )
        
        # 将输出写入文件
        with open('pylint_report.txt', 'w', encoding='utf-8') as f:
            f.write("STDOUT:\n")
            f.write(result.stdout)
            f.write("\n\nSTDERR:\n")
            f.write(result.stderr)
            f.write(f"\n\n返回码: {result.returncode}\n")
        
        # 同时打印到控制台
        print("STDOUT:")
        print(result.stdout)
        if result.stderr:
            print("\nSTDERR:")
            print(result.stderr)
        print(f"\n返回码: {result.returncode}")
        
        return result.returncode
        
    except Exception as e:
        error_msg = f"运行 Pylint 时出错: {e}"
        print(error_msg, file=sys.stderr)
        with open('pylint_report.txt', 'w', encoding='utf-8') as f:
            f.write(error_msg)
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())

