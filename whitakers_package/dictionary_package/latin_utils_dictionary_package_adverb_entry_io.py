from __future__ import annotations
from typing import TextIO
from pydantic import BaseModel, Field, ConfigDict

# --- Dependencies (Imported from previously migrated modules) ---
from .inflections_package import ComparisonType

# --- Core Logic Implementation ---

class AdverbEntry(BaseModel):
    """
    Expert migration of the Adverb_Entry record from Ada to Python 3.12+.
    Represents the grammatical properties of a Latin adverb.
    """
    model_config = ConfigDict(validate_assignment=True)

    # Adverbs in the WORDS system primarily track comparison (Positive, Comparative, Superlative)
    comparison: ComparisonType = Field(default=ComparisonType.X)

class AdverbEntryIOService:
    """
    Migration of the Adverb_Entry_IO package body.
    Handles the parsing and formatting of adverb metadata for dictionary records.
    """

    @staticmethod
    def get(input_str: str) -> AdverbEntry:
        """
        Implementation of procedure Get (Item : out Adverb_Entry).
        Reads the comparison integer from the input string.
        """
        # Integer_IO.Get in Ada skips leading whitespace and reads the next integer
        parts = input_str.split()
        if not parts:
            return AdverbEntry()

        try:
            # Map the integer value to the ComparisonType enum
            return AdverbEntry(comparison=ComparisonType(int(parts[0])))
        except (ValueError, IndexError):
            return AdverbEntry()

    @staticmethod
    def put(output: TextIO, item: AdverbEntry) -> None:
        """
        Implementation of procedure Put (Item : in Adverb_Entry).
        Formats the adverb comparison value for output to the dictionary file.
        """
        # Ada Integer_IO.Put utilizes default field widths for alignment
        # A width of 2 is used here to maintain visual parity with the legacy DICTLINE format.
        output.write(f"{item.comparison.value:>2}")

# --- Public API Stub (.pyi equivalent) ---

"""
from typing import TextIO
from pydantic import BaseModel

class AdverbEntry(BaseModel):
    comparison: int

class AdverbEntryIOService:
    @staticmethod
    def get(input_str: str) -> AdverbEntry: ...
    @staticmethod
    def put(output: TextIO, item: AdverbEntry) -> None: ...
"""
