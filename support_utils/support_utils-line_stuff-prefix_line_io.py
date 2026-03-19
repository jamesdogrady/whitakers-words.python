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
from .addons_package import PrefixEntry
from .prefix_entry_io import PrefixEntryIOService

# --- Core Data Model ---

class PrefixLine(BaseModel):
    """
    Expert migration of Prefix_Line from Ada to Python 3.12+.
    Represents a full line of data for a Latin prefix, coordinating its 
    transformation logic, stem identity, and dictionary meaning.
    """
    model_config = ConfigDict(validate_assignment=True, frozen=True)

    pofs: PartOfSpeechType = PartOfSpeechType.PREFIX
    fix: str = Field(default=" " * MAX_STEM_SIZE, max_length=MAX_STEM_SIZE)
    connect: str = Field(default=" ", min_length=1, max_length=1)
    entr: PrefixEntry = Field(default_factory=PrefixEntry)
    meaning: MeaningType = Field(default=" " * MAX_MEANING_SIZE, max_length=MAX_MEANING_SIZE)


# --- Migration Service ---

class PrefixLineIOService:
    """
    Migration of the Prefix_Line_IO package body.
    Handles fixed-width parsing and formatting for prefix data lines.
    """

    # Width constants matching Whitaker's Dictionary_Kind_IO and record defaults
    # Replicates logic: M := L + Dictionary_Kind_IO.Default_Width; 
    POFS_WIDTH: Final[int] = 3 
    SPACER: Final[str] = " "

    @staticmethod
    def get_from_string(source: str) -> Tuple[PrefixLine, int]:
        """
        Implementation of procedure Get (S : String; P : out Prefix_Line; Last : out Integer).
        Parses POFS, Fix, Connect, Entry, and Meaning using Whitaker's fixed-width logic.
        """
        # Current parsing offset (mimicking Ada's 'L' and 'M' tracking)
        low = 0
        
        # 1. Parse POFS 
        # Get (S (L + 1 .. S'Last), P.Pofs, L); L := M;
        pofs_segment = source[low : low + PrefixLineIOService.POFS_WIDTH].strip()
        pofs = PartOfSpeechType(pofs_segment) if pofs_segment else PartOfSpeechType.PREFIX
        low = PrefixLineIOService.POFS_WIDTH
        
        # 2. Skip Spacer and Parse Fix (Stem) 
        # L := L + 1; M := L + Max_Stem_Size; P.Fix := S (L + 1 .. M); L := M;
        low += 1
        fix = source[low : low + MAX_STEM_SIZE]
        low += MAX_STEM_SIZE
        
        # 3. Skip Spacer and Parse Connect character 
        # L := L + 1; P.Connect := S (L + 1); L := L + 1;
        low += 1
        connect = source[low : low + 1]
        low += 1
        
        # 4. Skip Spacer and Parse Prefix Entry 
        # M := L + Prefix_Entry_Io.Default_Width; Get (S (L + 1 .. S'Last), P.Entr, L); L := M + 1;
        low += 1
        # The PrefixEntryIOService.get_from_string handles its internal field widths (approx 37 chars)
        entry, last_entry_pos = PrefixEntryIOService.get_from_string(source[low:])
        low += 37 
        
        # 5. Parse Meaning 
        # M := L + Max_Meaning_Size; P.Mean := S (L + 1 .. M); Last := M;
        meaning = source[low : low + MAX_MEANING_SIZE]
        last = low + MAX_MEANING_SIZE

        target = PrefixLine(
            pofs=pofs,
            fix=fix,
            connect=connect,
            entr=entry,
            meaning=meaning
        )

        return target, last

    @staticmethod
    def put_to_string(item: PrefixLine, buffer_length: int = 150) -> str:
        """
        Implementation of procedure Put (S : out String; P : in Prefix_Line).
        Serializes a PrefixLine into a fixed-width segment with space delimiters.
        """
        # Replicates sequential field + spacer assignment logic 
        pofs_part = f"{item.pofs.value:<{PrefixLineIOService.POFS_WIDTH}}"
        fix_part = item.fix.ljust(MAX_STEM_SIZE)
        connect_part = item.connect
        entry_part = PrefixEntryIOService.put_to_string(item.entr, buffer_length=37)
        meaning_part = item.meaning.ljust(MAX_MEANING_SIZE)
        
        # Assemble with spacers
        result = (
            pofs_part + PrefixLineIOService.SPACER + 
            fix_part + PrefixLineIOService.SPACER + 
            connect_part + PrefixLineIOService.SPACER + 
            entry_part + PrefixLineIOService.SPACER + 
            meaning_part
        )
        
        return result.ljust(buffer_length)

    @staticmethod
    def put_to_file(file: TextIO, item: PrefixLine) -> None:
        """
        Implementation of procedure Put (F : File_Type; P : in Prefix_Line).
        Writes the formatted prefix data line directly to a stream.
        """
        # Ada: Put (P.Pofs); Put (' '); Put (P.Fix); Put (' '); Put (P.Connect); ... 
        file.write(f"{item.pofs.value:<{PrefixLineIOService.POFS_WIDTH}} ")
        file.write(f"{item.fix.ljust(MAX_STEM_SIZE)} ")
        file.write(f"{item.connect} ")
        PrefixEntryIOService.put_to_file(file, item.entr)
        file.write(" ")
        file.write(item.meaning.ljust(MAX_MEANING_SIZE))

# --- Public API Stub (.pyi equivalent) ---

"""
from typing import TextIO, Tuple
from .line_stuff import PrefixLine

class PrefixLineIOService:
    @staticmethod
    def get_from_string(source: str) -> Tuple[PrefixLine, int]: ...
    @staticmethod
    def put_to_string(item: PrefixLine, buffer_length: int = 150) -> str: ...
    @staticmethod
    def put_to_file(file: TextIO, item: PrefixLine) -> None: ...
"""
