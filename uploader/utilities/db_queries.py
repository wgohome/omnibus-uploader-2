from pymongo import ASCENDING
from pymongo.database import Database
from pymongo.errors import BulkWriteError
from pymongo.operations import UpdateOne

from uploader.models import (
    PyObjectId,
    GeneDoc,
    DocumentBaseModel,
)
from uploader.utilities.db_setup import get_db, get_collection


def upload_one_doc(doc: dict, model: DocumentBaseModel, db: Database = get_db()) -> dict:
    coll = get_collection(model, db)
    result = coll.insert_one(doc)
    return doc


#
# WARNING: Only use this assuming no duplicate entries
#
def upload_many_docs(data_dicts: list[dict], model: DocumentBaseModel, db: Database = get_db()) -> list[dict]:
    coll = get_collection(model, db)
    try:
        # default is `ordered=True`
        # will insert in order, when faced with error (eg. duplicate key),
        # operation terminated, documents already written will remain in the db
        # while those behind the problematic record will not be written
        result = coll.insert_many(data_dicts)
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
    coll = get_collection(model, db)
    cursor = coll.find(filter, {key_field: 1, value_field: 1})
    key_value_map = {doc[key_field]: doc[value_field] for doc in cursor}
    return key_value_map


def update_gene_doc_with_sa_id(
    id_to_list_of_id_map: dict[PyObjectId, list[PyObjectId]],
    model: DocumentBaseModel,
    db: Database = get_db(),
) -> None:
    coll = get_collection(model, db)
    requests = [
        UpdateOne(
            filter={"_id": gene_id},
            update={"$addToSet": {"ga_ids": {"$each": ga_ids}}},
            hint=[("_id", ASCENDING)]
        ) for gene_id, ga_ids in id_to_list_of_id_map.items()
    ]
    try:
        coll.bulk_write(requests)
    except BulkWriteError as bwe:
        print(bwe.details)


def update_gene_doc_with_neighbors(
    gene_id: PyObjectId,
    neighbors: list[dict],
    model: DocumentBaseModel = GeneDoc,
    db: Database = get_db(),
) -> None:
    coll = get_collection(model, db)
    _ = coll.update_one(
        {"_id": gene_id},
        {"$set": {"neighbors": neighbors}}
    )
