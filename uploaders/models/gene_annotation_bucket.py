from pydantic import Field
from uploaders.models.base import CustomBaseModel, DocumentBaseModel, PyObjectId


class GeneAnnotationBucketBase(CustomBaseModel):
    ga_id: PyObjectId  # Ref to GeneAnnotation
    tax: int = Field(alias="taxid")
    gene_ids: list[PyObjectId] = list()


class GeneAnnotationBucketDoc(GeneAnnotationBucketBase, DocumentBaseModel):
    class Mongo:
        collection_name: str = "gene_annotation_buckets"
