from __future__ import annotations
from enum import Enum, auto
from typing import Final, Optional, TextIO, BinaryIO
from pydantic import BaseModel, Field, ConfigDict
from pathlib import Path

# --- Dependencies (Imported from previously migrated modules) ---
from .latin_utils.strings_package import StringsPackage
from .latin_utils.inflections_package import DictionaryEntry, NullDictionaryEntry
from .latin_utils.latin_file_names import Dict_File_Name, Dict_Line_Name
from .latin_utils.dictionary_package import DictionaryEntryIOService, DictIOService

# --- Exceptions ---

class LinefileError(Exception):
    """Base exception for the linefile utility."""
    pass

class InvalidDictionaryKindError(LinefileError):
    """Raised when the user provides an unsupported dictionary identifier."""
    pass

# --- Core Data Models ---

class DictionaryKind(Enum):
    """
    Expert migration of Dictionary_Kind.
    Defines the types of dictionary files processed by Whitaker's engine.
    """
    GENERAL = auto()
    SPECIAL = auto()

    def extension(self) -> str:
        """Parity with the legacy Ext(D_K) function."""
        return "GEN" if self == DictionaryKind.GENERAL else "SPE"

# --- Migration Service ---

class LinefileService:
    """
    Expert migration of the Linefile Ada procedure to Python 3.12+.
    Converts a binary DICTFILE into a standard text DICTLINE format.
    """

    def __init__(self):
        self.d_k: DictionaryKind = DictionaryKind.GENERAL
        self.de: DictionaryEntry = NullDictionaryEntry

    def get_user_choice(self) -> DictionaryKind:
        """
        Implementation of the interactive dictionary selection logic.
        """
        print("Takes a DICTFILE.D_K and produces a DICTLINE.D_K")
        prompt = "What dictionary to convert, GENERAL or SPECIAL (Reply G or S) => "
        
        try:
            line = input(prompt).strip().upper()
            if not line:
                return DictionaryKind.GENERAL
            
            match line[0]:
                case 'G':
                    return DictionaryKind.GENERAL
                case 'S':
                    return DictionaryKind.SPECIAL
                case _:
                    print("No such dictionary")
                    # Replicates 'raise Text_IO.Data_Error'
                    raise InvalidDictionaryKindError("User entered invalid dictionary identifier")
        except EOFError:
            raise LinefileError("Input stream closed unexpectedly")

    def run(self) -> None:
        """
        Main execution loop for binary-to-text conversion.
        """
        # 1. Selection logic
        try:
            self.d_k = self.get_user_choice()
        except InvalidDictionaryKindError:
            return

        # 2. File Path Resolution
        # ADA: Dict_File_Name & '.' & Ext (D_K)
        input_filename = f"{Dict_File_Name}.{self.d_k.extension()}"
        # ADA: Dict_Line_Name & '.' & Ext (D_K)
        output_filename = f"{Dict_Line_Name}.{self.d_k.extension()}"

        try:
            # 3. Stream Processing Loop
            # Use binary mode for reading the direct IO Dictfile and text mode for the Output Dictline
            with open(input_filename, "rb") as dictfile, open(output_filename, "w", encoding="ascii") as output:
                while True:
                    # Logic: Read binary Dictionary_Entry record using Direct_IO parity
                    self.de = DictIOService.read_entry(dictfile)
                    if self.de is None:  # Replicates 'while not End_Of_File'
                        break
                    
                    # Logic: Format and Put to DICTLINE (Text Output)
                    DictionaryEntryIOService.put_to_file(output, self.de)
                    # Replicates 'New_Line (Output)'
                    output.write("\n")
                    
            print(f"Conversion complete: {output_filename}")

        except FileNotFoundError:
            raise LinefileError(f"Required file {input_filename} not found in path")
        except Exception as e:
            raise LinefileError(f"Fatal error during dictionary conversion: {e}")

# --- Public API Stub (.pyi equivalent) ---

"""
class LinefileService:
    def get_user_choice(self) -> DictionaryKind: ...
    def run(self) -> None: ...
"""

# --- Execution Entry Point ---

if __name__ == "__main__":
    try:
        service = LinefileService()
        service.run()
    except LinefileError as e:
        print(f"Error: {e}")
