import json
import os

from config import settings


def get_filepath(
    taxid: int,
    sub_dir: str,
    base_dir: str = settings.DATA_DIR
) -> str:
    sub_dir = sub_dir.strip("/")
    dir_path = f"{base_dir}{sub_dir}"
    files = [file for file in os.listdir(dir_path) if f"taxid{taxid}" in file]
    if len(files) == 0:
        raise FileNotFoundError(f"File for taxid{taxid} not found in {dir_path}")
    if len(files) > 1:
        raise FileExistsError(f"Multiple files for taxid {taxid} present in {dir_path}")
    return f"{dir_path}/{files[0]}"


def get_gene_label_map(taxid: int, dir_path: str = settings.GENE_LABEL_MAPPING_DIR) -> dict[str, str]:
    return json.load(open(f"{dir_path}/taxid{taxid}.json", "r"))
