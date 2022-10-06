import os
import pandas as pd
import shutil

from config.settings import settings

DATA_DIR = settings.TEST_DATA_DIR

#
# Helper functions
#

# Write a single file given filepath and df
def write_file(filepath: str, df: pd.DataFrame) -> None:
    df.to_csv(filepath, sep="\t", index=False)
    # pd automatically detects .gz suffix to gzip the file
    print(f"WRITTEN: {filepath}")


# Write files from given data_df
# data_df can be manipulated in the fixture before writing
# Expects directories to already exist
def write_files(data_df_base):
    write_file(
        f"{DATA_DIR}species_list.tsv",
        data_df_base["species_list_df"]
    )
    for sa_type, sa_df in data_df_base["sample_annotation_dfs"].items():
        write_file(
            f"{DATA_DIR}/sample-annotations/{sa_type}.tsv",
            sa_df
        )
    for ga_type, ga_df in data_df_base["gene_annotation_dfs"].items():
        write_file(
            f"{DATA_DIR}/gene-annotations/{ga_type}.tsv",
            ga_df
        )
    for taxid, content in data_df_base["species_specific_dfs"].items():
        write_file(
            f"{DATA_DIR}tpm-matrices/taxid{taxid}_tpm.tsv.gz",
            content["tpm_matrix"]
        )
        for sa_type, df in content["sa_assignments"].items():
            write_file(
                f"{DATA_DIR}sample-annotations-assignment/{sa_type}/taxid{taxid}_{sa_type}.tsv",
                df
            )
        for ga_type, df in content["ga_assignments"].items():
            write_file(
                f"{DATA_DIR}gene-annotations-assignment/{ga_type}/taxid{taxid}_{ga_type}.tsv",
                df
            )


#
# The following code has been deprecated
#


# import os
# import re
# import pandas as pd

# from tests.data_scripts.data_generator import DataDfType
# from tests.data_scripts.data_generator import get_data_dfs


# def write_data_dfs(data_dfs: DataDfType) -> None:
#     recursive_dfs_write("tests/data", data_dfs)


# def recursive_dfs_write(keys_string: str, curr_value: dict | pd.DataFrame):
#     if isinstance(curr_value, pd.DataFrame):
#         os.makedirs(re.sub(r"/[^/]*$", "", keys_string), exist_ok=True)
#         curr_value.to_csv(f"{keys_string}.tsv", sep="\t", index=False)
#         return None
#     assert isinstance(curr_value, dict)
#     for key, child in curr_value.items():
#         recursive_dfs_write(f"{keys_string}/{key}", child)


# data_dfs = get_data_dfs()
# write_data_dfs(data_dfs)
