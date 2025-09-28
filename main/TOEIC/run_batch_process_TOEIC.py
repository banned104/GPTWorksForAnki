import subprocess
import os

# 定义输入和输出文件路径
# 注意：这里的路径是相对于 run_batch_process_TOEIC.py 文件的
csv_input_file = "unmatched_txt_csv.csv"
jsonl_output_file = "TOEIC_output_words.jsonl"

# Step2_batch_process_MultiThread.py 脚本的路径
# 假设它在 main 目录下，相对于当前脚本的父目录
step2_script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Step2_batch_process_MultiThread.py")

def run_batch_process():
    print(f"   准备调用 Step2_batch_process_MultiThread.py")
    print(f"   输入 CSV: {csv_input_file}")
    print(f"   输出 JSONL: {jsonl_output_file}")
    print(f"   Step2 脚本路径: {step2_script_path}")

    # 构建命令行参数
    command = [
        "python",
        step2_script_path,
        "--csv", csv_input_file,
        "--output", jsonl_output_file,
        "--workers", "45",  # 可以根据需要调整并发数
        "--delay", "0.5"   # 可以根据需要调整延迟
    ]

    try:
        # 执行命令
        # cwd 设置为当前脚本所在的目录，以便相对路径正确解析
        result = subprocess.run(command, cwd=os.path.dirname(__file__), check=True, capture_output=True, text=True, encoding="gbk")
        print("  Step2_batch_process_MultiThread.py 执行成功！")
        print("--- 标准输出 ---")
        print(result.stdout)
        if result.stderr:
            print("--- 标准错误 ---")
            print(result.stderr)
    except subprocess.CalledProcessError as e:
        print(f"   Step2_batch_process_MultiThread.py 执行失败，错误码: {e.returncode}")
        print("--- 标准输出 ---")
        print(e.stdout)
        print("--- 标准错误 ---")
        print(e.stderr)
    except FileNotFoundError:
        print(f"  错误: 找不到 Python 解释器或脚本文件 {step2_script_path}。请确保 Python 已安装且在 PATH 中，并且脚本路径正确。")

if __name__ == "__main__":
    run_batch_process()