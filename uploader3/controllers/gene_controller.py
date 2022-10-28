from typing import Iterable
from pymongo.database import Database

from uploader3.models import (
    PyObjectId,
    SpeciesBase,
    SpeciesDoc,
    GeneBase,
    GeneDoc,
    gene,
)
from uploader3.utilities.db_setup import get_db
from uploader3.utilities.db_queries import (
    get_map_from_two_values,
    update_gene_doc_with_sa_id,
    upload_many_docs,
)


class GeneController:
    def __init__(self, taxid: int, species_id: PyObjectId, db: Database = get_db()) -> None:
        # Scope instances of GeneController by species
        self.taxid: int = taxid
        self.species_id: PyObjectId = species_id
        self.model = GeneDoc
        self.db = db
        self._label_id_map: dict[str, PyObjectId] | None = None

    def _update_label_id_map(self, data_dicts: list[dict]) -> None:
        self._label_id_map = {
            item["label"]: item["_id"]
            for item in data_dicts
        }

    def upload_many(self, docs: Iterable[GeneBase]) -> None:
        data_dicts = upload_many_docs(
            data_dicts=[doc.dict() for doc in docs],
            model=self.model,
            db=self.db
        )
        self._update_label_id_map(data_dicts)

    def get_label_id_map(self) -> dict[str, PyObjectId]:
        if self._label_id_map is None:
            # Access from DB
            self._label_id_map = get_map_from_two_values(
                "label",
                "_id",
                filter={"spe_id": self.species_id},  # Scoped to species!
                model=self.model,
                db=self.db)
        return self._label_id_map

    @property
    def label_id_map(self) -> dict[str, PyObjectId]:
        return self.get_label_id_map()

    def append_ga_ids(self, gene_to_ga_map: dict[PyObjectId, list[PyObjectId]]) -> None:
        update_gene_doc_with_sa_id(
            gene_to_ga_map,
            model=self.model,
            db=self.db
        )
