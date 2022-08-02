from pydantic import Field, validator
from uploader.models.base import CustomBaseModel


class InterproDetail(CustomBaseModel):
    desc: str = Field(alias="description")
    go_terms: list[str]

    @validator("go_terms", pre=True, always=True)
    def upcase_list_of_labels(cls, v):
        return [item.upper() for item in v]


class InterproRow(CustomBaseModel):
    gene_label: str
    label: str
    details: InterproDetail

    @validator("gene_label", "label", pre=True, always=True)
    def upcase_label(cls, v):
        return v.upper()

    def __eq__(self, other):
        return self.gene_label == other.gene_label and self.label == other.label
