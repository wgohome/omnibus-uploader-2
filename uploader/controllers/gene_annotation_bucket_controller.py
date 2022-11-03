from collections import defaultdict
from typing import Iterable
from pymongo.database import Database

from uploader.models import (
    PyObjectId,
    GeneAnnotationType,
    GeneAnnotationBucketBase,
    GeneAnnotationBucketDoc,
    GeneAnnotationAssignmentRow,
)
from uploader.utilities.db_setup import get_db
from uploader.utilities.db_queries import (
    upload_many_docs,
)


#
# Refer to the GeneAnnotation entity definition
# For assignments per species per gene, go to controller for GeneAnnotationBucket
# For variation in data schema for different types, to be handled by parsers
#
class GeneAnnotationBucketController:
    def __init__(
        self,
        species_id: PyObjectId,
        ga_type: GeneAnnotationType,
        ga_id_map: dict[str, PyObjectId],
        gene_id_map: dict[str, PyObjectId],
        db: Database = get_db()
    ) -> None:
        # Instance scoped by gene annotation type & species
        self.species_id = species_id
        self.ga_type: str = ga_type.value
        # Get existing DB ids
        self.ga_id_map = ga_id_map
        self.gene_id_map = gene_id_map
        # Others
        self.model = GeneAnnotationBucketDoc
        self.db = db
        # ga_label -> GA bucket mapping
        self._buckets: dict[str, GeneAnnotationBucketBase] = {}

    def append_row_to_bucket(self, assignment_row: GeneAnnotationAssignmentRow) -> None:
        # We assume that the ga label and gene label do exist and is already checked
        ga_id: PyObjectId = self.ga_id_map[assignment_row.ga_label]
        gene_id: PyObjectId = self.gene_id_map[assignment_row.gene_label]
        # Check if bucket already exist
        bucket = self._buckets.get(assignment_row.ga_label)
        if bucket is not None:
            bucket.append_gene_id(gene_id)
            return None
        self._buckets[assignment_row.ga_label] = GeneAnnotationBucketBase(
            ga_id=ga_id,
            spe_id=self.species_id,
            gene_ids=[gene_id]
        )

    def append_all_rows_to_buckets(self, rows: Iterable[GeneAnnotationAssignmentRow]) -> None:
        for ga_assignment in rows:
            self.append_row_to_bucket(ga_assignment)

    def upload_many(self, docs: Iterable[GeneAnnotationBucketBase]) -> None:
        data_dicts = upload_many_docs(
            data_dicts=[doc.dict() for doc in docs],
            model=self.model,
            db=self.db
        )

    def upload_many_from_buckets(self) -> None:
        self.upload_many(self._buckets.values())

    def get_gene_ga_refs(self) -> dict[PyObjectId, list[PyObjectId]]:
        if len(self._buckets) == 0:
            print("No gene annotations collected yet")
        gene_to_ga_map: dict[PyObjectId, list[PyObjectId]] = defaultdict(list)
        for bucket in self._buckets.values():
            for gene_id in bucket.gene_ids:
                gene_to_ga_map[gene_id].append(bucket.ga_id)
        if len(gene_to_ga_map) == 0:
            print("No gene ids in gene annotations collected yet")
        return gene_to_ga_map
