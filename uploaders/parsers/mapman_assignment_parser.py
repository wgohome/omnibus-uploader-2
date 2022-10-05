from uploaders.models import MapmanAssignmentRow
from uploaders.parsers import BaseParser


class MapmanAssignmentParser(BaseParser):
    def __init__(self, filepath: str):
        super().__init__(filepath, self._line_processor, self._line_validator)

    @staticmethod
    def _line_processor(row):
        return MapmanAssignmentRow(
            gene_label=row[0],
            bincode=row[1],
        )

    @staticmethod
    def _line_validator(row) -> bool:
        if row[0] and row[1]:
            return True
        return False
