from enum import Enum
from pydantic import validator
from uploaders.models.base import CustomBaseModel, DocumentBaseModel


class GeneAnnotationType(Enum):
    INTERPRO = "INTERPRO"
    MAPMAN = "MAPMAN"


class GeneAnnotationBase(CustomBaseModel):
    type: str  # Annotation type, eg MAPMAN, INTERPRO, etc
    label: str   # Annotation identifier to be indexed for uniqueness with type
    name: str  # Default name to be shown for frontend
    details: dict | None

    # Name no need to uppercase bcos not using it as a search filter
    @validator("type", pre=True, always=True)
    def upcase_type(cls, v):
        if isinstance(v, GeneAnnotationType):
            v = v.value
        return v.upper()

    @validator("label", pre=True, always=True)
    def upcase_label(cls, v):
        return v.upper()


class GeneAnnotationDoc(GeneAnnotationBase, DocumentBaseModel):
    class Mongo:
        collection_name: str = "gene_annotations"
