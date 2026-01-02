#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""生成 Pylint 分析报告"""
import sys
import os

# 确保在正确的目录
os.chdir(os.path.dirname(os.path.abspath(__file__)))

try:
    from pylint.lint import Run
    from pylint.reporters import JSONReporter
    from io import StringIO
except ImportError:
    print("错误: 需要安装 pylint")
    print("请运行: pip install pylint")
    sys.exit(1)

def main():
    """主函数"""
    files = ['main.py', 'models.py', 'services.py', 'repositories.py', 
             'gui_customer.py', 'gui_admin.py']
    
    # 检查文件是否存在
    existing_files = [f for f in files if os.path.exists(f)]
    
    if not existing_files:
        print("错误: 没有找到要检查的文件")
        return
    
    # 使用 JSON 报告器
    json_output = StringIO()
    reporter = JSONReporter(json_output)
    
    # 运行 Pylint
    args = existing_files + ['--rcfile=.pylintrc', '--output-format=json']
    
    try:
        Run(args, reporter=reporter, exit=False)
    except SystemExit:
        pass  # Pylint 可能会调用 sys.exit
    
    # 获取 JSON 输出
    json_str = json_output.getvalue()
    
    # 保存 JSON 报告
    with open('pylint_report.json', 'w', encoding='utf-8') as f:
        f.write(json_str)
    
    # 解析并生成文本报告
    import json
    try:
        issues = []
        for line in json_str.strip().split('\n'):
            if line.strip():
                issues.append(json.loads(line))
        
        # 生成文本报告
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("Pylint 代码分析报告")
        report_lines.append("=" * 80)
        report_lines.append("")
        
        if not issues:
            report_lines.append("✓ 未发现任何问题！")
        else:
            # 统计
            by_type = {}
            by_file = {}
            
            for issue in issues:
                msg_type = issue.get('type', 'unknown')
                filepath = issue.get('path', 'unknown')
                
                by_type[msg_type] = by_type.get(msg_type, 0) + 1
                if filepath not in by_file:
                    by_file[filepath] = []
                by_file[filepath].append(issue)
            
            report_lines.append(f"总计发现 {len(issues)} 个问题\n")
            
            # 问题类型统计
            report_lines.append("问题类型统计:")
            report_lines.append("-" * 80)
            type_names = {
                'error': '错误',
                'warning': '警告',
                'refactor': '重构建议',
                'convention': '代码规范',
                'info': '信息'
            }
            for msg_type, count in sorted(by_type.items(), key=lambda x: -x[1]):
                type_name = type_names.get(msg_type, msg_type)
                report_lines.append(f"  {type_name:15} ({msg_type:10}): {count:4} 个")
            
            # 详细列表
            report_lines.append("\n" + "=" * 80)
            report_lines.append("详细问题列表（按文件分组）")
            report_lines.append("=" * 80)
            
            for filepath, file_issues in sorted(by_file.items()):
                report_lines.append(f"\n文件: {filepath}")
                report_lines.append("-" * 80)
                
                for issue in sorted(file_issues, key=lambda x: x.get('line', 0)):
                    msg_type = issue.get('type', 'unknown')
                    line = issue.get('line', 0)
                    col = issue.get('column', 0)
                    symbol = issue.get('symbol', 'unknown')
                    message = issue.get('message', '')
                    msg_id = issue.get('message-id', '')
                    
                    type_name = type_names.get(msg_type, msg_type)
                    report_lines.append(
                        f"  [{type_name:6}] 行 {line:4d}:{col:3d} | {msg_id:6} | {symbol:25} | {message}"
                    )
        
        # 保存文本报告
        report_text = "\n".join(report_lines)
        with open('pylint_report.txt', 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        # 打印报告
        print(report_text)
        
    except json.JSONDecodeError as e:
        print(f"解析 JSON 时出错: {e}")
        print("原始输出:")
        print(json_str[:500])

if __name__ == '__main__':
    main()

