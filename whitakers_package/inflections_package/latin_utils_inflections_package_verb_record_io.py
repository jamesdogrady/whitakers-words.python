from __future__ import annotations
from typing import Final, TextIO, Tuple, Optional
from pydantic import BaseModel, Field, ConfigDict

# --- Dependencies (Imported from previously migrated Inflections_Package) ---
from .inflections_package import (
    DecnRecord,
    PersonType,
    NumberType,
    TenseVoiceMoodRecord
)
from .decn_record_io import DecnRecordIOService
from .tense_voice_mood_record_io import TenseVoiceMoodRecordIOService

# --- Core Data Model ---

class VerbRecord(BaseModel):
    """
    Expert migration of Verb_Record from Ada to Python 3.12+.
    Represents the full inflectional identity of a Latin verb instance [cite: 1174-1176].
    """
    model_config = ConfigDict(validate_assignment=True, frozen=True)

    con: DecnRecord = Field(default_factory=DecnRecord)
    tense_voice_mood: TenseVoiceMoodRecord = Field(default_factory=TenseVoiceMoodRecord)
    person: PersonType = Field(default=PersonType.X)
    number: NumberType = Field(default=NumberType.X)

# --- Migration Service ---

class VerbRecordIOService:
    """
    Migration of Verb_Record_IO package body.
    Handles fixed-width parsing and formatting for verbal inflection metadata.
    """

    # Field widths matching legacy IO packages to ensure bit-parity with INFLECT.LAT
    # Based on Whitaker's standard column alignments [cite: 1190-1197].
    PERS_WIDTH: Final[int] = 1
    NUM_WIDTH: Final[int] = 1

    @staticmethod
    def get_from_string(source: str) -> Tuple[VerbRecord, int]:
        """
        Implementation of procedure Get (Source : String; Target : out Verb_Record; Last : out Integer).
        Sequentially parses conjugation, tense/voice/mood, person, and number [cite: 1184-1188].
        """
        # Note: Ada logic tracks a 'Low' offset through the string buffer [cite: 1184-1185].
        
        # 1. Parse Conjugation Record (DecnRecord)
        con, low = DecnRecordIOService.get_from_string(source)
        
        # 2. Skip Spacer and Parse Tense/Voice/Mood composite record [cite: 1185-1186]
        low += 1
        tvm, last_tvm_pos = TenseVoiceMoodRecordIOService.get_from_string(source[low:])
        low += last_tvm_pos
        
        # 3. Skip Spacer and Parse Person [cite: 1187]
        low += 1
        person_segment = source[low : low + VerbRecordIOService.PERS_WIDTH].strip()
        person = PersonType(int(person_segment)) if person_segment.isdigit() else PersonType.X
        
        # 4. Skip Spacer and Parse Number [cite: 1187-1188]
        low += 1
        num_segment = source[low : low + VerbRecordIOService.NUM_WIDTH].strip()
        number = NumberType(int(num_segment)) if num_segment.isdigit() else NumberType.X

        target = VerbRecord(
            con=con,
            tense_voice_mood=tvm,
            person=person,
            number=number
        )

        return target, low + VerbRecordIOService.NUM_WIDTH

    @staticmethod
    def put_to_string(item: VerbRecord, buffer_length: int = 25) -> str:
        """
        Implementation of procedure Put (Target : out String; Item : in Verb_Record).
        Serializes a VerbRecord into a fixed-width segment with space delimiters [cite: 1189-1199].
        """
        # Replicates sequential field + space assignment [cite: 1191-1197]
        con_part = DecnRecordIOService.put_to_string(item.con, length=3)
        tvm_part = TenseVoiceMoodRecordIOService.put_to_string(item.tense_voice_mood, buffer_length=5)
        pers_part = f"{item.person.value:>{VerbRecordIOService.PERS_WIDTH}}"
        num_part = f"{item.number.value:>{VerbRecordIOService.NUM_WIDTH}}"
        
        # Assemble with single spaces
        result = f"{con_part} {tvm_part} {pers_part} {num_part}"
        
        # Fill remainder of string with spaces [cite: 1198-1199]
        # Target (High + 1 .. Target'Last) := (others => ' ');
        return result.ljust(buffer_length)

    @staticmethod
    def put_to_file(file: TextIO, item: VerbRecord) -> None:
        """
        Implementation of procedure Put (File : File_Type; Item : in Verb_Record).
        Writes formatted verb metadata directly to a file stream [cite: 1180-1182].
        """
        # Ada: Decn_Record_IO.Put(File, Item.Con); Put(File, ' '); ... [cite: 1180-1181]
        DecnRecordIOService.put_to_file(file, item.con)
        file.write(" ")
        TenseVoiceMoodRecordIOService.put_to_file(file, item.tense_voice_mood)
        file.write(f" {item.person.value:>{VerbRecordIOService.PERS_WIDTH}} ")
        file.write(f"{item.number.value:>{VerbRecordIOService.NUM_WIDTH}}")

# --- Public API Stub (.pyi equivalent) ---

"""
from typing import TextIO, Tuple
from .inflections_package import VerbRecord

class VerbRecordIOService:
    @staticmethod
    def get_from_string(source: str) -> Tuple[VerbRecord, int]: ...
    @staticmethod
    def put_to_string(item: VerbRecord, buffer_length: int = 25) -> str: ...
    @staticmethod
    def put_to_file(file: TextIO, item: VerbRecord) -> None: ...
"""
