import os
import shutil
from pymongo import MongoClient
import pytest
from unittest import mock

from config.settings import settings
from tests.data_scripts.data_generator import get_data_dfs
from tests.data_scripts.data_writer import write_files, DATA_DIR
from uploader.utilities.db_setup import setup_indexes


#
# Fixtures
#

def get_test_db():
    client = MongoClient(settings.DATABASE_URL)
    test_db_name = settings.TEST_DATABASE_NAME
    db = client[test_db_name]
    return db


@pytest.fixture(scope="session", autouse=True)
def mock_get_db():
    with mock.patch("uploader.utilities.db_setup.get_db", get_test_db()):
        yield


@pytest.fixture(scope="session", autouse=True)
def mock_default_n_neighbors():
    test_settings = settings
    test_settings.DEFAULT_N_NEIGHBORS = 5
    with mock.patch("config.settings", test_settings):
        yield


@pytest.fixture()
def test_db():
    client = MongoClient(settings.DATABASE_URL)
    test_db_name = settings.TEST_DATABASE_NAME
    client.drop_database(test_db_name)
    db = client[test_db_name]
    setup_indexes(db=db)
    yield db
    client.drop_database(test_db_name)


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
    print("Creating up mock dirs")
    os.makedirs(f"{DATA_DIR}sample-annotations", exist_ok=True)
    os.makedirs(f"{DATA_DIR}gene-annotations", exist_ok=True)
    os.makedirs(f"{DATA_DIR}tpm-matrices", exist_ok=True)
    os.makedirs(f"{DATA_DIR}pcc-results", exist_ok=True)
    os.makedirs(f"{DATA_DIR}sample-annotations-assignment/PO", exist_ok=True)
    os.makedirs(f"{DATA_DIR}gene-annotations-assignment/MAPMAN", exist_ok=True)
    os.makedirs(f"{DATA_DIR}gene-annotations-assignment/INTERPRO", exist_ok=True)
    yield
    for dirname in [item for item in os.listdir(DATA_DIR) if not item.startswith(".")]:
        try:
            shutil.rmtree(f"{DATA_DIR}/{dirname}")
        except NotADirectoryError as error:
            os.remove(f"{DATA_DIR}/{dirname}")
    print("Cleaning up mock files")


@pytest.fixture(scope="module")
def write_file_base(data_df_base, setup_data_dirs):
    write_files(data_df_base)
