from uploader.main import get_species_id_map
from uploader.readers.helpers import get_filepath
from uploader.setup_db import get_db

DB = get_db()
species_id_map = get_species_id_map(DB)

for taxid in species_id_map.keys():
    for sub_dir in ["sample-annotations", "tpm-matrices", "interpro-annotations"]:
        try:
            filepath = get_filepath(taxid=taxid, sub_dir=sub_dir)
        except FileNotFoundError as e:
            print(e)
            # print(f"MISSING FILE: {sub_dir} for taxid{taxid}")
        except FileExistsError as e:
            print(e)
