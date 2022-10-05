import os
import re
import pandas as pd

from tests.data.data_generator import DataDfType


def write_data_dfs(data_dfs: DataDfType) -> None:
    recursive_dfs_write("tests/data", data_dfs)


def recursive_dfs_write(keys_string: str, curr_value: dict | pd.DataFrame):
    if isinstance(curr_value, pd.DataFrame):
        os.makedirs(re.sub(r"/[^/]*$", "", keys_string), exist_ok=True)
        curr_value.to_csv(f"{keys_string}.tsv", sep="\t", index=False)
        return None
    assert isinstance(curr_value, dict)
    for key, child in curr_value.items():
        recursive_dfs_write(f"{keys_string}/{key}", child)


from tests.data.data_generator import get_data_dfs
data_dfs = get_data_dfs()
write_data_dfs(data_dfs)
