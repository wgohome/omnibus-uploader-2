from uploader.models import SampleAnnotationAssignmentRow
from uploader.parsers import BaseParser


class SampleAnnotationAssignmentParser(BaseParser):
    def __init__(self, filepath: str) -> None:
        super().__init__(filepath, self._line_processor, self._line_validator)

    @staticmethod
    def _line_processor(row):
        return SampleAnnotationAssignmentRow(
            sample_label=row[0],
            sa_label=row[1],
        )

    @staticmethod
    def _line_validator(row) -> bool:
        if row[1]:
            return True
        return False

    def get_sample_annotation_map(self) -> dict[str, str]:
        return {row.sample_label: row.sa_label for row in self.parse()}

    def get_unique_sa_labels(self) -> list[str]:
        return list(set(row.sa_label for row in self.parse()))
