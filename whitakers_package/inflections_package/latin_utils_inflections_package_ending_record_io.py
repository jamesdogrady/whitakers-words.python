from __future__ import annotations
from typing import Final, TextIO, Tuple
from pydantic import BaseModel, Field, ConfigDict

# --- Constants (Normally imported from Inflections_Package context) ---
# Whitaker's system defines the maximum length of a word ending suffix.
MAX_ENDING_SIZE: Final[int] = 10 

# --- Custom Exceptions ---

class EndingRecordError(Exception):
    """Raised when an error occurs during Ending_Record I/O operations[cite: 2869]."""
    pass

# --- Core Data Model ---

class EndingRecord(BaseModel):
    """
    Expert migration of the Ending_Record from Ada to Python 3.12+.
    Represents a Latin word ending and its actual character count[cite: 2835, 2847].
    """
    model_config = ConfigDict(validate_assignment=True, frozen=True)

    size: int = Field(default=0, ge=0, le=MAX_ENDING_SIZE) [cite: 2836, 2847]
    suf: str = Field(default=" " * MAX_ENDING_SIZE, max_length=MAX_ENDING_SIZE) [cite: 2846, 2848]

    @property
    def suffix(self) -> str:
        """Returns the active suffix string based on the recorded size."""
        return self.suf[:self.size].strip()


# --- Migration Service ---

class EndingRecordIOService:
    """
    Migration of the Ending_Record_IO package body.
    Handles fixed-width parsing and formatting for word ending metadata[cite: 2835].
    """

    @staticmethod
    def get_from_string(source: str) -> Tuple[EndingRecord, int]:
        """
        Implementation of procedure Get (Source : String; Target : out Ending_Record; Last : out Integer).
        Parses suffix metadata from a fixed-width string segment [cite: 2861-2868].
        """
        try:
            # 1. Parse the integer size (skipping leading whitespace) [cite: 2864]
            # Simulating Ada's Integer_Text_IO.Get behavior
            parts = source.split(maxsplit=1)
            if not parts:
                return EndingRecord(), 0
            
            ending_length = int(parts[0])
            
            if ending_length == 0:
                # Target := Null_Ending_Record; Last := Low; [cite: 2865]
                return EndingRecord(), source.find(parts[0]) + len(parts[0])

            # 2. Skip Spacer and extract suffix [cite: 2866-2867]
            # Logic: move past the integer and one spacer character
            start_idx = source.find(parts[0]) + len(parts[0]) + 1
            ending_suf = source[start_idx : start_idx + ending_length]
            
            # 3. Construct record and pad internal buffer with blanks [cite: 2867-2868]
            target = EndingRecord(
                size=ending_length,
                suf=ending_suf.ljust(MAX_ENDING_SIZE)
            )
            
            last_pos = start_idx + ending_length
            return target, last_pos

        except Exception as e:
            # Ada: exception when others => PUT_LINE ("ENDING ERROR " & Source); raise; 
            print(f"ENDING ERROR {source}")
            raise EndingRecordError(str(e)) from e

    @staticmethod
    def put_to_string(item: EndingRecord, buffer_length: int = 20) -> str:
        """
        Implementation of procedure Put (Target : out String; Item : in Ending_Record).
        Serializes an EndingRecord into a padded DICTLINE segment [cite: 2870-2878].
        """
        # Formats Size (Width 2) + Space + Suffix (Padded to MAX_ENDING_SIZE) [cite: 2871-2876]
        result = f"{item.size:>2} {item.suf[:item.size]:<{MAX_ENDING_SIZE}}"
        
        # Fill remainder of the target string with spaces [cite: 2877]
        return result.ljust(buffer_length)

    @staticmethod
    def put_to_file(file: TextIO, item: EndingRecord) -> None:
        """
        Implementation of procedure Put (File : File_Type; Item : in Ending_Record).
        Writes formatted ending metadata directly to a file stream [cite: 2857-2858].
        """
        # Ada: Put(File, Item.Size, 1); Put(File, ' '); Put(File, Suf_With_Blanks); [cite: 2857-2858]
        suf_segment = item.suf[:item.size].ljust(MAX_ENDING_SIZE)
        file.write(f"{item.size:1} {suf_segment}")

# --- Public API Stub (.pyi equivalent) ---

"""
from typing import TextIO, Tuple
from .inflections_package import EndingRecord

class EndingRecordIOService:
    @staticmethod
    def get_from_string(source: str) -> Tuple[EndingRecord, int]: ...
    @staticmethod
    def put_to_string(item: EndingRecord, buffer_length: int = 20) -> str: ...
    @staticmethod
    def put_to_file(file: TextIO, item: EndingRecord) -> None: ...
"""
