from __future__ import annotations
from typing import Final, TextIO, Tuple
from pydantic import BaseModel, Field, ConfigDict

# --- Dependencies (Imported from previously migrated modules) ---
from .inflections_package import (
    PartOfSpeechType, 
    MeaningType, 
    MAX_STEM_SIZE, 
    MAX_MEANING_SIZE
)
from .addons_package import TackonEntry
from .tackon_entry_io import TackonEntryIOService

# --- Core Data Model ---

class TackonLine(BaseModel):
    """
    Expert migration of Tackon_Line from Ada to Python 3.12+.
    Represents a full line of data for a Latin tackon (enclitic), coordinating its 
    transformation logic, stem identity, and dictionary meaning.
    """
    model_config = ConfigDict(validate_assignment=True, frozen=True)

    pofs: PartOfSpeechType = PartOfSpeechType.TACKON
    tack: str = Field(default=" " * MAX_STEM_SIZE, max_length=MAX_STEM_SIZE)
    entr: TackonEntry = Field(default_factory=TackonEntry)
    meaning: MeaningType = Field(default=" " * MAX_MEANING_SIZE, max_length=MAX_MEANING_SIZE)


# --- Migration Service ---

class TackonLineIOService:
    """
    Migration of the Tackon_Line_IO package body.
    Handles fixed-width parsing and formatting for tackon data lines.
    """

    # Width constants matching Whitaker's Dictionary_Kind_IO and record defaults
    # Replicates logic: M := L + Dictionary_Kind_IO.Default_Width;
    POFS_WIDTH: Final[int] = 3 
    SPACER: Final[str] = " "

    @staticmethod
    def get_from_string(source: str) -> Tuple[TackonLine, int]:
        """
        Implementation of procedure Get (S : String; P : out Tackon_Line; Last : out Integer).
        Parses POFS, Tack, Entry, and Meaning using Whitaker's fixed-width logic.
        """
        # Current parsing offset (mimicking Ada's 'L' and 'M' tracking)
        low = 0
        
        # 1. Parse POFS
        # Get (S (L + 1 .. M), P.Pofs, L);
        m = low + TackonLineIOService.POFS_WIDTH
        pofs_segment = source[low : m].strip()
        pofs = PartOfSpeechType(pofs_segment) if pofs_segment else PartOfSpeechType.TACKON
        
        # 2. Skip Spacer and Parse Tack (Stem)
        # L := M + 1; M := L + Max_Stem_Size; P.Tack := S (L + 1 .. M);
        low = m + 1
        m = low + MAX_STEM_SIZE
        tack = source[low : m]
        
        # 3. Skip Spacer and Parse Tackon Entry
        # L := M + 1; M := L + Tackon_Entry_Io.Default_Width; Get (S (L + 1 .. M), P.Entr, L);
        low = m + 1
        # TackonEntry default width for its internal stem component
        m = low + 18 
        entry, _ = TackonEntryIOService.get_from_string(source[low:m])
        
        # 4. Skip Spacer and Parse Meaning
        # L := M + 1; M := L + Max_Meaning_Size; P.Mean := S (L + 1 .. M); Last := M;
        low = m + 1
        m = low + MAX_MEANING_SIZE
        meaning = source[low : m]
        last = m

        target = TackonLine(
            pofs=pofs,
            tack=tack,
            entr=entry,
            meaning=meaning
        )

        return target, last

    @staticmethod
    def put_to_string(item: TackonLine, buffer_length: int = 150) -> str:
        """
        Implementation of procedure Put (S : out String; P : in Tackon_Line).
        Serializes a TackonLine into a fixed-width segment with space delimiters.
        """
        # Replicates sequential field + spacer assignment logic
        pofs_part = f"{item.pofs.value:<{TackonLineIOService.POFS_WIDTH}}"
        tack_part = item.tack.ljust(MAX_STEM_SIZE)
        entry_part = TackonEntryIOService.put_to_string(item.entr, buffer_length=18)
        meaning_part = item.meaning.ljust(MAX_MEANING_SIZE)
        
        # Assemble with spacers
        result = (
            pofs_part + TackonLineIOService.SPACER + 
            tack_part + TackonLineIOService.SPACER + 
            entry_part + TackonLineIOService.SPACER + 
            meaning_part
        )
        
        return result.ljust(buffer_length)

    @staticmethod
    def put_to_file(file: TextIO, item: TackonLine) -> None:
        """
        Implementation of procedure Put (F : File_Type; P : in Tackon_Line).
        Writes the formatted tackon data line directly to a stream.
        """
        # Ada: Put (P.Pofs); Put (' '); Put (P.Tack); Put (' '); Put (P.Entr); ...
        file.write(f"{item.pofs.value:<{TackonLineIOService.POFS_WIDTH}} ")
        file.write(f"{item.tack.ljust(MAX_STEM_SIZE)} ")
        TackonEntryIOService.put_to_file(file, item.entr)
        file.write(" ")
        file.write(item.meaning.ljust(MAX_MEANING_SIZE))

# --- Public API Stub (.pyi equivalent) ---

"""
from typing import TextIO, Tuple
from .line_stuff import TackonLine

class TackonLineIOService:
    @staticmethod
    def get_from_string(source: str) -> Tuple[TackonLine, int]: ...
    @staticmethod
    def put_to_string(item: TackonLine, buffer_length: int = 150) -> str: ...
    @staticmethod
    def put_to_file(file: TextIO, item: TackonLine) -> None: ...
"""
