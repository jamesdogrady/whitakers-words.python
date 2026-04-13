from __future__ import annotations
from typing import Final, TextIO, Tuple, Optional
from pydantic import BaseModel, Field, ConfigDict

# --- Core Data Model ---

class DecnRecord(BaseModel):
    """
    Expert migration of the Decn_Record from Ada to Python 3.12+.
    Represents a declension (or conjugation) and its variant code[cite: 2772, 2779, 2780].
    Used as the primary inflectional key for nouns and verbs in Whitaker's system.
    """
    model_config = ConfigDict(validate_assignment=True, frozen=True)

    which: int = Field(default=0, ge=0)
    var: int = Field(default=0, ge=0)

    def to_string(self) -> str:
        """Provides a standard space-separated representation of the record [cite: 2775-2778]."""
        return f"{self.which} {self.var}"


# --- Migration Service ---

class DecnRecordIOService:
    """
    Migration of the Decn_Record_IO package body.
    Handles fixed-width parsing and formatting for declension/variant metadata [cite: 2758-2760].
    """

    # Standard width for the two integers and their internal spacer [cite: 2783-2785].
    DEFAULT_WIDTH: Final[int] = 3

    @staticmethod
    def get_from_string(source: str) -> Tuple[DecnRecord, int]:
        """
        Implementation of procedure Get (Source : String; Target : out Decn_Record; Last : out Integer).
        Parses integers from a string slice, skipping leading and internal whitespace [cite: 2778-2780].
        """
        # Ada uses Integer_Text_IO.Get which skips leading whitespace.
        # The logic consumes 'Which', moves past a spacer, then consumes 'Var' [cite: 2779-2780].
        parts = source.split()
        if len(parts) < 2:
            return DecnRecord(), 0

        try:
            which_val = int(parts[0])
            var_val = int(parts[1])
            target = DecnRecord(which=which_val, var=var_val)
            
            # Calculate the Last index reached in the source string[cite: 2780].
            last_pos = source.find(parts[1]) + len(parts[1])
            return target, last_pos
        except (ValueError, IndexError):
            return DecnRecord(), 0

    @staticmethod
    def put_to_string(item: DecnRecord, length: int = 12) -> str:
        """
        Implementation of procedure Put (Target : out String; Item : in Decn_Record).
        Serializes a DecnRecord into a fixed-width segment with explicit padding [cite: 2781-2786].
        """
        # Formats Which (width 1) + Space + Var (width 1) [cite: 2783-2785].
        result = f"{item.which:1} {item.var:1}"
        
        # Fill remainder of string buffer with spaces to maintain column alignment.
        # In Ada: Target (High + 1 .. Target'Last) := (others => ' ');
        return result.ljust(length)

    @staticmethod
    def put_to_file(file: TextIO, item: DecnRecord) -> None:
        """
        Implementation of procedure Put (File : File_Type; Item : in Decn_Record).
        Writes formatted declension metadata directly to an output stream [cite: 2775-2776].
        """
        # Ada: Put(File, Item.Which, 1); Put(File, ' '); Put(File, Item.Var, 1); [cite: 2775-2776]
        file.write(f"{item.which:1} {item.var:1}")

# --- Public API Stub (.pyi equivalent) ---

"""
from typing import TextIO, Tuple
from .inflections_package import DecnRecord

class DecnRecordIOService:
    @staticmethod
    def get_from_string(source: str) -> Tuple[DecnRecord, int]: ...
    @staticmethod
    def put_to_string(item: DecnRecord, length: int = 12) -> str: ...
    @staticmethod
    def put_to_file(file: TextIO, item: DecnRecord) -> None: ...
"""
