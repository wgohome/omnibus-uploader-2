# To parse INTERPRO label (PFAM) assignment files for each species
from pydantic import validator

from uploader.models import CustomBaseModel


class GeneAnnotationAssignmentRow(CustomBaseModel):
    gene_label: str
    ga_label: str

    @validator("gene_label", "ga_label", pre=True, always=True)
    def upcase_label(cls, v):
        return v.upper()

    def __eq__(self, other):
        return self.gene_label == other.gene_label and self.ga_label == other.ga_label


__all__ = ["GeneAnnotationAssignmentRow"]
