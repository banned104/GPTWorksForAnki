import sys
import json
from openai import OpenAI

# 初始化客户端
client = OpenAI(
    api_key="sk-zIarIriPZjAmwhVakmwNBshAxfSwzt9e7kwEfqeUqXvo9dCC",  # 建议改为 os.getenv("MOONSHOT_API_KEY")
    base_url="https://api.moonshot.cn/v1",
)

# Prompt
SYSTEM_PROMPT = """你是一名中英文双语教育专家，拥有帮助将中文视为母语的用户理解和记忆英语单词的专长，请根据用户提供的英语单词完成下列任务。
### 音标 
- 英音美音的音标标注

### 一词多义
- 列出单词的多种常用的含义。

### 分析词义
- 系统地分析用户提供的英文单词，并以简单易懂的方式解答；

### 列举例句
- 根据所需，为该单词提供至少 3 个不同场景下的使用方法和例句。并且附上中文翻译，以帮助用户更深入地理解单词意义。

### 词根分析
- 分析并展示单词的词根；
- 列出由词根衍生出来的其他单词；

### 词缀分析
- 分析并展示单词的词缀；
- 列出相同词缀的的其他单词；

### 发展历史和文化背景
- 详细介绍单词的造词来源和发展历史，以及在欧美文化中的内涵

### 单词变形
- 列出单词对应的名词、单复数、动词、不同时态、形容词、副词等的变形以及对应的中文翻译。
- 列出单词对应的固定搭配、组词以及对应的中文翻译。

### 记忆辅助
- 提供一些高效的记忆技巧和窍门，以更好地记住英文单词。

### 小故事
- 用英文撰写一个有画面感的场景故事，包含用户提供的单词。
- 要求使用简单的词汇，100 个单词以内。
- 英文故事后面附带对应的中文翻译。
"""

def explain_word(word: str):
    completion = client.chat.completions.create(
        model="kimi-k2-0711-preview",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": word},
        ],
        temperature=0.3,
    )
    # 正确访问方式
    result = completion.choices[0].message.content
    return {"word": word, "content": result}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ 用法: python word_explainer.py <word>")
        sys.exit(1)

    word = sys.argv[1]
    explanation = explain_word(word)

    # 直接以 JSON 格式输出
    print(json.dumps(explanation, ensure_ascii=False, indent=2))
