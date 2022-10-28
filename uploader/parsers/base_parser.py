import csv
import gzip
import os
from typing import Callable, Iterator

from uploader.models.base import CustomBaseModel


class BaseParser:
    def __init__(
        self,
        filepath: str,
        line_processor: Callable,
        line_validator: Callable[[list], bool] | None = None,
        delimiter: str | None = None,
        quotechar: str | None = None,
        has_header: bool = True
    ):
        self.filepath: str = self._validate_existence(filepath)
        self.line_processor: Callable = line_processor
        self.line_validator: Callable[[list], bool] = line_validator or (lambda _: True)
        self.delimiter: str = delimiter or "\t"
        self.quotechar: str = quotechar or "'"
        self.has_header: bool = has_header
        self.header: list | None = self._get_header()

    @staticmethod
    def _validate_existence(filepath: str) -> str:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"{filepath} does not exist")
        return filepath

    def _get_header(self) -> list | None:
        if self.has_header is False:
            return None
        reader = self._get_reader()
        return next(reader)

    def parse(self) -> Iterator[CustomBaseModel]:
        reader = self._get_reader()
        if self.has_header:
            _ = next(reader)
        return (
            self.line_processor(row)
            for row in reader if self.line_validator(row)
        )

    def _get_reader(self) -> Iterator:
        if self.filepath.endswith(".gz"):
            return csv.reader(
                gzip.open(self.filepath, "rt"),
                delimiter=self.delimiter,
                quotechar=self.quotechar
            )
        return csv.reader(
            open(self.filepath, "r"),
            delimiter=self.delimiter,
            quotechar=self.quotechar
        )
