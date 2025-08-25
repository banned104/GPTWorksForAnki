import csv
import json
import time
from kimiv2 import explain_word  # 导入模块化的函数

class TimeoutException(Exception):
    print("链接超时")
    pass

def timeout_handler(signum, frame):
    raise TimeoutException()

def batch_process(csv_in, jsonl_out, timeout=60, rate=1.0):

    with open(jsonl_out, "a", encoding="utf-8") as fout:  # 追加模式打开文件
        with open(csv_in, encoding="utf-8") as fin:
            reader = csv.reader(fin)
            for idx, row in enumerate(reader, 1):
                word = row[0].strip()
                if not word:
                    continue

                print(f"[{idx}] Processing: {word}")
                try:
                    res = explain_word(word)
                except TimeoutException:
                    print(f"  Timeout: {word}")
                    res = {"word": word, "error": "timeout"}
                except Exception as e:
                    print(f"  Error: {word} -> {e}")
                    res = {"word": word, "error": str(e)}

                #  写入 JSONL：每行一个 JSON 对象
                json_line = json.dumps(res, ensure_ascii=False)
                fout.write(json_line + "\n")

                time.sleep(rate)

    print(f"Done! Processed {idx} words, results appended to {jsonl_out}")

# if __name__ == "__main__":
#     parser = argparse.ArgumentParser()
#     parser.add_argument("csv_in", help="Input unmatched words CSV")
#     parser.add_argument("jsonl_out", help="Output JSONL file path")
#     parser.add_argument("--timeout", type=int, default=60, help="Timeout per word (seconds, default 60)")
#     parser.add_argument("--rate", type=float, default=1.0, help="Delay between requests (seconds, default 1)")
#     args = parser.parse_args()

#     batch_process(args.csv_in, args.jsonl_out, args.timeout, args.rate)

if __name__ == "__main__":
    # 直接写死文件路径
    csv_in = "unmatched.csv"     # 输入CSV文件
    jsonl_out = "output_words.jsonl"   # 输出JSONL文件

    # 配置参数
    timeout = 60   # 每个单词超时时间（秒）
    rate = 1.0     # 请求之间的延迟（秒）

    batch_process(csv_in, jsonl_out, timeout, rate)

