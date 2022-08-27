import pandas as pd
import os

root = "/home/william/data-omnibus/tpm-matrices"
files = os.listdir(root)

for file in files:
    filepath= f"{root}/{file}"
    print(f"Reading: {file}")
    df = pd.read_csv(filepath, sep="\t", index_col=0)
    if df.isna().any(axis=None):
        print(f"{file}: Filling na with 0")
        df.fillna(0, inplace=True)
        df.to_csv(filepath, sep="\t")
        print(f"{file}: Filled na with 0")
