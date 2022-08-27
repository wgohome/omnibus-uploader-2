from collections import defaultdict
from pymongo.errors import BulkWriteError
from pymongo.database import Database

from config import settings
from uploader.readers import (
    SpeciesReader,
    GenesReader,
)
from uploader.models import (
    SpeciesDoc,
    GeneDoc,
)
from uploader.models.base import PyObjectId
from uploader.models.gene_annotation import GeneAnnotationDoc
from uploader.models.sample_annotation import SampleAnnotationDoc
from uploader.readers.aggregators import InteproAggregator, TpmBySampleAggregator
from uploader.readers.helpers import get_filepath
from uploader.readers.iterators import InterproIterator
from uploader.readers.map_readers import PlantOntologyMap
from uploader.readers.rows_readers import InterproReader, TpmReader
from uploader.setup_db import get_collection, get_db, get_db_reset

DB = get_db()

def main():
    # upload_species(DB)  # FIXME
    species_id_map = get_species_id_map(DB)
    for taxid, species_id in list(species_id_map.items())[28:28]:
    # for taxid, species_id in species_id_map.items():  # FIXME
        #
        # Upload genes
        #
        upload_genes(taxid, species_id, DB)
        gene_id_map = get_gene_id_map(species_id, DB)

        #
        # Create sample annotation doc with species id and gene id mapper, and upload
        #
        po_map = PlantOntologyMap(get_filepath(taxid=taxid, sub_dir="sample-annotations")).parse()

        # To handle taxid3055 with no annotations!
        if po_map == {}:
            print(f"NO DATA: taxid{taxid} has no PO annotation ...\nNext species...\n")
            continue

        tpm_reader = TpmReader(get_filepath(taxid=taxid, sub_dir="tpm-matrices"))
        tpm_aggregator = TpmBySampleAggregator(
            species_id=species_id,
            annotation_type="PO",
            annotation_map=po_map,
            sample_labels=tpm_reader.get_sample_labels(),
            row_iterator=tpm_reader.parse(),
            gene_id_map=gene_id_map,
        )
        while tpm_aggregator.rows_exhausted is False:
            docs = tpm_aggregator.get_docs_from_chunks(chunk_size=250)
            # TODO: refactor, clunky, logic should have lived in the aggregator itself
            if docs == []:
                continue
            upload_sa_docs(taxid, docs, DB)

        #
        # Upload mapman annotation by species
        #
        # TODO

    #
    # Group interpro annotations accrosss all species and handle
    #
    interpro_aggregator = InteproAggregator()
    for taxid, species_id in species_id_map.items():
        gene_id_map = get_gene_id_map(species_id, DB)
        interpro_reader = InterproReader(get_filepath(taxid=taxid, sub_dir="interpro-annotations"))
        interpro_aggregator.append_from_whole_species(taxid, interpro_reader.parse(), gene_id_map)

    while interpro_aggregator.rows_exhausted is False:
        docs = interpro_aggregator.get_docs_from_chunks(chunk_size=50)
        docs = upload_ga_docs(docs, DB)
        gene_id_to_ga_map = defaultdict(list)
        for doc in docs:
            for gene_id in doc["gene_ids"]:
                gene_id_to_ga_map[gene_id].append(doc["_id"])
        update_gene_doc_with_sa_id(gene_id_to_ga_map, DB)


def upload_species(db: Database = get_db()) -> None:
    species_reader = SpeciesReader(f"{settings.DATA_DIR}species_list.tsv")
    species_coll = get_collection(SpeciesDoc, db)  # type: ignore
    try:
        result = species_coll.insert_many(species_reader.parse(), ordered=False)
    except BulkWriteError as e:
        # print(e)
        print(f"Only {e.details['nInserted']} documents inserted ...")
    print(f"UPLOADED: species list")


def get_species_id_map(db: Database = get_db()) -> dict[int, PyObjectId]:
    # create species taxid -> species id mapper
    species_coll = get_collection(SpeciesDoc, db)  # type: ignore
    cursor = species_coll.find({}, {"_id": 1, "tax": 1})
    species_id_map = {int(doc["tax"]): doc["_id"] for doc in cursor}
    return species_id_map


def upload_genes(taxid: int, species_id: PyObjectId, db: Database = get_db()) -> None:
    genes_reader = GenesReader(
        filepath=get_filepath(taxid=taxid, sub_dir="tpm-matrices"),
        species_id=species_id
    )
    genes_coll = get_collection(GeneDoc, db)  # type: ignore
    genes = [*genes_reader.parse()]
    chunks = []
    for i in range(0, len(genes), 40000):
        end = min(i + 40000, len(genes))
        chunks.append(genes[i:end])
    for chunk in chunks:
        try:
            result = genes_coll.insert_many(chunk, ordered=False)
        except BulkWriteError as e:
            # print(e)
            print(f"Only {e.details['nInserted']} documents inserted ...")
    print(f"UPLOADED: genes for taxid{taxid}")


def get_gene_id_map(species_id: PyObjectId, db: Database = get_db()) -> dict[str, PyObjectId]:
    # create gene label -> gene id mapper to be used later
    genes_coll = get_collection(GeneDoc, db)  # type: ignore
    cursor = genes_coll.find({"spe_id": species_id}, {"_id": 1, "label": 1})
    gene_id_map = {doc["label"]: doc["_id"] for doc in cursor}
    return gene_id_map


def upload_sa_docs(taxid: int, docs: list[dict], db: Database = get_db()) -> None:
    sa_coll = get_collection(SampleAnnotationDoc, db)  # type: ignore
    try:
        result = sa_coll.insert_many(docs, ordered=False)
    except BulkWriteError as e:
        # print(e)
        print(f"Only {e.details['nInserted']} documents inserted ...")
    print(f"UPLOADED: attempted chunk of sample annotations w TPM for {taxid}")


def upload_ga_docs(docs: list[dict], db: Database = get_db()) -> list[dict]:
    ga_coll = get_collection(GeneAnnotationDoc, db)  # type: ignore
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
    genes_coll = get_collection(GeneDoc, db)  # type: ignore
    for gene_id, ga_ids in gene_id_to_ga_map.items():
        result = genes_coll.update_one(
            {"_id": gene_id},
            {"$addToSet": {"ga_ids": {"$each": ga_ids}}}
        )
    print(f"UPDATED: gene docs with gene annotation ids")


if __name__ == "__main__":
    main()
