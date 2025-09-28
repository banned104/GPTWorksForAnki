#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多线程KIMI API单词解析器测试脚本
"""

import os
import csv
import json
import time
from kimiv2_MultiThread import batch_process_multithread, explain_word

def create_test_csv():
    """创建测试用的CSV文件"""
    test_words = [
        "hello",
        "world", 
        "python",
        "artificial",
        "intelligence"
    ]
    
    with open("test_words.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        for word in test_words:
            writer.writerow([word])
    
    print("✅ 创建测试CSV文件: test_words.csv")
    return test_words

def test_single_thread():
    """测试单线程处理"""
    print("\n🔧 测试单线程处理...")
    start_time = time.time()
    
    result = explain_word("hello")
    
    end_time = time.time()
    print(f"   单词 'hello' 处理完成")
    print(f"   耗时: {end_time - start_time:.2f} 秒")
    print(f"   结果: {result['word']}")

def test_multi_thread():
    """测试多线程处理"""
    print("\n🚀 测试多线程处理...")
    
    # 创建测试数据
    test_words = create_test_csv()
    
    # 测试不同并发数
    for workers in [1, 3, 5]:
        print(f"\n--- 测试 {workers} 个并发线程 ---")
        
        output_file = f"test_output_{workers}workers.jsonl"
        if os.path.exists(output_file):
            os.remove(output_file)    
        
        start_time = time.time()
        batch_process_multithread(test_words, output_file, max_workers=workers, delay=0.2)
        end_time = time.time()
        
        # 检查结果
        result_count = 0
        if os.path.exists(output_file):
            with open(output_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        result_count += 1
        
        print(f"   ✓ 完成时间: {end_time - start_time:.2f} 秒")
        print(f"   ✓ 处理结果: {result_count}/{len(test_words)} 个单词")
        
        # 清理测试文件
        if os.path.exists(output_file):
            os.remove(output_file)

def test_file_safety():
    """测试文件读写安全性"""
    print("\n🔒 测试文件读写安全性...")
    
    from kimiv2_MultiThread import safe_write_to_file
    import threading
    
    test_file = "safety_test.jsonl"
    if os.path.exists(test_file):
        os.remove(test_file)
    
    # 模拟多个线程同时写入
    def write_data(thread_id):
        for i in range(5):
            data = {"thread_id": thread_id, "iteration": i, "message": f"Thread {thread_id} - Item {i}"}
            safe_write_to_file(test_file, data)
            time.sleep(0.01)  # 短暂延迟
    
    # 创建多个线程
    threads = []
    for i in range(3):
        thread = threading.Thread(target=write_data, args=(i,))
        threads.append(thread)
    
    # 启动所有线程
    start_time = time.time()
    for thread in threads:
        thread.start()
    
    # 等待所有线程完成
    for thread in threads:
        thread.join()
    
    end_time = time.time()
    
    # 检查结果
    line_count = 0
    if os.path.exists(test_file):
        with open(test_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    line_count += 1
    
    expected_lines = 3 * 5  # 3个线程，每个线程5次写入
    print(f"   ✓ 完成时间: {end_time - start_time:.2f} 秒")
    print(f"   ✓ 预期行数: {expected_lines}")
    print(f"   ✓ 实际行数: {line_count}")
    print(f"   ✓ 文件安全性: {'通过' if line_count == expected_lines else '失败'}")
    
    # 清理测试文件
    if os.path.exists(test_file):
        os.remove(test_file)

def main():
    """主测试函数"""
    print("🧪 开始多线程KIMI API单词解析器测试")
    print("=" * 50)
    
    try:
        # 测试单线程
        test_single_thread()
        
        # 测试多线程
        test_multi_thread()
        
        # 测试文件安全性
        test_file_safety()
        
        print("\n" + "=" * 50)
        print("✅ 所有测试完成！")
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
    
    finally:
        # 清理测试文件
        for file in ["test_words.csv", "safety_test.jsonl"]:
            if os.path.exists(file):
                os.remove(file)

if __name__ == "__main__":
    main()