from pydantic import Field, validator
from uploader.models import CustomBaseModel


# To be embedded in GeneAnnotation
class MapmanDetail(CustomBaseModel):
    desc: str = Field(alias="description")


__all__ = ["MapmanDetail"]
