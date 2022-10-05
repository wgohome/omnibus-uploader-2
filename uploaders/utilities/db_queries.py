from typing import Iterator
from pymongo.database import Database
from pymongo.errors import BulkWriteError

from uploaders.models import PyObjectId, SpeciesDoc, GeneDoc, GeneAnnotationDoc, DocumentBaseModel
from uploaders.utilities.db_setup import get_db, get_collection


def get_species_id_map(db: Database = get_db()) -> dict[int, PyObjectId]:
    # create species taxid -> species id mapper
    species_coll = get_collection(SpeciesDoc, db)
    cursor = species_coll.find({}, {"_id": 1, "tax": 1})
    species_id_map = {int(doc["tax"]): doc["_id"] for doc in cursor}
    return species_id_map


def get_gene_id_map(species_id: PyObjectId, db: Database = get_db()) -> dict[str, PyObjectId]:
    # create gene label -> gene id mapper to be used later
    genes_coll = get_collection(GeneDoc, db)
    cursor = genes_coll.find({"spe_id": species_id}, {"_id": 1, "label": 1})
    gene_id_map = {doc["label"]: doc["_id"] for doc in cursor}
    return gene_id_map


def upload_ga_docs(docs: list[dict], db: Database = get_db()) -> list[dict]:
    ga_coll = get_collection(GeneAnnotationDoc, db)
    try:
        result = ga_coll.insert_many(docs, ordered=False)
    except BulkWriteError as e:
        # print(e)
        print(f"Only {e.details['nInserted']} documents inserted ...")
    print(f"UPLOADED: attempted chunk of gene annotations")
    return docs


def update_gene_doc_with_sa_id(
    gene_id_to_ga_map: dict[PyObjectId, list[PyObjectId]],
    db: Database = get_db(),
) -> None:
    genes_coll = get_collection(GeneDoc, db)
    for gene_id, ga_ids in gene_id_to_ga_map.items():
        result = genes_coll.update_one(
            {"_id": gene_id},
            {"$addToSet": {"ga_ids": {"$each": ga_ids}}}
        )


def upload_one_doc(doc: dict, model: DocumentBaseModel, db: Database = get_db()) -> dict:
    coll = get_collection(model, db)
    result = coll.insert_one(doc)
    return doc


def get_gene_annotations_by_type(type: str, db: Database = get_db()) -> Iterator:
    ga_coll = get_collection(GeneAnnotationDoc, db)
    cursor = ga_coll.find({"type": type})
    return cursor


def upload_many_docs(docs: list[dict], model: DocumentBaseModel, db: Database = get_db()) -> list[dict]:
    ga_coll = get_collection(model, db)
    try:
        result = ga_coll.insert_many(docs)
    except BulkWriteError as e:
        # print(e)
        print(f"Only {e.details['nInserted']} documents inserted ...")
    # print(f"UPLOADED: attempted chunk of gene annotations")
    return docs
