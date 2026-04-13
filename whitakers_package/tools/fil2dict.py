from __future__ import annotations
from enum import Enum, auto
from typing import Final, Optional, TextIO, BinaryIO, Self
from pydantic import BaseModel, Field, ConfigDict
from pathlib import Path

# --- Dependencies (Imported from previously migrated modules) ---
from .latin_utils.strings_package import StringsPackage
from .latin_utils.inflections_package import DictionaryEntry, NullDictionaryEntry
from .latin_utils.latin_file_names import Dict_File_Name, Dict_Line_Name
from .latin_utils.dictionary_package import DictionaryEntryIOService, DictIOService

# --- Exceptions ---

class Fil2DictError(Exception):
    """Base exception for the fil2dict utility."""
    pass

class InvalidDictionaryKindError(Fil2DictError):
    """Raised when the user provides an unsupported dictionary identifier."""
    pass

# --- Core Data Models ---

class DictionaryKind(Enum):
    """
    Expert migration of Dictionary_Kind.
    Defines the types of dictionary files processed by Whitaker's engine [cite: 5313-5314, 5318-5319].
    """
    XXX = auto()
    GENERAL = auto()
    SPECIAL = auto()

    def extension(self) -> str:
        """Parity with the legacy Ext(D_K) function."""
        return "GEN" if self == DictionaryKind.GENERAL else "SPE"

# --- Migration Service ---

class Fil2DictService:
    """
    Expert migration of the Fil2dict Ada procedure to Python 3.12+.
    Reconstructs a DICTLINE (text format) from a binary DICTFILE [cite: 5314-5323].
    """

    def __init__(self):
        self.d_k: DictionaryKind = DictionaryKind.XXX
        self.de: DictionaryEntry = NullDictionaryEntry

    def get_user_choice(self) -> DictionaryKind:
        """
        Implementation of the interactive dictionary selection logic [cite: 5317-5320].
        """
        print("Takes a DICTFILE.D_K and reconstructs the DICTLINE.D_K it came from")
        prompt = "What dictionary to list, GENERAL or SPECIAL (Reply G or S) => "
        
        try:
            line = input(prompt).strip().upper()
            if not line:
                return DictionaryKind.XXX
            
            match line[0]:
                case 'G':
                    return DictionaryKind.GENERAL
                case 'S':
                    return DictionaryKind.SPECIAL
                case _:
                    print("No such dictionary")
                    raise InvalidDictionaryKindError("User entered invalid dictionary identifier")
        except EOFError:
            raise Fil2DictError("Input stream closed unexpectedly")

    def run(self) -> None:
        """
        Main execution loop for binary-to-text reconstruction [cite: 5321-5322].
        """
        # 1. Selection logic
        self.d_k = self.get_user_choice()
        if self.d_k == DictionaryKind.XXX:
            return

        # 2. File Path Resolution 
        # ADA: Dict_File_Name & '.' & Ext (D_K)
        input_filename = f"{Dict_File_Name}.{self.d_k.extension()}"
        # ADA: Dict_Line_Name & ".NEW"
        output_filename = f"{Dict_Line_Name}.NEW"

        try:
            # 3. Stream Processing Loop 
            # Use binary mode for the input DICTFILE and text mode for the output DICTLINE
            with open(input_filename, "rb") as dictfile, open(output_filename, "w", encoding="ascii") as dictline:
                while True:
                    # Logic: Read binary Dictionary_Entry record 
                    self.de = DictIOService.read_entry(dictfile)
                    if self.de is None:  # Replicates 'while not End_Of_File'
                        break
                    
                    # Logic: Format and Put to DICTLINE (Text Output) 
                    DictionaryEntryIOService.put_to_file(dictline, self.de)
                    
            print(f"Reconstruction complete: {output_filename}")

        except FileNotFoundError:
            raise Fil2DictError(f"Required file {input_filename} not found in path")
        except Exception as e:
            raise Fil2DictError(f"Fatal error during dictionary reconstruction: {e}")

# --- Public API Stub (.pyi equivalent) ---

"""
class Fil2DictService:
    def get_user_choice(self) -> DictionaryKind: ...
    def run(self) -> None: ...
"""

# --- Execution Entry Point ---

if __name__ == "__main__":
    try:
        service = Fil2DictService()
        service.run()
    except Fil2DictError as e:
        print(f"Error: {e}")
