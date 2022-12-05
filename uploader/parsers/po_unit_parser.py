from uploader.models import (
    InterproDetail,
    SampleAnnotationEntityBase,
    SampleAnnotationType,
)
from uploader.parsers import (
    BaseParser,
)


class PoUnitParser(BaseParser):
    def __init__(self, filepath: str):
        super().__init__(filepath, self._line_processor, self._line_validator)

    @staticmethod
    def _line_processor(row):
        return SampleAnnotationEntityBase(
            type=SampleAnnotationType.PO,
            label=row[0],
            name=row[1],
        )

    @staticmethod
    def _line_validator(row) -> bool:
        return True
