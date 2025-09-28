import json
import csv
import re
from pathlib import Path
import markdown  # pip install markdown

def process_content(text: str) -> str:
    """
    将 Markdown 格式的 content 转成 HTML
    并且对【小故事】部分加 <div class="story">
    """
    # 匹配【小故事】到最后
    story_match = re.search(r"(【小故事】[\s\S]*)", text)
    if story_match:
        story_text = story_match.group(1)
        story_html = f'<div class="story">{markdown.markdown(story_text)}</div>'
        text = text.replace(story_text, story_html)

    # 转 Markdown → HTML
    html = markdown.markdown(text)

    return html


def json_to_tsv(input_file: str, output_file: str):
    """
    将 JSONL 或 JSON 文件转成 Anki TSV
    字段： word \t content
    """
    input_path = Path(input_file)
    output_path = Path(output_file)

    # 读取 JSON（支持数组或 JSON Lines）
    data = []
    with open(input_path, "r", encoding="utf-8") as f:
        first_char = f.read(1)
        f.seek(0)
        if first_char == "[":
            data = json.load(f)  # JSON 数组
        else:
            for line in f:       # JSONL
                if line.strip():
                    data.append(json.loads(line))

    # 写 TSV
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        for item in data:
            word = item.get("word", "").strip()
            content = process_content(item.get("content", "").strip())
            writer.writerow([word, content])

    print(f"✅ 已生成 Anki 文件: {output_path}")


if __name__ == "__main__":
    json_to_tsv("Output/final_output.jsonl", "Output/anki_words.tsv")
    
