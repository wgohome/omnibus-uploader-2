from collections import defaultdict
import numpy as np
from typing import Generator

from uploader.models.base import PyObjectId
from uploader.models.gene_annotation import GeneAnnotationDoc
from uploader.models.interpro import InterproRow
from uploader.models.sample_annotation import Sample, SampleAnnotationDoc
from uploader.readers.helpers import strip_gene_isoform
from uploader.readers.iterators import InterproIterator


class TpmBySampleAggregator:
    def __init__(
        self,
        species_id: PyObjectId,
        annotation_type: str,
        annotation_map: dict[str, str],
        sample_labels: list[str],
        row_iterator: Generator,
        gene_id_map: dict[str, PyObjectId]
    ):
        self.species_id: PyObjectId = species_id
        self.annotation_type: str = annotation_type
        self.sample_labels: list[str] = sample_labels
        self.groups = self._group_annotation_by_indices(annotation_map, sample_labels)
        self.row_iterator: Generator = row_iterator
        self.gene_id_map: dict[str, PyObjectId] = gene_id_map
        self.rows_exhausted: bool = False

    def _group_annotation_by_indices(self, annotation_map, samples) -> dict[str, list[int]]:
        # {annotation_label: [indices of samples for this label]}
        groups = defaultdict(list)
        for i, sample in enumerate(samples):
            annotation_label = annotation_map.get(sample)
            if annotation_label is None:
                continue
            groups[annotation_label].append(i)
        return groups

    def get_docs_from_row(self, gene_id: PyObjectId, tpm_values: list[float]) -> list[dict]:
        if len(tpm_values) != len(self.sample_labels):
            raise ValueError(f"Number of samples ({len(self.sample_labels)}) != Number of tpm values ({len(tpm_values)})")
        docs = [
            SampleAnnotationDoc(
                species_id=self.species_id,
                gene_id=gene_id,
                type=self.annotation_type,
                label=annotation_label,
                avg_tpm=0 if (len(indices) == 0) else np.array(tpm_values)[indices].mean(),
                samples=[
                    Sample(
                        sample_label=self.sample_labels[i],
                        tpm_value=tpm_values[i],
                    )
                    for i in indices
                ],
            )
            for annotation_label, indices in self.groups.items()
        ]
        total_avg_tpm = sum(doc.avg_tpm for doc in docs)
        for doc in docs:
            doc.spm = doc.avg_tpm / total_avg_tpm if total_avg_tpm != 0 else 0
        return [doc.dict() for doc in docs]

    def get_docs_from_chunks(self, chunk_size: int = 50) -> list[dict]:
        result = []
        for _ in range(chunk_size):
            try:
                row = next(self.row_iterator)
                result.extend(
                    self.get_docs_from_row(
                        self.gene_id_map[row["gene_label"]],
                        row["tpm_values"]
                    )
                )
            except StopIteration:
                self.rows_exhausted = True
                break
        return result


class InteproAggregator:
    def __init__(self):
        self.type: str = "INTERPRO"
        self.ga_dict: dict[str, GeneAnnotationDoc] = {}
        self.iterator: Generator | None = None

    @property
    def rows_exhausted(self) -> bool:
        return self.iterator is None

    def _create_iterator(self) -> None:
        self.iterator = (doc.dict() for doc in self.ga_dict.values())

    def get_all_docs(self) -> list:
        return list(self.ga_dict.values())

    def append(self, row: InterproRow, gene_id: PyObjectId) -> None:
        # If interpro pfam label not in dict, add new entry of GA Doc
        if self.ga_dict.get(row.label) is None:
            self.ga_dict[row.label] = GeneAnnotationDoc(
                type=self.type,
                label=row.label,
                details=row.details.dict(),
                gene_ids=[gene_id]
            )
        # If pfam label already in dict
        # Append gene id to gene_ids list in doc
        else:
            self.ga_dict[row.label].gene_ids.append(gene_id)

    def append_from_whole_species(self, taxid: int, generator: Generator, gene_id_map: dict[str, PyObjectId]) -> None:
        iterator = InterproIterator(generator)
        while True:
            row = iterator.next_new_entry()
            if row is None:
                break
            # Trim isoform suffix in gene label before finding gene id
            # If gene id dont exist in the list, then skip
            gene_id = gene_id_map.get(strip_gene_isoform(row.gene_label))
            if gene_id is None:
                continue
            self.append(row, gene_id)
        print(f"AGGREGATED: interpro annotations for taxid{taxid}")
        self._create_iterator()

    def get_docs_from_chunks(self, chunk_size: int = 50) -> list[dict]:
        result = []
        # initialize iterator if not created yet
        if self.iterator is None:
            self._create_iterator()
        for _ in range(chunk_size):
            try:
                row = next(self.iterator)
                result.append(row)
            except StopIteration:
                self.iterator = None
                break
        return result
        # Return mapping of gene_id and gene annotation id to be add the
        # back reference in gene docs
