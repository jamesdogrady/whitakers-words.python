from __future__ import annotations
from typing import Final, TextIO, Tuple, List, Optional
from pydantic import BaseModel, Field, ConfigDict

# --- Dependencies (Imported from previously migrated Inflections_Package) ---
from .inflections_package import (
    DecnRecord, 
    CaseType, 
    NumberType, 
    GenderType, 
    TenseVoiceMoodRecord,
    StemType,
    MeaningType,
    NullStemType,
    NullMeaningType,
    PartOfSpeech
)
from .decn_record_io import DecnRecordIOService
from .tense_voice_mood_record_io import TenseVoiceMoodRecordIOService

# --- Core Data Models ---

class VparRecord(BaseModel):
    """
    Expert migration of the Vpar_Record from Ada to Python 3.12+.
    Represents the full inflectional identity of a Latin verbal participle .
    """
    model_config = ConfigDict(validate_assignment=True, frozen=True)

    con: DecnRecord = Field(default_factory=DecnRecord)
    case: CaseType = Field(default=CaseType.X, alias="of_case")
    number: NumberType = Field(default=NumberType.X)
    gender: GenderType = Field(default=GenderType.X)
    tense_voice_mood: TenseVoiceMoodRecord = Field(default_factory=TenseVoiceMoodRecord)


class DictionaryEntry(BaseModel):
    """
    Master record for a Whitaker's WORDS dictionary entry [cite: 1412-1414, 1580-1582].
    Coordinates stems, part-of-speech specific metadata, and meanings.
    """
    model_config = ConfigDict(validate_assignment=True, frozen=True)

    stems: List[StemType] = Field(default_factory=lambda: [NullStemType] * 4) [cite: 1412, 1580]
    # part: PartEntry = Field(default_factory=NullPartEntry) [cite: 1413, 1581]
    # tran: TranslationRecord = Field(default_factory=NullTranslationRecord) [cite: 1413, 1581]
    meaning: MeaningType = NullMeaningType [cite: 1414, 1582]

# --- Migration Services ---

class VparRecordIOService:
    """
    Migration of the Vpar_Record_IO package body.
    Handles fixed-width parsing and formatting for verbal participle metadata.
    """

    # Field widths matching legacy IO packages to ensure bit-parity with INFLECT.LAT
    DECN_WIDTH: Final[int] = 2
    CASE_WIDTH: Final[int] = 2
    NUM_WIDTH: Final[int] = 2
    GEND_WIDTH: Final[int] = 2

    @staticmethod
    def get_from_string(source: str) -> Tuple[VparRecord, int]:
        """
        Implementation of procedure Get (Source : String; Target : out Vpar_Record; Last : out Integer).
        Sequentially parses conjugation, case, number, gender, and tense/voice/mood [cite: 2467-2472].
        """
        # 1. Parse Conjugation (Mapped to DecnRecord) [cite: 2468]
        con, low = DecnRecordIOService.get_from_string(source)
        
        # 2. Skip Spacer and Parse Case [cite: 2469]
        low += 1
        case_segment = source[low : low + VparRecordIOService.CASE_WIDTH].strip()
        case = CaseType(int(case_segment)) if case_segment.isdigit() else CaseType.X
        
        # 3. Skip Spacer and Parse Number [cite: 2470]
        low += VparRecordIOService.CASE_WIDTH + 1
        num_segment = source[low : low + VparRecordIOService.NUM_WIDTH].strip()
        number = NumberType(int(num_segment)) if num_segment.isdigit() else NumberType.X
        
        # 4. Skip Spacer and Parse Gender [cite: 2471]
        low += VparRecordIOService.NUM_WIDTH + 1
        gend_segment = source[low : low + VparRecordIOService.GEND_WIDTH].strip()
        gender = GenderType(gend_segment) if gend_segment else GenderType.X
        
        # 5. Skip Spacer and Parse Tense/Voice/Mood composite record [cite: 2472]
        low += VparRecordIOService.GEND_WIDTH + 1
        tvm, last_pos = TenseVoiceMoodRecordIOService.get_from_string(source[low:])

        target = VparRecord(
            con=con,
            case=case,
            number=number,
            gender=gender,
            tense_voice_mood=tvm
        )

        return target, low + last_pos

    @staticmethod
    def put_to_string(item: VparRecord, buffer_length: int = 30) -> str:
        """
        Implementation of procedure Put (Target : out String; Item : in Vpar_Record).
        Serializes a VparRecord into a fixed-width segment with space delimiters [cite: 2473-2484].
        """
        # Replicates sequential field + space assignment [cite: 2475-2482]
        parts = [
            f"{item.con.to_string():<{VparRecordIOService.DECN_WIDTH}}",
            f"{item.case.value:>{VparRecordIOService.CASE_WIDTH}}",
            f"{item.number.value:>{VparRecordIOService.NUM_WIDTH}}",
            f"{item.gender.value:>{VparRecordIOService.GEND_WIDTH}}",
            TenseVoiceMoodRecordIOService.put_to_string(item.tense_voice_mood, buffer_length=8)
        ]
        
        result = " ".join(parts) [cite: 2476, 2477, 2479, 2481]
        
        # Fill remainder of string with spaces [cite: 2483]
        return result.ljust(buffer_length)

    @staticmethod
    def put_to_file(file: TextIO, item: VparRecord) -> None:
        """
        Implementation of procedure Put (File : File_Type; Item : in Vpar_Record).
        Writes formatted verbal participle metadata directly to a file stream [cite: 2462-2464].
        """
        # Ada: Decn_Record_IO.Put(File, Item.Con); Put(File, ' '); Case_Type_IO.Put(...); ... [cite: 2462-2464]
        DecnRecordIOService.put_to_file(file, item.con)
        file.write(" ")
        file.write(f"{item.case.value:>{VparRecordIOService.CASE_WIDTH}} ")
        file.write(f"{item.number.value:>{VparRecordIOService.NUM_WIDTH}} ")
        file.write(f"{item.gender.value:>{VparRecordIOService.GEND_WIDTH}} ")
        TenseVoiceMoodRecordIOService.put_to_file(file, item.tense_voice_mood)


class DictionaryPackageService:
    """
    Expert migration of the core Dictionary_Package logic.
    Handles global initialization andpart-of-speech stem counts [cite: 1606-1614].
    """

    @staticmethod
    def number_of_stems(part: PartOfSpeech) -> int:
        """Returns the expected number of stems for a given POS [cite: 1431, 1607-1614]."""
        match part:
            case PartOfSpeech.N | PartOfSpeech.PRON | PartOfSpeech.PACK: return 2 [cite: 1607-1608]
            case PartOfSpeech.ADJ | PartOfSpeech.NUM | PartOfSpeech.V: return 4 [cite: 1609-1610]
            case PartOfSpeech.ADV: return 3 [cite: 1610]
            case PartOfSpeech.PREP | PartOfSpeech.CONJ | PartOfSpeech.INTERJ: return 1 [cite: 1612-1613]
            case _: return 0 [cite: 1611, 1613-1614]

# --- Public API Stub (.pyi equivalent) ---

"""
from typing import TextIO, Tuple
from .inflections_package import VparRecord

class VparRecordIOService:
    @staticmethod
    def get_from_string(source: str) -> Tuple[VparRecord, int]: ...
    @staticmethod
    def put_to_string(item: VparRecord, buffer_length: int = 30) -> str: ...
    @staticmethod
    def put_to_file(file: TextIO, item: VparRecord) -> None: ...
"""
