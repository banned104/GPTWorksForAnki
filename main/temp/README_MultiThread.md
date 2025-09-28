# 多线程KIMI API单词解析器

这是一个使用Python多线程调用KIMI API来解析英文单词的项目。

## 功能特点

- ✅ 多线程并发处理，提高处理效率
- ✅ 可配置最大并发线程数
- ✅ 线程安全的文件读写操作
- ✅ 请求频率控制，避免API限制
- ✅ 错误处理和重试机制
- ✅ 支持单个单词和批量处理模式

## 文件说明

### 核心文件
- `kimiv2_SingleThread.py` - 单线程版本的单词解析器
- `kimiv2_MultiThread.py` - **多线程版本的单词解析器**
- `2_batch_process_MultiThread.py` - 多线程批量处理脚本

### 功能模块
1. **单词解析** - 使用KIMI API进行深度单词分析
2. **多线程处理** - 提高处理效率，支持并发控制
3. **文件安全** - 线程锁保护文件写入操作
4. **错误处理** - 完善的异常处理和错误记录

## 使用方法

### 1. 单个单词处理
```bash
python kimiv2_MultiThread.py hello
python kimiv2_MultiThread.py hello world python
```

### 2. 批量处理CSV文件
```bash
python kimiv2_MultiThread.py --batch unmatched.csv
python kimiv2_MultiThread.py --batch unmatched.csv 10  # 设置最大10个并发线程
```

### 3. 使用批量处理脚本
```bash
# 使用默认参数
python 2_batch_process_MultiThread.py

# 自定义参数
python 2_batch_process_MultiThread.py --csv words.csv --output results.jsonl --workers 8 --delay 0.3
```

## 参数配置

### 多线程参数
- `max_workers`: 最大并发线程数（默认: 5）
- `delay`: 请求间隔延迟，单位秒（默认: 0.5）

### 批量处理参数
- `--csv`: 输入CSV文件路径
- `--output`: 输出JSONL文件路径  
- `--workers`: 最大并发线程数
- `--delay`: 请求延迟时间

## 文件格式

### 输入格式 (CSV)
```csv
hello
world
python
artificial
intelligence
```

### 输出格式 (JSONL)
```json
{"word": "hello", "content": "### 音标\n英音: /həˈləʊ/\n美音: /həˈloʊ/\n..."}
{"word": "world", "content": "### 音标\n英音: /wɜːld/\n美音: /wɜːrld/\n..."}
```

## 线程安全特性

### 文件写入保护
- 使用 `threading.Lock()` 确保文件写入的原子性
- 避免多线程同时写入造成的数据混乱

### 错误处理
- 每个线程独立处理错误
- 失败的单词会记录错误信息到输出文件

## 性能优化建议

1. **并发数设置**: 根据API限制和服务器性能调整 `max_workers`
2. **请求延迟**: 适当的 `delay` 可避免触发API限流
3. **批量大小**: 大批量处理时可考虑分批处理

## 注意事项

1. **API密钥**: 请替换代码中的API密钥为您自己的密钥
2. **请求限制**: 注意KIMI API的请求频率限制
3. **文件权限**: 确保输出目录有写入权限
4. **内存使用**: 大批量处理时注意内存使用情况

## 错误排查

如果遇到问题，检查：
1. API密钥是否正确
2. 网络连接是否正常  
3. 输入文件格式是否正确
4. 输出目录是否有写入权限