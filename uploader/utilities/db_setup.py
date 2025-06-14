from functools import lru_cache
from pymongo import ASCENDING, DESCENDING, MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from config import settings
from uploader.models import (
    DocumentBaseModel,
    SpeciesDoc,
    GeneDoc,
    SampleAnnotationDoc,
    GeneAnnotationDoc,
    GeneAnnotationBucketDoc,
    SampleAnnotationEntityDoc,
)


def setup_indexes(db: Database) -> None:
    #
    # To search species by their taxid
    # and enforce unique taxids
    #
    get_collection(SpeciesDoc, db).create_index(  # type: ignore
        [("tax", ASCENDING)],
        unique=True,
        name="unique_taxids"
    )
    #
    # To search gene by their species and/or gene label
    # and enforce unique gene labels within each species scope
    #
    get_collection(GeneDoc, db).create_index(  # type: ignore
        [("spe_id", ASCENDING), ("label", ASCENDING)],
        unique=True,
        name="unique_species_gene_labels"
    )
    #
    # To search gene by their label only
    #
    get_collection(GeneDoc, db).create_index(  # type: ignore
        [("label", ASCENDING)],
    )
    #
    # To search gene annotations by type and label
    # and enforce uniqueness
    #
    get_collection(GeneAnnotationDoc, db).create_index(  # type: ignore
        [("type", ASCENDING), ("label", ASCENDING)],
        unique=True,
        name="unique_gene_annotations_type_and_label"
    )
    #
    # To search gene annotation buckets by spe_id
    # and ensure bucket uniqueness on spe_id and ga_id
    # NOTE: Additionally can create another index to search by ga_id if needed
    #
    get_collection(GeneAnnotationBucketDoc, db).create_index(  # type: ignore
        [("spe_id", ASCENDING), ("ga_id", ASCENDING)],
        unique=True,
        name="unique_spe_id_ga"
    )
    #
    # To search sample annotations by species + gene (+ type + label)
    #
    get_collection(SampleAnnotationDoc, db).create_index(  # type: ignore
        [
            ("spe_id", ASCENDING),
            ("g_id", ASCENDING),
            ("type", ASCENDING),
            ("label", ASCENDING),
        ],
        unique=True,
        name="unique_sample_annotation_doc"
    )
    # #
    # # To search sample annotations by type + label
    # #
    # get_collection(SampleAnnotationDoc, db).create_index(  # type: ignore
    #     [("type", ASCENDING), ("label", ASCENDING)],
    #     name="sample_annotation_by_type_labels"
    # )
    # #
    # # To sort sample annotations by spm_med
    # #
    # get_collection(SampleAnnotationDoc, db).create_index(  # type: ignore
    #     [("spm_med", DESCENDING)],
    #     name="spm_med_descending"
    # )
    # #
    # # To sort sample annotations by spm_med
    # #
    # get_collection(SampleAnnotationDoc, db).create_index(  # type: ignore
    #     [("spm", DESCENDING)],
    #     name="spm_mean_descending"
    # )
    #
    # To search sample annotations by type + label + spm mean
    #
    get_collection(SampleAnnotationDoc, db).create_index(
        [
            ("type", ASCENDING),
            ("label", ASCENDING),
            ("spe_id", ASCENDING),
            ("spm", DESCENDING),
        ],
        name="sample_annotation_by_spm_mean"
    )
    #
    # To search sample annotations by type + label + spm median
    #
    get_collection(SampleAnnotationDoc, db).create_index(
        [
            ("type", ASCENDING),
            ("label", ASCENDING),
            ("spe_id", ASCENDING),
            ("spm_med", DESCENDING),
        ],
        name="sample_annotation_by_spm_median"
    )
    #
    # To query sample annotation entities by type and label
    # and to enforce uniqueness constraint
    #
    get_collection(SampleAnnotationEntityDoc, db).create_index(
        [("type", ASCENDING), ("label", ASCENDING)],
        name="sample_annotation_entity_by_type_labels"
    )


# To be used for testing locally, to drop database before starting again
def get_db_reset() -> Database:
    client = MongoClient(settings.DATABASE_URL)
    client.drop_database(settings.DATABASE_NAME)
    db = client[settings.DATABASE_NAME]
    setup_indexes(db)
    return db


@lru_cache
def get_db() -> Database:
    client = MongoClient(settings.DATABASE_URL)
    db = client[settings.DATABASE_NAME]
    setup_indexes(db)
    return db
    # Returns db instead of yield as we are using lru_cache
    # With yield, a generator will be returned and
    # subsequent calls to get_db as a dependancy will yield nothing


@lru_cache
def get_collection(model: DocumentBaseModel, db: Database) -> Collection:
    return db[model.Mongo.collection_name]
