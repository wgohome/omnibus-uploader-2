import os
import re

from uploader.main import get_gene_id_map, get_species_id_map
from uploader.readers.helpers import get_filepath
from uploader.readers.map_readers import SpeciesMap
from uploader.readers.rows_readers import GenesReader
from uploader.setup_db import get_db


#
# For checking gene ids in database same as gene ids in fasta/tpm files
#

def print_gene_labels_compare() -> None:
    DB = get_db()
    species_id_map = get_species_id_map(DB)
    for taxid, species_id in species_id_map.items():
        gene_id_map = get_gene_id_map(species_id, DB)
        genes_in_db = list(gene_id_map.keys())[:150:50]
        print(f"TAXID {taxid}: \n\t{genes_in_db}")

        genes_reader = GenesReader(
            filepath=get_filepath(taxid=taxid, sub_dir="tpm-matrices"),
            species_id=species_id
        )
        genes_on_file = [gene["label"] for gene in [*genes_reader.parse()][:150:50]]
        print(f"\t{genes_on_file}")
        print()



#
# For changing file names from abbreviation to taxid based
#

def make_abbr(name: str) -> str:
    assert len(name.split()) == 2
    genus, species = name.upper().split()
    abbr = genus[:3] + species[:2]
    return abbr


def rename_abbr_to_taxid() -> None:
    species_map = SpeciesMap("/home/william/data-omnibus/species_list.tsv").parse()
    abbr_dict = {make_abbr(name): taxid for taxid, name in species_map.items()}
    fasta_dir = "/home/william/Downloads/FASTA"
    for filename in os.listdir(fasta_dir):
        abbr = re.match(r"^([A-Z]{5}).fasta$", filename).group(1)
        if abbr_dict.get(abbr) is None:
            print(f"{abbr} is missing from {fasta_dir}")
            continue
        taxid = abbr_dict[abbr]
        new_name = f"taxid{taxid}.fasta"
        print(f"Changing from {filename} to {new_name}")
        os.rename(f"{fasta_dir}/{filename}", f"{fasta_dir}/{new_name}")
