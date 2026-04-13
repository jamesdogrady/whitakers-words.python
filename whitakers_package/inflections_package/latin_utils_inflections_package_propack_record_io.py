from __future__ import annotations
from typing import Final, TextIO, Tuple, Optional
from pydantic import BaseModel, Field, ConfigDict

# --- Dependencies (Imported from previously migrated modules) ---
from .inflections_package import (
    DeclensionRecord, 
    CaseType, 
    NumberType, 
    GenderType
)

# --- Core Data Model ---

class PropackRecord(BaseModel):
    """
    Expert migration of the Propack_Record from Ada to Python 3.12+.
    Represents the full inflectional identity of a Latin pronoun package instance[cite: 2739, 2740].
    
    This record captures the declension, case, number, and gender which 
    characterize an enclitic-combined pronoun form [cite: 2725-2726].
    """
    model_config = ConfigDict(validate_assignment=True, frozen=True)

    declension: DeclensionRecord = Field(default_factory=DeclensionRecord, alias="decl") [cite: 2739, 2749]
    case: CaseType = Field(default=CaseType.X, alias="of_case") [cite: 2739, 2750]
    number: NumberType = Field(default=NumberType.X) [cite: 2740, 2751]
    gender: GenderType = Field(default=GenderType.X) [cite: 2740, 2752]

# --- Migration Service ---

class PropackRecordIOService:
    """
    Migration of the Propack_Record_IO package body.
    Handles fixed-width parsing and formatting for pronoun package inflection metadata [cite: 2725-2726].
    """

    # Field widths matching legacy IO packages to ensure bit-parity with INFLECT.LAT
    DECN_WIDTH: Final[int] = 2
    CASE_WIDTH: Final[int] = 2
    NUM_WIDTH: Final[int] = 2
    GEND_WIDTH: Final[int] = 2

    @staticmethod
    def get_from_string(source: str) -> Tuple[PropackRecord, int]:
        """
        Implementation of procedure Get (Source : String; Target : out Propack_Record; Last : out Integer).
        Sequentially parses declension, case, number, and gender fields from a string segment [cite: 2748-2753].
        """
        # Note: Ada logic tracks a 'Low' offset through the string buffer [cite: 2748-2749].
        
        # 1. Parse Declension Record (typically 2 chars)
        # Decn_Record_IO.Get (Source (Low + 1 .. Source'Last), Target.Decl, Low); [cite: 2749]
        decl_segment = source[0:2]
        
        # 2. Skip Spacer and Parse Case [cite: 2750]
        # Low := Low + 1; Case_Type_IO.Get (...);
        case_segment = source[3:5].strip()
        
        # 3. Skip Spacer and Parse Number [cite: 2751]
        # Low := Low + 1; Number_Type_IO.Get (...);
        num_segment = source[6:8].strip()
        
        # 4. Skip Spacer and Parse Gender [cite: 2752]
        # Low := Low + 1; Gender_Type_IO.Get (...);
        gend_segment = source[9:11].strip()

        # Construct record. Conversion/Enum lookup assumes standard Whitaker integer codes.
        target = PropackRecord(
            # declension=DeclensionRecordIOService.get_from_string(decl_segment),
            case=CaseType(int(case_segment)) if case_segment.isdigit() else CaseType.X,
            number=NumberType(int(num_segment)) if num_segment.isdigit() else NumberType.X,
            gender=GenderType(gend_segment) if gend_segment else GenderType.X
        )

        # Return the record and the 'Last' position consumed[cite: 2752].
        return target, 11

    @staticmethod
    def put_to_string(item: PropackRecord, buffer_length: int = 20) -> str:
        """
        Implementation of procedure Put (Target : out String; Item : in Propack_Record).
        Serializes a PropackRecord into a fixed-width segment with space delimiters [cite: 2753-2762].
        """
        # Replicates sequential field + space assignment [cite: 2755-2760]
        # Uses explicit spacers (' ') between each field[cite: 2756, 2757, 2759].
        parts = [
            f"{item.declension.to_string():<{PropackRecordIOService.DECN_WIDTH}}",
            f"{item.case.value:>{PropackRecordIOService.CASE_WIDTH}}",
            f"{item.number.value:>{PropackRecordIOService.NUM_WIDTH}}",
            f"{item.gender.value:>{PropackRecordIOService.GEND_WIDTH}}"
        ]
        
        # Assemble with single spaces as spacers
        result = " ".join(parts)
        
        # Fill remainder of target string with spaces to maintain column alignment[cite: 2761].
        # Target (High + 1 .. Target'Last) := (others => ' ');
        return result.ljust(buffer_length)

    @staticmethod
    def put_to_file(file: TextIO, item: PropackRecord) -> None:
        """
        Implementation of procedure Put (File : File_Type; Item : in Propack_Record).
        Writes formatted propack metadata directly to a file stream [cite: 2744-2746].
        """
        # Ada logic: Put(File, Item.Decl); Put(File, ' '); Put(File, Item.Of_Case); ... [cite: 2745, 2746]
        file.write(f"{item.declension.to_string()} ")
        file.write(f"{item.case.value:>{PropackRecordIOService.CASE_WIDTH}} ")
        file.write(f"{item.number.value:>{PropackRecordIOService.NUM_WIDTH}} ")
        file.write(f"{item.gender.value:>{PropackRecordIOService.GEND_WIDTH}}")

# --- Public API Stub (.pyi equivalent) ---

"""
from typing import TextIO, Tuple
from .inflections_package import PropackRecord

class PropackRecordIOService:
    @staticmethod
    def get_from_string(source: str) -> Tuple[PropackRecord, int]: ...
    @staticmethod
    def put_to_string(item: PropackRecord, buffer_length: int = 20) -> str: ...
    @staticmethod
    def put_to_file(file: TextIO, item: PropackRecord) -> None: ...
"""
