from pydantic import validator
from uploader.models.base import CustomBaseModel


class TpmRow(CustomBaseModel):
    # For each row in TPM matrix
    gene_label: str
    tpm_values: list[float]

    @validator("gene_label", pre=True, always=True)
    def upcase_label(cls, v):
        return v.upper()

    @validator("tpm_values", pre=True, always=True)
    def round_tpm_floats(cls, v):
        return [round(float(item), 3) for item in v]


__all__ = ["TpmRow"]
