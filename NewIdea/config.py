# -*- coding: utf-8 -*-
"""
KIMI API多线程配置文件
"""

import os

# API配置
API_CONFIG = {
    "api_key": os.getenv("MOONSHOT_API_KEY", "sk-JKoXtqgKrpKx89495wpkTU1XMFVWoiWDzB1llsLvQ0TD0Nry"),
    "base_url": "https://api.moonshot.cn/v1",
    "model": "kimi-k2-0711-preview",
    "temperature": 0.3
}

# 多线程配置
THREAD_CONFIG = {
    "max_workers": 40,           # 最大并发线程数
    "default_delay": 0.5,       # 默认请求延迟（秒）
    "timeout": 60,              # 单个请求超时时间（秒）
    "retry_count": 3,           # 重试次数
    "retry_delay": 1.0          # 重试延迟（秒）
}

# 文件配置
FILE_CONFIG = {
    "input_encoding": "utf-8",
    "output_encoding": "utf-8",
    "default_input": "unmatched.csv",
    "default_output": "output_words.jsonl",
    "backup_enabled": True      # 是否创建备份文件
}

# 日志配置
LOG_CONFIG = {
    "log_level": "INFO",
    "log_format": "%(asctime)s - %(levelname)s - %(message)s",
    "log_file": "word_processor.log"
}

def get_api_config():
    """获取API配置"""
    return API_CONFIG.copy()

def get_thread_config():
    """获取多线程配置"""
    return THREAD_CONFIG.copy()

def get_file_config():
    """获取文件配置"""
    return FILE_CONFIG.copy()

def get_log_config():
    """获取日志配置"""
    return LOG_CONFIG.copy()

def update_config(**kwargs):
    """更新配置参数"""
    for key, value in kwargs.items():
        if key.startswith("api_"):
            API_CONFIG[key[4:]] = value
        elif key.startswith("thread_"):
            THREAD_CONFIG[key[7:]] = value
        elif key.startswith("file_"):
            FILE_CONFIG[key[5:]] = value
        elif key.startswith("log_"):
            LOG_CONFIG[key[4:]] = value