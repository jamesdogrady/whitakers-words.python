from __future__ import annotations
from typing import Final, TextIO, Tuple, Optional
from pydantic import BaseModel, Field, ConfigDict

# --- Dependencies (Imported from previously migrated Inflections_Package) ---
from .inflections_package import (
    InflectionRecord,
    AgeType,
    FrequencyType,
    QualityRecord
)
from .quality_record_io import QualityRecordIOService
from .ending_record_io import EndingRecord, EndingRecordIOService

# --- Migration Service ---

class InflectionRecordIOService:
    """
    Migration of the Inflection_Record_IO package body.
    Handles fixed-width parsing and formatting for composite inflection metadata.
    """

    # Field widths matching legacy IO packages to ensure bit-parity with INFLECT.LAT
    KEY_WIDTH: Final[int] = 1
    AGE_WIDTH: Final[int] = 1
    FREQ_WIDTH: Final[int] = 1

    @staticmethod
    def get_from_string(source: str) -> Tuple[InflectionRecord, int]:
        """
        Implementation of procedure Get (Source : String; Target : out Inflection_Record; Last : out Integer).
        Sequentially parses quality, stem key, ending, age, and frequency fields [cite: 2948-2954].
        """
        # Note: Ada logic tracks a 'Low' offset through the string buffer [cite: 2949-2950].
        
        # 1. Parse Quality Record (Composite)
        qual_record, low = QualityRecordIOService.get_from_string(source)
        
        # 2. Skip Spacer and Parse Stem Key (Integer 1..4)
        low += 1
        key_segment = source[low : low + InflectionRecordIOService.KEY_WIDTH].strip()
        stem_key = int(key_segment) if key_segment.isdigit() else 0
        
        # 3. Skip Spacer and Parse Ending Record (Composite)
        low += InflectionRecordIOService.KEY_WIDTH + 1
        ending_record, last_ending_pos = EndingRecordIOService.get_from_string(source[low:])
        low += last_ending_pos
        
        # 4. Skip Spacer and Parse Age
        low += 1
        age_segment = source[low : low + InflectionRecordIOService.AGE_WIDTH].strip()
        age = AgeType(age_segment) if age_segment else AgeType.X
        
        # 5. Skip Spacer and Parse Frequency
        low += InflectionRecordIOService.AGE_WIDTH + 1
        freq_segment = source[low : low + InflectionRecordIOService.FREQ_WIDTH].strip()
        freq = FrequencyType(freq_segment) if freq_segment else FrequencyType.X

        # Construct master record [cite: 2950]
        target = InflectionRecord(
            qual=qual_record,
            key=stem_key,
            ending=ending_record,
            age=age,
            freq=freq
        )

        return target, low + InflectionRecordIOService.FREQ_WIDTH

    @staticmethod
    def put_to_string(item: InflectionRecord, buffer_length: int = 40) -> str:
        """
        Implementation of procedure Put (Target : out String; Item : in Inflection_Record).
        Serializes an InflectionRecord into a fixed-width segment with space delimiters [cite: 2955-2966].
        """
        # Formats record fields with explicit spacers to preserve column alignment [cite: 2957-2964]
        qual_part = QualityRecordIOService.put_to_string(item.qual)
        key_part = f"{item.key:1}"
        ending_part = EndingRecordIOService.put_to_string(item.ending)
        age_part = f"{item.age.value:1}"
        freq_part = f"{item.freq.value:1}"
        
        # Assemble with single spaces
        result = f"{qual_part} {key_part} {ending_part} {age_part} {freq_part}"
        
        # Fill remainder of target string buffer with spaces [cite: 2965]
        return result.ljust(buffer_length)

    @staticmethod
    def put_to_file(file: TextIO, item: InflectionRecord) -> None:
        """
        Implementation of procedure Put (File : File_Type; Item : in Inflection_Record).
        Writes formatted inflection metadata directly to a file stream [cite: 2943-2945].
        """
        # Ada: Quality_Record_IO.Put(File, Item.Qual); Put(File, ' '); Stem_Key_Type_IO.Put(File, Item.Key, 1); ...
        QualityRecordIOService.put_to_file(file, item.qual)
        file.write(" ")
        file.write(f"{item.key:1} ")
        EndingRecordIOService.put_to_file(file, item.ending)
        file.write(f" {item.age.value:1} {item.freq.value:1}")

# --- Public API Stub (.pyi equivalent) ---

"""
from typing import TextIO, Tuple
from .inflections_package import InflectionRecord

class InflectionRecordIOService:
    @staticmethod
    def get_from_string(source: str) -> Tuple[InflectionRecord, int]: ...
    @staticmethod
    def put_to_string(item: InflectionRecord, buffer_length: int = 40) -> str: ...
    @staticmethod
    def put_to_file(file: TextIO, item: InflectionRecord) -> None: ...
"""
