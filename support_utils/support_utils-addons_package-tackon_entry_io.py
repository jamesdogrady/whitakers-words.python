from __future__ import annotations
from typing import Final, TextIO, Tuple, Optional
from pydantic import BaseModel, Field, ConfigDict

# --- Dependencies (Imported from previously migrated modules) ---
from .inflections_package import StemType
from .stem_type_io import StemTypeIOService

# --- Core Data Model ---

class TackonEntry(BaseModel):
    """
    Expert migration of Tackon_Entry from Ada to Python 3.12+.
    Represents an entry in the ADDONS file used for Latin tackons (enclitics).
    """
    model_config = ConfigDict(validate_assignment=True, frozen=True)

    # In the Ada source, Tackon_Entry is characterized by a single 'Base' field.
    base: StemType = Field(default_factory=StemType)


# --- Migration Service ---

class TackonEntryIOService:
    """
    Migration of the Tackon_Entry_IO package body.
    Handles fixed-width parsing and formatting for tackon addon metadata.
    """

    @staticmethod
    def get_from_string(source: str) -> Tuple[TackonEntry, int]:
        """
        Implementation of procedure Get (S : String; I : out Tackon_Entry; Last : out Integer).
        Parses the tackon base directly from the provided string segment.
        """
        # Logic: Delegates parsing of the 'Base' component to the underlying stem IO logic.
        base_stem, last_idx = StemTypeIOService.get_from_string(source)
        
        entry = TackonEntry(base=base_stem)
        return entry, last_idx

    @staticmethod
    def put_to_string(item: TackonEntry, buffer_length: int = 20) -> str:
        """
        Implementation of procedure Put (S : out String; I : in Tackon_Entry).
        Serializes a TackonEntry into a fixed-width segment.
        """
        # Formats the base stem and ensures the string buffer is correctly padded.
        base_part = StemTypeIOService.put_to_string(item.base)
        
        # Fill remainder of string with spaces to maintain column alignment.
        return base_part.ljust(buffer_length)

    @staticmethod
    def put_to_file(file: TextIO, item: TackonEntry) -> None:
        """
        Implementation of procedure Put (F : File_Type; I : in Tackon_Entry).
        Writes the tackon base directly to a file stream.
        """
        # Ada: Put (F, I.Base);
        StemTypeIOService.put_to_file(file, item.base)

    @staticmethod
    def get_from_file(file: TextIO) -> TackonEntry:
        """
        Implementation of procedure Get (F : File_Type; I : out Tackon_Entry).
        Reads the tackon base sequentially from a stream.
        """
        # Ada: Get (F, I.Base);
        base_stem = StemTypeIOService.get_from_file(file)
        return TackonEntry(base=base_stem)

# --- Public API Stub (.pyi equivalent) ---

"""
from typing import TextIO, Tuple
from .addons_package import TackonEntry

class TackonEntryIOService:
    @staticmethod
    def get_from_string(source: str) -> Tuple[TackonEntry, int]: ...
    @staticmethod
    def put_to_string(item: TackonEntry, buffer_length: int = 20) -> str: ...
    @staticmethod
    def put_to_file(file: TextIO, item: TackonEntry) -> None: ...
    @staticmethod
    def get_from_file(file: TextIO) -> TackonEntry: ...
"""
