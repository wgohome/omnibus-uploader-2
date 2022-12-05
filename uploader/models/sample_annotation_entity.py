from enum import Enum
from pydantic import validator
from uploader.models import CustomBaseModel, DocumentBaseModel, PyObjectId, SampleAnnotationType


class SampleAnnotationEntityBase(CustomBaseModel):
    type: str  # Annotation type, eg PO, etc
    label: str
    name: str
    spe_ids: list[PyObjectId] = list()

    @validator("type", pre=True, always=True)
    def upcase_type(cls, v):
        if isinstance(v, SampleAnnotationType):
            v = v.value
        return v.upper()

    @validator("label", pre=True, always=True)
    def upcase_label(cls, v):
        return v.upper()

    @validator("name", pre=True, always=True)
    def capitalize_name(cls, v):
        return v.capitalize()


class SampleAnnotationEntityDoc(SampleAnnotationEntityBase, DocumentBaseModel):
    class Mongo:
        collection_name: str = "sample_annotation_entities"
