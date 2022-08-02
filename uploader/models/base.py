from bson import ObjectId
from pydantic import BaseModel, Extra


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

#
# For all models
#
class CustomBaseModel(BaseModel):
    class Config:
        allow_population_by_field_name = True
        #   Warning for potential leakages of attributes
        #   Acceptable risks for now
        json_encoders = {ObjectId: str}
        #   Note that we encode ObjectId, not PyObjectId because
        #   that is how we decode it in validate classmethod
        extra = Extra.forbid
        validate_assignment = True
        #   Allows validation when assigning new value to a field, eg:
        #       item.number = 1.23456 -> will perform the rounding as specified in validator

    # # For dict to be dumped into DB for creation
    # def dict_for_db(self) -> dict:
    #     # `exclude_none=True` allows
    #     # - downstream models to set the default values themselves
    #     # - not to store redudant fields (eg in polymorphic models)
    #     # `by_alias=False` as
    #     # - as we define field names as db keys, and alias as client facing keys
    #     #   as recommended by Samuel Colvin (Pydantic owner)
    #     return self.dict(exclude_none=True, by_alias=False)

    # # For dict to be dumped into DB for update of set fields only
    # def dict_for_update(self) -> dict:
    #     # To avoid overriding existing fields in the DB with default values on update
    #     return self.dict(exclude_unset=True, by_alias=True)


#
# Only for models representing DB document schema
#
class DocumentBaseModel(BaseModel):
    class Mongo:
        collection_name: str
