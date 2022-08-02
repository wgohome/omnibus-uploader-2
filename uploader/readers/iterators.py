from typing import Generator

from uploader.models.interpro import InterproRow


class InterproIterator:
    def __init__(self, iterator: Generator):
        self.iterator: Generator = iterator
        self.is_exhausted = False
        self.prev: InterproRow | None = None

    def next_new_entry(self) -> InterproRow | None:
        # Prevent duplicates
        # Context: some rows have the same Gene ID and PFAM ID but different other fields that we are not interested in
        if self.prev is None:
            doc = next(self.iterator)
            self.prev = doc
            return doc

        while True:
            try:
                doc = next(self.iterator)
                if doc != self.prev:
                    self.prev = doc
                    return doc
            except StopIteration:
                self.is_exhausted = True
                return None
