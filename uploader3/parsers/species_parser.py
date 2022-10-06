from uploader3.models import (
    Cds,
    SpeciesBase,
)
from uploader3.parsers import (
    BaseParser,
)


class SpeciesParser(BaseParser):
    def __init__(self, filepath: str):
        super().__init__(filepath, self._line_processor, self._line_validator)

    @staticmethod
    def _line_processor(row):
        # Ready to be inserted into DB collection
        doc = SpeciesBase(
            taxid=row[0],
            name=row[1],
            alias=row[2].split(","),
            cds=Cds(
                source=row[3],
                url=row[4],
            ),
            # TODO
            # ignoring qc stat for now
        )
        return doc

    @staticmethod
    def _line_validator(row) -> bool:
        return True
