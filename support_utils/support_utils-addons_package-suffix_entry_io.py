from __future__ import annotations
from typing import Final, TextIO, Tuple
from pydantic import BaseModel, Field, ConfigDict

# --- Dependencies (Imported from previously migrated modules) ---
from .inflections_package import StemType, StemKeyType
from .stem_type_io import StemTypeIOService

# --- Core Data Model ---

class SuffixEntry(BaseModel):
    """
    Expert migration of Suffix_Entry from Ada to Python 3.12+.
    Represents an entry in the ADDONS file used for suffix-to-stem transformations.
    """
    model_config = ConfigDict(validate_assignment=True, frozen=True)

    root: StemType = Field(default_factory=StemType)
    root_key: StemKeyType = Field(default=0)
    target: StemType = Field(default_factory=StemType)
    target_key: StemKeyType = Field(default=0)


# --- Migration Service ---

class SuffixEntryIOService:
    """
    Migration of the Suffix_Entry_IO package body.
    Handles fixed-width parsing and formatting for suffix addon metadata.
    """

    @staticmethod
    def get_from_string(source: str) -> Tuple[SuffixEntry, int]:
        """
        Implementation of procedure Get (S : String; P : out Suffix_Entry; Last : out Integer).
        Sequentially parses Root, Root_Key, Target, and Target_Key.
        """
        # Note: Ada logic tracks a 'Low' offset (L) through the string buffer.
        
        # 1. Parse Root stem
        root, last_root = StemTypeIOService.get_from_string(source)
        
        # 2. Skip Spacer (L := L + 1) and Parse Root_Key
        # In Ada: Get (S (L + 1 .. S'Last), P.Root_Key, L);
        key_start = last_root + 1
        # Extract numeric key segment (width 2 in Whitaker's system)
        root_key_val = int(source[key_start : key_start + 2].strip())
        last_root_key = key_start + 2
        
        # 3. Skip Spacer and Parse Target stem
        target_start = last_root_key + 1
        target, last_target = StemTypeIOService.get_from_string(source[target_start:])
        
        # 4. Skip Spacer and Parse Target_Key
        target_key_start = target_start + last_target + 1
        target_key_val = int(source[target_key_start : target_key_start + 2].strip())
        last_target_key = target_key_start + 2
        
        entry = SuffixEntry(
            root=root, 
            root_key=root_key_val, 
            target=target, 
            target_key=target_key_val
        )
        
        return entry, last_target_key

    @staticmethod
    def put_to_string(item: SuffixEntry, buffer_length: int = 50) -> str:
        """
        Implementation of procedure Put (S : out String; P : in Suffix_Entry).
        Serializes a SuffixEntry into a fixed-width segment with space delimiters.
        """
        # Replicates sequential formatting: Root + Root_Key + Target + Target_Key.
        root_part = StemTypeIOService.put_to_string(item.root)
        target_part = StemTypeIOService.put_to_string(item.target)
        
        # Ada body implies keys are put with width 2
        result = f"{root_part} {item.root_key:>2} {target_part} {item.target_key:>2}"
        
        # Fill remainder of string with spaces to maintain column alignment.
        return result.ljust(buffer_length)

    @staticmethod
    def put_to_file(file: TextIO, item: SuffixEntry) -> None:
        """
        Implementation of procedure Put (F : File_Type; P : in Suffix_Entry).
        Writes formatted suffix entries directly to a file stream.
        """
        # Ada: Put (F, P.Root); Put (F, P.Root_Key, 2); Put (F, ' '); ...
        StemTypeIOService.put_to_file(file, item.root)
        file.write(f" {item.root_key:>2} ")
        StemTypeIOService.put_to_file(file, item.target)
        file.write(f" {item.target_key:>2}")

    @staticmethod
    def get_from_file(file: TextIO) -> SuffixEntry:
        """
        Implementation of procedure Get (F : File_Type; P : out Suffix_Entry).
        Reads suffix components sequentially from a stream.
        """
        # Ada: Get (F, P.Root); Get (F, P.Root_Key); Get (F, Spacer); ...
        root = StemTypeIOService.get_from_file(file)
        
        # Integer Get in Ada typically consumes whitespace
        root_key_str = file.read(3).strip() # spacer + 2 chars
        root_key = int(root_key_str) if root_key_str else 0
        
        file.read(1) # spacer
        target = StemTypeIOService.get_from_file(file)
        
        target_key_str = file.read(3).strip()
        target_key = int(target_key_str) if target_key_str else 0
        
        return SuffixEntry(
            root=root, 
            root_key=root_key, 
            target=target, 
            target_key=target_key
        )

# --- Public API Stub (.pyi equivalent) ---

"""
from typing import TextIO, Tuple
from .addons_package import SuffixEntry

class SuffixEntryIOService:
    @staticmethod
    def get_from_string(source: str) -> Tuple[SuffixEntry, int]: ...
    @staticmethod
    def put_to_string(item: SuffixEntry, buffer_length: int = 50) -> str: ...
    @staticmethod
    def put_to_file(file: TextIO, item: SuffixEntry) -> None: ...
    @staticmethod
    def get_from_file(file: TextIO) -> SuffixEntry: ...
"""
