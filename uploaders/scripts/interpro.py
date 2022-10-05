from config import settings
from uploaders.aggregators import (
    GeneAnnotationAggregator,
    GeneAnnotationBucketAggregator,
)
from uploaders.models import (
    GeneAnnotationType,
    GeneAnnotationBucketDoc,
    GeneAnnotationBase,
    MapmanDetail,
)
from uploaders.parsers import (
    InterproParser,
    MapmanAssignmentParser,
    MapmanDetailParser,
)
from uploaders.utilities.db_queries import (
    get_species_id_map,
    get_gene_id_map,
    update_gene_doc_with_sa_id,
    upload_many_docs,
    upload_one_doc,
)
from uploaders.utilities.db_setup import get_db
from uploaders.utilities.helpers import get_filepath

DB = get_db()
species_id_map = get_species_id_map(DB)

#
# Some assumptions:
# - Gene labels in Interpro files are already cleaned to match those in TPM matrices
# - Each row in Interpro file is a unique (gene, PFAM) pair, no repeat
# - Last column is either "-" or comma-sep string of GO terms
#

print("AGGREGATING INTERPRO annotations")
ga_aggregator = GeneAnnotationAggregator(type=GeneAnnotationType.INTERPRO)
print("taxid\tgenes_aggregated\tgenes_in_db\t\% annotated")
for taxid, species_id in list(species_id_map.items())[:10]:
    # 29729 is GOSAR
    if taxid in [29729]:
        continue
    # For getting DB's id of genes
    gene_id_map = get_gene_id_map(species_id, DB)
    interpro_parser = InterproParser(
        get_filepath(taxid=taxid, sub_dir="interpro-annotations")
    )
    ga_bucket_aggregator = GeneAnnotationBucketAggregator(taxid=taxid)
    gene_ids_aggregated = set()
    for row in interpro_parser.parse():
        ga_bucket_aggregator.append_from_row(
            gene_id=gene_id_map[row.gene_label],
            ga_id=ga_aggregator.register_row(row)
        )
        gene_ids_aggregated.add(gene_id_map[row.gene_label])
    print(f"{taxid}\t{len(gene_ids_aggregated)}\t{len(gene_id_map)}\t{len(gene_ids_aggregated)/len(gene_id_map)}")
    # Upload all GeneAnnotationBucket
    upload_many_docs(
        docs=[bucket.dict() for bucket in ga_bucket_aggregator.get_buckets()],
        model=GeneAnnotationBucketDoc
    )
    update_gene_doc_with_sa_id(ga_bucket_aggregator.gene_ga_map)


print("AGGREGATING MAPMAN annotations")
ga_aggregator = GeneAnnotationAggregator(type=GeneAnnotationType.MAPMAN)
# For MAPMAN, push all the Gene Annotation into the DB first
mapman_detail_parser = MapmanDetailParser(f"{settings.DATA_DIR}bin_details.tsv")
ga_aggregator.push_gene_annotations(
    (ga_aggregator.mapman_row_to_ga(row) for row in mapman_detail_parser.parse())
)
print("taxid\tgenes_aggregated\tgenes_in_db\t\% annotated")
for taxid, species_id in list(species_id_map.items())[:10]:
    # 29729 is GOSAR
    if taxid in [29729]:
        continue
    # For getting DB's id of genes
    gene_id_map = get_gene_id_map(species_id, DB)
    mapman_parser = MapmanAssignmentParser(
        get_filepath(taxid=taxid, sub_dir="bin-assignments")
    )
    ga_bucket_aggregator = GeneAnnotationBucketAggregator(taxid=taxid)
    gene_ids_aggregated = set()
    for row in mapman_parser.parse():
        ga_bucket_aggregator.append_from_row(
            gene_id=gene_id_map[row.gene_label],
            ga_id=ga_aggregator.get_ga_id(row.bincode)
        )
        gene_ids_aggregated.add(gene_id_map[row.gene_label])
    print(f"{taxid}\t{len(gene_ids_aggregated)}\t{len(gene_id_map)}\t{len(gene_ids_aggregated)/len(gene_id_map)}")
    # Upload all GeneAnnotationBucket
    upload_many_docs(
        docs=[bucket.dict() for bucket in ga_bucket_aggregator.get_buckets()],
        model=GeneAnnotationBucketDoc
    )
    update_gene_doc_with_sa_id(ga_bucket_aggregator.gene_ga_map)
