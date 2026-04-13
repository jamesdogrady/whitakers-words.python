from __future__ import annotations
from typing import Final, TextIO, Tuple, Optional
from pydantic import BaseModel, Field, ConfigDict

# --- Dependencies (Imported from previously migrated Inflections_Package) ---
from .inflections_package import CaseType

# --- Core Data Model ---

class PrepositionRecord(BaseModel):
    """
    Expert migration of the Preposition_Record from Ada to Python 3.12+.
    Represents the inflectional metadata of a Latin preposition.
    """
    model_config = ConfigDict(validate_assignment=True, frozen=True)

    # Prepositions primarily track the Case they govern (e.g., Accusative or Ablative) [cite: 2602-2604].
    of_case: CaseType = Field(default=CaseType.X) [cite: 2602]


# --- Migration Service ---

class PrepositionRecordIOService:
    """
    Migration of the Preposition_Record_IO package body.
    Handles fixed-width parsing and formatting for preposition inflection metadata.
    """

    # Matches Case_Type_IO.Default_Width (typically 2) used in the original system[cite: 2608].
    CASE_WIDTH: Final[int] = 2

    @staticmethod
    def get_from_string(source: str) -> Tuple[PrepositionRecord, int]:
        """
        Implementation of procedure Get (Source : String; Target : out Preposition_Record; Last : out Integer).
        Reads the case requirement from a string segment [cite: 2606-2607].
        """
        # Ada: Case_Type_IO.Get (Source, Target.Of_Case, Last); [cite: 2607]
        segment = source.strip()
        if not segment:
            return PrepositionRecord(), 0
        
        # Extract the numeric case code
        parts = segment.split()
        case_val = int(parts[0]) if parts[0].isdigit() else 0
        
        target = PrepositionRecord(of_case=CaseType(case_val)) [cite: 2602]
        
        # Return the record and the last character position processed [cite: 2607]
        last_pos = source.find(parts[0]) + len(parts[0])
        return target, last_pos

    @staticmethod
    def put_to_string(item: PrepositionRecord, buffer_length: int = 20) -> str:
        """
        Implementation of procedure Put (Target : out String; Item : in Preposition_Record).
        Serializes a PrepositionRecord into a fixed-width segment with padding .
        """
        # Formats the Case enum value right-justified within its defined field width [cite: 2608-2609].
        # High := Target'First - 1 + Case_Type_IO.Default_Width; [cite: 2608]
        case_part = f"{item.of_case.value:>{PrepositionRecordIOService.CASE_WIDTH}}" [cite: 2609]
        
        # Fill remainder of string buffer with spaces to maintain column alignment [cite: 2609-2610].
        # Target (High + 1 .. Target'Last) := (others => ' '); [cite: 2610]
        return case_part.ljust(buffer_length)

    @staticmethod
    def put_to_file(file: TextIO, item: PrepositionRecord) -> None:
        """
        Implementation of procedure Put (File : File_Type; Item : in Preposition_Record).
        Writes formatted preposition metadata directly to a file stream [cite: 2604-2605].
        """
        # Ada: Case_Type_IO.Put (File, Item.Of_Case); [cite: 2605]
        file.write(f"{item.of_case.value:>{PrepositionRecordIOService.CASE_WIDTH}}")

# --- Public API Stub (.pyi equivalent) ---

"""
from typing import TextIO, Tuple
from .inflections_package import PrepositionRecord

class PrepositionRecordIOService:
    @staticmethod
    def get_from_string(source: str) -> Tuple[PrepositionRecord, int]: ...
    @staticmethod
    def put_to_string(item: PrepositionRecord, buffer_length: int = 20) -> str: ...
    @staticmethod
    def put_to_file(file: TextIO, item: PrepositionRecord) -> None: ...
"""
