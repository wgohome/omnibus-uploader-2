import json
from uploader.readers.helpers import get_filepath
from uploader.readers.rows_readers import InterproReader


taxid = 2711

gene_label_map_path = get_filepath(taxid=taxid, sub_dir="pep-label-mappings")
gene_label_map = json.loads(open(gene_label_map_path, "r").read())
InterproReader()