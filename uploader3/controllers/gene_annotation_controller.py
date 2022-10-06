from typing import Iterable
from pymongo.database import Database

from uploader3.models import (
    PyObjectId,
    GeneAnnotationType,
    GeneAnnotationBase,
    GeneAnnotationDoc,
)
from uploader3.utilities.db_setup import get_db
from uploader3.utilities.db_queries import (
    get_map_from_two_values,
    upload_many_docs,
)


#
# Refer to the GeneAnnotation entity definition
# For assignments per species per gene, go to controller for GeneAnnotationBucket
# For variation in data schema for different types, to be handled by parsers
#
class GeneAnnotationController:
    def __init__(self, ga_type: GeneAnnotationType, db: Database = get_db()) -> None:
        # Instance scoped by Gene Annotation Type
        self.ga_type: str = ga_type.value
        self.model = GeneAnnotationDoc
        self.db = db
        self._label_id_map: dict[int, PyObjectId] | None = None

    def _update_label_id_map(self, data_dicts: list[dict]) -> None:
        self._label_id_map = {
            item["label"]: item["_id"]
            for item in data_dicts
        }

    def upload_many(self, docs: Iterable[GeneAnnotationBase]) -> None:
        data_dicts = upload_many_docs(
            data_dicts=[doc.dict() for doc in docs],
            model=self.model,
            db=self.db
        )
        self._update_label_id_map(data_dicts)

    def get_label_id_map(self) -> dict[int, PyObjectId]:
        if self._label_id_map is None:
            # Access from DB
            self._label_id_map = get_map_from_two_values(
                "label",
                "_id",
                filter={"type": self.ga_type},
                model=self.model,
                db=self.db)
        return self._label_id_map

    @property
    def label_id_map(self) -> dict[int, PyObjectId]:
        return self.get_label_id_map()
