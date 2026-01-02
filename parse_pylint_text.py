#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
解析 Pylint 文本报告并生成整理后的缺陷报告
"""

import re
from collections import defaultdict

def parse_pylint_text_report(text_file='pylint_report.txt'):
    """解析 Pylint 文本格式报告"""
    issues = []
    current_module = None
    
    with open(text_file, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            # 匹配模块行: ************* Module module_name
            module_match = re.match(r'\*{13} Module (.+)', line)
            if module_match:
                current_module = module_match.group(1)
                continue
            
            # 匹配缺陷行: file.py:line:col: CODE: message (symbol)
            # 例如: main.py:18:0: C0303: Trailing whitespace (trailing-whitespace)
            # 或者: main.py:18:0: C0303: Trailing whitespace
            issue_match = re.match(r'([^:]+):(\d+):(\d+):\s+([A-Z]\d+):\s+(.+?)(?:\s+\(([^)]+)\))?$', line)
            if issue_match:
                filepath = issue_match.group(1)
                line_num = int(issue_match.group(2))
                col_num = int(issue_match.group(3))
                msg_id = issue_match.group(4)
                message = issue_match.group(5)
                symbol = issue_match.group(6) if issue_match.group(6) else msg_id.lower().replace(':', '-')
                
                # 确定类型
                issue_type = 'unknown'
                if msg_id.startswith('C'):
                    issue_type = 'convention'
                elif msg_id.startswith('R'):
                    issue_type = 'refactor'
                elif msg_id.startswith('W'):
                    issue_type = 'warning'
                elif msg_id.startswith('E'):
                    issue_type = 'error'
                elif msg_id.startswith('F'):
                    issue_type = 'fatal'
                
                issues.append({
                    'filepath': filepath,
                    'line': line_num,
                    'column': col_num,
                    'type': issue_type,
                    'message_id': msg_id,
                    'symbol': symbol,
                    'message': message,
                    'module': current_module
                })
    
    return issues

def generate_markdown_report(issues):
    """生成 Markdown 格式的缺陷报告"""
    if not issues:
        return "# Pylint 代码缺陷分析报告\n\n未发现任何缺陷。\n"
    
    # 统计信息
    by_type = defaultdict(list)
    by_file = defaultdict(list)
    by_symbol = defaultdict(int)
    
    for issue in issues:
        by_type[issue['type']].append(issue)
        by_file[issue['filepath']].append(issue)
        by_symbol[issue['symbol']] += 1
    
    lines = []
    lines.append("# Pylint 代码缺陷分析报告\n")
    lines.append("\n## 1. 总体统计\n")
    lines.append(f"- **总缺陷数**: {len(issues)}\n")
    lines.append(f"- **涉及文件数**: {len(by_file)}\n")
    
    # 按类型统计
    lines.append("\n### 按缺陷类型统计\n")
    type_names = {
        'convention': '代码规范 (C)',
        'refactor': '重构建议 (R)',
        'warning': '警告 (W)',
        'error': '错误 (E)',
        'fatal': '致命错误 (F)'
    }
    
    for issue_type in ['convention', 'refactor', 'warning', 'error', 'fatal']:
        if issue_type in by_type:
            type_name = type_names.get(issue_type, issue_type)
            count = len(by_type[issue_type])
            percentage = (count / len(issues)) * 100
            lines.append(f"- **{type_name}**: {count} 个 ({percentage:.1f}%)\n")
    
    # 按文件统计
    lines.append("\n### 按文件统计\n")
    for filepath in sorted(by_file.keys()):
        count = len(by_file[filepath])
        lines.append(f"- **{filepath}**: {count} 个缺陷\n")
    
    # 按缺陷符号统计（Top 20）
    lines.append("\n### 按缺陷类型（符号）统计（Top 20）\n")
    lines.append("| 缺陷类型 | 数量 | 占比 |\n")
    lines.append("|---------|------|------|\n")
    for symbol, count in sorted(by_symbol.items(), key=lambda x: -x[1])[:20]:
        percentage = (count / len(issues)) * 100
        lines.append(f"| {symbol} | {count} | {percentage:.1f}% |\n")
    
    # 详细缺陷列表（按文件）
    lines.append("\n## 2. 详细缺陷列表（按文件分组）\n")
    
    for filepath in sorted(by_file.keys()):
        file_issues = by_file[filepath]
        lines.append(f"\n### 文件: {filepath}\n")
        lines.append(f"**缺陷总数**: {len(file_issues)}\n")
        lines.append("\n| 行号 | 列号 | 类型 | 缺陷代码 | 缺陷类型 | 描述 |\n")
        lines.append("|------|------|------|----------|----------|------|\n")
        
        for issue in sorted(file_issues, key=lambda x: x['line']):
            lines.append(f"| {issue['line']} | {issue['column']} | {issue['type']} | "
                        f"{issue['message_id']} | {issue['symbol']} | {issue['message']} |\n")
    
    # 严重缺陷汇总
    lines.append("\n## 3. 需要优先处理的缺陷\n")
    
    critical_issues = []
    for issue in issues:
        issue_type = issue['type']
        symbol = issue['symbol']
        if issue_type in ['error', 'fatal']:
            critical_issues.append(issue)
        elif issue_type == 'warning' and symbol in [
            'broad-exception-caught',
            'attribute-defined-outside-init',
            'unused-variable',
            'unused-import'
        ]:
            critical_issues.append(issue)
        elif issue_type == 'refactor' and symbol in [
            'too-many-positional-arguments',
            'too-many-instance-attributes',
            'too-many-statements',
            'too-many-return-statements',
            'too-many-locals'
        ]:
            critical_issues.append(issue)
    
    if critical_issues:
        lines.append(f"共发现 **{len(critical_issues)}** 个需要优先处理的缺陷：\n\n")
        for issue in sorted(critical_issues, key=lambda x: (x['filepath'], x['line'])):
            lines.append(f"- **{issue['filepath']}:{issue['line']}** "
                        f"[{issue['type']}] `{issue['symbol']}`: {issue['message']}\n")
    else:
        lines.append("未发现需要优先处理的严重缺陷。\n")
    
    # 代码质量评分说明
    lines.append("\n## 4. 代码质量评分\n")
    lines.append("根据 Pylint 的评分标准：\n")
    lines.append("- **10.0/10**: 完美代码\n")
    lines.append("- **8.0-9.9/10**: 优秀代码\n")
    lines.append("- **6.0-7.9/10**: 良好代码（当前评分：**6.64/10**）\n")
    lines.append("- **4.0-5.9/10**: 需要改进\n")
    lines.append("- **<4.0/10**: 需要大量重构\n")
    
    lines.append("\n## 5. 修复建议\n")
    lines.append("### 高优先级修复项：\n")
    lines.append("1. **移除未使用的导入**：清理所有 `unused-import` 警告\n")
    lines.append("2. **修复属性定义位置**：将属性定义移到 `__init__` 方法中\n")
    lines.append("3. **减少函数参数数量**：重构参数过多的函数，考虑使用数据类或配置对象\n")
    lines.append("4. **修复异常捕获**：使用更具体的异常类型而不是通用的 `Exception`\n")
    lines.append("\n### 中优先级修复项：\n")
    lines.append("1. **移除尾随空白**：清理所有 `trailing-whitespace` 问题（可使用编辑器自动修复）\n")
    lines.append("2. **移除未使用的变量**：清理所有 `unused-variable` 警告\n")
    lines.append("3. **优化代码结构**：减少 `too-many-instance-attributes` 和 `too-many-statements` 问题\n")
    lines.append("\n### 低优先级修复项：\n")
    lines.append("1. **统一代码格式**：修复 `trailing-newlines` 问题\n")
    lines.append("2. **优化导入位置**：将函数内的导入移到文件顶部\n")
    
    return ''.join(lines)

if __name__ == '__main__':
    print("正在解析 Pylint 文本报告...")
    issues = parse_pylint_text_report()
    print(f"解析完成，共发现 {len(issues)} 个缺陷")
    
    print("正在生成 Markdown 报告...")
    report = generate_markdown_report(issues)
    
    output_file = 'Pylint缺陷报告.md'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"缺陷报告已生成: {output_file}")

