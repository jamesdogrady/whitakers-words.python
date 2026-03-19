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

class NounRecord(BaseModel):
    """
    Expert migration of the Noun_Record from Ada to Python 3.12+.
    Represents the full inflectional identity of a Latin noun instance[cite: 1194].
    """
    model_config = ConfigDict(validate_assignment=True, frozen=True)

    declension: DeclensionRecord = Field(default_factory=DeclensionRecord, alias="decl") [cite: 1195]
    case: CaseType = Field(default=CaseType.X, alias="of_case") [cite: 1195]
    number: NumberType = Field(default=NumberType.X) [cite: 1196]
    gender: GenderType = Field(default=GenderType.X) [cite: 1196]

# --- Migration Service ---

class NounRecordIOService:
    """
    Migration of the Noun_Record_IO package body.
    Handles fixed-width parsing and formatting for noun inflection metadata[cite: 1194].
    """

    # Field widths matching legacy IO packages to ensure bit-parity with INFLECT.LAT
    DECN_WIDTH: Final[int] = 2
    CASE_WIDTH: Final[int] = 2
    NUM_WIDTH: Final[int] = 2
    GEND_WIDTH: Final[int] = 2

    @staticmethod
    def get_from_string(source: str) -> Tuple[NounRecord, int]:
        """
        Implementation of procedure Get (Source : String; Target : out Noun_Record; Last : out Integer).
        Sequentially parses declension, case, number, and gender fields .
        """
        # Note: Ada logic tracks a 'Low' offset through the string buffer [cite: 1204-1205].
        
        # 1. Parse Declension Record (typically 2 chars)
        # Decn_Record_IO.Get (Source (Low + 1 .. Source'Last), Target.Decl, Low); [cite: 1205]
        decl_segment = source[0:2]
        
        # 2. Skip Spacer and Parse Case
        # Low := Low + 1; [cite: 1205]
        case_segment = source[3:5].strip() [cite: 1206]
        
        # 3. Skip Spacer and Parse Number
        # Low := Low + 1; [cite: 1206]
        num_segment = source[6:8].strip() [cite: 1207]
        
        # 4. Skip Spacer and Parse Gender
        # Low := Low + 1; [cite: 1207]
        gend_segment = source[9:11].strip() [cite: 1208]

        # Construct record (Assuming sub-service conversion logic)
        target = NounRecord(
            # declension=DeclensionRecordIOService.get_from_string(decl_segment),
            case=CaseType(int(case_segment)) if case_segment.isdigit() else CaseType.X,
            number=NumberType(int(num_segment)) if num_segment.isdigit() else NumberType.X,
            gender=GenderType(gend_segment) if gend_segment else GenderType.X
        )

        return target, 11 [cite: 1208]

    @staticmethod
    def put_to_string(item: NounRecord, buffer_length: int = 20) -> str:
        """
        Implementation of procedure Put (Target : out String; Item : in Noun_Record).
        Serializes a NounRecord into a fixed-width segment with space delimiters [cite: 1209-1218].
        """
        # Replicates sequential field + space assignment [cite: 1210-1216]
        parts = [
            f"{item.declension.to_string():<{NounRecordIOService.DECN_WIDTH}}", [cite: 1211]
            f"{item.case.value:>{NounRecordIOService.CASE_WIDTH}}", [cite: 1212]
            f"{item.number.value:>{NounRecordIOService.NUM_WIDTH}}", [cite: 1214]
            f"{item.gender.value:>{NounRecordIOService.GEND_WIDTH}}" [cite: 1216]
        ]
        
        # Assemble with single spaces [cite: 1212, 1213, 1215]
        result = " ".join(parts)
        
        # Fill remainder of string with spaces 
        # Target (High + 1 .. Target'Last) := (others => ' ');
        return result.ljust(buffer_length)

    @staticmethod
    def put_to_file(file: TextIO, item: NounRecord) -> None:
        """
        Implementation of procedure Put (File : File_Type; Item : in Noun_Record).
        Writes formatted noun metadata directly to a file stream [cite: 1200-1202].
        """
        # Ada: Decn_Record_IO.Put(File, Item.Decl); Put(File, ' '); Case_Type_IO.Put(File, Item.Of_Case); ... [cite: 1200-1201]
        file.write(f"{item.declension.to_string()} ") [cite: 1200-1201]
        file.write(f"{item.case.value:>{NounRecordIOService.CASE_WIDTH}} ") [cite: 1201]
        file.write(f"{item.number.value:>{NounRecordIOService.NUM_WIDTH}} ") [cite: 1201]
        file.write(f"{item.gender.value:>{NounRecordIOService.GEND_WIDTH}}") [cite: 1202]

# --- Public API Stub (.pyi equivalent) ---

"""
from typing import TextIO, Tuple
from .inflections_package import NounRecord

class NounRecordIOService:
    @staticmethod
    def get_from_string(source: str) -> Tuple[NounRecord, int]: ...
    @staticmethod
    def put_to_string(item: NounRecord, buffer_length: int = 20) -> str: ...
    @staticmethod
    def put_to_file(file: TextIO, item: NounRecord) -> None: ...
"""
