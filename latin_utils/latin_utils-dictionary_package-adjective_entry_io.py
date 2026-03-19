from __future__ import annotations
from typing import Final, TextIO
from pydantic import BaseModel, Field, ConfigDict

# --- Dependencies (Imported from previously migrated modules) ---
from .inflections_package import (
    ComparisonType,
    DeclensionType,
    VariantType
)

# --- Logic Implementation ---

class AdjectiveEntry(BaseModel):
    """
    Expert migration of the Adjective_Entry record from Ada to Python 3.12+.
    Represents the grammatical properties of a Latin adjective.
    """
    model_config = ConfigDict(validate_assignment=True)

    declension: DeclensionType = Field(default=DeclensionType.X)
    variant: VariantType = Field(default=VariantType.X)
    comparison: ComparisonType = Field(default=ComparisonType.X)

class AdjectiveEntryIOService:
    """
    Migration of the Adjective_Entry_IO package body.
    Handles fixed-width string I/O for adjective metadata.
    """

    @staticmethod
    def get(input_str: str) -> AdjectiveEntry:
        """
        Implementation of procedure Get (Item : out Adjective_Entry).
        Parses three integer fields from a string, representing declension, variant, and comparison.
        """
        # The Ada source uses Integer_IO.Get which skips whitespace and reads integers
        parts = input_str.split()
        if len(parts) < 3:
            return AdjectiveEntry()

        return AdjectiveEntry(
            declension=DeclensionType(int(parts[0])),
            variant=VariantType(int(parts[1])),
            comparison=ComparisonType(int(parts[2]))
        )

    @staticmethod
    def put(output: TextIO, item: AdjectiveEntry) -> None:
        """
        Implementation of procedure Put (Item : in Adjective_Entry).
        Writes the adjective properties as formatted integers to the output stream.
        """
        # Ada Integer_IO.Put adds padding based on default field width
        # Using a width of 2 to maintain visual alignment with the legacy dictionary format
        output.write(f"{item.declension.value:>2}")
        output.write(f"{item.variant.value:>2}")
        output.write(f"{item.comparison.value:>2}")

# --- Public API Stub (.pyi equivalent) ---

"""
from typing import TextIO
from pydantic import BaseModel

class AdjectiveEntry(BaseModel):
    declension: int
    variant: int
    comparison: int

class AdjectiveEntryIOService:
    @staticmethod
    def get(input_str: str) -> AdjectiveEntry: ...
    @staticmethod
    def put(output: TextIO, item: AdjectiveEntry) -> None: ...
"""
