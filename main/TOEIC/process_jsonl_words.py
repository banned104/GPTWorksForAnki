import json
import os

def process_jsonl_file(input_file_path, output_file_path):
    """
    处理JSONL文件，将'word'字段中的中文部分移动到'content'字段中。
    
    Args:
        input_file_path (str): 输入JSONL文件的路径。
        output_file_path (str): 输出JSONL文件的路径。
    """
    processed_count = 0
    with open(input_file_path, 'r', encoding='utf-8') as infile, \
         open(output_file_path, 'w', encoding='utf-8') as outfile:
        for line in infile:
            try:
                data = json.loads(line.strip())
                
                original_word_field = data.get("word", "")
                
                # 尝试分割英文和中文部分，只分割第一个空格
                parts = original_word_field.split(' ', 1)
                
                english_word = parts[0].strip()
                chinese_meaning_from_word = ""
                if len(parts) > 1:
                    chinese_meaning_from_word = parts[1].strip()
                
                # 更新 'word' 字段为纯英文
                data["word"] = english_word
                
                # 处理 'content' 字段
                if "content" in data and data["content"]:
                    try:
                        # 尝试解析 content 字段为 JSON 对象
                        content_dict = json.loads(data["content"])
                    except json.JSONDecodeError:
                        # 如果 content 不是有效的 JSON，则将其视为普通字符串
                        content_dict = {"original_content_text": data["content"]}
                    
                    if chinese_meaning_from_word:
                        # 创建一个新的字典，将中文含义作为第一个键
                        new_content_dict = {"original_word_chinese_meaning": chinese_meaning_from_word}
                        # 将现有的 content_dict 合并到新字典中，确保中文含义在前
                        new_content_dict.update(content_dict)
                        content_dict = new_content_dict
                    
                    data["content"] = json.dumps(content_dict, ensure_ascii=False)
                elif chinese_meaning_from_word:
                    # 如果没有 content 字段，且有中文含义，则创建 content 字段
                    data["content"] = json.dumps({"original_word_chinese_meaning": chinese_meaning_from_word}, ensure_ascii=False)
                
                outfile.write(json.dumps(data, ensure_ascii=False) + '\n')
                processed_count += 1
            except json.JSONDecodeError as e:
                print(f"跳过无效的JSON行: {line.strip()} - 错误: {e}")
            except Exception as e:
                print(f"处理行时发生未知错误: {line.strip()} - 错误: {e}")
    
    print(f"处理完成。共处理 {processed_count} 行，结果保存到 {output_file_path}")

if __name__ == "__main__":
    input_file = "d:\\Codes\\09_Python\\GPTWorksForAnki\\main\\TOEIC\\TOEIC_output_words.jsonl"
    output_file = "d:\\Codes\\09_Python\\GPTWorksForAnki\\main\\TOEIC\\TOEIC_output_words_processed.jsonl"
    
    # 检查输入文件是否存在
    if not os.path.exists(input_file):
        print(f"错误: 输入文件不存在 - {input_file}")
    else:
        process_jsonl_file(input_file, output_file)