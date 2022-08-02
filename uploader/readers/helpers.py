import os
from config import settings
import re


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


def strip_gene_isoform(label: str) -> str:
    # Identify isoform suffix by: `.XX` dot and one or two characters at the end of the label
    # If present, strip the isoform suffix
    match = re.match(r"(^.+)\.[^\.]{1,2}$", label)
    if match is None:
        return label
    return match.group(1)
