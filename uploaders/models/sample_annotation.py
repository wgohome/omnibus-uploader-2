from pydantic import validator, Field

from uploaders.models.base import CustomBaseModel, DocumentBaseModel, PyObjectId


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


class Sample(CustomBaseModel):
    label: str = Field(alias="sample_label")
    tpm: float = Field(alias="tpm_value")

    @validator("label", pre=True, always=True)
    def upcase_label(cls, v):
        return v.upper()

    @validator("tpm", pre=True, always=True)
    def round_float(cls, v):
        return round(float(v), 3)


class SampleAnnotationBase(CustomBaseModel):
    spe_id: PyObjectId = Field(alias="species_id")
    g_id: PyObjectId = Field(alias="gene_id")
    type: str
    label: str
    avg_tpm: float = 0
    spm: float = 0
    samples: list[Sample]

    @validator("type", "label", pre=True, always=True)
    def upcase_label(cls, v):
        return v.upper()

    @validator("avg_tpm", "spm", pre=True, always=True)
    def round_float(cls, v):
        return round(float(v), 3)


class SampleAnnotationDoc(SampleAnnotationBase, DocumentBaseModel):
    class Mongo:
        collection_name: str = "sample_annotations"


__all__ = ["SampleAnnotationDoc", "Sample", "TpmRow"]
