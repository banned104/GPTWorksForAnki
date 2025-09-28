# 基于LLM的英语单词助记卡片生成系统

## 项目概述

本项目是一个基于大语言模型（LLM）的英语单词学习助手，通过调用Moonshot AI的Kimi模型API，为英语单词生成详细的学习内容，并最终转换为Anki记忆卡片格式，帮助用户更好地学习和记忆英语单词。

## 核心功能

- **智能单词分析**：使用LLM深度分析英语单词的音标、词义、词根词缀、例句等
- **批量处理**：支持批量处理大量单词，提高效率
- **数据匹配**：智能匹配已有词汇数据，避免重复处理
- **Anki集成**：自动生成Anki导入格式，无缝集成到记忆学习流程

## 项目架构

### 核心模块

#### 1. `kimiv2.py` - LLM调用核心模块
- **功能**：封装Moonshot AI API调用逻辑
- **特点**：
  - 使用OpenAI兼容的API接口
  - 内置专业的中英文双语教育专家Prompt
  - 生成包含音标、词义、例句、词根分析、记忆技巧、小故事等全方位内容
- **输出格式**：JSON格式，包含单词和详细解释内容

#### 2. `batch_process.py` - 批量处理模块
- **功能**：批量处理CSV格式的单词列表
- **特点**：
  - 支持超时处理和错误恢复
  - 可配置处理速率，避免API限流
  - 追加模式写入，支持断点续传
- **输出格式**：JSONL格式（每行一个JSON对象）

#### 3. `compare_words.py` - 数据匹配模块
- **功能**：比较已有数据和待处理数据，避免重复处理
- **工作流程**：
  1. 读取已处理的JSONL数据
  2. 读取待处理的CSV单词列表
  3. 匹配已存在的单词，分离出未处理的单词
- **输出**：
  - `matched.json`：已匹配的完整数据
  - `unmatched.csv`：需要新处理的单词列表

#### 4. `formatter.py` - 格式转换模块
- **功能**：将JSON数组格式转换为JSONL格式
- **用途**：统一数据格式，便于后续处理

#### 5. `merge.py` - 数据合并模块
- **功能**：合并多个JSONL文件
- **用途**：将已有数据和新生成数据合并为最终数据集

#### 6. `AnkiConvert.py` - Anki格式转换模块
- **功能**：将JSONL数据转换为Anki可导入的TSV格式
- **特点**：
  - 支持Markdown到HTML的转换
  - 为小故事部分添加特殊CSS类
  - 生成标准的Anki导入格式

## 工作流程

### 完整处理流程

```
原始单词列表(CSV) 
       ↓
[compare_words.py] 数据匹配
       ↓
已匹配数据 + 未匹配单词列表
       ↓
[batch_process.py] 批量LLM处理
       ↓
新生成数据(JSONL)
       ↓
[formatter.py] 格式统一
       ↓
[merge.py] 数据合并
       ↓
最终数据集(JSONL)
       ↓
[AnkiConvert.py] Anki格式转换
       ↓
Anki导入文件(TSV)
```

### 详细步骤

1. **数据预处理**
   ```python
   # 比较已有数据和新单词列表
   python compare_words.py
   ```

2. **批量LLM处理**
   ```python
   # 处理未匹配的单词
   from batch_process import batch_process
   batch_process('unmatched.csv', 'output_words.jsonl')
   ```

3. **格式转换**
   ```python
   # 转换已匹配数据格式
   python formatter.py
   ```

4. **数据合并**
   ```python
   # 合并所有数据
   python merge.py
   ```

5. **生成Anki卡片**
   ```python
   # 转换为Anki格式
   python AnkiConvert.py
   ```

## LLM Prompt设计

系统使用精心设计的教育专家Prompt，生成的内容包括：

- **音标**：英音美音标注
- **一词多义**：多种常用含义
- **分析词义**：系统性词义解析
- **列举例句**：不同场景的使用示例
- **词根分析**：词根及衍生词
- **词缀分析**：词缀及相关词汇
- **发展历史**：词汇来源和文化背景
- **单词变形**：各种词性变化和固定搭配
- **记忆辅助**：高效记忆技巧
- **小故事**：包含目标单词的场景故事

## 技术特点

### 设计模式应用

1. **模块化设计**：每个功能独立成模块，便于维护和扩展
2. **管道模式**：数据处理采用管道式流程，每个阶段职责明确
3. **错误处理**：完善的异常处理和超时机制
4. **可配置性**：支持参数配置，适应不同使用场景

### Python高级特性

1. **文件I/O优化**：使用追加模式和缓冲写入
2. **JSON处理**：支持多种JSON格式（数组、JSONL）
3. **正则表达式**：智能内容解析和格式转换
4. **路径处理**：使用pathlib进行现代化路径操作

### API集成最佳实践 <mcreference link="https://blog.csdn.net/weixin_48389642/article/details/149534781" index="0">0</mcreference>

1. **OpenAI兼容接口**：使用标准OpenAI SDK格式
2. **错误恢复**：超时和异常处理机制
3. **速率控制**：可配置的请求间隔，避免API限流
4. **安全性**：API密钥管理（建议使用环境变量）

## 文件结构

```
NewIdea/
├── kimiv2.py              # LLM API调用核心
├── batch_process.py       # 批量处理模块
├── compare_words.py       # 数据匹配模块
├── formatter.py           # 格式转换工具
├── merge.py              # 数据合并工具
├── AnkiConvert.py        # Anki格式转换
├── words_clean.csv       # 输入单词列表
├── gptwords.json         # 已有处理数据
├── matched.json          # 匹配结果
├── unmatched.csv         # 未匹配单词
├── output_words.jsonl    # 新生成数据
├── matched_output.jsonl  # 格式化匹配数据
├── final_output.jsonl    # 最终合并数据
└── Output/
    ├── anki_words.tsv    # Anki导入文件
    ├── final_output.jsonl # 最终数据副本
    └── gpt_dictionary.apkg # Anki卡包
```

## 使用说明

### 环境要求

```bash
pip install openai markdown
```

### 配置API密钥

建议将API密钥设置为环境变量：
```bash
export MOONSHOT_API_KEY="your-api-key-here"
```

然后修改`kimiv2.py`中的API密钥获取方式：
```python
import os
client = OpenAI(
    api_key=os.getenv("MOONSHOT_API_KEY"),
    base_url="https://api.moonshot.cn/v1",
)
```

### 快速开始

1. 准备单词列表CSV文件（格式：word,content）
2. 运行完整处理流程
3. 导入生成的TSV文件到Anki

## 扩展性

### 支持其他LLM服务 <mcreference link="https://zhuanlan.zhihu.com/p/645878637" index="1">1</mcreference>

项目采用OpenAI兼容接口，可轻松切换到其他LLM服务：
- OpenAI GPT系列
- 阿里云通义千问
- 其他兼容OpenAI API的服务

### 自定义Prompt

可根据需要修改`SYSTEM_PROMPT`，调整生成内容的格式和重点。

### 输出格式扩展

可扩展支持其他记忆卡片格式，如SuperMemo、Quizlet等。

## 注意事项

1. **API成本控制**：合理设置处理速率，避免不必要的API调用
2. **数据备份**：重要数据请及时备份
3. **网络稳定性**：确保网络连接稳定，避免处理中断
4. **内容质量**：定期检查生成内容的质量，必要时调整Prompt

## 贡献指南

欢迎提交Issue和Pull Request来改进项目。主要改进方向：
- 支持更多LLM服务
- 优化Prompt设计
- 增加更多输出格式
- 提升处理效率
- 完善错误处理

---

*本项目展示了如何将现代LLM技术与传统学习工具相结合，为语言学习提供智能化解决方案。*