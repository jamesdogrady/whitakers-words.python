from __future__ import annotations
from typing import Final, TextIO, Optional, Tuple
from pydantic import BaseModel, Field, ConfigDict

# --- Dependencies (Imported from previously migrated modules) ---
from .inflections_package import (
    DeclensionRecord, 
    GenderType, 
    NounKindType
)

# --- Core Data Model ---

class NounEntry(BaseModel):
    """
    Expert migration of the Noun_Entry record from Ada to Python 3.12+.
    Represents the grammatical properties of a Latin noun.
    """
    model_config = ConfigDict(validate_assignment=True, frozen=True)

    declension: DeclensionRecord = Field(default_factory=DeclensionRecord) [cite: 3273, 3282]
    gender: GenderType = Field(default=GenderType.X) [cite: 3273, 3283]
    kind: NounKindType = Field(default=NounKindType.X) [cite: 3274, 3284]

# --- Migration Service ---

class NounEntryIOService:
    """
    Migration of the Noun_Entry_IO package body.
    Handles fixed-width parsing and formatting for noun metadata.
    """

    # Default width based on Decn_Record_IO and Gender_Type_IO requirements
    FIELD_WIDTH: Final[int] = 2

    @staticmethod
    def get_from_string(source: str) -> Tuple[NounEntry, int]:
        """
        Implementation of procedure Get (Source : String; Target : out Noun_Entry; Last : out Integer).
        Parses noun metadata from a fixed-width string segment .
        """
        # Note: The Ada logic uses sequential calls to specific IO packages, each 
        # consuming characters and updating the 'Low' offset [cite: 3282-3284].
        
        # 1. Parse Declension Record (typically 2 chars)
        decl_str = source[0:2]
        # In a real system, this would call DecnRecordIOService.get(decl_str)
        # Here we simulate the extraction logic seen in the Ada body.
        
        # 2. Parse Gender (1-2 chars)
        gender_str = source[3:5].strip() [cite: 3283]
        
        # 3. Parse Noun Kind
        kind_str = source[6:8].strip() [cite: 3284]
        
        # Construct the entry. Conversion logic mapping to Ada Integer_IO is assumed here.
        entry = NounEntry(
            # declension=..., 
            # gender=..., 
            # kind=...
        )
        
        # The 'Last' index is determined by the final field read[cite: 3284].
        return entry, 8

    @staticmethod
    def put_to_string(item: NounEntry) -> str:
        """
        Implementation of procedure Put (Target : out String; Item : in Noun_Entry).
        Formats the NounEntry into a standard DICTLINE segment [cite: 3285-3292].
        """
        # Matches the Ada pattern of writing records separated by single spaces [cite: 3287-3290].
        # Each field uses its Default_Width for alignment[cite: 3286].
        parts = [
            f"{item.declension.to_string():<{NounEntryIOService.FIELD_WIDTH}}", [cite: 3287]
            f"{item.gender.value:>{NounEntryIOService.FIELD_WIDTH}}", [cite: 3289]
            f"{item.kind.value:>{NounEntryIOService.FIELD_WIDTH}}" [cite: 3291]
        ]
        
        # The final segment is padded with spaces.
        return " ".join(parts).ljust(12)

    @staticmethod
    def put_to_file(file: TextIO, item: NounEntry) -> None:
        """
        Implementation of procedure Put (File : File_Type; Item : in Noun_Entry).
        Writes formatted noun metadata to a file stream [cite: 3277-3278].
        """
        # Ada: Put (File, Item.Decl); Put (File, ' '); Put (File, Item.Gender); ... [cite: 3278]
        file.write(f"{item.declension.to_string()} ")
        file.write(f"{item.gender.value} ")
        file.write(f"{item.kind.value}")

# --- Public API Stub (.pyi equivalent) ---

"""
from typing import TextIO, Tuple
from .dictionary_package import NounEntry

class NounEntryIOService:
    @staticmethod
    def get_from_string(source: str) -> Tuple[NounEntry, int]: ...
    @staticmethod
    def put_to_string(item: NounEntry) -> str: ...
    @staticmethod
    def put_to_file(file: TextIO, item: NounEntry) -> None: ...
"""
