from datetime import datetime
from pydantic import Field, validator

from . import (
    CustomBaseModel,
    DocumentBaseModel,
)


class Cds(CustomBaseModel):
    source: str  # Eg: "Ensembl"
    url: str | None = None

    @validator("source", pre=True, always=True)
    def upcase_label(cls, v):
        return v.upper()


class QcStat(CustomBaseModel):
    logp: float = Field(0, alias="log_processed")
    palgn: int = Field(0, alias="p_pseudoaligned", ge=0, le=100)


class SpeciesBase(CustomBaseModel):
    tax: int = Field(alias="taxid")
    name: str
    alias: list[str] = list()  # Must be a factory for mutable objects
    cds: Cds
    # QC stats should not be set on species creation, but on uploading TPM
    qc_stat: QcStat = Field(default_factory=QcStat)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class SpeciesDoc(SpeciesBase, DocumentBaseModel):
    class Mongo:
        collection_name: str = "species"


__all__ = ["SpeciesBase", "SpeciesDoc", "Cds", "QcStat"]
