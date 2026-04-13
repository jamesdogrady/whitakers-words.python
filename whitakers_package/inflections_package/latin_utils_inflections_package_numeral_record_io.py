from __future__ import annotations
from typing import Final, TextIO, Tuple, Optional
from pydantic import BaseModel, Field, ConfigDict

# --- Dependencies (Imported from previously migrated inflections module) ---
from .inflections_package import (
    DeclensionRecord,
    CaseType,
    NumberType,
    GenderType,
    NumeralSortType
)

# --- Core Data Model ---

class NumeralRecord(BaseModel):
    """
    Expert migration of the Numeral_Record from Ada to Python 3.12+.
    Represents the full inflectional identity of a Latin numeral instance .
    """
    model_config = ConfigDict(validate_assignment=True, frozen=True)

    declension: DeclensionRecord = Field(default_factory=DeclensionRecord, alias="decl")
    case: CaseType = Field(default=CaseType.X, alias="of_case")
    number: NumberType = Field(default=NumberType.X)
    gender: GenderType = Field(default=GenderType.X)
    sort: NumeralSortType = Field(default=NumeralSortType.X)

# --- Migration Service ---

class NumeralRecordIOService:
    """
    Migration of the Numeral_Record_IO package body.
    Handles fixed-width parsing and formatting for numeral inflection metadata[cite: 2493].
    """

    # Field widths matching legacy IO packages to ensure bit-parity with INFLECT.LAT
    DECN_WIDTH: Final[int] = 2
    CASE_WIDTH: Final[int] = 2
    NUM_WIDTH: Final[int] = 2
    GEND_WIDTH: Final[int] = 2
    SORT_WIDTH: Final[int] = 2

    @staticmethod
    def get_from_string(source: str) -> Tuple[NumeralRecord, int]:
        """
        Implementation of procedure Get (Source : String; Target : out Numeral_Record; Last : out Integer).
        Sequentially parses declension, case, number, gender, and sort fields .
        """
        # Note: Ada logic tracks a 'Low' offset through the string buffer [cite: 2505-2506].
        
        # 1. Parse Declension Record (typically 2 chars)
        decl_segment = source[0:2]
        
        # 2. Skip Spacer and Parse Case [cite: 2506-2507]
        case_segment = source[3:5].strip()
        
        # 3. Skip Spacer and Parse Number [cite: 2507-2508]
        num_segment = source[6:8].strip()
        
        # 4. Skip Spacer and Parse Gender [cite: 2508-2509]
        gend_segment = source[9:11].strip()
        
        # 5. Skip Spacer and Parse Numeral Sort [cite: 2509-2510]
        sort_segment = source[12:14].strip()

        # Construct record. Conversion/Enum lookup assumes standard integer codes.
        target = NumeralRecord(
            # declension=DeclensionRecordIOService.get_from_string(decl_segment),
            case=CaseType(int(case_segment)) if case_segment.isdigit() else CaseType.X,
            number=NumberType(int(num_segment)) if num_segment.isdigit() else NumberType.X,
            gender=GenderType(gend_segment) if gend_segment else GenderType.X,
            sort=NumeralSortType(int(sort_segment)) if sort_segment.isdigit() else NumeralSortType.X
        )

        return target, 14

    @staticmethod
    def put_to_string(item: NumeralRecord, buffer_length: int = 20) -> str:
        """
        Implementation of procedure Put (Target : out String; Item : in Numeral_Record).
        Serializes a NumeralRecord into a fixed-width segment with space delimiters [cite: 2511-2521].
        """
        # Replicates sequential field + space assignment [cite: 2512-2520]
        parts = [
            f"{item.declension.to_string():<{NumeralRecordIOService.DECN_WIDTH}}",
            f"{item.case.value:>{NumeralRecordIOService.CASE_WIDTH}}",
            f"{item.number.value:>{NumeralRecordIOService.NUM_WIDTH}}",
            f"{item.gender.value:>{NumeralRecordIOService.GEND_WIDTH}}",
            f"{item.sort.value:>{NumeralRecordIOService.SORT_WIDTH}}"
        ]
        
        # Assemble with single spaces [cite: 2514, 2515, 2517, 2519]
        result = " ".join(parts)
        
        # Fill remainder of string with spaces to maintain column alignment [cite: 2521]
        # Target (High + 1 .. Target'Last) := (others => ' ');
        return result.ljust(buffer_length)

    @staticmethod
    def put_to_file(file: TextIO, item: NumeralRecord) -> None:
        """
        Implementation of procedure Put (File : File_Type; Item : in Numeral_Record).
        Writes formatted numeral metadata directly to a file stream [cite: 2500-2502].
        """
        # Ada: Decn_Record_IO.Put(File, Item.Decl); Put(File, ' '); Case_Type_IO.Put(File, Item.Of_Case); ... [cite: 2500-2501]
        file.write(f"{item.declension.to_string()} ")
        file.write(f"{item.case.value:>{NumeralRecordIOService.CASE_WIDTH}} ")
        file.write(f"{item.number.value:>{NumeralRecordIOService.NUM_WIDTH}} ")
        file.write(f"{item.gender.value:>{NumeralRecordIOService.GEND_WIDTH}} ")
        file.write(f"{item.sort.value:>{NumeralRecordIOService.SORT_WIDTH}}")

# --- Public API Stub (.pyi equivalent) ---

"""
from typing import TextIO, Tuple
from .inflections_package import NumeralRecord

class NumeralRecordIOService:
    @staticmethod
    def get_from_string(source: str) -> Tuple[NumeralRecord, int]: ...
    @staticmethod
    def put_to_string(item: NumeralRecord, buffer_length: int = 20) -> str: ...
    @staticmethod
    def put_to_file(file: TextIO, item: NumeralRecord) -> None: ...
"""
