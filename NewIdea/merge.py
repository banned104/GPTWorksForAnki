import shutil

def merge_jsonl(file1, file2, output_file):
    with open(output_file, 'w', encoding='utf-8') as out_f:
        # 直接复制第一个文件内容
        with open(file1, 'r', encoding='utf-8') as f1:
            shutil.copyfileobj(f1, out_f)
        # 再复制第二个文件内容
        with open(file2, 'r', encoding='utf-8') as f2:
            shutil.copyfileobj(f2, out_f)

# 用法举例
merge_jsonl('matched_output.jsonl', 'output_words.jsonl', 'final_output.jsonl')