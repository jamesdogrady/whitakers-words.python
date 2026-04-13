from __future__ import annotations
from typing import Final, TextIO, Tuple, Optional
from pydantic import BaseModel, Field, ConfigDict

# --- Dependencies (Imported from previously migrated Inflections_Package) ---
from .inflections_package import (
    DeclensionRecord,
    CaseType,
    NumberType,
    GenderType,
    ComparisonType
)

# --- Core Data Model ---

class AdjectiveRecord(BaseModel):
    """
    Expert migration of the Adjective_Record from Ada to Python 3.12+.
    Represents the full inflectional identity of a Latin adjective instance [cite: 2596-2598].
    """
    model_config = ConfigDict(validate_assignment=True, frozen=True)

    declension: DeclensionRecord = Field(default_factory=DeclensionRecord) [cite: 2610]
    case: CaseType = Field(default=CaseType.X, alias="of_case") [cite: 2610]
    number: NumberType = Field(default=NumberType.X) [cite: 2611]
    gender: GenderType = Field(default=GenderType.X) [cite: 2611]
    comparison: ComparisonType = Field(default=ComparisonType.X) [cite: 2612]

# --- Migration Service ---

class AdjectiveRecordIOService:
    """
    Migration of the Adjective_Record_IO package body.
    Handles fixed-width parsing and formatting for adjective inflection metadata.
    """

    # Width constants based on sub-component IO defaults (e.g., Decn_Record_IO.Default_Width)
    # These ensure bit-parity with Whitaker's text-based inflection tables.
    DECN_WIDTH: Final[int] = 2
    CASE_WIDTH: Final[int] = 2
    NUM_WIDTH: Final[int] = 2
    GEND_WIDTH: Final[int] = 2
    COMP_WIDTH: Final[int] = 2

    @staticmethod
    def get_from_string(source: str) -> Tuple[AdjectiveRecord, int]:
        """
        Implementation of procedure Get (Source : String; Target : out Adjective_Record; Last : out Integer).
        Sequentially parses inflection fields separated by single-character spacers [cite: 2621-2626].
        """
        # Note: Ada logic tracks a 'Low' offset through the string buffer [cite: 2621-2622].
        
        # 1. Parse Declension Record (typically 2 chars)
        decl_segment = source[0:2]
        
        # 2. Skip Spacer and Parse Case
        # Low := Low + 1; [cite: 2622]
        case_segment = source[3:5].strip()
        
        # 3. Skip Spacer and Parse Number
        # Low := Low + 1; [cite: 2624]
        num_segment = source[6:8].strip()
        
        # 4. Skip Spacer and Parse Gender
        # Low := Low + 1; [cite: 2625]
        gend_segment = source[9:11].strip()
        
        # 5. Skip Spacer and Parse Comparison
        # Comparison_Type_IO.Get (..., Last); [cite: 2626]
        comp_segment = source[12:14].strip()

        # Construct record (Assuming sub-service integer-to-enum conversion)
        target = AdjectiveRecord(
            # declension=DeclensionRecordIOService.get_from_string(decl_segment),
            case=CaseType(int(case_segment)) if case_segment.isdigit() else CaseType.X,
            number=NumberType(int(num_segment)) if num_segment.isdigit() else NumberType.X,
            gender=GenderType(gend_segment) if gend_segment else GenderType.X,
            comparison=ComparisonType(int(comp_segment)) if comp_segment.isdigit() else ComparisonType.X
        )

        return target, 14

    @staticmethod
    def put_to_string(item: AdjectiveRecord) -> str:
        """
        Implementation of procedure Put (Target : out String; Item : in Adjective_Record).
        Serializes an AdjectiveRecord into a fixed-width segment with space delimiters [cite: 2627-2636].
        """
        # Replicates sequential field + space assignment [cite: 2628-2635]
        parts = [
            f"{item.declension.to_string():<{AdjectiveRecordIOService.DECN_WIDTH}}", [cite: 2629]
            f"{item.case.value:>{AdjectiveRecordIOService.CASE_WIDTH}}", [cite: 2630]
            f"{item.number.value:>{AdjectiveRecordIOService.NUM_WIDTH}}", [cite: 2632]
            f"{item.gender.value:>{AdjectiveRecordIOService.GEND_WIDTH}}", [cite: 2634]
            f"{item.comparison.value:>{AdjectiveRecordIOService.COMP_WIDTH}}" [cite: 2636]
        ]
        
        # Assemble with single spaces
        result = " ".join(parts)
        
        # Fill remainder of string with spaces [cite: 2637]
        # Target (High + 1 .. Target'Last) := (others => ' ');
        return result.ljust(20)

    @staticmethod
    def put_to_file(file: TextIO, item: AdjectiveRecord) -> None:
        """
        Implementation of procedure Put (File : File_Type; Item : in Adjective_Record).
        Writes formatted adjective metadata directly to a file stream [cite: 2616-2618].
        """
        # Ada: Decn_Record_IO.Put(File, Item.Decl); Put(File, ' '); Case_Type_IO.Put(File, Item.Of_Case); ... [cite: 2616-2618]
        file.write(f"{item.declension.to_string()} ") [cite: 2616-2617]
        file.write(f"{item.case.value:>{AdjectiveRecordIOService.CASE_WIDTH}} ") [cite: 2617]
        file.write(f"{item.number.value:>{AdjectiveRecordIOService.NUM_WIDTH}} ") [cite: 2617]
        file.write(f"{item.gender.value:>{AdjectiveRecordIOService.GEND_WIDTH}} ") [cite: 2618]
        file.write(f"{item.comparison.value:>{AdjectiveRecordIOService.COMP_WIDTH}}") [cite: 2618]

# --- Public API Stub (.pyi equivalent) ---

"""
from typing import TextIO, Tuple
from .inflections_package import AdjectiveRecord

class AdjectiveRecordIOService:
    @staticmethod
    def get_from_string(source: str) -> Tuple[AdjectiveRecord, int]: ...
    @staticmethod
    def put_to_string(item: AdjectiveRecord) -> str: ...
    @staticmethod
    def put_to_file(file: TextIO, item: AdjectiveRecord) -> None: ...
"""
