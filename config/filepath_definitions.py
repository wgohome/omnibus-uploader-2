from enum import Enum

from uploader3.models.gene_annotation import GeneAnnotationType
from .settings import settings

# File paths should be relative to settings.DATA_DIR

# filepath_definitions = {
#     "species_list": {
#         "sub_dirs": [],
#         "get_filename": lambda: "species_list.tsv",
#     },
#     "tpm_matrices": {
#         "sub_dirs": ["tpm-matrices"],
#         "get_filename": lambda taxid: f"taxid{taxid}_tpm.tsv.gz",  # TODO:make all gz
#     },
#     "sample_annotations": {
#         "sub_dirs": ["sample-annotations"],
#         "get_filename": lambda taxid: f"taxid{taxid}_po.tsv",
#     },
#     "interpro_annotations": {
#         "sub_dirs": ["interpro-annotations"],
#         "get_filename": lambda taxid: f"taxid{taxid}_interpro.tsv",
#     },
#     # "mapman_annotations": {
#     #     "sub_dirs": ["mapman-annotations"],
#     #     "get_filename": lambda taxid: f"taxid{taxid}_mapman.tsv",
#     # },
# }


class FilepathDefinitions:
    #
    # This class defines the naming convention for directories and files
    # and is configurable by you.
    #
    # All files expected to be in tsv format and has .tsv suffix.
    #
    # Abbreviations:
    #   sa: sample annotations
    #   ga: gene annotations
    #
    def __init__(self, data_dir: str | None = None) -> None:
        # To override for tests
        self.DATA_DIR = data_dir or settings.DATA_DIR
        # TOEDIT: Determines the filename of the species list
        self.species_list_filename = "species_list.tsv"
        # TOEDIT: Determines the directory names for the data files
        self.tpm_dirname = "tpm-matrices"
        self.sa_dirname = "sample-annotations"
        self.ga_dirname = "gene-annotations"
        self.sa_assignment_dirname = "sample-annotations-assignment"
        self.ga_assignment_dirname = "gene-annotations-assignment"

    def get_species_list_filepath(self) -> str:
        return f"{self.DATA_DIR}{self.species_list_filename}"

    def get_sa_filepath(self, sa_type: str) -> str:
        return f"{self.DATA_DIR}{self.sa_dirname}/{sa_type}.tsv"

    def get_ga_filepath(self, ga_type: GeneAnnotationType | str) -> str:
        ga_type = self._stringify_if_enum(ga_type)
        return f"{self.DATA_DIR}{self.ga_dirname}/{ga_type}.tsv"

    def get_tpm_filepath(self, taxid: int) -> str:
        # Write an if else check if some files are gunzipped and some are not
        return f"{self.DATA_DIR}{self.tpm_dirname}/taxid{taxid}_tpm.tsv.gz"

    def get_sa_assignment_filepath(self, sa_type: str, taxid: int) -> str:
        return f"{self.DATA_DIR}{self.sa_assignment_dirname}/{sa_type}/taxid{taxid}_{sa_type}.tsv"

    def get_ga_assignment_filepath(self, ga_type: GeneAnnotationType | str, taxid: int) -> str:
        ga_type = self._stringify_if_enum(ga_type)
        return f"{self.DATA_DIR}{self.ga_assignment_dirname}/{ga_type}/taxid{taxid}_{ga_type}.tsv"

    @staticmethod
    def _stringify_if_enum(type_val: Enum | str) -> str:
        if isinstance(type_val, Enum):
            return type_val.value
        return type_val


filepath_definitions = FilepathDefinitions()
test_filepath_definitions = FilepathDefinitions(data_dir=settings.TEST_DATA_DIR)

__all__ = ["filepath_definitions", "test_filepath_definitions"]
