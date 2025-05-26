import pandas as pd
df = pd.read_parquet("miccheck_a8749ce.parquet")
df.to_csv("miccheck_a8749ce.csv", index=False)
