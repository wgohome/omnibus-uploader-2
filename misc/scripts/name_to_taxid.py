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


def rename_abbr_to_taxid(data_dir) -> None:
    species_map = SpeciesMap("/home/william/data-omnibus/species_list.tsv").parse()
    abbr_dict = {make_abbr(name): taxid for taxid, name in species_map.items()}
    for filename in os.listdir(data_dir):
        abbr = re.match(r"^([A-Z]{5})_pep$", filename).group(1)
        if abbr_dict.get(abbr) is None:
            print(f"{abbr} is missing from {data_dir}")
            continue
        taxid = abbr_dict[abbr]
        new_name = f"taxid{taxid}.pep.fasta"
        print(f"Changing from {filename} to {new_name}")
        os.rename(f"{data_dir}/{filename}", f"{data_dir}/{new_name}")


# data_dir = "/home/william/Downloads/pep"
# rename_abbr_to_taxid(data_dir)


def get_gene_labels():
    DB = get_db()
    species_id_map = get_species_id_map(DB)
    data_dir = "/home/william/Downloads/pep"
    for taxid, species_id in species_id_map.items():
        if str(taxid) == "29729":
            continue
        filepath = f"{data_dir}/taxid{taxid}.pep.fasta"
        # Collect all pep gene ids
        pep_gene_ids = []
        with open(filepath, "r") as file:
            line = file.readline()
            while line:
                if line.startswith(">"):
                    gene_label = line.split()[0].lstrip(">").strip()
                    pep_gene_ids.append(gene_label)
                line = file.readline()
        # Collect all tpm gene ids
        genes_reader = GenesReader(
            filepath=get_filepath(taxid=taxid, sub_dir="tpm-matrices"),
            species_id=species_id
        )
        tpm_gene_ids = [gene["label"] for gene in genes_reader.parse()]
        # Try to match them tgt
        out_dir = "/home/william/code/diamond-testing/data"
        with open(f"{out_dir}/pep/taxid{taxid}.txt", "w") as file:
            file.write("\n".join(pep_gene_ids) + "\n")
        with open(f"{out_dir}/tpm/taxid{taxid}.txt", "w") as file:
            file.write("\n".join(tpm_gene_ids) + "\n")
        print(f"Written for taxid {taxid}")


# get_gene_labels()
