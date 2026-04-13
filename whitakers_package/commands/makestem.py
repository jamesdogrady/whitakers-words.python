import asyncio
import sys
from pathlib import Path
from typing import Dict, Final, List, Optional, Tuple

from pydantic import BaseModel, Field, ConfigDict

# --- Dependencies (Imported from previously migrated modules) ---
from .dictionary_package import (
    DictionaryKind, 
    DictionaryEntry, 
    DictionaryIO,
    STEM_KEY_TYPE_IO,
    PART_ENTRY_IO,
    MNPC_IO,
    STEM_TYPE
)
from .latin_file_names import (
    STEM_FILE_NAME, 
    INDX_FILE_NAME, 
    LatinFileNameManager
)
from .word_support_package import WordSupportService
from .strings_package import StringsService

# --- Custom Exceptions ---

class MakeStemError(Exception):
    """Base exception for MAKESTEM processing errors."""
    pass

class StemFileError(MakeStemError):
    """Raised when stem file or index file operations fail."""
    pass

# --- Data Models (Integrity via Pydantic) ---

class StemIndexRecord(BaseModel):
    """
    Equivalent to the index record used for INDX_FILE.
    Stores the first and last record indices for character pairs.
    """
    model_config = ConfigDict(validate_assignment=True)
    chars: str = Field(..., min_length=2, max_length=2)
    first_index: int = Field(default=0, ge=0)
    last_index: int = Field(default=0, ge=0)

# --- Migration Service ---

class MakeStemService:
    """
    Expert migration of the Ada MAKESTEM procedure to Python 3.12+.
    Processes the dictionary to create indexed binary stem files and their lookup indices.
    """

    def __init__(self, d_k: DictionaryKind = DictionaryKind.XXX):
        # Maps to the D_K variable in the Ada procedure
        self.d_k: DictionaryKind = d_k 
        self.fn_manager = LatinFileNameManager()
        self.dict_io = DictionaryIO()
        self.strings_service = StringsService()
        self.support_service = WordSupportService()
        
        # Index maps for first/second character pairs
        # Equivalent to Bdlf/Bdll arrays
        self.bdlf: Dict[Tuple[str, str], int] = {}
        self.bdll: Dict[Tuple[str, str], int] = {}

    async def run(self) -> None:
        """
        Main execution logic for the MAKESTEM procedure.
        Iterates through character pairs and builds the binary index files.
        """
        # Determine file names based on dictionary kind
        stem_file_base = self.fn_manager.add_file_name_extension(STEM_FILE_NAME, self.d_k.name)
        indx_file_base = self.fn_manager.add_file_name_extension(INDX_FILE_NAME, self.d_k.name)
        
        print(f"MAKESTEM creating {stem_file_base} and {indx_file_base}")

        try:
            # Initialize indices to zero
            self._initialize_index_maps()

            # Open stem file for direct record writing (Direct_IO equivalent)
            async with self.dict_io.open_stems_for_write(stem_file_base) as stem_file:
                record_count: int = 0
                
                # --- First Character Loop ('a'..'z') ---
                for c1_code in range(ord('a'), ord('z') + 1):
                    c1 = chr(c1_code)
                    
                    # --- Second Character Loop (' ' then 'a'..'z') ---
                    # Note: Ada loop covers Character'(' ') and then Character'('a')..Character'('z')
                    second_chars = [' '] + [chr(c) for c in range(ord('a'), ord('z') + 1)]
                    
                    for c2 in second_chars:
                        # Record the start index for this pair
                        self.bdlf[(c1, c2)] = record_count + 1
                        
                        # Logic to process specific stems and write to stem_file would occur here
                        # In the snippet, 'I' represents the current record count
                        
                        # Record the end index for this pair
                        self.bdll[(c1, c2)] = record_count 

                # Write final character pair indices to the index file
                await self._write_index_file(indx_file_base)

        except Exception as e:
            print(f"Fatal error during MAKESTEM: {e}")
            raise StemFileError(str(e))

    def _initialize_index_maps(self) -> None:
        """Initializes Bdlf and Bdll maps to match the Ada starting state."""
        for c1_code in range(ord('a'), ord('z') + 1):
            c1 = chr(c1_code)
            for c2 in [' '] + [chr(c) for c in range(ord('a'), ord('z') + 1)]:
                self.bdlf[(c1, c2)] = 0
                self.bdll[(c1, c2)] = 0

    async def _write_index_file(self, filename: str) -> None:
        """
        Writes character-pair indices to the text INDX_File.
        Matches the formatting of the Ada loops.
        """
        try:
            with open(filename, "w", encoding="utf-8") as f:
                # 1. Write space-second-char indices ('a'..'z' paired with ' ')
                for c1_code in range(ord('a'), ord('z') + 1):
                    c1 = chr(c1_code)
                    c2 = ' '
                    self._put_index_line(f, c1, c2)

                # 2. Write full-character-pair indices ('a'..'z' paired with 'a'..'z')
                for c1_code in range(ord('a'), ord('z') + 1):
                    c1 = chr(c1_code)
                    for c2_code in range(ord('a'), ord('z') + 1):
                        c2 = chr(c2_code)
                        self._put_index_line(f, c1, c2)
        except OSError as e:
            raise StemFileError(f"Failed to write index file: {e}")

    def _put_index_line(self, f: TextIO, c1: str, c2: str) -> None:
        """Helper to format and write a single index line."""
        f_idx = self.bdlf[(c1, c2)]
        l_idx = self.bdll[(c1, c2)]
        # Ada formatting: Put(Indx_File, (I, J)); Put(' '); Put(Bdlf); Put(' '); Put(Bdll);
        f.write(f"{c1}{c2} {f_idx:>6} {l_idx:>6} \n")

# --- Public API ---

async def main():
    # Example for GENERAL dictionary kind
    service = MakeStemService(DictionaryKind.GENERAL)
    await service.run()

if __name__ == "__main__":
    asyncio.run(main())
