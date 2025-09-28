import json
import csv
import os

# 文件路径
# file1_path = "gptwords.json"  # 一行一个 JSON 
# file2_path = "words_clean.csv"    # CSV: word,content words_clean.csv 

# 新的比较文件路径
txt_file_path = "TOEIC/TOEIC.txt"  # TXT文件路径
csv_file_path = "words_clean.csv"    # CSV文件路径

output_matched_path_txt_csv = "TOEIC/matched_txt_csv.json"      # 匹配成功的完整 JSON
output_unmatched_path_txt_csv = "TOEIC/unmatched_txt_csv.csv"   # 未匹配的 CSV

def load_file1(path):
    """逐行读取 JSONL (一行一个 JSON 对象)"""
    data = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                data.append(obj)
            except json.JSONDecodeError as e:
                print(f"⚠️ JSON 解析失败: {e} -> {line[:50]}...")
    return data

def load_file2(path):
    """读取 CSV -> {word: content}"""
    words = {}
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:
                continue
            word = row[0].strip().lower()
            content = row[1].strip() if len(row) > 1 else ""
            words[word] = content
    return words

def load_txt(path):
    """逐行读取 TXT 文件，返回清理后的行列表"""
    lines = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:  # 只添加非空行
                lines.append(line)
    return lines

def main():
    txt_data = load_txt(txt_file_path)
    csv_data = load_file2(csv_file_path)

    matched = []
    unmatched = []

    for line in txt_data:
        parts = line.split(',', 1)
        if not parts:
            continue
        txt_word = parts[0].strip().lower()
        
        if txt_word in csv_data:
            matched.append({"word": txt_word, "content": csv_data[txt_word]})
        else:
            definition_part = parts[1].strip() if len(parts) > 1 else ""
            unmatched.append({"word": txt_word, "content": definition_part})

    # 保存匹配结果 (完整 JSON)
    os.makedirs(os.path.dirname(output_matched_path_txt_csv), exist_ok=True)
    with open(output_matched_path_txt_csv, "w", encoding="utf-8") as f:
        json.dump(matched, f, ensure_ascii=False)

    # 保存未匹配结果 (CSV)
    os.makedirs(os.path.dirname(output_unmatched_path_txt_csv), exist_ok=True)
    with open(output_unmatched_path_txt_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        for entry in unmatched:
            writer.writerow([entry["word"], entry["content"]])

    print(f"✅ 完成！匹配 {len(matched)} 个，未匹配 {len(unmatched)} 个。")

if __name__ == "__main__":
    main()