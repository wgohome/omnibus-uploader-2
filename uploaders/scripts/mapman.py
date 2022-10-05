from collections import defaultdict
from config import settings

from uploaders.aggregators import MapmanAggregator
from uploaders.models import mapman
from uploaders.models.base import PyObjectId
from uploaders.parsers import MapmanAssignmentParser, MapmanDetailParser
from uploaders.utilities.db_queries import (
    get_species_id_map,
    get_gene_id_map,
    update_gene_doc_with_sa_id,
    upload_ga_docs,
)
from uploaders.utilities.db_setup import get_db
from uploaders.utilities.helpers import get_filepath

DB = get_db()

species_id_map = get_species_id_map(DB)
mapman_aggregator = MapmanAggregator()
mapman_detail_parser = MapmanDetailParser(f"{settings.DATA_DIR}bin_details.tsv")
mapman_aggregator.init_mapman_bins(mapman_detail_parser.parse())
print("AGGREGATING mapman annotations")
print("taxid\tgenes_aggregated\tgenes_in_db\t\% annotated")


for taxid, species_id in species_id_map.items():
    # 29729 is GOSAR
    if taxid in [29729]:
        continue
    # For getting DB id of genes
    gene_id_map = get_gene_id_map(species_id, DB)
    mapman_assignment_parser = MapmanAssignmentParser(
        get_filepath(taxid=taxid, sub_dir="bin-assignments")
    )
    mapman_aggregator.append_from_whole_species(
        taxid=taxid,
        rows=mapman_assignment_parser.parse(),
        gene_id_map=gene_id_map,
    )


total_docs = 7517
chunk = 1
chunk_size = 50
while mapman_aggregator.rows_exhausted is False:
    docs = mapman_aggregator.get_docs_from_chunks(chunk_size=chunk_size)
    docs = upload_ga_docs(docs, DB)
    gene_id_to_ga_map: dict[PyObjectId, list[PyObjectId]] = defaultdict(list)
    for doc in docs:
        for gene_id in doc["gene_ids"]:
            gene_id_to_ga_map[gene_id].append(doc["_id"])
    update_gene_doc_with_sa_id(gene_id_to_ga_map, DB)
    chunk += 1
    print(f"Done with chunk #{chunk} / {total_docs / chunk_size}")
