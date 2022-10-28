from pydantic import Field, validator

from uploader.models import (
    CustomBaseModel,
    DocumentBaseModel,
    PyObjectId,
)


class GeneBase(CustomBaseModel):
    label: str
    #   label refers to the main gene identifier we use in the TPM matrix
    #   indexed for search by label
    alias: list[str] = list()
    #   alias - other alternative gene identifiers
    spe_id: PyObjectId = Field(alias="species_id")
    ga_ids: list[PyObjectId] = Field(default_factory=list, alias="annotation_ids")
    #   reference to gene_annotations collection

    @validator("label", pre=True, always=True)
    def upcase_label(cls, v):
        return v.upper()


class GeneDoc(GeneBase, DocumentBaseModel):
    class Mongo:
        collection_name: str = "genes"


__all__ = ["GeneBase", "GeneDoc"]
