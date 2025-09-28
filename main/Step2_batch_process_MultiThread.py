import csv
import json
import time
import os
from kimiv2_MultiThread import batch_process_multithread  # 导入多线程批量处理函数

def batch_process(csv_in, jsonl_out, max_workers=5, delay=0.5):
    """
    使用多线程批量处理CSV文件中的单词
    
    Args:
        csv_in: 输入CSV文件路径
        jsonl_out: 输出JSONL文件路径
        max_workers: 最大并发线程数
        delay: 请求间隔延迟（秒）
    """
    if not os.path.exists(csv_in):
        print(f"输入文件不存在: {csv_in}")
        return
    
    # 读取CSV文件中的单词
    words = []
    try:
        with open(csv_in, encoding="utf-8") as fin:
            reader = csv.reader(fin)
            words = [row[0] for row in reader if row and row[0].strip()]
    except UnicodeDecodeError:
        print(f"使用 UTF-8 编码读取 {csv_in} 失败，尝试使用 GBK 编码...")
        try:
            with open(csv_in, encoding="gbk") as fin:
                reader = csv.reader(fin)
                words = [row[0] for row in reader if row and row[0].strip()]
        except Exception as e:
            print(f"使用 GBK 编码读取 {csv_in} 失败: {e}")
            return
    except Exception as e:
        print(f"读取CSV文件失败: {e}")
        return
    
    if not words:
        print("CSV文件中没有找到有效的单词")
        return
    
    print(f"从 {csv_in} 读取到 {len(words)} 个单词")
    print(f"开始多线程处理，最大并发数: {max_workers}，延迟: {delay}秒")
    
    # 清空输出文件（如果存在）
    if os.path.exists(jsonl_out):
        os.remove(jsonl_out)
    
    # 使用多线程批量处理
    batch_process_multithread(words, jsonl_out, max_workers, delay)
    
    print(f"处理完成！结果已保存到 {jsonl_out}")

# if __name__ == "__main__":
#     parser = argparse.ArgumentParser()
#     parser.add_argument("csv_in", help="Input unmatched words CSV")
#     parser.add_argument("jsonl_out", help="Output JSONL file path")
#     parser.add_argument("--timeout", type=int, default=60, help="Timeout per word (seconds, default 60)")
#     parser.add_argument("--rate", type=float, default=1.0, help="Delay between requests (seconds, default 1)")
#     args = parser.parse_args()

#     batch_process(args.csv_in, args.jsonl_out, args.timeout, args.rate)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="多线程批量处理英文单词解析")
    parser.add_argument("--csv", default="unmatched.csv", help="输入CSV文件路径（默认: unmatched.csv）")
    parser.add_argument("--output", default="output_words.jsonl", help="输出JSONL文件路径（默认: output_words.jsonl）")
    parser.add_argument("--workers", type=int, default=5, help="最大并发线程数（默认: 5）")
    parser.add_argument("--delay", type=float, default=0.5, help="请求间隔延迟秒数（默认: 0.5）")
    
    args = parser.parse_args()
    
    print(f"配置参数:")
    print(f"   输入文件: {args.csv}")
    print(f"   输出文件: {args.output}")
    print(f"   最大并发数: {args.workers}")
    print(f"   请求延迟: {args.delay}秒")
    print()
    
    batch_process(args.csv, args.output, args.workers, args.delay)

