from pydantic import Field, validator
from uploaders.models import CustomBaseModel


# To be embedded in GeneAnnotation
class MapmanDetail(CustomBaseModel):
    name: str
    desc: str = Field(alias="description")


# To parse from single file of details for all mapman bins
class MapmanDetailRow(CustomBaseModel):
    label: str
    name: str
    desc: str = Field(alias="description")

    @validator("label", pre=True, always=True)
    def upcase_label(cls, v):
        return v.upper()


# To parse Mapman bin assignment files for each species
class MapmanAssignmentRow(CustomBaseModel):
    gene_label: str
    bincode: str

    @validator("gene_label", pre=True, always=True)
    def upcase_label(cls, v):
        return v.upper()


__all__ = ["MapmanAssignmentRow", "MapmanDetailRow", "MapmanDetail"]
