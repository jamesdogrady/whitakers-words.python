from __future__ import annotations
from typing import Final, TextIO, Tuple, Optional
from pydantic import BaseModel, Field, ConfigDict

# --- Dependencies (Imported from previously migrated modules) ---
from .inflections_package import CaseType

# --- Core Data Model ---

class PrepositionEntry(BaseModel):
    """
    Expert migration of the Preposition_Entry record from Ada to Python 3.12+.
    Represents the grammatical properties of a Latin preposition, specifically 
    the case of the object it governs.
    """
    model_config = ConfigDict(validate_assignment=True, frozen=True)

    # In Whitaker's system, prepositions primarily track the Case (Obj) they take.
    obj: CaseType = Field(default=CaseType.X)

# --- Migration Service ---

class PrepositionEntryIOService:
    """
    Migration of the Preposition_Entry_IO package body.
    Handles fixed-width parsing and formatting for preposition metadata in dictionary files.
    """

    # Matches Case_Type_IO.Default_Width used in the original system
    CASE_FIELD_WIDTH: Final[int] = 2

    @staticmethod
    def get_from_string(source: str) -> Tuple[PrepositionEntry, int]:
        """
        Implementation of procedure Get (Source : String; Target : out Preposition_Entry; Last : out Integer).
        Parses the case requirement from a string segment.
        """
        # Note: Ada logic skips leading whitespace via Integer_IO behavior.
        trimmed = source.strip()
        if not trimmed:
            return PrepositionEntry(), 0

        # Extract the numeric case code (e.g., 1 for Nominative, 2 for Genitive, etc.)
        parts = trimmed.split()
        case_val = int(parts[0]) if parts[0].isdigit() else 0
        
        entry = PrepositionEntry(obj=CaseType(case_val))
        
        # Calculate the 'Last' index reached in the source string
        last_pos = source.find(parts[0]) + len(parts[0])
        return entry, last_pos

    @staticmethod
    def put_to_string(item: PrepositionEntry) -> str:
        """
        Implementation of procedure Put (Target : out String; Item : in Preposition_Entry).
        Serializes the preposition data into a fixed-width segment with padding.
        """
        # Formats the Case enum value right-justified within its field width.
        # High := Low + Case_Type_IO.Default_Width;
        case_part = f"{item.obj.value:>{PrepositionEntryIOService.CASE_FIELD_WIDTH}}"
        
        # Fill remainder of string with spaces
        # Target (High + 1 .. Target'Last) := (others => ' ');
        return case_part.ljust(12) 

    @staticmethod
    def put_to_file(file: TextIO, item: PrepositionEntry) -> None:
        """
        Implementation of procedure Put (File : File_Type; Item : in Preposition_Entry).
        Writes formatted preposition metadata to a file stream.
        """
        # Ada: Case_Type_IO.Put (File, Item.Obj);
        file.write(f"{item.obj.value:>{PrepositionEntryIOService.CASE_FIELD_WIDTH}}")

# --- Public API Stub (.pyi equivalent) ---

"""
from typing import TextIO, Tuple
from .dictionary_package import PrepositionEntry

class PrepositionEntryIOService:
    @staticmethod
    def get_from_string(source: str) -> Tuple[PrepositionEntry, int]: ...
    @staticmethod
    def put_to_string(item: PrepositionEntry) -> str: ...
    @staticmethod
    def put_to_file(file: TextIO, item: PrepositionEntry) -> None: ...
"""
