import pandas as pd

df = pd.read_csv("./data/virgo_stars.csv", comment="#")

# 距離の最小値と最大値の行を表示
print(df[df["distance_pc"] == df["distance_pc"].min()])
print(df[df["distance_pc"] == df["distance_pc"].max()])

print(df)