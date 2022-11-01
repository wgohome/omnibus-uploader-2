from collections import defaultdict
from typing import Iterable
import numpy as np
from pymongo.database import Database

from uploader.models import (
    PyObjectId,
    SampleAnnotationType,
    SampleAnnotationBase,
    SampleAnnotationDoc,
    Sample,
    TpmRow,
)
from uploader.utilities.db_setup import get_db
from uploader.utilities.db_queries import (
    update_median_spms_to_sas,
    upload_many_docs,
)

"""
Initialize:
Scoped to each species
Get header ordered row of sample labels
Get sample label -> sa label mapping
Store this as sample label -> sa label mapping??

Pass in TPM row, with gene label
group them into SA Docs
"""


class SampleAnnotationController:
    def __init__(
        self,
        species_id: PyObjectId,
        gene_id_map: dict[str, PyObjectId],
        sa_type: SampleAnnotationType,
        sample_labels: list[str],
        sa_assignments: dict[str, str],
        db: Database = get_db(),
    ) -> None:
        # Controller instance scoped by species & sample annotation type
        self._species_id = species_id
        self._sa_type: str = sa_type.value
        self._gene_id_map: dict[str, PyObjectId] = gene_id_map
        self._model = SampleAnnotationDoc
        self._db = db
        # We assume that list of tpm floats is ordered according to this order of sample labels header
        self._sample_labels: list[str] = sample_labels
        if set(sample_labels) - sa_assignments.keys() != set():
            raise ValueError("Not all sample_labels are found in the sa_assignments")
        self._sample_indices_map: dict[str, list[int]] = self._group_tpm_indices_by_annotation(
            sample_labels=sample_labels,
            sa_assignments=sa_assignments,
        )

    def _group_tpm_indices_by_annotation(
        self,
        sample_labels: list[str],
        sa_assignments: dict[str, str],
    ) -> dict[str, list[int]]:
        # Format of dictionary
        #   {annotation_label: [indices of samples for this label]}
        groups = defaultdict(list)
        for i, sample_label in enumerate(sample_labels):
            annotation_label = sa_assignments.get(sample_label)
            if annotation_label is None:
                continue
            groups[annotation_label].append(i)
        return groups

    # Because there can be a huge number of tpm rows,
    # Process and upload row by row instead of delayed uploading for the whole species,
    # to avoid hogging memory

    def aggregate_into_sa_docs(self, gene_id: PyObjectId, tpm_values: list[float]) -> list[SampleAnnotationBase]:
        if len(tpm_values) != len(self._sample_labels):
            raise ValueError(f"Number of samples ({len(self._sample_labels)}) != Number of tpm values ({len(tpm_values)})")
        docs = [
            SampleAnnotationBase(
                species_id=self._species_id,
                gene_id=gene_id,
                type=self._sa_type,
                label=annotation_label,
                avg_tpm=0 if (len(indices) == 0) else np.array(tpm_values)[indices].mean(),
                med_tpm=0 if (len(indices) == 0) else np.median(np.array(tpm_values)[indices]),
                samples=[
                    Sample(
                        sample_label=self._sample_labels[i],
                        tpm_value=tpm_values[i],
                    )
                    for i in indices
                ],
            )
            for annotation_label, indices in self._sample_indices_map.items()
        ]
        total_avg_tpm = sum(doc.avg_tpm for doc in docs)
        total_med_tpm = sum(doc.med_tpm for doc in docs)
        for doc in docs:
            doc.spm = doc.avg_tpm / total_avg_tpm if total_avg_tpm != 0 else 0
            doc.spm_med = doc.med_tpm / total_med_tpm if total_med_tpm != 0 else 0
        return docs

    def upload_many(self, row_iterator: Iterable[TpmRow]) -> None:
        for row in row_iterator:
            sa_docs = self.aggregate_into_sa_docs(
                gene_id=self._gene_id_map[row.gene_label],
                tpm_values=row.tpm_values,
            )
            _ = upload_many_docs(
                data_dicts=[doc.dict() for doc in sa_docs],
                model=self._model,
            )


#
# For migration purposes
#
class SampleAnnotationSpmUpdater:
    def __init__(
        self,
        species_id: PyObjectId,
        gene_id_map: dict[str, PyObjectId],
        sa_type: SampleAnnotationType,
        db: Database = get_db(),
    ) -> None:
        # Controller instance scoped by species & sample annotation type
        self._species_id = species_id
        self._sa_type: str = sa_type.value
        self._gene_id_map: dict[str, PyObjectId] = gene_id_map
        self._model = SampleAnnotationDoc
        self._db = db

    def update_median_spms(self) -> None:
        # Gene by gene, so that we can update the spm for all genes together
        for gene_label, gene_id in self._gene_id_map.items():
            update_median_spms_to_sas(
                species_id=self._species_id,
                gene_id=gene_id,
                sa_type=self._sa_type,
            )
