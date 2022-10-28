from typing import Iterable
from pymongo.database import Database

from uploader3.models import (
    PyObjectId,
    SpeciesBase,
    SpeciesDoc,
)
from uploader3.utilities.db_setup import get_db
from uploader3.utilities.db_queries import (
    get_map_from_two_values,
    upload_many_docs,
)


class SpeciesController:
    def __init__(self, db: Database = get_db()) -> None:
        self.model = SpeciesDoc
        self.db = db
        self._taxid_id_map: dict[int, PyObjectId] | None = None

    def _update_taxid_id_map(self, data_dicts: list[dict]) -> None:
        self._taxid_id_map = {
            item["tax"]: item["_id"]
            for item in data_dicts
        }

    def upload_many(self, docs: Iterable[SpeciesBase]) -> None:
        data_dicts = upload_many_docs(
            data_dicts=[doc.dict() for doc in docs],
            model=self.model,
            db=self.db
        )
        self._update_taxid_id_map(data_dicts)

    def get_taxid_id_map(self) -> dict[int, PyObjectId]:
        if self._taxid_id_map is None:
            # Access from DB
            self._taxid_id_map = get_map_from_two_values("tax", "_id", model=self.model, db=self.db)
        return self._taxid_id_map

    @property
    def taxid_id_map(self) -> dict[int, PyObjectId]:
        return self.get_taxid_id_map()
