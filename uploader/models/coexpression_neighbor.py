from pydantic import validator

from uploader.models import CustomBaseModel, PyObjectId


class CoexpressionNeighbor(CustomBaseModel):
    gene_id: PyObjectId
    pcc: float

    @validator("pcc", pre=True, always=True)
    def round_float(cls, v):
        return round(float(v), 3)


class CoexpressionRow(CustomBaseModel):
    gene_label: str
    neighbors: list[CoexpressionNeighbor]

    @validator("gene_label", pre=True, always=True)
    def upcase_label(cls, v):
        return v.upper()
