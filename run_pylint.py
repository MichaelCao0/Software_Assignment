#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""运行 Pylint 并生成报告"""
import sys
import os
from io import StringIO

try:
    from pylint import lint
    from pylint.reporters import BaseReporter
except ImportError:
    print("错误: 未安装 pylint，请运行: pip install pylint")
    sys.exit(1)

class CollectingReporter(BaseReporter):
    """收集所有消息的报告器"""
    def __init__(self):
        super().__init__()
        self.messages = []
    
    def handle_message(self, msg):
        """处理消息"""
        self.messages.append({
            'type': msg.category,
            'module': msg.module,
            'obj': msg.obj,
            'line': msg.line,
            'column': msg.column,
            'path': msg.path,
            'symbol': msg.symbol,
            'message': msg.msg,
            'message_id': msg.msg_id
        })
    
    def display_messages(self, layout):
        """显示消息"""
        pass

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
    
    # 创建报告器
    reporter = CollectingReporter()
    
    # 配置参数
    args = existing_files + ['--rcfile=.pylintrc', '--disable=all', '--enable=all']
    
    # 运行 Pylint
    try:
        lint.Run(args, reporter=reporter, exit=False)
    except Exception as e:
        print(f"运行 Pylint 时出错: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # 输出结果
    if reporter.messages:
        print("=" * 80)
        print("Pylint 代码分析报告")
        print("=" * 80)
        print()
        
        # 按文件分组
        by_file = {}
        for msg in reporter.messages:
            filepath = msg['path']
            if filepath not in by_file:
                by_file[filepath] = []
            by_file[filepath].append(msg)
        
        # 输出每个文件的问题
        for filepath, messages in sorted(by_file.items()):
            print(f"\n文件: {filepath}")
            print("-" * 80)
            for msg in messages:
                msg_type = msg['type']
                line = msg['line']
                col = msg['column']
                symbol = msg['symbol']
                message = msg['message']
                msg_id = msg['message_id']
                
                print(f"  {msg_type:8} | 行 {line:4d}:{col:3d} | {msg_id} | {symbol:20} | {message}")
        
        print("\n" + "=" * 80)
        print(f"总计发现 {len(reporter.messages)} 个问题")
        
        # 统计问题类型
        by_type = {}
        for msg in reporter.messages:
            msg_type = msg['type']
            by_type[msg_type] = by_type.get(msg_type, 0) + 1
        
        print("\n问题类型统计:")
        for msg_type, count in sorted(by_type.items()):
            print(f"  {msg_type}: {count}")
    else:
        print("未发现任何问题！")
    
    return len(reporter.messages)

if __name__ == '__main__':
    exit_code = main()
    sys.exit(0 if exit_code == 0 else 1)
