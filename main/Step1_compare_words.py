import json
import csv

# 文件路径
file1_path = "gptwords.json"  # 一行一个 JSON 
file2_path = "words_clean.csv"    # CSV: word,content words_clean.csv 

output_matched_path = "matched.json"      # 匹配成功的完整 JSON
output_unmatched_path = "unmatched.csv"   # 未匹配的 CSV

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
            word = row[0].strip()
            content = row[1].strip() if len(row) > 1 else ""
            words[word] = content
    return words

def main():
    file1_data = load_file1(file1_path)
    file2_data = load_file2(file2_path)

    # 建立 file1 的快速索引 {word -> full_record}
    file1_dict = {entry["word"]: entry for entry in file1_data if "word" in entry}

    matched = []
    unmatched = {}

    for word, content in file2_data.items():
        if word in file1_dict:
            matched.append(file1_dict[word])
        else:
            unmatched[word] = content

    # 保存匹配结果 (完整 JSON)
    with open(output_matched_path, "w", encoding="utf-8") as f:
        json.dump(matched, f, ensure_ascii=False, indent=2)

    # 保存未匹配结果 (CSV)
    with open(output_unmatched_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        for word, content in unmatched.items():
            writer.writerow([word, content])

    print(f"✅ 完成！匹配 {len(matched)} 个，未匹配 {len(unmatched)} 个。")

if __name__ == "__main__":
    main()
