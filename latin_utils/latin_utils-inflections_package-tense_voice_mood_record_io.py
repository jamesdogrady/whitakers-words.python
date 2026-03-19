from __future__ import annotations
from typing import Final, TextIO, Tuple, Optional
from pydantic import BaseModel, Field, ConfigDict

# --- Dependencies (Imported from previously migrated Inflections_Package) ---
from .inflections_package import (
    TenseType,
    VoiceType,
    MoodType
)

# --- Core Data Model ---

class TenseVoiceMoodRecord(BaseModel):
    """
    Expert migration of Tense_Voice_Mood_Record from Ada to Python 3.12+.
    Represents the composite verbal qualities of a Latin verb instance.
    """
    model_config = ConfigDict(validate_assignment=True, frozen=True)

    tense: TenseType = Field(default=TenseType.X)
    voice: VoiceType = Field(default=VoiceType.X)
    mood: MoodType = Field(default=MoodType.X)

# --- Migration Service ---

class TenseVoiceMoodRecordIOService:
    """
    Migration of Tense_Voice_Mood_Record_IO package body.
    Handles fixed-width parsing and formatting for verbal metadata.
    """

    # Width constants matching legacy IO defaults to ensure bit-parity with INFLECT.LAT
    TENSE_WIDTH: Final[int] = 1
    VOICE_WIDTH: Final[int] = 1
    MOOD_WIDTH: Final[int] = 1

    @staticmethod
    def get_from_string(source: str) -> Tuple[TenseVoiceMoodRecord, int]:
        """
        Implementation of procedure Get (Source : String; Target : out Tense_Voice_Mood_Record; Last : out Integer).
        Sequentially parses tense, voice, and mood separated by single-character spacers [cite: 1149-1152].
        """
        # Note: Ada logic tracks a 'Low' offset through the string buffer [cite: 1149-1150].
        
        # 1. Parse Tense
        tense_segment = source[0:TenseVoiceMoodRecordIOService.TENSE_WIDTH].strip()
        tense = TenseType(tense_segment) if tense_segment else TenseType.X
        
        # 2. Skip Spacer and Parse Voice [cite: 1150-1151]
        # Low := Low + 1;
        voice_start = TenseVoiceMoodRecordIOService.TENSE_WIDTH + 1
        voice_segment = source[voice_start : voice_start + TenseVoiceMoodRecordIOService.VOICE_WIDTH].strip()
        voice = VoiceType(voice_segment) if voice_segment else VoiceType.X
        
        # 3. Skip Spacer and Parse Mood [cite: 1151-1152]
        # Low := Low + 1;
        mood_start = voice_start + TenseVoiceMoodRecordIOService.VOICE_WIDTH + 1
        mood_segment = source[mood_start : mood_start + TenseVoiceMoodRecordIOService.MOOD_WIDTH].strip()
        mood = MoodType(mood_segment) if mood_segment else MoodType.X

        target = TenseVoiceMoodRecord(tense=tense, voice=voice, mood=mood)
        
        # Return record and last character position processed [cite: 1152]
        return target, mood_start + TenseVoiceMoodRecordIOService.MOOD_WIDTH

    @staticmethod
    def put_to_string(item: TenseVoiceMoodRecord, buffer_length: int = 20) -> str:
        """
        Implementation of procedure Put (Target : out String; Item : in Tense_Voice_Mood_Record).
        Serializes verbal metadata into a fixed-width segment with space delimiters [cite: 1153-1160].
        """
        # Replicates sequential field + space assignment [cite: 1155-1158]
        tense_part = f"{item.tense.value:>{TenseVoiceMoodRecordIOService.TENSE_WIDTH}}"
        voice_part = f"{item.voice.value:>{TenseVoiceMoodRecordIOService.VOICE_WIDTH}}"
        mood_part = f"{item.mood.value:>{TenseVoiceMoodRecordIOService.MOOD_WIDTH}}"
        
        # Assemble with single spaces [cite: 1156, 1158]
        result = f"{tense_part} {voice_part} {mood_part}"
        
        # Fill remainder of string with spaces [cite: 1159-1160]
        # Target (High + 1 .. Target'Last) := (others => ' ');
        return result.ljust(buffer_length)

    @staticmethod
    def put_to_file(file: TextIO, item: TenseVoiceMoodRecord) -> None:
        """
        Implementation of procedure Put (File : File_Type; Item : in Tense_Voice_Mood_Record).
        Writes formatted verbal metadata directly to a file stream [cite: 1145-1146].
        """
        # Ada: Tense_Type_IO.Put(File, Item.Tense); Put(File, ' '); Voice_Type_IO.Put(File, Item.Voice); ... [cite: 1145-1146]
        file.write(f"{item.tense.value:>{TenseVoiceMoodRecordIOService.TENSE_WIDTH}} ")
        file.write(f"{item.voice.value:>{TenseVoiceMoodRecordIOService.VOICE_WIDTH}} ")
        file.write(f"{item.mood.value:>{TenseVoiceMoodRecordIOService.MOOD_WIDTH}}")

# --- Public API Stub (.pyi equivalent) ---

"""
from typing import TextIO, Tuple
from .inflections_package import TenseVoiceMoodRecord

class TenseVoiceMoodRecordIOService:
    @staticmethod
    def get_from_string(source: str) -> Tuple[TenseVoiceMoodRecord, int]: ...
    @staticmethod
    def put_to_string(item: TenseVoiceMoodRecord, buffer_length: int = 20) -> str: ...
    @staticmethod
    def put_to_file(file: TextIO, item: TenseVoiceMoodRecord) -> None: ...
"""
