from __future__ import annotations
from typing import Final, TextIO, Tuple, Optional
from pydantic import BaseModel, Field, ConfigDict

# --- Dependencies (Imported from previously migrated modules) ---
from .inflections_package import StemType
from .stem_type_io import StemTypeIOService

# --- Core Data Model ---

class PrefixEntry(BaseModel):
    """
    Expert migration of Prefix_Entry from Ada to Python 3.12+.
    Represents an entry in the ADDONS file used for prefix-to-stem transformations.
    """
    model_config = ConfigDict(validate_assignment=True, frozen=True)

    root: StemType = Field(default_factory=StemType)
    target: StemType = Field(default_factory=StemType)


# --- Migration Service ---

class PrefixEntryIOService:
    """
    Migration of the Prefix_Entry_IO package body.
    Handles fixed-width parsing and formatting for prefix addon metadata.
    """

    @staticmethod
    def get_from_string(source: str) -> Tuple[PrefixEntry, int]:
        """
        Implementation of procedure Get (S : String; P : out Prefix_Entry; Last : out Integer).
        Sequentially parses Root, skips a spacer, and parses Target.
        """
        # Note: Ada logic tracks a 'Low' offset (L) through the string buffer.
        
        # 1. Parse Root stem
        root, last_root = StemTypeIOService.get_from_string(source)
        
        # 2. Skip Spacer (L := L + 1) and Parse Target stem
        target_start = last_root + 1
        target, last_target = StemTypeIOService.get_from_string(source[target_start:])
        
        entry = PrefixEntry(root=root, target=target)
        
        return entry, target_start + last_target

    @staticmethod
    def put_to_string(item: PrefixEntry, buffer_length: int = 40) -> str:
        """
        Implementation of procedure Put (S : out String; P : in Prefix_Entry).
        Serializes a PrefixEntry into a fixed-width segment with a space delimiter.
        """
        # Replicates sequential Root + Space + Target assignment.
        root_part = StemTypeIOService.put_to_string(item.root)
        target_part = StemTypeIOService.put_to_string(item.target)
        
        result = f"{root_part} {target_part}"
        
        # Fill remainder of string with spaces to maintain column alignment.
        return result.ljust(buffer_length)

    @staticmethod
    def put_to_file(file: TextIO, item: PrefixEntry) -> None:
        """
        Implementation of procedure Put (F : File_Type; P : in Prefix_Entry).
        Writes formatted prefix entries directly to a file stream.
        """
        # Ada: Put (F, P.Root); Put (F, ' '); Put (F, P.Target);
        StemTypeIOService.put_to_file(file, item.root)
        file.write(" ")
        StemTypeIOService.put_to_file(file, item.target)

    @staticmethod
    def get_from_file(file: TextIO) -> PrefixEntry:
        """
        Implementation of procedure Get (F : File_Type; P : out Prefix_Entry).
        Reads root and target stems sequentially from a stream.
        """
        # Ada: Get (F, P.Root); Get (F, Spacer); Get (F, P.Target);
        root = StemTypeIOService.get_from_file(file)
        file.read(1)  # Consume the spacer character
        target = StemTypeIOService.get_from_file(file)
        
        return PrefixEntry(root=root, target=target)

# --- Public API Stub (.pyi equivalent) ---

"""
from typing import TextIO, Tuple
from .addons_package import PrefixEntry

class PrefixEntryIOService:
    @staticmethod
    def get_from_string(source: str) -> Tuple[PrefixEntry, int]: ...
    @staticmethod
    def put_to_string(item: PrefixEntry, buffer_length: int = 40) -> str: ...
    @staticmethod
    def put_to_file(file: TextIO, item: PrefixEntry) -> None: ...
    @staticmethod
    def get_from_file(file: TextIO) -> PrefixEntry: ...
"""
