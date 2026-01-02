#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""运行 Pylint 分析并生成详细报告"""
import subprocess
import sys
import os
import json
from pathlib import Path

def run_pylint_analysis():
    """运行 Pylint 分析"""
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
    
    if not existing_files:
        return {"error": "没有找到要检查的文件"}
    
    # 运行 Pylint 并获取 JSON 输出
    cmd = [sys.executable, '-m', 'pylint'] + existing_files + [
        '--rcfile=.pylintrc',
        '--output-format=json'
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            check=False
        )
        
        # 解析 JSON 输出
        issues = []
        if result.stdout:
            try:
                # Pylint 可能输出多行 JSON，每行一个对象
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        issues.append(json.loads(line))
            except json.JSONDecodeError:
                # 如果不是 JSON 格式，使用文本输出
                return {
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "returncode": result.returncode,
                    "format": "text"
                }
        
        return {
            "issues": issues,
            "stderr": result.stderr,
            "returncode": result.returncode,
            "format": "json"
        }
        
    except Exception as e:
        return {"error": str(e), "exception_type": type(e).__name__}

def generate_report(analysis_result):
    """生成可读的报告"""
    report_lines = []
    report_lines.append("=" * 80)
    report_lines.append("Pylint 代码分析报告")
    report_lines.append("=" * 80)
    report_lines.append("")
    
    if "error" in analysis_result:
        report_lines.append(f"错误: {analysis_result['error']}")
        return "\n".join(report_lines)
    
    if analysis_result.get("format") == "text":
        report_lines.append("文本格式输出:")
        report_lines.append(analysis_result.get("stdout", ""))
        if analysis_result.get("stderr"):
            report_lines.append("\n错误输出:")
            report_lines.append(analysis_result.get("stderr", ""))
        return "\n".join(report_lines)
    
    issues = analysis_result.get("issues", [])
    
    if not issues:
        report_lines.append("✓ 未发现任何问题！代码质量良好。")
        return "\n".join(report_lines)
    
    # 按文件分组
    by_file = {}
    for issue in issues:
        filepath = issue.get('path', 'unknown')
        if filepath not in by_file:
            by_file[filepath] = []
        by_file[filepath].append(issue)
    
    # 统计信息
    total_issues = len(issues)
    by_type = {}
    by_symbol = {}
    
    for issue in issues:
        msg_type = issue.get('type', 'unknown')
        symbol = issue.get('symbol', 'unknown')
        by_type[msg_type] = by_type.get(msg_type, 0) + 1
        by_symbol[symbol] = by_symbol.get(symbol, 0) + 1
    
    report_lines.append(f"总计发现 {total_issues} 个问题\n")
    
    # 问题类型统计
    report_lines.append("问题类型统计:")
    report_lines.append("-" * 80)
    for msg_type, count in sorted(by_type.items(), key=lambda x: -x[1]):
        type_name = {
            'error': '错误',
            'warning': '警告',
            'refactor': '重构建议',
            'convention': '代码规范',
            'info': '信息'
        }.get(msg_type, msg_type)
        report_lines.append(f"  {type_name:15} ({msg_type:10}): {count:4} 个")
    
    # 详细问题列表
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
            
            type_name = {
                'error': '错误',
                'warning': '警告',
                'refactor': '重构',
                'convention': '规范',
                'info': '信息'
            }.get(msg_type, msg_type)
            
            report_lines.append(
                f"  [{type_name:6}] 行 {line:4d}:{col:3d} | {msg_id:6} | {symbol:25} | {message}"
            )
    
    return "\n".join(report_lines)

def main():
    """主函数"""
    # 运行分析
    analysis_result = run_pylint_analysis()
    
    # 生成报告
    report = generate_report(analysis_result)
    
    # 保存报告
    report_file = Path('pylint_report.txt')
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    # 打印报告
    print(report)
    
    # 同时保存 JSON 格式的详细数据
    json_file = Path('pylint_report.json')
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(analysis_result, f, indent=2, ensure_ascii=False)
    
    return 0 if not analysis_result.get("issues") else 1

if __name__ == '__main__':
    sys.exit(main())

