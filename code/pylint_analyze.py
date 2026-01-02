#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Pylint 缺陷报告分析脚本
解析 JSON 格式的 Pylint 报告并生成整理后的缺陷报告
"""

import json
from collections import defaultdict
from pathlib import Path

def analyze_pylint_report(json_file='pylint_report.json'):
    """分析 Pylint JSON 报告"""
    try:
        with open(json_file, 'rb') as f:
            content = f.read().decode('utf-8', errors='ignore')
            issues = json.loads(content)
    except Exception as e:
        print(f"读取 JSON 文件失败: {e}")
        return None
    
    # 按类型分类
    by_type = defaultdict(list)
    by_file = defaultdict(list)
    by_symbol = defaultdict(int)
    
    for issue in issues:
        issue_type = issue.get('type', 'unknown')
        filepath = issue.get('path', 'unknown')
        symbol = issue.get('symbol', 'unknown')
        
        by_type[issue_type].append(issue)
        by_file[filepath].append(issue)
        by_symbol[symbol] += 1
    
    return {
        'total': len(issues),
        'by_type': dict(by_type),
        'by_file': dict(by_file),
        'by_symbol': dict(by_symbol),
        'all_issues': issues
    }

def generate_report(analysis_result):
    """生成 Markdown 格式的缺陷报告"""
    if not analysis_result:
        return "无法生成报告：分析失败"
    
    lines = []
    lines.append("# Pylint 代码缺陷分析报告\n")
    lines.append("## 1. 总体统计\n")
    lines.append(f"- **总缺陷数**: {analysis_result['total']}\n")
    
    # 按类型统计
    lines.append("\n### 按缺陷类型统计\n")
    type_names = {
        'convention': '代码规范 (C)',
        'refactor': '重构建议 (R)',
        'warning': '警告 (W)',
        'error': '错误 (E)',
        'fatal': '致命错误 (F)'
    }
    
    for issue_type, issues in sorted(analysis_result['by_type'].items()):
        type_name = type_names.get(issue_type, issue_type)
        lines.append(f"- **{type_name}**: {len(issues)} 个\n")
    
    # 按文件统计
    lines.append("\n### 按文件统计\n")
    for filepath, issues in sorted(analysis_result['by_file'].items()):
        lines.append(f"- **{filepath}**: {len(issues)} 个缺陷\n")
    
    # 按缺陷符号统计
    lines.append("\n### 按缺陷类型（符号）统计\n")
    for symbol, count in sorted(analysis_result['by_symbol'].items(), key=lambda x: -x[1]):
        lines.append(f"- **{symbol}**: {count} 个\n")
    
    # 详细缺陷列表
    lines.append("\n## 2. 详细缺陷列表\n")
    
    # 按文件分组显示
    for filepath in sorted(analysis_result['by_file'].keys()):
        issues = analysis_result['by_file'][filepath]
        lines.append(f"\n### 文件: {filepath}\n")
        lines.append(f"**缺陷总数**: {len(issues)}\n")
        lines.append("\n| 行号 | 列号 | 类型 | 缺陷代码 | 描述 |\n")
        lines.append("|------|------|------|----------|------|\n")
        
        for issue in sorted(issues, key=lambda x: x.get('line', 0)):
            line = issue.get('line', 0)
            col = issue.get('column', 0)
            issue_type = issue.get('type', 'unknown')
            symbol = issue.get('symbol', 'unknown')
            message = issue.get('message', '')
            msg_id = issue.get('message-id', '')
            
            lines.append(f"| {line} | {col} | {issue_type} | {msg_id} ({symbol}) | {message} |\n")
    
    # 严重缺陷汇总
    lines.append("\n## 3. 严重缺陷汇总\n")
    
    # 错误和警告
    critical_issues = []
    for issue in analysis_result['all_issues']:
        issue_type = issue.get('type', '')
        if issue_type in ['error', 'warning', 'fatal']:
            critical_issues.append(issue)
        elif issue_type == 'refactor' and issue.get('symbol') in [
            'too-many-positional-arguments',
            'too-many-instance-attributes',
            'too-many-statements',
            'too-many-return-statements',
            'too-many-locals'
        ]:
            critical_issues.append(issue)
    
    if critical_issues:
        lines.append(f"共发现 {len(critical_issues)} 个需要优先处理的缺陷：\n\n")
        for issue in sorted(critical_issues, key=lambda x: (x.get('path', ''), x.get('line', 0))):
            filepath = issue.get('path', 'unknown')
            line = issue.get('line', 0)
            issue_type = issue.get('type', 'unknown')
            symbol = issue.get('symbol', 'unknown')
            message = issue.get('message', '')
            lines.append(f"- **{filepath}:{line}** [{issue_type}] {symbol}: {message}\n")
    else:
        lines.append("未发现严重缺陷。\n")
    
    return ''.join(lines)

if __name__ == '__main__':
    result = analyze_pylint_report()
    if result:
        report = generate_report(result)
        with open('Pylint缺陷报告.md', 'w', encoding='utf-8') as f:
            f.write(report)
        print("缺陷报告已生成: Pylint缺陷报告.md")
        print(f"总缺陷数: {result['total']}")
    else:
        print("生成报告失败")



















