from typing import Generator, Iterator

from uploaders.models import (
    CustomBaseModel,
    PyObjectId,
    GeneAnnotationBase,
    GeneAnnotationDoc,
    GeneAnnotationType,
    MapmanDetail,
    MapmanDetailRow,
)
from uploaders.utilities.db_queries import get_gene_annotations_by_type, upload_one_doc


#
# Global aggregator across all species
#
class GeneAnnotationAggregator:
    def __init__(self, type: GeneAnnotationType):
        self.type: str = type.value.upper()  # This instance scoped to one GA type (eg. INTERPRO)
        self.ga_dict: dict[str, GeneAnnotationDoc] = self._get_gas_from_db()
        self.iterator: Generator | None = None

    def _get_gas_from_db(self) -> dict[str, GeneAnnotationDoc]:
        docs = get_gene_annotations_by_type(self.type)
        return {
            doc["label"]: GeneAnnotationDoc(**doc)
            for doc in docs
        }

    def mapman_row_to_ga(self, mapman_row: MapmanDetailRow) -> GeneAnnotationBase:
        return GeneAnnotationBase(
            type=GeneAnnotationType.MAPMAN.value,
            label=mapman_row.label,
            details=MapmanDetail(
                name=mapman_row.name,
                description=mapman_row.desc,
            ).dict()
        )

    def push_gene_annotations(self, gene_annotations: Iterator[GeneAnnotationBase]) -> None:
        for gene_annotation in gene_annotations:
            if self.ga_dict.get(gene_annotation.label) is not None:
                continue
            doc = gene_annotation.dict()
            upload_one_doc(doc=doc, model=GeneAnnotationDoc)
            self.ga_dict[gene_annotation.label] = GeneAnnotationDoc(**doc)

    def register_row(self, row: CustomBaseModel) -> PyObjectId:
        # If GeneAnnotationDoc does not exist in DB yet,
        #   Create and push to DB
        #   Maintain state in self.ga_dict
        if self.ga_dict.get(row.label) is None:
            ga_base = GeneAnnotationBase(
                type=self.type,
                label=row.label,
                details=row.details.dict(),
            )
            inserted_doc = upload_one_doc(doc=ga_base.dict(), model=GeneAnnotationDoc)
            self.ga_dict[row.label] = GeneAnnotationDoc(_id=inserted_doc["_id"], **ga_base.dict())
        # If GeneAnnotationDoc already exists in db, just get back the _id
        return self.ga_dict[row.label].id

    def get_ga_id(self, label: str) -> PyObjectId:
        return self.ga_dict[label].id
