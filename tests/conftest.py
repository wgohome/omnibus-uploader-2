import pytest

from tests.data.data_generator import get_data_dfs


@pytest.fixture
def data_df_base():
    return get_data_dfs()


@pytest.fixture
def make_file_base(data_df_base):
    pass
