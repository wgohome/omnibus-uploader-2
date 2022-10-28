from uploader.models import GeneAnnotationAssignmentRow
from uploader.parsers import BaseParser


class GeneAnnotationAssignmentParser(BaseParser):
    def __init__(self, filepath: str) -> None:
        super().__init__(filepath, self._line_processor, self._line_validator)

    @staticmethod
    def _line_processor(row):
        return GeneAnnotationAssignmentRow(
            gene_label=row[0],
            ga_label=row[1],
        )

    @staticmethod
    def _line_validator(row) -> bool:
        # Exclude rows with no annotations
        if row[0] and row[1]:
            return True
        return False
