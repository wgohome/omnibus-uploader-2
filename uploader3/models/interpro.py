from pydantic import validator
from uploaders.models import CustomBaseModel


# To be embedded in GeneAnnotation
class InterproDetail(CustomBaseModel):
    go_terms: list[str]

    @validator("go_terms", pre=True, always=True)
    def upcase_list_of_labels(cls, v):
        return [item.upper() for item in v]


# To parse INTERPRO label (PFAM) assignment files for each species
class InterproAssignmentRow(CustomBaseModel):
    gene_label: str
    ga_label: str

    @validator("gene_label", "ga_label", pre=True, always=True)
    def upcase_label(cls, v):
        return v.upper()

    def __eq__(self, other):
        return self.gene_label == other.gene_label and self.ga_label == other.ga_label


__all__ = ["InterproAssignmentRow", "InterproDetail"]
