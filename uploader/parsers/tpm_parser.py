from uploader.models import TpmRow
from uploader.parsers import BaseParser


class TpmParser(BaseParser):
    def __init__(self, filepath: str) -> None:
        super().__init__(filepath, self._line_processor, self._line_validator)

    @staticmethod
    def _line_processor(row):
        return TpmRow(
            gene_label=row[0],
            tpm_values=[round(float(tpm), 3) for tpm in row[1:]]
        )

    def _line_validator(self, row) -> bool:
        # Rows with no annotations should still be recorded to preserve order of samples
        if len(row) != len(self.header or []):
            raise ValueError("Number of TPM values do not match the number of samples")
        return True

    def get_sample_labels(self) -> list[str]:
        if self.header is None:
            raise ValueError("Header missing from TPM matrix")
        # First column header is not a sample label
        return [label.upper() for label in self.header[1:]]
