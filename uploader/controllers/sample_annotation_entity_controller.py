from typing import Iterable

from uploader.models import (
    PyObjectId,
    SampleAnnotationEntityDoc,
)
from uploader.utilities.db_setup import get_db
from uploader.utilities.db_queries import (
    upload_many_docs,
)


class SampleAnnotationEntityController:
    def __init__(self, new_sa_entities: Iterable) -> None:
        self._sa_entities = {sa.label: sa for sa in new_sa_entities}

    def update_with_species(self, species_id: PyObjectId, sa_labels: list[str]) -> None:
        if len(sa_labels - self._sa_entities.keys()) > 0:
            raise ValueError("Check to ensure that all sa_labels passed already exists when initializing the SampleAnnotationEntityController")
        for sa_label in sa_labels:
            self._sa_entities[sa_label].spe_ids.append(species_id)

    def upload_all(self) -> None:
        # Ensure all sa_entity have at least one species
        for sa_entity in self._sa_entities.values():
            if len(sa_entity.spe_ids) < 1:
                raise ValueError(f"{sa_entity.label} does not have any species_id assigned to it yet")
        # Actual upload
        upload_many_docs(
            data_dicts=[sa_entity.dict() for sa_entity in self._sa_entities.values()],
            model=SampleAnnotationEntityDoc,
            db=get_db(),
        )
