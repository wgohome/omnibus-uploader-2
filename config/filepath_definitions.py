from .settings import settings

# File paths should be relative to settings.DATA_DIR

filepath_definitions = {
    "species_list": {
        "sub_dirs": [],
        "get_filename": lambda: "species_list.tsv",
    },
    "tpm_matrices": {
        "sub_dirs": ["tpm-matrices"],
        "get_filename": lambda taxid: f"taxid{taxid}_tpm.tsv.gz",  # TODO:make all gz
    },
    "sample_annotations": {
        "sub_dirs": ["sample-annotations"],
        "get_filename": lambda taxid: f"taxid{taxid}_po.tsv",
    },
    "interpro_annotations": {
        "sub_dirs": ["interpro-annotations"],
        "get_filename": lambda taxid: f"taxid{taxid}_interpro.tsv",
    },
    # "mapman_annotations": {
    #     "sub_dirs": ["mapman-annotations"],
    #     "get_filename": lambda taxid: f"taxid{taxid}_mapman.tsv",
    # },
}
