from typing import Iterator
from pymongo.database import Database
from pymongo.errors import BulkWriteError

from uploader3.models import (
    PyObjectId,
    SpeciesDoc,
    GeneDoc,
    GeneAnnotationDoc,
    CustomBaseModel,
    DocumentBaseModel,
)
from uploader3.utilities.db_setup import get_db, get_collection


def upload_one_doc(doc: dict, model: DocumentBaseModel, db: Database = get_db()) -> dict:
    coll = get_collection(model, db)
    result = coll.insert_one(doc)
    return doc


#
# WARNING: Only use this assuming no duplicate entries
#
def upload_many_docs(data_dicts: list[dict], model: DocumentBaseModel, db: Database = get_db()) -> list[dict]:
    ga_coll = get_collection(model, db)
    try:
        # default is `ordered=True`
        # will insert in order, when faced with error (eg. duplicate key),
        # operation terminated, documents already written will remain in the db
        # while those behind the problematic record will not be written
        result = ga_coll.insert_many(data_dicts)
    except BulkWriteError as e:
        print(
            "Failed to due to duplicate keys:\n"
            f"{[detail['keyValue'] for detail in e.details['writeErrors']]}"
        )
        raise e
    return data_dicts


def get_map_from_two_values(
    key_field: str,
    value_field: str,
    model: DocumentBaseModel,
    filter: dict = dict(),
    db: Database = get_db(),
) -> dict:
    species_coll = get_collection(model, db)
    cursor = species_coll.find(filter, {key_field: 1, value_field: 1})
    species_id_map = {doc[key_field]: doc[value_field] for doc in cursor}
    return species_id_map
