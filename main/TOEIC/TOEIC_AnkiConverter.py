#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TOEIC单词Anki卡片转换器
将处理后的JSONL文件转换为美观的Anki卡片格式
"""

import json
import csv
import re
from pathlib import Path
import html

def clean_and_parse_content(content_str):
    """
    清理并解析content字段，处理各种编码和格式问题
    """
    try:
        # 首先检查是否已经是一个字典（某些情况下content可能已经是解析过的）
        if isinstance(content_str, dict):
            return content_str
            
        # 处理转义字符
        content_str = content_str.replace('\\\\', '\\')
        content_str = content_str.replace('\\\\"', '"')
        content_str = content_str.replace('\\n', '\n')
        
        # 尝试解析为JSON
        if content_str.startswith('{') and content_str.endswith('}'):
            try:
                content_data = json.loads(content_str)
                return content_data
            except json.JSONDecodeError:
                # 如果直接解析失败，尝试处理嵌套的JSON字符串
                # 有些content字段可能是JSON字符串的字符串形式
                try:
                    # 尝试去掉外层引号并再次解析
                    if content_str.startswith('"{') and content_str.endswith('}"'):
                        inner_content = content_str[1:-1]
                        inner_content = inner_content.replace('\\"', '"')
                        content_data = json.loads(inner_content)
                        return content_data
                except:
                    pass
                
                # 最后尝试eval（谨慎使用）
                try:
                    content_data = eval(content_str)
                    if isinstance(content_data, dict):
                        return content_data
                except:
                    pass
        
        # 如果所有解析都失败，返回原始文本
        return {"raw_content": content_str}
    except Exception as e:
        print(f"⚠️  内容解析警告: {str(e)[:100]}")
        return {"raw_content": str(content_str)}

def format_phonetics(phonetics_data):
    """
    格式化音标显示
    """
    if isinstance(phonetics_data, dict):
        uk = phonetics_data.get('英音', '')
        us = phonetics_data.get('美音', '')
        if uk or us:
            result = []
            if uk:
                result.append(f"🇬🇧 {uk}")
            if us:
                result.append(f"🇺🇸 {us}")
            return " | ".join(result)
    return str(phonetics_data) if phonetics_data else ""

def format_meanings(meanings_data):
    """
    格式化一词多义
    """
    if isinstance(meanings_data, list):
        formatted = []
        for i, meaning in enumerate(meanings_data, 1):
            formatted.append(f"<div class='meaning-item'>{i}. {meaning}</div>")
        return "".join(formatted)
    return str(meanings_data) if meanings_data else ""

def format_examples(examples_data):
    """
    格式化例句
    """
    if isinstance(examples_data, list):
        formatted = []
        for i, example in enumerate(examples_data, 1):
            if isinstance(example, dict):
                eng = example.get('英文', '')
                chn = example.get('中文', '')
                formatted.append(f"""
                <div class='example-item'>
                    <div class='example-num'>{i}.</div>
                    <div class='example-en'>{eng}</div>
                    <div class='example-zh'>{chn}</div>
                </div>
                """)
            else:
                formatted.append(f"<div class='example-item'>{i}. {example}</div>")
        return "".join(formatted)
    return str(examples_data) if examples_data else ""

def format_word_forms(forms_data):
    """
    格式化单词变形
    """
    if isinstance(forms_data, dict):
        formatted = []
        for key, value in forms_data.items():
            if isinstance(value, list):
                value_str = "; ".join(value)
            elif isinstance(value, dict):
                value_str = "; ".join([f"{k}: {v}" for k, v in value.items()])
            else:
                value_str = str(value)
            formatted.append(f"<span class='word-form'><strong>{key}:</strong> {value_str}</span>")
        return "<br>".join(formatted)
    return str(forms_data) if forms_data else ""

def format_story(story_data):
    """
    格式化小故事
    """
    if isinstance(story_data, dict):
        eng = story_data.get('英文', '')
        chn = story_data.get('中文', '') or story_data.get('中文翻译', '')
        if eng or chn:
            return f"""
            <div class='story-section'>
                <div class='story-en'>{eng}</div>
                <div class='story-zh'>{chn}</div>
            </div>
            """
    elif isinstance(story_data, str):
        # 尝试分离英文和中文
        parts = story_data.split('\\n中文')
        if len(parts) == 2:
            eng = parts[0].replace('英文：', '').strip()
            chn = parts[1].replace('：', '').strip()
            return f"""
            <div class='story-section'>
                <div class='story-en'>{eng}</div>
                <div class='story-zh'>{chn}</div>
            </div>
            """
        else:
            return f"<div class='story-section'>{story_data}</div>"
    return str(story_data) if story_data else ""

def process_word_content(word, content_data):
    """
    将解析后的content数据转换为HTML格式
    """
    # 如果是原始文本，直接返回简化版本
    if "raw_content" in content_data:
        return f"""
        <div class="word-card">
            <div class="word-title">{word}</div>
            <div class="content-raw">{html.escape(content_data['raw_content'][:500])}</div>
        </div>
        """
    
    # 获取各部分数据
    chinese_meaning = content_data.get('中文释义', '')
    phonetics = content_data.get('音标', {})
    meanings = content_data.get('一词多义', [])
    analysis = content_data.get('分析词义', '')
    examples = content_data.get('列举例句', [])
    etymology = content_data.get('发展历史和文化背景', '')
    word_forms = content_data.get('单词变形', {})
    memory_aid = content_data.get('记忆辅助', '')
    story = content_data.get('小故事', {})
    
    # 构建HTML内容
    html_content = f"""
    <div class="toeic-word-card">
        <div class="word-header">
            <h2 class="word-title">{word}</h2>
            <div class="phonetics">{format_phonetics(phonetics)}</div>
            <div class="main-meaning">{chinese_meaning}</div>
        </div>
        
        {f'<div class="section meanings"><h3>📝 词义解析</h3>{format_meanings(meanings)}</div>' if meanings else ''}
        
        {f'<div class="section analysis"><h3>🔍 词义分析</h3><p>{analysis}</p></div>' if analysis else ''}
        
        {f'<div class="section examples"><h3>📚 例句</h3>{format_examples(examples)}</div>' if examples else ''}
        
        {f'<div class="section word-forms"><h3>🔄 单词变形</h3>{format_word_forms(word_forms)}</div>' if word_forms else ''}
        
        {f'<div class="section memory"><h3>💡 记忆辅助</h3><p class="memory-tip">{memory_aid}</p></div>' if memory_aid else ''}
        
        {f'<div class="section etymology"><h3>📖 词汇背景</h3><p>{etymology}</p></div>' if etymology else ''}
        
        {f'<div class="section story"><h3>📖 小故事</h3>{format_story(story)}</div>' if story else ''}
    </div>
    
    <style>
    .toeic-word-card {{
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
        line-height: 1.6;
        color: #333;
        max-width: 100%;
        margin: 0 auto;
    }}
    
    .word-header {{
        text-align: center;
        margin-bottom: 20px;
        padding: 15px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
    }}
    
    .word-title {{
        font-size: 2.2em;
        font-weight: bold;
        margin: 0 0 10px 0;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
    }}
    
    .phonetics {{
        font-size: 1.1em;
        margin: 8px 0;
        opacity: 0.9;
    }}
    
    .main-meaning {{
        font-size: 1.3em;
        font-weight: 500;
        margin-top: 10px;
    }}
    
    .section {{
        margin: 15px 0;
        padding: 12px;
        border-left: 4px solid #667eea;
        background: #f8f9ff;
        border-radius: 0 8px 8px 0;
    }}
    
    .section h3 {{
        margin: 0 0 10px 0;
        color: #5a67d8;
        font-size: 1.1em;
    }}
    
    .meaning-item {{
        margin: 5px 0;
        padding: 5px 10px;
        background: white;
        border-radius: 5px;
        border-left: 3px solid #a5b4fc;
    }}
    
    .example-item {{
        margin: 10px 0;
        padding: 10px;
        background: white;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }}
    
    .example-en {{
        font-weight: 500;
        color: #2d3748;
        margin-bottom: 5px;
    }}
    
    .example-zh {{
        color: #718096;
        font-style: italic;
    }}
    
    .word-form {{
        display: inline-block;
        margin: 3px 8px 3px 0;
        color: #4a5568;
    }}
    
    .memory-tip {{
        background: #fff3cd;
        padding: 10px;
        border-radius: 6px;
        border: 1px solid #ffeaa7;
        font-weight: 500;
        color: #856404;
    }}
    
    .story-section {{
        background: white;
        padding: 12px;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
    }}
    
    .story-en {{
        font-weight: 500;
        color: #2d3748;
        margin-bottom: 8px;
        line-height: 1.5;
    }}
    
    .story-zh {{
        color: #718096;
        font-style: italic;
        line-height: 1.5;
    }}
    </style>
    """
    
    return html_content

def jsonl_to_anki_tsv(input_file, output_tsv):
    """
    将JSONL文件转换为Anki TSV格式
    """
    input_path = Path(input_file)
    output_path = Path(output_tsv)
    
    if not input_path.exists():
        print(f"❌ 输入文件不存在: {input_file}")
        return
    
    processed_count = 0
    error_count = 0
    
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        
        with open(input_path, "r", encoding="utf-8") as infile:
            for line_num, line in enumerate(infile, 1):
                line = line.strip()
                if not line:
                    continue
                
                try:
                    # 解析JSON行
                    data = json.loads(line)
                    word = data.get("word", "").strip()
                    content = data.get("content", "")
                    
                    if not word:
                        print(f"⚠️  第{line_num}行：单词为空，跳过")
                        continue
                    
                    # 清理并解析content
                    content_data = clean_and_parse_content(content)
                    
                    # 生成HTML格式的卡片内容
                    html_content = process_word_content(word, content_data)
                    
                    # 写入TSV
                    writer.writerow([word, html_content])
                    processed_count += 1
                    
                    if processed_count % 50 == 0:
                        print(f"✅ 已处理 {processed_count} 个单词...")
                
                except json.JSONDecodeError as e:
                    error_count += 1
                    print(f"❌ 第{line_num}行JSON解析错误: {e}")
                except Exception as e:
                    error_count += 1
                    print(f"❌ 第{line_num}行处理错误: {e}")
    
    print(f"🎉 转换完成！")
    print(f"   ✅ 成功处理: {processed_count} 个单词")
    print(f"   ❌ 处理失败: {error_count} 个")
    print(f"   📄 输出文件: {output_path}")
    print(f"   📋 可直接导入Anki使用")

if __name__ == "__main__":
    # 输入和输出文件路径
    input_jsonl = "../output/TOEIC_output_words_processed.jsonl"
    output_tsv = "TOEIC_anki_cards.tsv"
    
    print("🚀 开始转换TOEIC单词为Anki卡片...")
    print(f"📂 输入文件: {input_jsonl}")
    print(f"📂 输出文件: {output_tsv}")
    print("-" * 50)
    
    jsonl_to_anki_tsv(input_jsonl, output_tsv)