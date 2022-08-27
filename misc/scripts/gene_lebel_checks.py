from uploader.main import get_gene_id_map, get_species_id_map
from uploader.readers.helpers import get_filepath
from uploader.readers.rows_readers import InterproReader
from uploader.setup_db import get_db

DB = get_db()
species_id_map = get_species_id_map(DB)
for taxid, species_id in species_id_map.items():
    # Gene labels from DB (genes collection)
    gene_id_map = get_gene_id_map(species_id, DB)
    db_gene_labels = set(gene_id_map.keys())
    # Gene labels form Interpro output files
    interpro_reader = InterproReader(get_filepath(taxid=taxid, sub_dir="interpro-annotations"))
    interpro_gene_labels = set(doc.gene_label for doc in interpro_reader.parse())
    # Compare gene labels in DB to gene labels in Interpro files
    import pdb; pdb.set_trace()
