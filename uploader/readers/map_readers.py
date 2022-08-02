from collections.abc import Callable
import csv
import gzip
import os
from typing import Any, Iterator


class MapperReader:
    def __init__(
        self,
        filepath: str,
        key_extractor: Callable[[list], Any],
        value_extractor: Callable[[list], Any],
        line_validator: Callable[[list], bool] | None = None,
        delimiter: str | None = None,
        quotechar: str | None = None,
        has_header: bool = True
    ):
        self.filepath: str = self._validate_existence(filepath)
        self.key_extractor: Callable = key_extractor
        self.value_extractor: Callable = value_extractor
        self.line_validator: Callable[[list], bool] = line_validator or (lambda _: True)
        self.delimiter: str = delimiter or "\t"
        self.quotechar: str = quotechar or "'"
        self.has_header: bool = has_header

    @staticmethod
    def _validate_existence(filepath: str) -> str:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"{filepath} does not exist")
        return filepath

    def parse(self) -> dict:
        reader = self._get_reader()
        if self.has_header:
            _ = next(reader)
        return {
            self.key_extractor(row): self.value_extractor(row)
            for row in reader if self.line_validator(row)
        }

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


class SpeciesMap(MapperReader):
    def __init__(self, filepath: str):
        super().__init__(filepath, self._key_extractor, self._value_extractor, self._line_validator)

    @staticmethod
    def _key_extractor(row):
        # taxid
        return row[1]

    @staticmethod
    def _value_extractor(row):
        # scientific name
        return row[0]

    @staticmethod
    def _line_validator(row) -> bool:
        if row[1]:
            return True
        return False


class PlantOntologyMap(MapperReader):
    def __init__(self, filepath: str):
        super().__init__(filepath, self._key_extractor, self._value_extractor, self._line_validator)

    @staticmethod
    def _key_extractor(row):
        # sample label
        return row[0].upper()

    @staticmethod
    def _value_extractor(row):
        # PO Term label
        return row[1].upper()

    @staticmethod
    def _line_validator(row) -> bool:
        if row[1]:
            return True
        return False


__all__ = ["PlantOntologyMap", "SpeciesMap"]
