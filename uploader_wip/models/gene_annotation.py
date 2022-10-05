from pydantic import validator
from uploader.models.base import CustomBaseModel, DocumentBaseModel, PyObjectId


class GeneAnnotationBase(CustomBaseModel):
    type: str  # Annotation type, eg Gene Ontology, Mapman
    label: str   # Annotation identifier to be indexed for uniqueness with type
    details: dict | None
    gene_ids: list[PyObjectId] = list()

    @validator("type", "label", pre=True)
    def upcase_type(cls, v):
        return v.upper()


class GeneAnnotationDoc(GeneAnnotationBase, DocumentBaseModel):
    class Mongo:
        collection_name: str = "gene_annotations"
