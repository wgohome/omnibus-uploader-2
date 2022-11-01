from typing import Iterator
from config import settings
from config.filepath_definitions import filepath_definitions
from uploader.models import (
    PyObjectId,
    CoexpressionNeighbor,
    CoexpressionRow,
)
from uploader.parsers import (
    CoexpressionIndexParser,
    CoexpressionPccParser,
    GeneParser,
)


class CoexpressionController:
    def __init__(
        self,
        taxid: int,
        species_id: PyObjectId,
        gene_id_map: dict[str, PyObjectId],
        n_neighbors: int = settings.DEFAULT_N_NEIGHBORS,
    ) -> None:
        self._gene_id_map = gene_id_map
        gene_parser = GeneParser(
            filepath=filepath_definitions.get_tpm_filepath(taxid=taxid),
            species_id=species_id
        )
        index_parser = CoexpressionIndexParser(
            filepath=filepath_definitions.get_coexpression_index_filepath(taxid=taxid)
        )
        pcc_parser = CoexpressionPccParser(
            filepath=filepath_definitions.get_coexpression_pcc_filepath(taxid=taxid)
        )
        # Checks
        if not (
            len([*gene_parser.parse()]) == \
            len([*index_parser.parse()]) == \
            len([*pcc_parser.parse()])
        ):
            raise ValueError("length of rows in index and pcc files must be equal to number of genes")
        if len([*index_parser.parse()]) < n_neighbors + 1:
            raise ValueError(f"Your coexpression files have fewer than {n_neighbors} neighbors")
        self._n_neighbors: int = n_neighbors
        # For accessing the gene label by index
        self._gene_labels: list[str] = [doc.label for doc in gene_parser.parse()]
        # For knowing which gene is the current row corresponding to
        self._gene_iterator: Iterator[str] = (doc.label for doc in gene_parser.parse())
        self._index_iterator: Iterator[list[int]] = index_parser.parse()
        self._pcc_iterator: Iterator[list[float]] = pcc_parser.parse()

    def get_next_row(self) -> CoexpressionRow | None:
        try:
            curr_gene = next(self._gene_iterator)
            indices = next(self._index_iterator)
            pccs = next(self._pcc_iterator)
            if len(indices) != len(pccs):
                raise ValueError("len(indices) must equal len(pccs)")
            row_result = CoexpressionRow(
                gene_label=curr_gene,
                neighbors=[]
            )
            # First neighbor is itself, exclude
            for i in range(1, self._n_neighbors + 1):
                # If there are no coexpressed neighbors, empty array will be returned
                # If one of the ranked PCC is nan, implies no more valid pcc values down the line
                if pccs[i] is None:
                    break
                row_result.neighbors.append(
                    CoexpressionNeighbor(
                        gene=self._gene_id_map[self._gene_labels[indices[i]]],
                        pcc=pccs[i],
                    )
                )
            return row_result
        except StopIteration as e:
            # When all rows have been exhausted
            return None
        except Exception as e:
            raise e
