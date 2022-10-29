from uploader.parsers import BaseParser


class CoexpressionPccParser(BaseParser):
    def __init__(self, filepath: str) -> None:
        self._n_cols: int | None = None
        super().__init__(filepath, self._line_processor, self._line_validator, has_header=False)

    @staticmethod
    def _line_processor(row):
        # pcc could be None, to be handled by controller
        return [
            round(float(pcc), 3) if pcc else pcc
            for pcc in row
        ]

    def _line_validator(self, row) -> bool:
        # Ensure that number of cells in this row is consistent
        if self._n_cols is None:
            self._n_cols = len(row)
        else:
            if len(row) != self._n_cols:
                raise ValueError(f"Number of values in row is not == {self._n_cols}")
        return True
