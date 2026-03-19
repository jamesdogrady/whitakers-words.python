from __future__ import annotations
import re
from typing import Final, TextIO, Tuple
from pydantic import BaseModel, Field, ConfigDict

# --- Constants (Imported from previously migrated modules) ---
# Whitaker's system defines the maximum length of a word stem as 18.
MAX_STEM_SIZE: Final[int] = 18
NULL_STEM_TYPE: Final[str] = " " * MAX_STEM_SIZE


class StemType(BaseModel):
    """
    Expert migration of the Stem_Type from Ada to Python 3.12+.
    Represents a Latin word stem, adhering to fixed-width constraints [cite: 3084-3085].
    """
    model_config = ConfigDict(validate_assignment=True, frozen=True)

    value: str = Field(
        default=NULL_STEM_TYPE, 
        max_length=MAX_STEM_SIZE, 
        pattern=r"^[A-Za-z ]*$"
    )

    def __str__(self) -> str:
        return self.value


class StemTypeIOService:
    """
    Migration of the Stem_Type_IO package body.
    Handles the parsing and formatting of stems from text streams and strings [cite: 3084-3088].
    """

    # Matches Stem_Type_IO.Default_Width (typically MAX_STEM_SIZE)
    DEFAULT_WIDTH: Final[int] = MAX_STEM_SIZE

    @staticmethod
    def get_from_string(source: str) -> Tuple[StemType, int]:
        """
        Implementation of procedure Get (Source : String; Target : out Stem_Type; Last : out Integer).
        Reads alphabetical characters until a non-alpha character or width limit is reached [cite: 3095-3100].
        """
        result_chars = []
        last_idx = 0
        
        # Iterate up to Default_Width [cite: 3096]
        for i in range(min(len(source), StemTypeIOService.DEFAULT_WIDTH)):
            char = source[i]
            # Check for non-alphabetical character [cite: 3097]
            if not char.isalpha():
                break
            
            result_chars.append(char)
            last_idx = i + 1  # Last consumed index [cite: 3099]
            
        # Construct stem and pad with spaces to maintain fixed width [cite: 3095, 3098]
        stem_str = "".join(result_chars).ljust(StemTypeIOService.DEFAULT_WIDTH)
        return StemType(value=stem_str), last_idx

    @staticmethod
    def put_to_string(item: StemType) -> str:
        """
        Implementation of procedure Put (Target : out String; Item : in Stem_Type).
        Returns the fixed-width stem string[cite: 3100].
        """
        return item.value.ljust(StemTypeIOService.DEFAULT_WIDTH)

    @staticmethod
    def put_to_file(file: TextIO, item: StemType) -> None:
        """
        Implementation of procedure Put (File : File_Type; Item : in Stem_Type).
        Writes the stem directly to a text stream [cite: 3092-3093].
        """
        file.write(item.value)

    @staticmethod
    def get_from_file(file: TextIO) -> StemType:
        """
        Implementation of procedure Get (File : File_Type; Item : out Stem_Type).
        Reads characters from a file stream until non-alpha character encountered [cite: 3084-3088].
        """
        # Ada implementation reads one char at a time [cite: 3085-3086]
        result_chars = []
        for _ in range(StemTypeIOService.DEFAULT_WIDTH):
            char = file.read(1)
            if not char or not char.isalpha():
                break
            result_chars.append(char)
            
        stem_str = "".join(result_chars).ljust(StemTypeIOService.DEFAULT_WIDTH)
        return StemType(value=stem_str)


# --- Public API Stub (.pyi equivalent) ---

"""
from typing import TextIO, Tuple
from .inflections_package import StemType

class StemTypeIOService:
    DEFAULT_WIDTH: int = 18
    @staticmethod
    def get_from_string(source: str) -> Tuple[StemType, int]: ...
    @staticmethod
    def put_to_string(item: StemType) -> str: ...
    @staticmethod
    def put_to_file(file: TextIO, item: StemType) -> None: ...
    @staticmethod
    def get_from_file(file: TextIO) -> StemType: ...
"""
