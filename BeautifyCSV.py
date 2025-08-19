import pandas as pd

# 读取时，指定 quoting=csv.QUOTE_ALL 会自动识别多行内容
df = pd.read_csv("merged_unique.csv", encoding="utf-8", header=None, names=["word", "meaning"])

# 清理掉 meaning 里的换行符（可选）
df["meaning"] = df["meaning"].str.replace("\n", " ", regex=False)

# 保存为干净的 CSV
df.to_csv("words_clean.csv", index=False, encoding="utf-8")

print(f"清理完成！共 {len(df)} 条记录，已输出到 words_clean.csv")
