import pandas as pd


import pandas as pd

# 你的输入文件列表
files = [ "雅思标准词汇3800（第二版）.csv", "雅思阅读机经词汇.csv", "雅思真词汇（第7版）无同根词版.csv"]

dfs = []
for f in files:
    # 每个 CSV 文件没有表头，第一列是单词，第二列是释义
    df = pd.read_csv(f, encoding="utf-8", header=None, names=["word", "meaning"])
    dfs.append(df)

# 合并所有文件
merged = pd.concat(dfs, ignore_index=True)

# 按单词去重（保留第一个）
merged_unique = merged.drop_duplicates(subset=["word"], keep="first")

# 输出到新文件
merged_unique.to_csv("merged_unique.csv", index=False, encoding="utf-8")

print(f"合并完成！原来 {len(merged)} 条，去重后 {len(merged_unique)} 条，输出到 merged_unique.csv")
