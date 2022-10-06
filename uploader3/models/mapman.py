from pydantic import Field, validator
from uploaders.models import CustomBaseModel


# To be embedded in GeneAnnotation
class MapmanDetail(CustomBaseModel):
    desc: str = Field(alias="description")


# To parse MAPMAN bin assignment files for each species
class MapmanAssignmentRow(CustomBaseModel):
    gene_label: str
    ga_label: str

    @validator("gene_label", "ga_label", pre=True, always=True)
    def upcase_label(cls, v):
        return v.upper()

    def __eq__(self, other):
        return self.gene_label == other.gene_label and self.ga_label == other.ga_label


__all__ = ["MapmanAssignmentRow", "MapmanDetail"]
