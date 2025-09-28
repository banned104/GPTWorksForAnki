import json

# 读取原始 JSON 文件
with open('matched.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 写入 jsonl 文件
with open('matched_output.jsonl', 'w', encoding='utf-8') as f_out:
    for entry in data:
        # 每个 entry 是一个 dict {"word": ..., "content": ...}
        f_out.write(json.dumps(entry, ensure_ascii=False) + '\n')

print("转换完成，结果已保存到 output.jsonl")