from uploaders.models import InterproRow, InterproDetail
from uploaders.parsers import BaseParser


class InterproParser(BaseParser):
    def __init__(self, filepath: str):
        # No header line in interpro output file
        super().__init__(filepath, self._line_processor, self._line_validator, has_header=False)

    @staticmethod
    def _line_processor(row):
        return InterproRow(
            gene_label=row[0],
            label=row[4],
            details=InterproDetail(
                description=row[5],
                go_terms=InterproParser._parse_go_terms(row)
            )
        )

    @staticmethod
    def _parse_go_terms(row) -> list[str]:
        if len(row) < 14 or row[13] in ["", "-"]:
            return []
        return row[13].split("|")

    @staticmethod
    def _line_validator(row) -> bool:
        if row[2]:
            return True
        return False
