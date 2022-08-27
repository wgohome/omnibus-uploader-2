from uploader.main import get_gene_id_map, get_species_id_map, DB
from uploader.readers.aggregators import TpmBySampleAggregator
from uploader.readers.helpers import get_filepath
from uploader.readers.map_readers import PlantOntologyMap
from uploader.readers.rows_readers import TpmReader


species_id_map = get_species_id_map(DB)
taxid = 4097
species_id = species_id_map[taxid]
gene_id_map = get_gene_id_map(species_id, DB)

po_map = PlantOntologyMap(get_filepath(taxid=taxid, sub_dir="sample-annotations")).parse()

if po_map == {}:
    print(f"NO DATA: taxid{taxid} has no PO annotation ...\nNext species...\n")

tpm_reader = TpmReader(get_filepath(taxid=taxid, sub_dir="tpm-matrices"))
tpm_aggregator = TpmBySampleAggregator(
    species_id=species_id,
    annotation_type="PO",
    annotation_map=po_map,
    sample_labels=tpm_reader.get_sample_labels(),
    row_iterator=tpm_reader.parse(),
    gene_id_map=gene_id_map,
)
# while tpm_aggregator.rows_exhausted is False:
#     docs = tpm_aggregator.get_docs_from_chunks(chunk_size=250)
#     if docs == []:
#         # import pdb; pdb.set_trace()
#     else:
#         print("list ok")
