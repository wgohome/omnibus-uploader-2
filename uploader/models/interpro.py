from pydantic import validator
from uploader.models import CustomBaseModel


# To be embedded in GeneAnnotation
class InterproDetail(CustomBaseModel):
    go_terms: list[str]

    @validator("go_terms", pre=True, always=True)
    def upcase_list_of_labels(cls, v):
        return [item.upper() for item in v]


__all__ = ["InterproDetail"]
