from uploader.parsers import BaseParser
from uploader.models import (
    PyObjectId,
    GeneBase,
)


class GeneParser(BaseParser):
    def __init__(self, filepath: str, species_id: PyObjectId):
        self.species_id: PyObjectId = species_id
        super().__init__(filepath, self.line_processor, self._line_validator)

    def line_processor(self, row):
        doc = GeneBase(label=row[0], species_id=self.species_id)
        return doc

    @staticmethod
    def _line_validator(row) -> bool:
        if row[0]:
            return True
        return False
