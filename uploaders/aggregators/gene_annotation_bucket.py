from collections import defaultdict
from typing import Iterator
from uploaders.aggregators.gene_annotation import GeneAnnotationAggregator
from uploaders.models import (
    GeneAnnotationBucketBase,
    PyObjectId,
)
from uploaders.parsers.base_parser import BaseParser


class GeneAnnotationBucketAggregator:
    def __init__(self, taxid: int):
        self.taxid: int = taxid
        # Map of ga_id to ga_bucket doc,
        # which each hold a list of genes in this species attached to that ga
        self.ga_ga_bucket_map: dict[PyObjectId, GeneAnnotationBucketBase] = {}
        # Map of gene_id to ga_id
        # to be used to update gene docs in the DB at the end of aggregation
        self.gene_ga_map: dict[PyObjectId, list[PyObjectId]] = defaultdict(list)

    def append_from_row(self, gene_id: PyObjectId, ga_id: PyObjectId) -> None:
        if self.ga_ga_bucket_map.get(ga_id) is None:
            self.ga_ga_bucket_map[ga_id] = GeneAnnotationBucketBase(
                taxid=self.taxid,
                ga_id=ga_id,
                gene_ids=[]
            )
        self.gene_ga_map[gene_id].append(ga_id)
        self.ga_ga_bucket_map[ga_id].gene_ids.append(gene_id)

    def get_buckets(self) -> Iterator[GeneAnnotationBucketBase]:
        return (bucket for bucket in self.ga_ga_bucket_map.values())

    # get_gene_id_list
