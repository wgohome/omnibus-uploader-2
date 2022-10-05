import os
import shutil
import pandas as pd
import pytest

from tests.data_scripts.data_generator import get_data_dfs

#
# Helper functions
#
def write_file(filepath: str, df: pd.DataFrame) -> None:
    df.to_csv(filepath, sep="\t", index=False)
    print(f"WRITTEN: {filepath}")


DATA_DIR = "tests/data/"


#
# Fixtures
#
@pytest.fixture(scope="module")
def data_df_base():
    return get_data_dfs()


#
# Directory structure
#
# - /data
#   - /species_list.tsv
#   - /sample-annotations/{sa_type}.tsv
#   - /gene-annotations/{ga_type}.tsv
#   - /tpm-matrices/taxid{taxid}_tpm.tsv
#   - /sample-annotations-assignment/
#       - /po/taxid{taxid}_po.tsv
#   - /gene-annotations-assignment/
#       - /po/taxid{taxid}_mapman.tsv
#       - /po/taxid{taxid}_interpro.tsv
#
@pytest.fixture(scope="module")
def setup_data_dirs():
    os.makedirs(f"{DATA_DIR}sample-annotations", exist_ok=True)
    os.makedirs(f"{DATA_DIR}gene-annotations", exist_ok=True)
    os.makedirs(f"{DATA_DIR}tpm-matrices", exist_ok=True)
    os.makedirs(f"{DATA_DIR}sample-annotations-assignment/PO", exist_ok=True)
    os.makedirs(f"{DATA_DIR}gene-annotations-assignment/MAPMAN", exist_ok=True)
    os.makedirs(f"{DATA_DIR}gene-annotations-assignment/INTERPRO", exist_ok=True)
    yield
    for dirname in [item for item in os.listdir(DATA_DIR) if not item.startswith(".")]:
        try:
            shutil.rmtree(f"{DATA_DIR}/{dirname}")
        except NotADirectoryError as error:
            os.remove(f"{DATA_DIR}/{dirname}")


@pytest.fixture(scope="module")
def write_file_base(data_df_base, setup_data_dirs):
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
            f"{DATA_DIR}tpm-matrices/taxid{taxid}_tpm.tsv",
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
