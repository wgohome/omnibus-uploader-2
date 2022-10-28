from uploader.models import (
    InterproDetail,
    GeneAnnotationBase,
    GeneAnnotationType,
)
from uploader.parsers import (
    BaseParser,
)


class InterproUnitParser(BaseParser):
    def __init__(self, filepath: str):
        super().__init__(filepath, self._line_processor, self._line_validator)

    @staticmethod
    def _line_processor(row):
        return GeneAnnotationBase(
            type=GeneAnnotationType.INTERPRO,
            label=row[0],
            name=row[1],
            details=InterproDetail(
                go_terms=InterproUnitParser._parse_go_terms(row[2])
            ).dict()
        )

    @staticmethod
    def _parse_go_terms(go_terms_string: str) -> list[str]:
        return go_terms_string.split("|")

    @staticmethod
    def _line_validator(row) -> bool:
        return True
