from collections.abc import Callable
import csv
import gzip
import os
import re
from typing import Generator, Iterator

from uploader.models import (
    SpeciesDoc,
    Cds,
    GeneDoc,
)
from uploader.models.base import PyObjectId
from uploader.models.interpro import InterproDetail, InterproRow
from uploader.models.sample_annotation import SampleAnnotationDoc, TpmRow
from uploader.readers.aggregators import TpmBySampleAggregator


class RowsReader:
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

    def parse(self) -> Generator[dict, None, None]:
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


class SpeciesReader(RowsReader):
    def __init__(self, filepath: str):
        super().__init__(filepath, self._line_processor, self._line_validator)

    @staticmethod
    def _line_processor(row):
        # Ready to be inserted into DB collection
        doc = SpeciesDoc(
            taxid=row[1],
            name=row[0],
            cds=Cds(
                source=row[6],
                url=row[7],
            ),
        )
        return doc.dict()

    @staticmethod
    def _line_validator(row) -> bool:
        if row[1]:
            return True
        return False


class GenesReader(RowsReader):
    def __init__(self, filepath: str, species_id: PyObjectId):
        self.species_id: PyObjectId = species_id
        super().__init__(filepath, self.line_processor, self._line_validator)

    def line_processor(self, row):
        # Ready to be inserted into DB collection
        doc = GeneDoc(label=row[0], species_id=self.species_id)
        return doc.dict()

    @staticmethod
    def _line_validator(row) -> bool:
        if row[0]:
            return True
        return False


class TpmReader(RowsReader):
    def __init__(self, filepath: str):
        super().__init__(filepath, self._line_processor, self._line_validator, has_header=True)

    def get_sample_labels(self) -> list[str]:
        if self.header is None or len(self.header) < 2:
            raise RuntimeError("Tpm Matrix needs to have a header of sample labels")
        return [self._clean_sample_label(label) for label in self.header[1:]]

    @staticmethod
    def _clean_sample_label(label: str) -> str:
        # There were sample labels like 'SRR866568.HTSEQ'
        # like wtf are those ppl uploading the SRR samples doing pfft!! 😡
        # Now our script takes longer to do these regex 💢
        match = re.match(r"^([a-zA-Z]+[\d]+)[\W].+$", label)
        if match is None:
            return label.upper()
        return match.group(1).upper()

    @staticmethod
    def _line_processor(row):
        row = TpmRow(
            gene_label=row[0],
            tpm_values=row[1:]
        )
        return row.dict()

    @staticmethod
    def _line_validator(row) -> bool:
        if row[0]:
            return True
        return False


class MapmanReader(RowsReader):
    def __init__(self, filepath: str):
        super().__init__(filepath, self._line_processor, self._line_validator)

    @staticmethod
    def _line_processor(row):
        return {
            "gene_label": row[2].upper(),
            "label": row[0].upper(),
            "details": {
                "desc": row[3],  # might be redundant to store?
                "binname": row[1]
            }
        }

    @staticmethod
    def _line_validator(row) -> bool:
        if row[2]:
            return True
        return False


class InterproReader(RowsReader):
    def __init__(self, filepath: str):
        # No header line in interpro output file
        super().__init__(filepath, self._line_processor, self._line_validator, has_header=False)

    @staticmethod
    def _line_processor(row):
        row = InterproRow(
            gene_label=row[0],
            label=row[4],
            details=InterproDetail(
                description=row[3],
                go_terms=InterproReader._parse_go_terms(row)
            )
        )
        # return row.dict()
        return row

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
