import re
input_path = '(完整版)托业考试词汇大全(整理版).txt'
output_path = '(完整版)托业考试词汇大全(最终版).txt'
results = []
with open(input_path, encoding='utf-8') as f:
    buffer = ''
    for line in f:
        line = line.strip()
        # 合并被拆开的英文（如buckle\nup）
        if re.match(r'^[a-zA-Z]+$', line):
            buffer += line + ' '
            continue
        # 去除序号和特殊字符
        line = re.sub(r'^[\d\.]+', '', line)
        # 合并buffer
        if buffer:
            line = buffer + line
            buffer = ''
        # 拆分一行多个词条
        parts = re.split(r'(?<=[\u4e00-\u9fa5])\s+(?=[a-zA-Z])', line)
        for part in parts:
            part = part.strip()
            if part:
                results.append(part)
with open(output_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(results))