# -*- coding: utf-8 -*-
"""
修正《Claude code AI 主导API测试与pytest自动化落地》文档中的错误和不完整内容。
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

from docx import Document

doc = Document('Claude code AI 主导API测试与pytest自动化落地.docx')

# ============================================================
# 定义替换规则：(段落索引, 旧文本, 新文本)
# ============================================================
replacements = [
    # --- 章节编号修正 ---
    (226, '六、API 06 自动化就绪评估', '五、API 05 自动化就绪评估'),
    (274, '七、API 06pytest自动化', '六、API 06 pytest自动化'),

    # --- 正文引用修正 ---
    (227, 'APl04结束后', 'API 04结束后'),
    (229, 'APl05并不是', 'API 05并不是'),
    (250, 'APl 05个直接', 'API 05并不直接'),
    (248, 'APi自动化', 'API自动化'),
    (305, '以 API 05 的直接为实现依据', '以 API 05 的交接内容为实现依据'),

    # --- 错别字修正 ---
    (12, 'cladue code', 'Claude Code'),
    (114, '坏境', '环境'),
    (27, '上一个几口产出', '上一个接口产出'),
    (280, 'pytest、unittes、docstest', 'pytest、unittest、doctest'),
    (298, '    1ogs/', '    logs/'),
    (330, 'co1lect-on1y', 'collect-only'),
    (216, '**筛选PO级别**', '**筛选P0级别**'),
    (318, '已授权测捷环境', '已授权测试环境'),
    (275, '就可用让Agent', '就可让Agent'),

    # --- 截断内容补充 ---
    (271,
     '说明动态值从哪里取得、应该取得几条、如何交给后续请求；说明字段按精确值、数值、模式、非空或空值中的哪种语义判断，并保',
     '说明动态值从哪里取得、应该取得几条、如何交给后续请求；说明字段按精确值、数值、模式、非空或空值中的哪种语义判断，并保留断言失败时的诊断信息和数据清理策略。'),
]

# ============================================================
# 执行替换
# ============================================================
changed = 0
for idx, old_text, new_text in replacements:
    para = doc.paragraphs[idx]
    if old_text in para.text:
        # 保留原有格式：遍历 run 进行替换
        full_text = para.text
        new_full = full_text.replace(old_text, new_text)

        # 清空所有 run 的文本
        for run in para.runs:
            run.text = ''

        # 把新文本写入第一个 run
        if para.runs:
            para.runs[0].text = new_full
        else:
            para.text = new_full

        changed += 1
        print(f'[OK] 段落 {idx}: "{old_text}" -> "{new_text[:40]}..."')
    else:
        print(f'[SKIP] 段落 {idx}: 未找到 "{old_text[:30]}..."')

print(f'\n共修改 {changed} 处')

# ============================================================
# 保存
# ============================================================
output_path = 'Claude code AI 主导API测试与pytest自动化落地_修正版.docx'
doc.save(output_path)
print(f'已保存: {output_path}')