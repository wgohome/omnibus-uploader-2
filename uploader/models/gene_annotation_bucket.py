from pydantic import Field
from uploaders.models.base import CustomBaseModel, DocumentBaseModel, PyObjectId


class GeneAnnotationBucketBase(CustomBaseModel):
    ga_id: PyObjectId  # Ref to GeneAnnotation
    tax: int = Field(alias="taxid")
    gene_ids: list[PyObjectId] = list()

    # Push gene id in to array if it is not already inside
    def append_gene_id(self, gene_id: PyObjectId) -> bool:
        if len(set([gene_id]) - set(self.gene_ids)) == 0:
            # gene_id already in the list
            return False
        self.gene_ids.append(gene_id)
        return True


class GeneAnnotationBucketDoc(GeneAnnotationBucketBase, DocumentBaseModel):
    class Mongo:
        collection_name: str = "gene_annotation_buckets"
