from uploaders.models import MapmanDetailRow
from uploaders.parsers import BaseParser


class MapmanDetailParser(BaseParser):
    def __init__(self, filepath: str):
        super().__init__(filepath, self._line_processor, self._line_validator)

    @staticmethod
    def _line_processor(row):
        return MapmanDetailRow(
            label=row[0],
            name=row[1],
            description=row[2],
        )

    @staticmethod
    def _line_validator(row) -> bool:
        return True
