# -*- coding: utf-8 -*-
"""
测试报告生成脚本
解析allure-results目录中的JSON文件，生成HTML报告
无需Java环境
"""
import json
import os
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict


def parse_allure_results(results_dir):
    """解析allure-results目录中的测试结果"""
    test_cases = []
    results_path = Path(results_dir)

    if not results_path.exists():
        return test_cases

    for json_file in results_path.glob("*.json"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if 'name' in data and 'status' in data:
                    test_cases.append(data)
        except:
            continue

    return test_cases


def generate_html_report(test_cases, output_file):
    """生成HTML报告"""
    # 统计数据
    total = len(test_cases)
    passed = sum(1 for t in test_cases if t.get('status') == 'passed')
    failed = sum(1 for t in test_cases if t.get('status') == 'failed')
    skipped = sum(1 for t in test_cases if t.get('status') == 'skipped')
    broken = sum(1 for t in test_cases if t.get('status') == 'broken')
    pass_rate = (passed / total * 100) if total > 0 else 0

    # 按feature分组
    features = defaultdict(list)
    for tc in test_cases:
        labels = tc.get('labels', [])
        feature = 'Other'
        for label in labels:
            if label.get('name') == 'feature':
                feature = label.get('value', 'Other')
                break
        features[feature].append(tc)

    # 生成HTML
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>API自动化测试报告</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 20px; }}
        .header h1 {{ font-size: 28px; margin-bottom: 10px; }}
        .header .subtitle {{ opacity: 0.9; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin-bottom: 20px; }}
        .stat-card {{ background: white; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .stat-card .number {{ font-size: 32px; font-weight: bold; }}
        .stat-card .label {{ color: #666; margin-top: 5px; }}
        .stat-card.passed .number {{ color: #4CAF50; }}
        .stat-card.failed .number {{ color: #f44336; }}
        .stat-card.skipped .number {{ color: #FF9800; }}
        .stat-card.total .number {{ color: #2196F3; }}
        .progress-bar {{ background: #e0e0e0; border-radius: 10px; height: 20px; margin-bottom: 20px; overflow: hidden; }}
        .progress-fill {{ height: 100%; border-radius: 10px; transition: width 0.3s; }}
        .progress-fill.passed {{ background: linear-gradient(90deg, #4CAF50, #8BC34A); }}
        .progress-fill.failed {{ background: linear-gradient(90deg, #f44336, #FF5722); }}
        .feature-section {{ background: white; border-radius: 10px; margin-bottom: 20px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .feature-header {{ padding: 15px 20px; background: #f8f9fa; border-bottom: 1px solid #e0e0e0; cursor: pointer; }}
        .feature-header h3 {{ color: #333; }}
        .feature-header .badge {{ display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 12px; margin-left: 10px; }}
        .badge.passed {{ background: #E8F5E9; color: #2E7D32; }}
        .badge.failed {{ background: #FFEBEE; color: #C62828; }}
        .test-case {{ padding: 15px 20px; border-bottom: 1px solid #f0f0f0; }}
        .test-case:last-child {{ border-bottom: none; }}
        .test-case .name {{ font-weight: 500; margin-bottom: 5px; }}
        .test-case .status {{ display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 12px; }}
        .status.passed {{ background: #E8F5E9; color: #2E7D32; }}
        .status.failed {{ background: #FFEBEE; color: #C62828; }}
        .status.skipped {{ background: #FFF3E0; color: #E65100; }}
        .status.broken {{ background: #FCE4EC; color: #880E4F; }}
        .test-case .duration {{ color: #999; font-size: 12px; }}
        .test-case .error {{ background: #FFF3F3; padding: 10px; border-radius: 5px; margin-top: 10px; font-size: 13px; color: #C62828; }}
        .footer {{ text-align: center; padding: 20px; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>API自动化测试报告</h1>
            <div class="subtitle">生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        </div>

        <div class="stats">
            <div class="stat-card total">
                <div class="number">{total}</div>
                <div class="label">总用例数</div>
            </div>
            <div class="stat-card passed">
                <div class="number">{passed}</div>
                <div class="label">通过</div>
            </div>
            <div class="stat-card failed">
                <div class="number">{failed}</div>
                <div class="label">失败</div>
            </div>
            <div class="stat-card skipped">
                <div class="number">{skipped + broken}</div>
                <div class="label">跳过/异常</div>
            </div>
        </div>

        <div class="progress-bar">
            <div class="progress-fill passed" style="width: {pass_rate}%"></div>
        </div>
        <p style="text-align: center; margin-bottom: 20px;">通过率: {pass_rate:.1f}%</p>
"""

    # 按feature生成测试详情
    for feature, cases in features.items():
        feature_passed = sum(1 for c in cases if c.get('status') == 'passed')
        feature_total = len(cases)

        html += f"""
        <div class="feature-section">
            <div class="feature-header">
                <h3>{feature}
                    <span class="badge passed">{feature_passed}/{feature_total}</span>
                </h3>
            </div>
"""
        for tc in cases:
            status = tc.get('status', 'unknown')
            name = tc.get('name', 'Unknown')
            duration = tc.get('time', {}).get('duration', 0)
            duration_sec = duration / 1000 if duration > 0 else 0

            html += f"""
            <div class="test-case">
                <div class="name">
                    <span class="status {status}">{status.upper()}</span>
                    {name}
                    <span class="duration">{duration_sec:.2f}s</span>
                </div>
"""
            # 如果有失败信息
            if status == 'failed':
                status_details = tc.get('statusDetails', {})
                message = status_details.get('message', '')
                trace = status_details.get('trace', '')
                if message:
                    html += f'<div class="error">{message}</div>'

            html += "</div>"

        html += "</div>"

    html += """
        <div class="footer">
            <p>Powered by Pytest + Allure</p>
        </div>
    </div>
</body>
</html>"""

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

    return output_file


def main():
    root = Path(__file__).parent
    results_dir = root / "artifacts" / "allure-results"
    report_file = root / "artifacts" / "report.html"

    print("=" * 50)
    print("  测试报告生成器 (无需Java)")
    print("=" * 50)

    print(f"\n[1/2] 解析测试结果: {results_dir}")
    test_cases = parse_allure_results(results_dir)
    print(f"      找到 {len(test_cases)} 条测试用例")

    if not test_cases:
        print("\n[!] 未找到测试结果，请先运行测试:")
        print("    python -m pytest tests/ -v --alluredir=artifacts/allure-results")
        return

    print(f"\n[2/2] 生成HTML报告: {report_file}")
    generate_html_report(test_cases, report_file)
    print(f"      报告已生成!")

    # 打开报告（仅 Windows 本地执行，CI/Linux 环境跳过）
    if sys.platform == 'win32':
        os.startfile(report_file)
        print(f"\n[OK] 测试报告已打开")
    else:
        print(f"\n[OK] 测试报告已生成: {report_file}")


if __name__ == "__main__":
    main()