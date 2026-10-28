# -*- coding: utf-8 -*-
"""
API自动化测试执行脚本
执行测试并生成报告（无需Java）
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path
from generate_report import parse_allure_results, generate_html_report


def run_command(cmd, desc):
    """执行命令并打印结果"""
    print(f"\n{'='*50}")
    print(f"  {desc}")
    print(f"{'='*50}")
    result = subprocess.run(cmd, shell=True, capture_output=False)
    return result.returncode == 0


def main():
    # 项目根目录
    root = Path(__file__).parent
    os.chdir(root)

    # 目录路径
    allure_results = root / "artifacts" / "allure-results"
    html_report = root / "artifacts" / "report.html"

    print("""
    ================================================
        API自动化测试执行脚本
        Pytest + Requests + Allure
    ================================================
    """)

    # 步骤1: 清理旧报告
    print("[1/3] 清理旧报告...")
    if allure_results.exists():
        shutil.rmtree(allure_results)
    if html_report.exists():
        html_report.unlink()
    allure_results.mkdir(parents=True, exist_ok=True)

    # 步骤2: 执行测试
    print("\n[2/3] 执行测试用例...")
    test_cmd = f'python -m pytest tests/ -v --alluredir={allure_results}'
    tests_passed = run_command(test_cmd, "执行pytest测试")

    # 步骤3: 生成报告（无论测试通过与否都生成，便于失败排查）
    print("\n[3/3] 生成测试报告...")
    test_cases = parse_allure_results(allure_results)

    if test_cases:
        generate_html_report(test_cases, html_report)
        print(f"\n[OK] 报告已生成: {html_report}")

        # 统计
        total = len(test_cases)
        passed = sum(1 for t in test_cases if t.get('status') == 'passed')
        failed = sum(1 for t in test_cases if t.get('status') == 'failed')
        print(f"\n     总计: {total} | 通过: {passed} | 失败: {failed}")

        # 打开报告（仅 Windows 本地执行，CI/Linux 环境跳过）
        if sys.platform == 'win32':
            os.startfile(html_report)
    else:
        print("\n[X] 未找到测试结果")

    if not tests_passed:
        print("\n[X] 测试执行失败！")
        sys.exit(1)

    print(f"""
    ================================================
      测试执行完成！
    ================================================
    """)


if __name__ == "__main__":
    main()