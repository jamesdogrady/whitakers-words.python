from __future__ import annotations
from typing import Final, List, Optional, TextIO, Tuple
from pydantic import BaseModel, Field, ConfigDict, field_validator
from pathlib import Path

# --- Dependencies (Simulated from previously migrated modules) ---
from .latin_utils.inflections_package import (
    PartOfSpeechType, 
    FrequencyType, 
    DictionaryKind
)

# --- Core Constants and Subtypes ---

# Fixed-width sizes for English word metadata [cite: 5504-5505, 5531-5532]
EWORD_SIZE: Final[int] = 24
AUX_WORD_SIZE: Final[int] = 12
LINE_NUMBER_WIDTH: Final[int] = 10
PRIORITY_WIDTH: Final[int] = 3
NWIDTH: Final[int] = 5  # For numeric segments semi, kind, rank [cite: 5552]

class PriorityType(int):
    """Expert migration of Priority_Type range 0 .. 99."""
    def __new__(cls, value: int):
        if not (0 <= value <= 99):
            raise ValueError("Priority must be in range 0..99")
        return super().__new__(cls, value)


# --- Core Data Models ---

class EwdsRecord(BaseModel):
    """
    Expert migration of Ewds_Record.
    Represents an entry in the English-to-Latin mapping database [cite: 5509-5511, 5536-5538].
    """
    model_config = ConfigDict(validate_assignment=True)

    w: str = Field(default=" " * EWORD_SIZE, max_length=EWORD_SIZE)
    aux: str = Field(default=" " * AUX_WORD_SIZE, max_length=AUX_WORD_SIZE)
    n: int = 0
    pofs: PartOfSpeechType = Field(default=PartOfSpeechType.X)
    freq: FrequencyType = Field(default=FrequencyType.X)
    semi: int = 0
    kind: int = 0
    rank: int = 0

    @field_validator("w", "aux")
    @classmethod
    def pad_string_fields(cls, v: str, info) -> str:
        """Ensures string fields maintain fixed-width parity via space padding[cite: 5600, 5629]."""
        target_size = EWORD_SIZE if info.field_name == "w" else AUX_WORD_SIZE
        return v.ljust(target_size)[:target_size]

# Null record constant [cite: 5511, 5538]
NULL_EWDS_RECORD: Final[EwdsRecord] = EwdsRecord()


# --- Migration Service ---

class EnglishSupportService:
    """
    Expert migration of Words_Engine.English_Support_Package logic.
    Handles I/O and state management for the English dictionary lookup[cite: 5504, 5531].
    """

    def __init__(self):
        # Global state migrated to instance attributes [cite: 5517, 5544]
        self.english_dictionary_available: List[bool] = [False] * 11
        self.number_of_ewords: int = 0

    @staticmethod
    def get_from_string(source: str) -> Tuple[EwdsRecord, int]:
        """
        Implementation of Ewds_Record_Io.Get (S : String; P : out Ewds_Record; Last : out Integer).
        Parses a fixed-width string segment[cite: 5515, 5542].
        """
        # Whitaker's fixed-width consumption logic
        low = 0
        
        # 1. Word (24)
        w = source[low : low + EWORD_SIZE]
        low += EWORD_SIZE + 1  # Skip spacer
        
        # 2. Aux (12)
        aux = source[low : low + AUX_WORD_SIZE]
        low += AUX_WORD_SIZE + 1
        
        # 3. Line Number (10)
        n = int(source[low : low + LINE_NUMBER_WIDTH].strip() or 0)
        low += LINE_NUMBER_WIDTH + 1
        
        # 4. Part of Speech (Enum Width)
        pofs_segment = source[low : low + 3].strip()
        pofs = PartOfSpeechType(pofs_segment) if pofs_segment else PartOfSpeechType.X
        low += 4
        
        # 5. Frequency (Enum Width)
        freq_segment = source[low : low + 3].strip()
        freq = FrequencyType(freq_segment) if freq_segment else FrequencyType.X
        low += 4
        
        # 6. Numeric metadata fields (using NWIDTH=5) [cite: 5552]
        semi = int(source[low : low + NWIDTH].strip() or 0)
        low += NWIDTH + 1
        
        kind = int(source[low : low + NWIDTH].strip() or 0)
        low += NWIDTH + 1
        
        rank = int(source[low : low + NWIDTH].strip() or 0)
        last = low + NWIDTH

        return EwdsRecord(
            w=w, aux=aux, n=n, pofs=pofs, 
            freq=freq, semi=semi, kind=kind, rank=rank
        ), last

    @staticmethod
    def put_to_string(item: EwdsRecord) -> str:
        """
        Implementation of Ewds_Record_Io.Put (S : out String; P : in Ewds_Record).
        Serializes a record into Whitaker's fixed-width string format[cite: 5516, 5543].
        """
        # Building segments with spacers mimicking Ada body logic
        segments = [
            item.w.ljust(EWORD_SIZE),
            item.aux.ljust(AUX_WORD_SIZE),
            f"{item.n:>{LINE_NUMBER_WIDTH}}",
            f"{item.pofs.value:<3}",
            f"{item.freq.value:<3}",
            f"{item.semi:>{NWIDTH}}",
            f"{item.kind:>{NWIDTH}}",
            f"{item.rank:>{NWIDTH}}"
        ]
        return " ".join(segments)

    def write_to_file(self, file: TextIO, item: EwdsRecord) -> None:
        """
        Implementation of procedure Put (F : File_Type; P : in Ewds_Record).
        Writes formatted entry with spacers to a text stream[cite: 5514, 5541].
        """
        file.write(self.put_to_string(item) + "\n")

# --- Public API Stub (.pyi equivalent) ---

"""
from typing import Tuple, TextIO
from .english_support import EwdsRecord

class EnglishSupportService:
    def get_from_string(source: str) -> Tuple[EwdsRecord, int]: ...
    def put_to_string(item: EwdsRecord) -> str: ...
    def write_to_file(file: TextIO, item: EwdsRecord) -> None: ...
"""
