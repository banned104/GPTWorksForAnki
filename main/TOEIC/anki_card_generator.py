import json
import csv
import os

def generate_anki_card_html(word_data):
    """
    根据解析后的单词数据生成 Anki 卡片的 HTML 内容。
    """
    word = word_data.get("word", "")
    content_str = word_data.get("content", "{}")
    
    try:
        content = json.loads(content_str)
    except json.JSONDecodeError:
        content = {"original_content_text": content_str} # Fallback if content is not valid JSON

    html_parts = []

    # 嵌入 CSS 样式
    html_parts.append("""
    <style>
        .card {
            font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
            font-size: 16px;
            color: #333;
            background-color: #f9f9f9;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            max-width: 600px;
            margin: auto;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            line-height: 1.6;
        }
        .word-section {
            text-align: center;
            margin-bottom: 20px;
            border-bottom: 1px solid #eee;
            padding-bottom: 15px;
        }
        .word {
            font-size: 3em;
            font-weight: bold;
            color: #0056b3;
            margin: 0;
        }
        .phonetics {
            font-size: 1.2em;
            color: #666;
            margin-top: 5px;
        }
        .phonetic-label {
            font-weight: bold;
            margin-right: 5px;
        }
        .phonetic-symbol {
            font-style: italic;
        }
        .chinese-meaning {
            font-size: 1.5em;
            color: #008000;
            margin-top: 10px;
        }
        .details-section {
            margin-top: 20px;
        }
        .section {
            margin-bottom: 15px;
            padding: 10px;
            background-color: #fff;
            border-radius: 5px;
            border: 1px solid #f0f0f0;
        }
        .section h2 {
            font-size: 1.3em;
            color: #0056b3;
            border-bottom: 2px solid #0056b3;
            padding-bottom: 5px;
            margin-top: 0;
            margin-bottom: 10px;
        }
        .section p, .section ul {
            margin: 0 0 8px 0;
            line-height: 1.6;
        }
        .section ul {
            list-style-type: disc;
            padding-left: 20px;
        }
        .section li {
            margin-bottom: 5px;
        }
        .example-en {
            font-style: italic;
            color: #555;
        }
        .example-zh {
            color: #777;
            font-size: 0.9em;
        }
        .story-section h2 {
            color: #8B4513; /* Brown for story */
            border-bottom-color: #8B4513;
        }
    </style>
    """)

    # 单词和基本释义部分
    html_parts.append(f"""
    <div class="card">
        <div class="word-section">
            <h1 class="word">{word}</h1>
            <div class=""phonetics"">
                <span class=""phonetic-label"">英音:</span> <span class=""phonetic-symbol"">{content.get("音标", {}).get("英音", "")}</span>
                <span class=""phonetic-label"">美音:</span> <span class=""phonetic-symbol"">{content.get("音标", {}).get("美音", "")}</span>
            </div>
            <div class=""chinese-meaning"">{content.get("中文释义", content.get("original_word_chinese_meaning", ""))}</div>
        </div>
        <div class=""details-section"">
    """)

    # 一词多义
    if content.get("一词多义"):
        html_parts.append(f"""
            <div class=""section"">
                <h2>一词多义</h2>
                <ul>
                    {''.join([f'<li>{item}</li>' for item in content["一词多义"]])}
                </ul>
            </div>
        """)

    # 分析词义
    if content.get("分析词义"):
        html_parts.append(f"""
            <div class=""section"">
                <h2>分析词义</h2>
                <p>{content["分析词义"]}</p>
            </div>
        """)

    # 列举例句
    if content.get("列举例句"):
        html_parts.append(f"""
            <div class=""section"">
                <h2>列举例句</h2>
                {''.join([f'<p><span class=""example-en"">{ex.get("英文", "")}</span><br><span class=""example-zh"">{ex.get("中文", "")}</span></p>' for ex in content["列举例句"]])}
            </div>
        """)

    # 词根分析
    if content.get("词根分析"):
        html_parts.append(f"""
            <div class=""section"">
                <h2>词根分析</h2>
                <p><span class=""phonetic-label"">词根:</span> {content["词根分析"].get("词根", "")} ({content["词根分析"].get("含义", "")})</p>
                {f'<p><span class=""phonetic-label"">衍生词:</span> {", ".join(content["词根分析"]["衍生词"])}</p>' if content["词根分析"].get("衍生词") else ''}
            </div>
        """)

    # 词缀分析
    if content.get("词缀分析"):
        html_parts.append(f"""
            <div class=""section"">
                <h2>词缀分析</h2>
                <p><span class=""phonetic-label"">前缀:</span> {content["词缀分析"].get("前缀", "")} ({content["词缀分析"].get("含义", "")})</p>
                <p><span class=""phonetic-label"">后缀:</span> {content["词缀分析"].get("后缀", "")} ({content["词缀分析"].get("含义", "")})</p>
                {f'<p><span class=""phonetic-label"">同缀词:</span> {", ".join(content["词缀分析"]["同缀词"])}</p>' if content["词缀分析"].get("同缀词") else ''}
            </div>
        """)

    # 发展历史和文化背景
    if content.get("发展历史和文化背景"):
        html_parts.append(f"""
            <div class=""section"">
                <h2>发展历史和文化背景</h2>
                <p>{content["发展历史和文化背景"]}</p>
            </div>
        """)

    # 单词变形
    if content.get("单词变形"):
        html_parts.append(f"""
            <div class=""section"">
                <h2>单词变形</h2>
                <ul>
                    {f'<li><span class=""phonetic-label"">名词:</span> {content["单词变形"].get("名词", "")}</li>' if content["单词变形"].get("名词") else ''}
                    {f'<li><span class=""phonetic-label"">复数:</span> {content["单词变形"].get("复数", "")}</li>' if content["单词变形"].get("复数") else ''}
                    {f'<li><span class=""phonetic-label"">动词:</span> {content["单词变形"].get("动词", "")}</li>' if content["单词变形"].get("动词") else ''}
                    {f'<li><span class=""phonetic-label"">形容词:</span> {content["单词变形"].get("形容词", "")}</li>' if content["单词变形"].get("形容词") else ''}
                    {f'<li><span class=""phonetic-label"">副词:</span> {content["单词变形"].get("副词", "")}</li>' if content["单词变形"].get("副词") else ''}
                    {f'<li><span class=""phonetic-label"">固定搭配:</span> {", ".join(content["单词变形"]["固定搭配"])}</li>' if content["单词变形"].get("固定搭配") and isinstance(content["单词变形"]["固定搭配"], list) else ''}
                    {f'<li><span class=""phonetic-label"">固定搭配:</span> {", ".join([f"{k}: {v}" for k, v in content["单词变形"]["固定搭配"].items()])}</li>' if content["单词变形"].get("固定搭配") and isinstance(content["单词变形"]["固定搭配"], dict) else ''}
                </ul>
            </div>
        """)

    # 记忆辅助
    if content.get("记忆辅助"):
        html_parts.append(f"""
            <div class=""section"">
                <h2>记忆辅助</h2>
                <p>{content["记忆辅助"]}</p>
            </div>
        """)

    # 小故事
    if content.get("小故事"):
        story_en = content["小故事"].get("英文", "")
        story_zh = content["小故事"].get("中文", "")
        html_parts.append(f"""
            <div class=""section story-section"">
                <h2>小故事</h2>
                {f'<p><span class=""example-en"">英文:</span> {story_en}</p>' if story_en else ''}
                {f'<p><span class=""example-zh"">中文:</span> {story_zh}</p>' if story_zh else ''}
            </div>
        """)
    
    # 如果有 original_content_text，作为最后一部分
    if content.get("original_content_text"):
        html_parts.append(f"""
            <div class=""section"">
                <h2>原始内容</h2>
                <pre>{content["original_content_text"]}</pre>
            </div>
        """)

    html_parts.append("""
        </div>
    </div>
    """)

    return "".join(html_parts)

def jsonl_to_anki_tsv(input_jsonl_path, output_tsv_path):
    """
    读取 JSONL 文件，生成 Anki 卡片 HTML，并保存为 TSV 文件。
    """
    processed_count = 0
    with open(input_jsonl_path, 'r', encoding='utf-8') as infile, \
         open(output_tsv_path, 'w', encoding='utf-8', newline='') as outfile:
        
        writer = csv.writer(outfile, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        
        for line in infile:
            if not line.strip():
                continue
            try:
                word_data = json.loads(line.strip())
                word = word_data.get("word", "").strip()
                
                if not word:
                    print(f"跳过缺少 'word' 字段的行: {line.strip()}")
                    continue

                anki_html_content = generate_anki_card_html(word_data)
                
                # Anki 卡片通常是 "正面\\t背面"
                # 这里我们将 word 作为正面，生成的 HTML 作为背面
                writer.writerow([word, anki_html_content])
                processed_count += 1
            except json.JSONDecodeError as e:
                print(f"跳过无效的JSON行: {line.strip()} - 错误: {e}")
            except Exception as e:
                print(f"处理行时发生未知错误: {line.strip()} - 错误: {e}")
    
    print(f"处理完成。共生成 {processed_count} 张 Anki 卡片，结果保存到 {output_tsv_path}")

if __name__ == "__main__":
    input_file = "d:\\\\Codes\\\\09_Python\\\\GPTWorksForAnki\\\\main\\\\TOEIC\\\\TOEIC_output_words_processed.jsonl"
    output_file = "d:\\\\Codes\\\\09_Python\\\\GPTWorksForAnki\\\\main\\\\TOEIC\\\\TOEIC_anki_cards.tsv"
    
    if not os.path.exists(input_file):
        print(f"错误: 输入文件不存在 - {input_file}")
    else:
        jsonl_to_anki_tsv(input_file, output_file)