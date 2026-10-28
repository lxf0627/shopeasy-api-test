#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Allure HTML 报告生成器

从 allure-results 目录读取 JSON 数据，生成独立的 HTML 测试报告。
无需 Java 环境，纯 Python 实现。

用法:
    python generate_report.py
    python generate_report.py --input reports/allure-results --output reports/allure-report
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from html import escape


# ==================== 数据解析 ====================


def parse_allure_results(results_dir: str) -> dict:
    """
    解析 allure-results 目录中的 JSON 文件

    Args:
        results_dir: allure-results 目录路径

    Returns:
        dict: 包含测试用例列表和容器信息的字典
    """
    results_path = Path(results_dir)
    if not results_path.exists():
        print(f"[ERROR] 目录不存在: {results_dir}")
        sys.exit(1)

    test_results = []
    containers = {}

    for json_file in results_path.glob("*.json"):
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            filename = json_file.name

            # 区分 result 文件和 container 文件
            if filename.endswith("-result.json"):
                test_results.append(data)
            elif filename.endswith("-container.json"):
                uid = filename.replace("-container.json", "")
                containers[uid] = data
        except (json.JSONDecodeError, IOError) as e:
            print(f"[WARN] 跳过文件 {json_file}: {e}")

    return {"results": test_results, "containers": containers}


def build_test_cases(raw_data: dict) -> list:
    """
    构建结构化的测试用例列表

    Args:
        raw_data: parse_allure_results 返回的原始数据

    Returns:
        list: 结构化的测试用例字典列表
    """
    results = raw_data["results"]
    test_cases = []

    for r in results:
        # 提取标签信息
        labels = {l["name"]: l["value"] for l in r.get("labels", [])}

        # 提取步骤
        steps = extract_steps(r.get("steps", []))

        # 计算持续时间
        start = r.get("start", 0)
        stop = r.get("stop", 0)
        duration_ms = stop - start if stop and start else 0

        case = {
            "name": r.get("name", "未命名"),
            "title": r.get("name", "未命名"),
            "status": r.get("status", "unknown"),
            "description": (r.get("description") or "").strip(),
            "steps": steps,
            "duration_ms": duration_ms,
            "duration_str": format_duration(duration_ms),
            "start_time": format_timestamp(start),
            "epic": labels.get("epic", ""),
            "feature": labels.get("feature", ""),
            "story": labels.get("story", ""),
            "severity": labels.get("severity", "normal"),
            "tags": [v for k, v in labels.items() if k == "tag"],
            "suite": labels.get("suite", ""),
            "sub_suite": labels.get("subSuite", ""),
            "parent_suite": labels.get("parentSuite", ""),
            "full_name": r.get("fullName", ""),
            "host": labels.get("host", ""),
            "framework": labels.get("framework", ""),
            "history_id": r.get("historyId", ""),
            "attachments": r.get("attachments", []),
            "status_message": r.get("statusMessage", ""),
            "status_trace": r.get("statusTrace", ""),
        }
        test_cases.append(case)

    return test_cases


def extract_steps(steps_data: list) -> list:
    """递归提取测试步骤"""
    steps = []
    for s in steps_data:
        step = {
            "name": s.get("name", ""),
            "status": s.get("status", "unknown"),
            "duration_ms": (s.get("stop", 0) or 0) - (s.get("start", 0) or 0),
            "parameters": s.get("parameters", []),
        }
        # 递归处理子步骤
        sub_steps = s.get("steps", [])
        if sub_steps:
            step["children"] = extract_steps(sub_steps)
        else:
            step["children"] = []
        steps.append(step)
    return steps


# ==================== 统计计算 ====================


def calculate_statistics(test_cases: list) -> dict:
    """
    计算测试统计数据

    Args:
        test_cases: 结构化的测试用例列表

    Returns:
        dict: 统计信息字典
    """
    total = len(test_cases)
    passed = sum(1 for t in test_cases if t["status"] == "passed")
    failed = sum(1 for t in test_cases if t["status"] == "failed")
    broken = sum(1 for t in test_cases if t["status"] == "broken")
    skipped = sum(1 for t in test_cases if t["status"] == "skipped")
    unknown = total - passed - failed - broken - skipped

    total_duration = sum(t["duration_ms"] for t in test_cases)

    # 按 epic 分组统计
    epic_stats = {}
    for t in test_cases:
        epic = t["epic"] or "未分类"
        if epic not in epic_stats:
            epic_stats[epic] = {"total": 0, "passed": 0, "failed": 0, "broken": 0, "skipped": 0}
        epic_stats[epic]["total"] += 1
        status = t["status"]
        if status in epic_stats[epic]:
            epic_stats[epic][status] += 1

    # 按 severity 分组统计
    severity_stats = {}
    for t in test_cases:
        sev = t["severity"] or "normal"
        if sev not in severity_stats:
            severity_stats[sev] = {"total": 0, "passed": 0, "failed": 0, "broken": 0, "skipped": 0}
        severity_stats[sev]["total"] += 1
        status = t["status"]
        if status in severity_stats[sev]:
            severity_stats[sev][status] += 1

    # 按 feature 分组
    feature_groups = {}
    for t in test_cases:
        key = f"{t['epic'] or '未分类'} > {t['feature'] or '未分类'}"
        if key not in feature_groups:
            feature_groups[key] = []
        feature_groups[key].append(t)

    pass_rate = (passed / total * 100) if total > 0 else 0

    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "broken": broken,
        "skipped": skipped,
        "unknown": unknown,
        "pass_rate": round(pass_rate, 1),
        "total_duration_ms": total_duration,
        "total_duration_str": format_duration(total_duration),
        "epic_stats": epic_stats,
        "severity_stats": severity_stats,
        "feature_groups": feature_groups,
    }


# ==================== 工具函数 ====================


def format_duration(ms: int) -> str:
    """格式化持续时间"""
    if ms < 1000:
        return f"{ms}ms"
    elif ms < 60000:
        return f"{ms / 1000:.1f}s"
    else:
        minutes = ms // 60000
        seconds = (ms % 60000) / 1000
        return f"{minutes}m {seconds:.1f}s"


def format_timestamp(ts: int) -> str:
    """格式化时间戳"""
    if not ts:
        return ""
    try:
        dt = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, OSError):
        return ""


def status_label(status: str) -> str:
    """状态中文标签"""
    mapping = {
        "passed": "通过",
        "failed": "失败",
        "broken": "异常",
        "skipped": "跳过",
        "unknown": "未知",
    }
    return mapping.get(status, status)


def severity_label(severity: str) -> str:
    """严重级别中文标签"""
    mapping = {
        "blocker": "阻塞",
        "critical": "严重",
        "normal": "一般",
        "minor": "次要",
        "trivial": "轻微",
    }
    return mapping.get(severity, severity)


# ==================== HTML 模板 ====================


def generate_html_report(test_cases: list, stats: dict, output_dir: str) -> str:
    """
    生成 HTML 测试报告

    Args:
        test_cases: 结构化的测试用例列表
        stats: 统计信息
        output_dir: 输出目录

    Returns:
        str: 生成的 HTML 文件路径
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 构建测试用例 HTML 行
    test_rows_html = build_test_rows(test_cases)

    # 构建 Epic 分组 HTML
    epic_sections_html = build_epic_sections(stats["epic_stats"])

    # 构建 Feature 分组 HTML
    feature_sections_html = build_feature_sections(stats["feature_groups"])

    # 构建 Severity 表格 HTML
    severity_table_html = build_severity_table(stats["severity_stats"])

    # Chart.js 数据
    chart_data = json.dumps({
        "passed": stats["passed"],
        "failed": stats["failed"],
        "broken": stats["broken"],
        "skipped": stats["skipped"],
    })

    severity_chart_data = json.dumps({
        k: v["total"] for k, v in stats["severity_stats"].items()
    })

    epic_chart_data = json.dumps({
        k: v for k, v in stats["epic_stats"].items()
    })

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ShopEasy 自动化测试报告</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        :root {{
            --color-passed: #52c41a;
            --color-failed: #ff4d4f;
            --color-broken: #fa8c16;
            --color-skipped: #d9d9d9;
            --color-unknown: #bfbfbf;
            --color-bg: #f5f7fa;
            --color-card: #ffffff;
            --color-border: #e8e8e8;
            --color-text: #333333;
            --color-text-secondary: #666666;
            --color-primary: #1890ff;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: var(--color-bg);
            color: var(--color-text);
            line-height: 1.6;
        }}

        /* 头部 */
        .header {{
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            color: white;
            padding: 24px 32px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
        }}

        .header h1 {{
            font-size: 22px;
            font-weight: 600;
        }}

        .header .meta {{
            font-size: 13px;
            opacity: 0.85;
        }}

        /* 导航标签 */
        .nav-tabs {{
            display: flex;
            background: white;
            border-bottom: 2px solid var(--color-border);
            padding: 0 32px;
            position: sticky;
            top: 0;
            z-index: 100;
            box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
        }}

        .nav-tab {{
            padding: 12px 24px;
            cursor: pointer;
            border-bottom: 3px solid transparent;
            font-size: 14px;
            font-weight: 500;
            color: var(--color-text-secondary);
            transition: all 0.2s;
            user-select: none;
        }}

        .nav-tab:hover {{
            color: var(--color-primary);
            background: #f0f5ff;
        }}

        .nav-tab.active {{
            color: var(--color-primary);
            border-bottom-color: var(--color-primary);
        }}

        /* 主体 */
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 24px 32px;
        }}

        .tab-content {{
            display: none;
        }}

        .tab-content.active {{
            display: block;
        }}

        /* 概览卡片 */
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }}

        .stat-card {{
            background: var(--color-card);
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
            border: 1px solid var(--color-border);
            transition: transform 0.2s;
        }}

        .stat-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }}

        .stat-card .number {{
            font-size: 36px;
            font-weight: 700;
            line-height: 1.2;
        }}

        .stat-card .label {{
            font-size: 14px;
            color: var(--color-text-secondary);
            margin-top: 4px;
        }}

        .stat-card.passed .number {{ color: var(--color-passed); }}
        .stat-card.failed .number {{ color: var(--color-failed); }}
        .stat-card.broken .number {{ color: var(--color-broken); }}
        .stat-card.skipped .number {{ color: var(--color-skipped); }}
        .stat-card.total .number {{ color: var(--color-primary); }}
        .stat-card.rate .number {{ color: {('#52c41a' if stats['pass_rate'] >= 90 else '#fa8c16' if stats['pass_rate'] >= 70 else '#ff4d4f')}; }}

        /* 图表区 */
        .charts-row {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 24px;
            margin-bottom: 24px;
        }}

        .chart-card {{
            background: var(--color-card);
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
            border: 1px solid var(--color-border);
        }}

        .chart-card h3 {{
            font-size: 16px;
            margin-bottom: 16px;
            color: var(--color-text);
        }}

        .chart-container {{
            position: relative;
            width: 100%;
            max-height: 300px;
        }}

        /* 进度条 */
        .progress-bar {{
            width: 100%;
            height: 24px;
            background: #f0f0f0;
            border-radius: 12px;
            overflow: hidden;
            display: flex;
            margin-bottom: 24px;
        }}

        .progress-segment {{
            height: 100%;
            transition: width 0.5s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 11px;
            font-weight: 600;
            color: white;
            min-width: 0;
        }}

        .progress-segment.passed {{ background: var(--color-passed); }}
        .progress-segment.failed {{ background: var(--color-failed); }}
        .progress-segment.broken {{ background: var(--color-broken); }}
        .progress-segment.skipped {{ background: var(--color-skipped); }}

        /* 表格 */
        .table-wrapper {{
            background: var(--color-card);
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
            border: 1px solid var(--color-border);
            margin-bottom: 24px;
        }}

        .table-header {{
            padding: 16px 20px;
            font-size: 16px;
            font-weight: 600;
            border-bottom: 1px solid var(--color-border);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
        }}

        th {{
            background: #fafafa;
            padding: 12px 16px;
            text-align: left;
            font-size: 13px;
            font-weight: 600;
            color: var(--color-text-secondary);
            border-bottom: 1px solid var(--color-border);
            white-space: nowrap;
        }}

        td {{
            padding: 12px 16px;
            font-size: 13px;
            border-bottom: 1px solid #f0f0f0;
            vertical-align: top;
        }}

        tr:hover {{
            background: #fafafa;
        }}

        tr.expandable {{
            cursor: pointer;
        }}

        /* 状态标签 */
        .status-badge {{
            display: inline-block;
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
        }}

        .status-badge.passed {{ background: #f6ffed; color: var(--color-passed); border: 1px solid #b7eb8f; }}
        .status-badge.failed {{ background: #fff2f0; color: var(--color-failed); border: 1px solid #ffccc7; }}
        .status-badge.broken {{ background: #fff7e6; color: var(--color-broken); border: 1px solid #ffd591; }}
        .status-badge.skipped {{ background: #fafafa; color: #999; border: 1px solid #d9d9d9; }}
        .status-badge.unknown {{ background: #fafafa; color: #999; border: 1px solid #d9d9d9; }}

        /* 严重级别 */
        .severity-badge {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 500;
        }}

        .severity-badge.blocker {{ background: #ff4d4f; color: white; }}
        .severity-badge.critical {{ background: #fa541c; color: white; }}
        .severity-badge.normal {{ background: #1890ff; color: white; }}
        .severity-badge.minor {{ background: #52c41a; color: white; }}
        .severity-badge.trivial {{ background: #d9d9d9; color: #666; }}

        /* 步骤展开区 */
        .steps-container {{
            display: none;
            padding: 0 16px 16px;
            background: #fafafa;
        }}

        .steps-container.open {{
            display: table-row;
        }}

        .step-item {{
            padding: 8px 16px;
            border-left: 3px solid var(--color-border);
            margin: 4px 0;
            font-size: 13px;
            background: white;
            border-radius: 0 4px 4px 0;
        }}

        .step-item.passed {{ border-left-color: var(--color-passed); }}
        .step-item.failed {{ border-left-color: var(--color-failed); }}
        .step-item.broken {{ border-left-color: var(--color-broken); }}

        .step-item .step-status {{
            font-weight: 600;
            margin-right: 8px;
        }}

        .step-item .step-status.passed {{ color: var(--color-passed); }}
        .step-item .step-status.failed {{ color: var(--color-failed); }}
        .step-item .step-status.broken {{ color: var(--color-broken); }}

        .step-children {{
            margin-left: 20px;
        }}

        /* 错误信息 */
        .error-info {{
            background: #fff2f0;
            border: 1px solid #ffccc7;
            border-radius: 6px;
            padding: 12px 16px;
            margin-top: 8px;
            font-size: 12px;
            font-family: 'Consolas', 'Monaco', monospace;
            white-space: pre-wrap;
            word-break: break-all;
            color: var(--color-failed);
            max-height: 200px;
            overflow-y: auto;
        }}

        /* 筛选区 */
        .filter-bar {{
            display: flex;
            gap: 12px;
            margin-bottom: 16px;
            flex-wrap: wrap;
            align-items: center;
        }}

        .filter-bar input, .filter-bar select {{
            padding: 8px 12px;
            border: 1px solid var(--color-border);
            border-radius: 6px;
            font-size: 13px;
            outline: none;
            transition: border-color 0.2s;
        }}

        .filter-bar input:focus, .filter-bar select:focus {{
            border-color: var(--color-primary);
            box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
        }}

        .filter-bar input {{
            width: 280px;
        }}

        .btn-filter {{
            padding: 8px 16px;
            border: 1px solid var(--color-border);
            border-radius: 6px;
            background: white;
            cursor: pointer;
            font-size: 13px;
            transition: all 0.2s;
        }}

        .btn-filter:hover {{ background: #f0f5ff; border-color: var(--color-primary); color: var(--color-primary); }}
        .btn-filter.active {{ background: var(--color-primary); color: white; border-color: var(--color-primary); }}

        /* Epic / Feature 卡片 */
        .group-card {{
            background: var(--color-card);
            border-radius: 8px;
            margin-bottom: 16px;
            box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
            border: 1px solid var(--color-border);
            overflow: hidden;
        }}

        .group-card-header {{
            padding: 14px 20px;
            font-weight: 600;
            font-size: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            cursor: pointer;
            background: #fafafa;
            border-bottom: 1px solid var(--color-border);
        }}

        .group-card-header:hover {{
            background: #f0f5ff;
        }}

        .group-card-body {{
            padding: 0;
        }}

        .group-mini-stats {{
            display: flex;
            gap: 12px;
            font-size: 12px;
        }}

        .group-mini-stats span {{
            padding: 2px 8px;
            border-radius: 10px;
        }}

        /* 响应式 */
        @media (max-width: 768px) {{
            .header {{ flex-direction: column; gap: 8px; }}
            .charts-row {{ grid-template-columns: 1fr; }}
            .stats-grid {{ grid-template-columns: repeat(2, 1fr); }}
            .container {{ padding: 16px; }}
            .filter-bar input {{ width: 100%; }}
        }}

        /* 展开/折叠箭头 */
        .expand-icon {{
            transition: transform 0.2s;
            display: inline-block;
            margin-right: 8px;
        }}

        .expand-icon.open {{
            transform: rotate(90deg);
        }}

        /* 无数据提示 */
        .no-data {{
            text-align: center;
            padding: 40px;
            color: var(--color-text-secondary);
            font-size: 14px;
        }}

        /* 搜索高亮 */
        mark {{
            background: #fff3cd;
            padding: 0 2px;
            border-radius: 2px;
        }}

        /* 页脚 */
        .footer {{
            text-align: center;
            padding: 20px;
            color: var(--color-text-secondary);
            font-size: 12px;
            border-top: 1px solid var(--color-border);
            margin-top: 40px;
        }}
    </style>
</head>
<body>

<!-- 头部 -->
<div class="header">
    <h1> ShopEasy 自动化测试报告</h1>
    <div class="meta">
        <div>生成时间: {now}</div>
        <div>总耗时: {stats['total_duration_str']} | 主机: {test_cases[0]['host'] if test_cases else 'N/A'}</div>
    </div>
</div>

<!-- 导航标签 -->
<div class="nav-tabs">
    <div class="nav-tab active" onclick="switchTab('overview')"> 概览</div>
    <div class="nav-tab" onclick="switchTab('suites')"> 按模块</div>
    <div class="nav-tab" onclick="switchTab('behaviors')"> 按行为</div>
    <div class="nav-tab" onclick="switchTab('all-tests')"> 全部用例</div>
</div>

<div class="container">

<!-- ==================== 概览 Tab ==================== -->
<div id="tab-overview" class="tab-content active">

    <!-- 统计卡片 -->
    <div class="stats-grid">
        <div class="stat-card total">
            <div class="number">{stats['total']}</div>
            <div class="label">用例总数</div>
        </div>
        <div class="stat-card passed">
            <div class="number">{stats['passed']}</div>
            <div class="label">通过</div>
        </div>
        <div class="stat-card failed">
            <div class="number">{stats['failed']}</div>
            <div class="label">失败</div>
        </div>
        <div class="stat-card broken">
            <div class="number">{stats['broken']}</div>
            <div class="label">异常</div>
        </div>
        <div class="stat-card skipped">
            <div class="number">{stats['skipped']}</div>
            <div class="label">跳过</div>
        </div>
        <div class="stat-card rate">
            <div class="number">{stats['pass_rate']}%</div>
            <div class="label">通过率</div>
        </div>
    </div>

    <!-- 通过率进度条 -->
    <div class="progress-bar">
        {"" if stats['passed'] == 0 else f'<div class="progress-segment passed" style="width:{stats["passed"]/stats["total"]*100:.1f}%">{stats["passed"]}</div>'}
        {"" if stats['failed'] == 0 else f'<div class="progress-segment failed" style="width:{stats["failed"]/stats["total"]*100:.1f}%">{stats["failed"]}</div>'}
        {"" if stats['broken'] == 0 else f'<div class="progress-segment broken" style="width:{stats["broken"]/stats["total"]*100:.1f}%">{stats["broken"]}</div>'}
        {"" if stats['skipped'] == 0 else f'<div class="progress-segment skipped" style="width:{stats["skipped"]/stats["total"]*100:.1f}%">{stats["skipped"]}</div>'}
    </div>

    <!-- 图表区 -->
    <div class="charts-row">
        <div class="chart-card">
            <h3>用例状态分布</h3>
            <div class="chart-container">
                <canvas id="statusChart"></canvas>
            </div>
        </div>
        <div class="chart-card">
            <h3>严重级别分布</h3>
            <div class="chart-container">
                <canvas id="severityChart"></canvas>
            </div>
        </div>
    </div>

    <!-- 严重级别统计表 -->
    {severity_table_html}

    <!-- Epic 统计表 -->
    {epic_sections_html}

</div>

<!-- ==================== 按模块 Tab ==================== -->
<div id="tab-suites" class="tab-content">
    <h2 style="margin-bottom:16px;">按模块（Suite）分组</h2>
    {feature_sections_html}
</div>

<!-- ==================== 按行为 Tab ==================== -->
<div id="tab-behaviors" class="tab-content">
    <h2 style="margin-bottom:16px;">按行为（Epic / Feature / Story）分组</h2>
    {build_behavior_tree(test_cases)}
</div>

<!-- ==================== 全部用例 Tab ==================== -->
<div id="tab-all-tests" class="tab-content">

    <!-- 筛选栏 -->
    <div class="filter-bar">
        <input type="text" id="searchInput" placeholder=" 搜索用例名称..." oninput="filterTests()">
        <select id="statusFilter" onchange="filterTests()">
            <option value="">全部状态</option>
            <option value="passed">通过</option>
            <option value="failed">失败</option>
            <option value="broken">异常</option>
            <option value="skipped">跳过</option>
        </select>
        <select id="severityFilter" onchange="filterTests()">
            <option value="">全部级别</option>
            <option value="blocker">阻塞</option>
            <option value="critical">严重</option>
            <option value="normal">一般</option>
            <option value="minor">次要</option>
            <option value="trivial">轻微</option>
        </select>
        <button class="btn-filter" onclick="clearFilters()">清除筛选</button>
    </div>

    <!-- 测试用例表格 -->
    <div class="table-wrapper">
        <table id="testTable">
            <thead>
                <tr>
                    <th style="width:40px;"></th>
                    <th>用例名称</th>
                    <th>状态</th>
                    <th>级别</th>
                    <th>Epic</th>
                    <th>Feature</th>
                    <th>Story</th>
                    <th>耗时</th>
                    <th>开始时间</th>
                </tr>
            </thead>
            <tbody>
                {test_rows_html}
            </tbody>
        </table>
    </div>
</div>

</div>

<!-- 页脚 -->
<div class="footer">
    ShopEasy 自动化测试报告 · 由 Allure 数据生成 · {now}
</div>

<script>
// ==================== Tab 切换 ====================
function switchTab(tabName) {{
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
    document.getElementById('tab-' + tabName).classList.add('active');
    event.target.classList.add('active');
}}

// ==================== 展开/折叠步骤 ====================
function toggleSteps(id) {{
    const container = document.getElementById('steps-' + id);
    const icon = document.getElementById('icon-' + id);
    if (container.style.display === 'none' || container.style.display === '') {{
        container.style.display = 'table-row';
        icon.classList.add('open');
    }} else {{
        container.style.display = 'none';
        icon.classList.remove('open');
    }}
}}

// ==================== 展开/折叠分组 ====================
function toggleGroup(id) {{
    const body = document.getElementById('group-' + id);
    const icon = document.getElementById('group-icon-' + id);
    if (body.style.display === 'none' || body.style.display === '') {{
        body.style.display = 'block';
        icon.classList.add('open');
    }} else {{
        body.style.display = 'none';
        icon.classList.remove('open');
    }}
}}

// ==================== 筛选 ====================
function filterTests() {{
    const search = document.getElementById('searchInput').value.toLowerCase();
    const statusFilter = document.getElementById('statusFilter').value;
    const severityFilter = document.getElementById('severityFilter').value;

    const rows = document.querySelectorAll('#testTable tbody tr[data-name]');
    rows.forEach(row => {{
        const name = (row.dataset.name || '').toLowerCase();
        const status = row.dataset.status || '';
        const severity = row.dataset.severity || '';
        const epic = (row.dataset.epic || '').toLowerCase();
        const feature = (row.dataset.feature || '').toLowerCase();
        const story = (row.dataset.story || '').toLowerCase();

        const matchSearch = !search || name.includes(search) || epic.includes(search) || feature.includes(search) || story.includes(search);
        const matchStatus = !statusFilter || status === statusFilter;
        const matchSeverity = !severityFilter || severity === severityFilter;

        // 同时控制步骤行
        const stepsRow = document.getElementById('steps-' + row.dataset.id);
        if (matchSearch && matchStatus && matchSeverity) {{
            row.style.display = '';
            if (stepsRow) stepsRow.style.display = 'none';
        }} else {{
            row.style.display = 'none';
            if (stepsRow) stepsRow.style.display = 'none';
        }}
    }});
}}

function clearFilters() {{
    document.getElementById('searchInput').value = '';
    document.getElementById('statusFilter').value = '';
    document.getElementById('severityFilter').value = '';
    filterTests();
}}

// ==================== 图表 ====================
const chartData = {chart_data};
const severityData = {severity_chart_data};

// 状态分布饼图
new Chart(document.getElementById('statusChart'), {{
    type: 'doughnut',
    data: {{
        labels: ['通过', '失败', '异常', '跳过'],
        datasets: [{{
            data: [chartData.passed, chartData.failed, chartData.broken, chartData.skipped],
            backgroundColor: ['#52c41a', '#ff4d4f', '#fa8c16', '#d9d9d9'],
            borderWidth: 2,
            borderColor: '#ffffff'
        }}]
    }},
    options: {{
        responsive: true,
        maintainAspectRatio: true,
        plugins: {{
            legend: {{
                position: 'bottom',
                labels: {{ padding: 16, font: {{ size: 13 }} }}
            }}
        }}
    }}
}});

// 严重级别柱状图
const sevLabels = Object.keys(severityData).map(k => {{
    const map = {{'blocker':'阻塞','critical':'严重','normal':'一般','minor':'次要','trivial':'轻微'}};
    return map[k] || k;
}});
const sevColors = Object.keys(severityData).map(k => {{
    const map = {{'blocker':'#ff4d4f','critical':'#fa541c','normal':'#1890ff','minor':'#52c41a','trivial':'#d9d9d9'}};
    return map[k] || '#1890ff';
}});

new Chart(document.getElementById('severityChart'), {{
    type: 'bar',
    data: {{
        labels: sevLabels,
        datasets: [{{
            label: '用例数',
            data: Object.values(severityData),
            backgroundColor: sevColors,
            borderRadius: 6,
            maxBarThickness: 60
        }}]
    }},
    options: {{
        responsive: true,
        maintainAspectRatio: true,
        plugins: {{ legend: {{ display: false }} }},
        scales: {{
            y: {{ beginAtZero: true, ticks: {{ stepSize: 1 }} }}
        }}
    }}
}});
</script>

</body>
</html>"""

    # 确保输出目录存在
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    html_file = output_path / "report.html"
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html)

    return str(html_file)


# ==================== HTML 片段构建 ====================


def build_test_rows(test_cases: list) -> str:
    """构建测试用例表格行"""
    rows = []
    for i, t in enumerate(test_cases):
        status = t["status"]
        severity = t["severity"]
        name_esc = escape(t["name"])
        epic_esc = escape(t["epic"])
        feature_esc = escape(t["feature"])
        story_esc = escape(t["story"])
        desc_esc = escape(t["description"])

        # 标签数据（用于筛选）
        data_attrs = (
            f'data-id="{i}" data-name="{name_esc}" data-status="{status}" '
            f'data-severity="{severity}" data-epic="{epic_esc}" '
            f'data-feature="{feature_esc}" data-story="{story_esc}"'
        )

        row = f"""
                <tr class="expandable" {data_attrs} onclick="toggleSteps({i})">
                    <td><span id="icon-{i}" class="expand-icon">&#9654;</span></td>
                    <td>
                        <strong>{name_esc}</strong>
                        {f'<div style="font-size:11px;color:#999;margin-top:2px;">{desc_esc[:80]}{"..." if len(desc_esc)>80 else ""}</div>' if t['description'] else ''}
                    </td>
                    <td><span class="status-badge {status}">{status_label(status)}</span></td>
                    <td><span class="severity-badge {severity}">{severity_label(severity)}</span></td>
                    <td>{epic_esc}</td>
                    <td>{feature_esc}</td>
                    <td>{story_esc}</td>
                    <td>{t['duration_str']}</td>
                    <td>{t['start_time']}</td>
                </tr>
                <tr id="steps-{i}" style="display:none;">
                    <td colspan="9" style="padding:0;">
                        <div style="padding:16px 20px;background:#fafafa;">
                            <h4 style="margin-bottom:12px;font-size:14px;">测试步骤</h4>
                            {build_step_html(t['steps'], 0)}
                            {build_error_html(t)}
                        </div>
                    </td>
                </tr>"""
        rows.append(row)

    return "\n".join(rows) if rows else '<tr><td colspan="9" class="no-data">暂无测试用例数据</td></tr>'


def build_step_html(steps: list, depth: int) -> str:
    """递归构建步骤 HTML"""
    if not steps:
        return ""

    html_parts = []
    for s in steps:
        status = s["status"]
        status_icon = {"passed": "✓", "failed": "✗", "broken": "⚠", "skipped": "○"}.get(status, "?")
        name_esc = escape(s["name"])
        duration = format_duration(s["duration_ms"])
        indent = depth * 20

        html_parts.append(
            f'<div class="step-item {status}" style="margin-left:{indent}px;">'
            f'<span class="step-status {status}">{status_icon}</span> {name_esc}'
            f' <span style="color:#999;font-size:11px;">({duration})</span>'
            f'</div>'
        )

        # 递归子步骤
        if s.get("children"):
            html_parts.append(f'<div class="step-children" style="margin-left:{indent}px;">')
            html_parts.append(build_step_html(s["children"], depth + 1))
            html_parts.append('</div>')

    return "\n".join(html_parts)


def build_error_html(test_case: dict) -> str:
    """构建错误信息 HTML"""
    parts = []
    if test_case.get("status_message"):
        parts.append(f'<h4 style="margin:12px 0 8px;font-size:14px;color:var(--color-failed);">错误信息</h4>')
        parts.append(f'<div class="error-info">{escape(test_case["status_message"])}</div>')
    if test_case.get("status_trace"):
        parts.append(f'<div class="error-info">{escape(test_case["status_trace"][:2000])}</div>')
    return "\n".join(parts)


def build_epic_sections(epic_stats: dict) -> str:
    """构建 Epic 统计表格"""
    if not epic_stats:
        return ""

    rows = []
    for epic, s in epic_stats.items():
        rate = (s["passed"] / s["total"] * 100) if s["total"] else 0
        rows.append(f"""
                <tr>
                    <td><strong>{escape(epic)}</strong></td>
                    <td>{s['total']}</td>
                    <td style="color:var(--color-passed);">{s['passed']}</td>
                    <td style="color:var(--color-failed);">{s['failed']}</td>
                    <td style="color:var(--color-broken);">{s['broken']}</td>
                    <td>{s['skipped']}</td>
                    <td>{rate:.1f}%</td>
                </tr>""")

    return f"""
    <div class="table-wrapper">
        <div class="table-header"> Epic 模块统计</div>
        <table>
            <thead>
                <tr>
                    <th>Epic</th><th>总数</th><th>通过</th><th>失败</th><th>异常</th><th>跳过</th><th>通过率</th>
                </tr>
            </thead>
            <tbody>{"".join(rows)}</tbody>
        </table>
    </div>"""


def build_severity_table(severity_stats: dict) -> str:
    """构建严重级别统计表"""
    if not severity_stats:
        return ""

    rows = []
    order = ["blocker", "critical", "normal", "minor", "trivial"]
    for sev in order:
        if sev not in severity_stats:
            continue
        s = severity_stats[sev]
        rate = (s["passed"] / s["total"] * 100) if s["total"] else 0
        rows.append(f"""
                <tr>
                    <td><span class="severity-badge {sev}">{severity_label(sev)}</span></td>
                    <td>{s['total']}</td>
                    <td style="color:var(--color-passed);">{s['passed']}</td>
                    <td style="color:var(--color-failed);">{s['failed']}</td>
                    <td style="color:var(--color-broken);">{s['broken']}</td>
                    <td>{s['skipped']}</td>
                    <td>{rate:.1f}%</td>
                </tr>""")

    return f"""
    <div class="table-wrapper">
        <div class="table-header"> 严重级别统计</div>
        <table>
            <thead>
                <tr>
                    <th>级别</th><th>总数</th><th>通过</th><th>失败</th><th>异常</th><th>跳过</th><th>通过率</th>
                </tr>
            </thead>
            <tbody>{"".join(rows)}</tbody>
        </table>
    </div>"""


def build_feature_sections(feature_groups: dict) -> str:
    """构建 Feature 分组 HTML"""
    sections = []
    for idx, (feature, cases) in enumerate(feature_groups.items()):
        passed = sum(1 for c in cases if c["status"] == "passed")
        failed = sum(1 for c in cases if c["status"] == "failed")
        broken = sum(1 for c in cases if c["status"] == "broken")
        total = len(cases)
        pass_rate = (passed / total * 100) if total else 0

        case_rows = []
        for c in cases:
            case_rows.append(f"""
                    <tr>
                        <td>{escape(c['name'])}</td>
                        <td><span class="status-badge {c['status']}">{status_label(c['status'])}</span></td>
                        <td><span class="severity-badge {c['severity']}">{severity_label(c['severity'])}</span></td>
                        <td>{c['duration_str']}</td>
                    </tr>""")

        sections.append(f"""
        <div class="group-card">
            <div class="group-card-header" onclick="toggleGroup('f-{idx}')">
                <div>
                    <span id="group-icon-f-{idx}" class="expand-icon">&#9654;</span>
                    {escape(feature)}
                </div>
                <div class="group-mini-stats">
                    <span style="background:#f6ffed;color:var(--color-passed);">通过 {passed}</span>
                    <span style="background:#fff2f0;color:var(--color-failed);">失败 {failed}</span>
                    <span style="background:#fff7e6;color:var(--color-broken);">异常 {broken}</span>
                    <span style="background:#e6f7ff;color:var(--color-primary);">通过率 {pass_rate:.0f}%</span>
                </div>
            </div>
            <div id="group-f-{idx}" class="group-card-body" style="display:none;">
                <table>
                    <thead><tr><th>用例名称</th><th>状态</th><th>级别</th><th>耗时</th></tr></thead>
                    <tbody>{"".join(case_rows)}</tbody>
                </table>
            </div>
        </div>""")

    return "\n".join(sections) if sections else '<div class="no-data">暂无模块数据</div>'


def build_behavior_tree(test_cases: list) -> str:
    """构建行为树（Epic > Feature > Story）"""
    # 按 epic > feature > story 分组
    tree = {}
    for t in test_cases:
        epic = t["epic"] or "未分类"
        feature = t["feature"] or "未分类"
        story = t["story"] or "未分类"
        tree.setdefault(epic, {}).setdefault(feature, {}).setdefault(story, []).append(t)

    sections = []
    idx = 0
    for epic, features in tree.items():
        epic_cases = [c for feats in features.values() for stories in feats.values() for c in stories]
        epic_passed = sum(1 for c in epic_cases if c["status"] == "passed")
        epic_total = len(epic_cases)

        feature_html = []
        for feature, stories in features.items():
            story_html = []
            for story, cases in stories.items():
                case_items = []
                for c in cases:
                    case_items.append(
                        f'<div class="step-item {c["status"]}">'
                        f'<span class="step-status {c["status"]}">'
                        f'{"✓" if c["status"]=="passed" else "✗" if c["status"]=="failed" else "⚠" if c["status"]=="broken" else "○"}'
                        f'</span> {escape(c["name"])} '
                        f'<span style="color:#999;font-size:11px;">({c["duration_str"]})</span>'
                        f'</div>'
                    )
                story_html.append(
                    f'<div style="margin:8px 0 4px 16px;font-weight:500;font-size:13px;color:#555;">'
                    f'{escape(story)} ({len(cases)})</div>'
                    + "\n".join(case_items)
                )
            feature_html.append(
                f'<div style="margin:12px 0;">'
                f'<div style="font-weight:600;font-size:14px;padding:8px 0;">{escape(feature)}</div>'
                + "\n".join(story_html)
                + '</div>'
            )

        sections.append(f"""
        <div class="group-card">
            <div class="group-card-header" onclick="toggleGroup('b-{idx}')">
                <div>
                    <span id="group-icon-b-{idx}" class="expand-icon">&#9654;</span>
                    {escape(epic)}
                </div>
                <div class="group-mini-stats">
                    <span style="background:#e6f7ff;color:var(--color-primary);">{epic_passed}/{epic_total} 通过</span>
                </div>
            </div>
            <div id="group-b-{idx}" class="group-card-body" style="display:none;padding:16px;">
                {"".join(feature_html)}
            </div>
        </div>""")
        idx += 1

    return "\n".join(sections) if sections else '<div class="no-data">暂无行为数据</div>'


# ==================== 主入口 ====================


def main():
    parser = argparse.ArgumentParser(description="Allure HTML 测试报告生成器")
    parser.add_argument(
        "--input", "-i",
        default="reports/allure-results",
        help="allure-results 目录路径 (默认: reports/allure-results)"
    )
    parser.add_argument(
        "--output", "-o",
        default="reports/allure-report",
        help="HTML 报告输出目录 (默认: reports/allure-report)"
    )
    parser.add_argument(
        "--open", "-b",
        action="store_true",
        default=False,
        help="生成后自动在浏览器中打开报告"
    )

    args = parser.parse_args()

    print(f"[INFO] 正在解析测试结果: {args.input}")

    # 解析数据
    raw_data = parse_allure_results(args.input)
    test_cases = build_test_cases(raw_data)

    if not test_cases:
        print("[WARN] 未找到测试结果数据")
        sys.exit(0)

    # 计算统计
    stats = calculate_statistics(test_cases)

    print(f"[INFO] 共 {stats['total']} 个用例: "
          f"通过 {stats['passed']}, 失败 {stats['failed']}, "
          f"异常 {stats['broken']}, 跳过 {stats['skipped']}")
    print(f"[INFO] 通过率: {stats['pass_rate']}%, 总耗时: {stats['total_duration_str']}")

    # 生成 HTML 报告
    html_file = generate_html_report(test_cases, stats, args.output)
    print(f"[OK] 报告已生成: {html_file}")

    # 自动打开浏览器
    if args.open:
        import webbrowser
        webbrowser.open(f"file://{os.path.abspath(html_file)}")


if __name__ == "__main__":
    main()
