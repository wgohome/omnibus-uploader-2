from enum import Enum
from pydantic import validator
from uploaders.models.base import CustomBaseModel, DocumentBaseModel, PyObjectId


class GeneAnnotationType(Enum):
    INTERPRO = "INTERPRO"
    MAPMAN = "MAPMAN"


class GeneAnnotationBase(CustomBaseModel):
    type: str  # Annotation type, eg Gene Ontology, Mapman, Interpro, etc
    label: str   # Annotation identifier to be indexed for uniqueness with type
    details: dict | None

    @validator("type", "label", pre=True)
    def upcase_type(cls, v):
        return v.upper()


class GeneAnnotationDoc(GeneAnnotationBase, DocumentBaseModel):
    class Mongo:
        collection_name: str = "gene_annotations"
