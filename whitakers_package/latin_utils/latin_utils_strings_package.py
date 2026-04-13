from __future__ import annotations
from enum import Enum
from typing import Final, TextIO, Tuple
from pydantic import BaseModel, Field, ConfigDict

# --- Types and Constants ---

class TrimEnd(Enum):
    """Mapped from Ada.Strings.Trim_End."""
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    BOTH = "BOTH"

NULL_STRING: Final[str] = ""

# --- Custom Exceptions ---

class StringsError(Exception):
    """Base exception for Strings_Package operations."""
    pass

# --- Migration Service ---

class StringsPackage:
    """
    Expert migration of Latin_Utils.Strings_Package to Python 3.12+.
    Provides basic subprograms for operating on Strings and Characters [cite: 5387-5388].
    """

    @staticmethod
    def lower_case(item: str) -> str:
        """
        Implementation of function Lower_Case (C : Character) and (S : String).
        Converts input to lower case [cite: 5396, 5406-5415].
        """
        return item.lower()

    @staticmethod
    def upper_case(item: str) -> str:
        """
        Implementation of function Upper_Case (C : Character) and (S : String).
        Converts input to upper case [cite: 5417, 5427-5436].
        """
        return item.upper()

    @staticmethod
    def trim(source: str, side: TrimEnd = TrimEnd.BOTH) -> str:
        """
        Implementation of function Trim (S : String; Side : Trim_End := Both).
        Removes leading and/or trailing whitespace [cite: 5438, 5448-5456].
        """
        match side:
            case TrimEnd.LEFT:
                return source.lstrip()
            case TrimEnd.RIGHT:
                return source.rstrip()
            case TrimEnd.BOTH:
                return source.strip()
            case _:
                return source

    @staticmethod
    def head(source: str, size: int, pad: str = " ") -> str:
        """
        Implementation of function Head (S : String; Size : Natural; Pad : Character := ' ').
        Returns the first 'size' characters of the string, padded if necessary [cite: 5458, 5468-5474].
        """
        if size <= 0:
            return ""
        
        # Python's ljust handles both truncation (via slicing) and padding
        return source[:size].ljust(size, pad)

    @staticmethod
    def get_non_comment_line(file: TextIO) -> Tuple[str, int]:
        """
        Implementation of procedure Get_Non_Comment_Line.
        Reads lines from a file until a non-comment line is found, 
        stripping inline comments [cite: 5476, 5486-5523].
        
        A line is considered a comment if it starts with '--' [cite: 5506-5507].
        Inline comments starting with '--' are truncated [cite: 5509-5515].
        Parsing stops if a Carriage Return (Val 13) is the first character [cite: 5502-5504].
        """
        last_length = 0
        result_line = ""

        try:
            for line in file:
                # Remove newline characters
                line = line.rstrip('\n\r')
                trimmed = line.lstrip()

                # Ada logic check for CR (Val 13) at head [cite: 5502-5504]
                if trimmed and ord(trimmed[0]) == 13:
                    break

                # Ignore full-line comments [cite: 5506-5507]
                if trimmed.startswith("--"):
                    continue

                # Search for inline comment start [cite: 5509-5515]
                comment_idx = line.find("--")
                if comment_idx != -1:
                    line = line[:comment_idx]
                
                result_line = line
                last_length = len(line)
                break # Found valid data or end of line [cite: 5517-5518]

        except EOFError:
            pass

        return result_line, last_length

# --- Public API Stub (.pyi equivalent) ---

"""
from typing import TextIO, Tuple
from enum import Enum

class TrimEnd(Enum):
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    BOTH = "BOTH"

class StringsPackage:
    @staticmethod
    def lower_case(item: str) -> str: ...
    @staticmethod
    def upper_case(item: str) -> str: ...
    @staticmethod
    def trim(source: str, side: TrimEnd = TrimEnd.BOTH) -> str: ...
    @staticmethod
    def head(source: str, size: int, pad: str = " ") -> str: ...
    @staticmethod
    def get_non_comment_line(file: TextIO) -> Tuple[str, int]: ...
"""
