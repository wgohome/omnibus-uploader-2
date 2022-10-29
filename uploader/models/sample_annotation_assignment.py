from pydantic import validator

from uploader.models import CustomBaseModel


class SampleAnnotationAssignmentRow(CustomBaseModel):
    sample_label: str
    sa_label: str

    @validator("sample_label", "sa_label", pre=True, always=True)
    def upcase_label(cls, v):
        return v.upper()

    def __eq__(self, other):
        return self.sample_label == other.sample_label and self.sa_label == other.sa_label


__all__ = ["SampleAnnotationAssignmentRow"]
