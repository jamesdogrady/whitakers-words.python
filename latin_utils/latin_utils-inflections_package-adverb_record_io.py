from __future__ import annotations
from typing import Final, TextIO, Tuple, Optional
from pydantic import BaseModel, Field, ConfigDict

# --- Dependencies (Imported from previously migrated Inflections_Package) ---
from .inflections_package import ComparisonType

# --- Core Data Model ---

class AdverbRecord(BaseModel):
    """
    Expert migration of the Adverb_Record from Ada to Python 3.12+.
    Represents the inflectional metadata of a Latin adverb [cite: 2661-2663].
    """
    model_config = ConfigDict(validate_assignment=True, frozen=True)

    # Adverbs primarily track Comparison (Positive, Comparative, Superlative) 
    comparison: ComparisonType = Field(default=ComparisonType.X)

# --- Migration Service ---

class AdverbRecordIOService:
    """
    Migration of the Adverb_Record_IO package body.
    Handles fixed-width parsing and formatting for adverb inflection metadata.
    """

    # Matches the Default_Width defined in the legacy Comparison_Type_IO package
    COMP_WIDTH: Final[int] = 2

    @staticmethod
    def get_from_string(source: str) -> Tuple[AdverbRecord, int]:
        """
        Implementation of procedure Get (Source : String; Target : out Adverb_Record; Last : out Integer).
        Reads the comparison code from a string segment [cite: 2678-2679].
        """
        # Comparison_Type_IO.Get reads the integer code from the string
        segment = source.strip()
        if not segment:
            return AdverbRecord(), 0
        
        # Extract the numeric comparison value (e.g., 1 for Positive, 2 for Comparative)
        parts = segment.split()
        comp_val = int(parts[0]) if parts[0].isdigit() else 0
        
        target = AdverbRecord(comparison=ComparisonType(comp_val)) [cite: 2678]
        
        # Returns the record and the last character position processed [cite: 2679]
        last_pos = source.find(parts[0]) + len(parts[0])
        return target, last_pos

    @staticmethod
    def put_to_string(item: AdverbRecord) -> str:
        """
        Implementation of procedure Put (Target : out String; Item : in Adverb_Record).
        Serializes an AdverbRecord into a fixed-width segment with padding [cite: 2679-2681].
        """
        # Formats the Comparison enum value within its defined field width [cite: 2680]
        # High := Target'First - 1 + Comparison_Type_IO.Default_Width;
        comp_part = f"{item.comparison.value:>{AdverbRecordIOService.COMP_WIDTH}}" [cite: 2680]
        
        # Fill remainder of string with spaces [cite: 2681]
        # Target (High + 1 .. Target'Last) := (others => ' ');
        # Standard record width for these inflection blocks is typically 20 characters
        return comp_part.ljust(20)

    @staticmethod
    def put_to_file(file: TextIO, item: AdverbRecord) -> None:
        """
        Implementation of procedure Put (File : File_Type; Item : in Adverb_Record).
        Writes formatted adverb metadata directly to a file stream [cite: 2676-2677].
        """
        # Ada: Comparison_Type_IO.Put (File, Item.Comparison); [cite: 2676]
        file.write(f"{item.comparison.value:>{AdverbRecordIOService.COMP_WIDTH}}") [cite: 2676]

# --- Public API Stub (.pyi equivalent) ---

"""
from typing import TextIO, Tuple
from .inflections_package import AdverbRecord

class AdverbRecordIOService:
    @staticmethod
    def get_from_string(source: str) -> Tuple[AdverbRecord, int]: ...
    @staticmethod
    def put_to_string(item: AdverbRecord) -> str: ...
    @staticmethod
    def put_to_file(file: TextIO, item: AdverbRecord) -> None: ...
"""
