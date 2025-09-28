import sys
import json
import threading
import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from openai import OpenAI
from config import get_api_config, get_thread_config, get_log_config

# 配置日志
log_config = get_log_config()
logging.basicConfig(
    level=getattr(logging, log_config["log_level"]),
    format=log_config["log_format"],
    handlers=[
        logging.FileHandler(log_config["log_file"], encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 初始化客户端
api_config = get_api_config()
client = OpenAI(
    api_key=api_config["api_key"],
    base_url=api_config["base_url"],
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

# 文件写入锁
write_lock = threading.Lock()

def explain_word(word: str, retry_count=None):
    """
    单个单词解析函数，支持重试机制
    """
    thread_config = get_thread_config()
    if retry_count is None:
        retry_count = thread_config["retry_count"]
    
    for attempt in range(retry_count + 1):
        try:
            completion = client.chat.completions.create(
                model=api_config["model"],
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": word},
                ],
                temperature=api_config["temperature"],
                timeout=thread_config["timeout"]
            )
            result = completion.choices[0].message.content
            logger.info(f"Successfully processed word: {word}")
            return {"word": word, "content": result}
            
        except Exception as e:
            if attempt < retry_count:
                logger.warning(f"Attempt {attempt + 1} failed for word '{word}': {e}. Retrying...")
                time.sleep(thread_config["retry_delay"])
            else:
                logger.error(f"Failed to process word '{word}' after {retry_count + 1} attempts: {e}")
                return {"word": word, "error": str(e)}

def process_word_with_index(word_index_tuple):
    """
    带索引的单词处理函数，用于多线程处理
    """
    index, word = word_index_tuple
    print(f"[{index}] Processing: {word}")
    return explain_word(word)

def safe_write_to_file(file_path, content):
    """
    线程安全的文件写入函数
    """
    with write_lock:
        try:
            with open(file_path, "a", encoding="utf-8") as f:
                json_line = json.dumps(content, ensure_ascii=False)
                f.write(json_line + "\n")
                f.flush()  # 立即刷新到磁盘
        except Exception as e:
            logger.error(f"Failed to write to file {file_path}: {e}")
            raise

def batch_process_multithread(words, output_file, max_workers=None, delay=None):
    """
    多线程批量处理单词
    
    Args:
        words: 单词列表
        output_file: 输出文件路径
        max_workers: 最大并发线程数（默认从配置文件读取）
        delay: 请求间隔延迟（秒，默认从配置文件读取）
    """
    thread_config = get_thread_config()
    if max_workers is None:
        max_workers = thread_config["max_workers"]
    if delay is None:
        delay = thread_config["default_delay"]
    
    logger.info(f"开始多线程处理 {len(words)} 个单词，最大并发数: {max_workers}，延迟: {delay}秒")
    
    # 为单词添加索引并过滤空白
    word_index_pairs = [(i+1, word.strip()) for i, word in enumerate(words) if word.strip()]
    
    if not word_index_pairs:
        logger.warning("没有有效的单词需要处理")
        return
    
    success_count = 0
    error_count = 0
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务
        future_to_word = {
            executor.submit(process_word_with_index, pair): pair 
            for pair in word_index_pairs
        }
        
        # 处理完成的任务
        for future in as_completed(future_to_word):
            word_index_pair = future_to_word[future]
            try:
                result = future.result()
                safe_write_to_file(output_file, result)
                
                if "error" in result:
                    error_count += 1
                    print(f"  ✗ Failed [{word_index_pair[0]}]: {word_index_pair[1]} -> {result['error']}")
                else:
                    success_count += 1
                    print(f"  ✓ Completed [{word_index_pair[0]}]: {word_index_pair[1]} ({success_count + error_count}/{len(word_index_pairs)})")
                
                # 添加延迟以控制请求频率
                if delay > 0:
                    time.sleep(delay)
                    
            except Exception as e:
                error_count += 1
                logger.error(f"Future execution failed for [{word_index_pair[0]}]: {word_index_pair[1]} -> {e}")
                # 记录失败的单词
                error_result = {"word": word_index_pair[1], "error": f"Future execution failed: {str(e)}"}
                safe_write_to_file(output_file, error_result)
    
    end_time = time.time()
    total_time = end_time - start_time
    
    logger.info(f"多线程处理完成！成功: {success_count}, 失败: {error_count}, 总计: {len(word_index_pairs)}")
    logger.info(f"总耗时: {total_time:.2f}秒, 平均: {total_time/len(word_index_pairs):.2f}秒/词")
    
    print(f"✅ 多线程处理完成！")
    print(f"   成功处理: {success_count} 个单词")
    print(f"   处理失败: {error_count} 个单词") 
    print(f"   总耗时: {total_time:.2f} 秒")
    print(f"   平均耗时: {total_time/len(word_index_pairs):.2f} 秒/词")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ 用法: python kimiv2_MultiThread.py <word1> [word2] [word3] ...")
        print("❌ 或者: python kimiv2_MultiThread.py --batch <csv_file> [max_workers]")
        sys.exit(1)

    if sys.argv[1] == "--batch" and len(sys.argv) >= 3:
        # 批量处理模式
        import csv
        
        csv_file = sys.argv[2]
        max_workers = int(sys.argv[3]) if len(sys.argv) > 3 else 5
        
        # 读取CSV文件中的单词
        words = []
        try:
            with open(csv_file, encoding="utf-8") as f:
                reader = csv.reader(f)
                words = [row[0] for row in reader if row and row[0].strip()]
        except FileNotFoundError:
            print(f"❌ 文件未找到: {csv_file}")
            sys.exit(1)
        
        output_file = "output_words.jsonl"
        batch_process_multithread(words, output_file, max_workers)
        
    else:
        # 单个或多个单词处理模式
        words = sys.argv[1:]
        max_workers = min(len(words), 5)  # 默认最大5个线程
        
        output_file = "single_words_output.jsonl"
        batch_process_multithread(words, output_file, max_workers)
