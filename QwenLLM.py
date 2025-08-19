import dashscope
import pandas as pd
import json
import os
import time
import logging
import asyncio
from aiohttp import ClientSession, ClientError, ClientResponseError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from functools import lru_cache
import threading
from queue import Queue
import numpy as np
from tqdm import tqdm
import hashlib

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("word_processing.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("WordMemory")

# 全局配置
CONFIG = {
    "BATCH_SIZE": 50,          # 每批次处理单词数
    "MAX_CONCURRENT": 5,       # 最大并发请求数
    "RETRY_ATTEMPTS": 3,       # 最大重试次数
    "MIN_DELAY": 0.5,          # 最小延迟(秒)
    "MAX_DELAY": 5.0,          # 最大延迟(秒)
    "PROGRESS_FILE": "progress.json",
    "CACHE_FILE": "word_cache.json",
    "MODEL_SELECTION_THRESHOLD": 0.7,  # 用于模型选择的阈值
}

class APIManager:
    """管理API调用，处理配额、限流和错误"""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.dashscope = dashscope
        self.dashscope.api_key = api_key
        self.success_count = 0
        self.error_count = 0
        self.last_call_time = 0
        self.call_lock = threading.Lock()
        self.rate_limit = 5  # 默认QPS
        self.dynamic_delay = CONFIG["MIN_DELAY"]
        
    def update_rate_limit(self, new_limit):
        """动态更新速率限制"""
        with self.call_lock:
            self.rate_limit = max(1, new_limit)
            # 根据新限制调整延迟
            self.dynamic_delay = max(CONFIG["MIN_DELAY"], 1.0 / self.rate_limit * 1.5)
    
    def get_delay(self):
        """获取适当的延迟时间"""
        with self.call_lock:
            now = time.time()
            elapsed = now - self.last_call_time
            delay = max(0, self.dynamic_delay - elapsed)
            self.last_call_time = now + delay
            return delay
    
    @retry(
        stop=stop_after_attempt(CONFIG["RETRY_ATTEMPTS"]),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((ClientError, ClientResponseError, TimeoutError))
    )
    async def call_api(self, word_data, model_type="auto"):
        """调用API，带重试机制"""
        # 根据单词复杂度选择模型
        if model_type == "auto":
            # 简单规则：根据单词长度和定义复杂度判断
            complexity = len(word_data) / 100
            model = "qwen-turbo" if complexity < CONFIG["MODEL_SELECTION_THRESHOLD"] else "qwen-max"
        else:
            model = model_type
            
        delay = self.get_delay()
        if delay > 0:
            await asyncio.sleep(delay)
        
        try:
            # 使用异步调用
            async with ClientSession() as session:
                response = await self.dashscope.Generation.acall(
                    model=model,
                    prompt=self._build_prompt(word_data),
                    temperature=0.6,
                    api_key=self.api_key,
                    session=session
                )
                
                if response.status_code == 200:
                    self.success_count += 1
                    # 动态调整速率
                    if self.success_count % 100 == 0:
                        self.update_rate_limit(min(self.rate_limit * 1.1, 20))
                    return response.output.text
                else:
                    self.error_count += 1
                    logger.error(f"API调用失败 [状态码: {response.status_code}]: {response.message}")
                    # 降低调用速率
                    if self.error_count > 5:
                        self.update_rate_limit(max(self.rate_limit * 0.8, 1))
                    raise Exception(f"API调用失败: {response.message}")
                    
        except Exception as e:
            logger.error(f"API调用异常: {str(e)}")
            raise

    def _build_prompt(self, word_data):
        """构建优化的提示词，减少token使用"""
        return f"""
        请简洁但全面地分析以下英语单词，格式严格遵循要求：
        
        {word_data}
        
        ### 分析词义
        [简明列出主要含义，3-5点]
        
        ### 列举例句
        [4个实用例句，中英文对照]
        
        ### 词根词缀
        [词根+词缀分析，不超过2句]
        
        ### 记忆技巧
        [1个核心记忆点+小故事]
        
        注意：内容要精炼实用，避免冗长，总字数控制在300-500字。
        """

class WordProcessor:
    """单词处理核心类，管理处理流程"""
    
    def __init__(self, api_manager, csv_path):
        self.api_manager = api_manager
        self.csv_path = csv_path
        self.progress = self._load_progress()
        self.word_cache = self._load_cache()
        self.processed_words = set(self.progress.get("processed", []))
        self.total_words = 0
        self.processed_count = len(self.processed_words)
        self.error_words = self.progress.get("errors", [])
        self.lock = threading.Lock()
        
    def _load_progress(self):
        """加载处理进度"""
        if os.path.exists(CONFIG["PROGRESS_FILE"]):
            try:
                with open(CONFIG["PROGRESS_FILE"], "r") as f:
                    return json.load(f)
            except:
                return {"processed": [], "errors": []}
        return {"processed": [], "errors": []}
    
    def _save_progress(self):
        """保存处理进度"""
        with self.lock:
            progress = {
                "processed": list(self.processed_words),
                "errors": self.error_words,
                "timestamp": time.time()
            }
            with open(CONFIG["PROGRESS_FILE"], "w") as f:
                json.dump(progress, f, indent=2)
    
    def _load_cache(self):
        """加载缓存"""
        cache = {}
        if os.path.exists(CONFIG["CACHE_FILE"]):
            try:
                with open(CONFIG["CACHE_FILE"], "r") as f:
                    cache_data = json.load(f)
                    # 转换为需要的格式
                    for item in cache_data:
                        cache[item["word"]] = item["content"]
            except:
                pass
        return cache
    
    def _save_cache(self, word, content):
        """保存到缓存"""
        self.word_cache[word] = content
        cache_data = [{"word": w, "content": c} for w, c in self.word_cache.items()]
        with open(CONFIG["CACHE_FILE"], "w") as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
    
    def _is_word_processed(self, word):
        """检查单词是否已处理"""
        return word in self.processed_words
    
    def _mark_as_processed(self, word):
        """标记单词为已处理"""
        with self.lock:
            self.processed_words.add(word)
            self.processed_count += 1
            if self.processed_count % 50 == 0:
                self._save_progress()
    
    def _add_error(self, word, error):
        """记录错误"""
        with self.lock:
            self.error_words.append({
                "word": word,
                "error": str(error),
                "timestamp": time.time()
            })
            if len(self.error_words) % 10 == 0:
                self._save_progress()
    
    async def process_word(self, word_data):
        """处理单个单词"""
        word = word_data.split(',')[0].strip()
        
        # 检查是否已处理
        if self._is_word_processed(word):
            logger.info(f"跳过已处理单词: {word}")
            return None
            
        # 检查缓存
        cache_key = self._get_cache_key(word_data)
        if cache_key in self.word_cache:
            logger.info(f"使用缓存结果: {word}")
            self._mark_as_processed(word)
            return {"word": word, "content": self.word_cache[cache_key]}
        
        try:
            # 调用API
            content = await self.api_manager.call_api(word_data)
            
            # 保存结果
            result = {"word": word, "content": content}
            self._mark_as_processed(word)
            self._save_cache(word, content)
            
            return result
            
        except Exception as e:
            self._add_error(word, e)
            logger.error(f"处理单词失败 [{word}]: {str(e)}")
            return None
    
    def _get_cache_key(self, word_data):
        """生成缓存键"""
        return hashlib.md5(word_data.encode()).hexdigest()
    
    async def process_batch(self, word_data_list):
        """处理一批单词"""
        tasks = [self.process_word(word_data) for word_data in word_data_list]
        results = []
        
        for f in asyncio.as_completed(tasks):
            result = await f
            if result:
                results.append(result)
                
        return results
    
    def prepare_word_list(self):
        """准备待处理单词列表"""
        df = pd.read_csv(self.csv_path)
        self.total_words = len(df)
        
        # 构建单词数据列表
        word_data_list = []
        for _, row in df.iterrows():
            word = row['word']
            definition = row['definition']
            word_data = f"{word},{definition}"
            
            # 只处理未完成的单词
            if word not in self.processed_words:
                word_data_list.append(word_data)
                
        logger.info(f"共发现 {self.total_words} 个单词，已处理 {self.processed_count} 个，剩余 {len(word_data_list)} 个需要处理")
        return word_data_list
    
    async def process_all(self):
        """处理所有单词"""
        word_data_list = self.prepare_word_list()
        if not word_data_list:
            logger.info("所有单词已处理完毕")
            return []
        
        # 分批次处理
        results = []
        total_batches = (len(word_data_list) + CONFIG["BATCH_SIZE"] - 1) // CONFIG["BATCH_SIZE"]
        
        # 创建进度条
        pbar = tqdm(total=len(word_data_list), desc="处理单词")
        
        for i in range(0, len(word_data_list), CONFIG["BATCH_SIZE"]):
            batch = word_data_list[i:i+CONFIG["BATCH_SIZE"]]
            batch_results = await self.process_batch(batch)
            results.extend(batch_results)
            
            # 更新进度条
            pbar.update(len(batch))
            pbar.set_postfix({
                "进度": f"{self.processed_count}/{self.total_words}",
                "成功率": f"{len(batch_results)/len(batch):.1%}"
            })
            
            # 每处理100个单词保存一次进度
            if (i // CONFIG["BATCH_SIZE"]) % 2 == 0:
                self._save_progress()
                
        pbar.close()
        self._save_progress()
        return results

class OptimizedWordMemoryApp:
    """优化版单词记忆应用入口"""
    
    def __init__(self, api_key, csv_path, output_file="word_memory.json"):
        self.api_manager = APIManager(api_key)
        self.processor = WordProcessor(self.api_manager, csv_path)
        self.output_file = output_file
        
    async def run(self):
        """运行处理流程"""
        logger.info("===== 开始单词记忆优化项目 =====")
        logger.info(f"处理文件: {self.processor.csv_path}")
        logger.info(f"输出文件: {self.output_file}")
        
        start_time = time.time()
        results = await self.processor.process_all()
        
        # 保存最终结果
        if results:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            logger.info(f"处理完成！共处理 {len(results)} 个单词，结果已保存至 {self.output_file}")
        else:
            logger.info("没有新单词需要处理")
        
        # 统计信息
        elapsed = time.time() - start_time
        logger.info(f"总耗时: {elapsed:.2f}秒, 平均 {len(results)/elapsed:.2f} 单词/秒")
        
        # 错误报告
        if self.processor.error_words:
            error_file = "error_words.json"
            with open(error_file, 'w') as f:
                json.dump(self.processor.error_words, f, indent=2)
            logger.warning(f"共 {len(self.processor.error_words)} 个单词处理失败，详情见 {error_file}")
        
        return results

def main():
    """主函数"""
    # 从环境变量获取API Key（推荐）
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        # 或者从配置文件获取（次选）
        try:
            with open(".api_key", "r") as f:
                api_key = f.read().strip()
        except:
            logger.error("API Key未配置！请设置DASHSCOPE_API_KEY环境变量或创建.api_key文件")
            return
    
    # 配置文件路径
    csv_path = "words.csv"  # 你的6000+单词CSV文件
    output_file = "word_memory.json"
    
    # 检查CSV文件
    if not os.path.exists(csv_path):
        logger.error(f"CSV文件不存在: {csv_path}")
        logger.info("请创建包含以下列的CSV文件:\nword,definition")
        return
    
    # 运行应用
    app = OptimizedWordMemoryApp(api_key, csv_path, output_file)
    asyncio.run(app.run())
    
    logger.info("===== 单词处理流程结束 =====")

if __name__ == "__main__":
    main()