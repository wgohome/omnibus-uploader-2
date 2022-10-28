from uploader.models import (
    MapmanDetail,
    GeneAnnotationBase,
    GeneAnnotationType,
)
from uploader.parsers import (
    BaseParser,
)


class MapmanUnitParser(BaseParser):
    def __init__(self, filepath: str):
        super().__init__(filepath, self._line_processor, self._line_validator)

    @staticmethod
    def _line_processor(row):
        return GeneAnnotationBase(
            type=GeneAnnotationType.MAPMAN,
            label=row[0],
            name=row[1],
            details=MapmanDetail(
                description=row[2]
            ).dict()
        )

    @staticmethod
    def _line_validator(row) -> bool:
        return True
