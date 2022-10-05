from typing import Generator
from uploaders.models import (
    PyObjectId,
    InterproRow,
    GeneAnnotationDoc,
)


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

    def append_from_whole_species(
        self,
        taxid: int,
        rows: Generator,
        gene_id_map: dict[str, PyObjectId],
    ) -> None:
        gene_ids: set[PyObjectId] = set()
        for row in rows:
            gene_id = gene_id_map[row.gene_label]
            self.append(row=row, gene_id=gene_id)
            gene_ids.add(gene_id)
        print(f"{taxid}\t{len(gene_ids)}\t{len(gene_id_map)}\t{round(len(gene_ids)/len(gene_id_map), 3)}")
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
