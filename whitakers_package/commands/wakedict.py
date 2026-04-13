import asyncio
import sys
from pathlib import Path
from typing import Final, List, Optional, TextIO

from pydantic import BaseModel, Field, ConfigDict

# --- Dependencies (Imported from previously migrated modules) ---
from .dictionary_package import (
    DictionaryEntry, 
    DictionaryKind, 
    PartEntry, 
    TranslationRecord,
    DictionaryIO,
    NULL_STEM_TYPE,
    MAX_STEM_SIZE,
    MAX_MEANING_SIZE,
    VerbEntry
)
from .latin_file_names import LatinFileNameManager
from .line_stuff import LineStuffService
from .strings_package import StringsService

# --- Constants & Offsets ---
# Derived from fixed-width logic in the Ada body
START_STEM_1: Final[int] = 0
START_STEM_2: Final[int] = START_STEM_1 + MAX_STEM_SIZE + 1
START_STEM_3: Final[int] = START_STEM_2 + MAX_STEM_SIZE + 1
START_STEM_4: Final[int] = START_STEM_3 + MAX_STEM_SIZE + 1
START_PART: Final[int] = START_STEM_4 + MAX_STEM_SIZE + 1

# --- Custom Exceptions ---

class WakeDictError(Exception):
    """Base exception for WAKEDICT processing errors."""
    pass

class DataFormatError(WakeDictError):
    """Raised when the input line format is invalid or interactive choice fails."""
    pass

# --- Migration Service ---

class WakeDictService:
    """
    Expert migration of Ada WAKEDICT to Python 3.12+.
    Translates DICTLINE text files into binary DICTFILE records and STEMLISTS.
    """

    def __init__(self, porting: bool = True):
        self.porting: bool = porting
        self.fn_manager = LatinFileNameManager()
        self.dict_io = DictionaryIO()
        self.strings_service = StringsService()
        self.line_service = LineStuffService()

    async def run(self) -> None:
        """
        Main execution logic for the WAKEDICT procedure.
        Handles file setup, ESSE initialization, and the main parsing loop.
        """
        print("Takes a DICTLINE.D_K and produces a STEMLIST.D_K and DICTFILE.D_K")
        print("This version inserts ESSE when D_K = GEN")
        
        # Interactive Dictionary Kind Selection
        choice = input("What dictionary to list, GENERAL or SPECIAL (Reply G or S) => ").strip().lower()
        if choice.startswith('g'):
            d_k = DictionaryKind.GENERAL
        elif choice.startswith('s'):
            d_k = DictionaryKind.SPECIAL
        else:
            print("No such dictionary")
            return

        # File Naming Logic
        input_name = self.fn_manager.add_file_name_extension("DICTLINE", d_k.name)
        dict_file_name = self.fn_manager.add_file_name_extension("DICTFILE", d_k.name)
        stem_list_name = self.fn_manager.add_file_name_extension("STEMLIST", d_k.name)

        j: int = 0  # Dictionary count tracker

        try:
            if not Path(input_name).exists():
                print(f"Error: {input_name} not found.")
                return

            with open(input_name, "r", encoding="utf-8") as input_file:
                # DICTFILE is handled by the DictionaryIO service (Direct_IO equivalent)
                async with self.dict_io.open_for_write(dict_file_name) as dict_file:
                    
                    stem_list: Optional[TextIO] = None
                    if not self.porting:
                        stem_list = open(stem_list_name, "w", encoding="utf-8")

                    # --- Main Parsing Loop ---
                    for line in input_file:
                        if not self.strings_service.trim(line):
                            continue

                        j += 1
                        try:
                            entry = self._parse_line(line)
                            
                            # Write to binary dictionary file
                            await dict_file.write_record(entry, j)

                            # Handle STEMLIST generation if not porting
                            if stem_list:
                                await self._write_to_stem_list(stem_list, entry, j)

                        except Exception as e:
                            print(f"Exception at record {j}: {e}")
                            print(f"Line: {line.strip()}")

                    # --- Finalize ESSE for General Dictionary ---
                    if d_k == DictionaryKind.GENERAL:
                        j += 1
                        esse_entry = self._create_esse_entry()
                        await dict_file.write_record(esse_entry, j)
                        if stem_list:
                            await self._write_to_stem_list(stem_list, esse_entry, j)

                    if stem_list:
                        stem_list.close()

        except Exception as e:
            print(f"Fatal error during WAKEDICT: {e}")
            raise WakeDictError(str(e))

    def _parse_line(self, line: str) -> DictionaryEntry:
        """
        Parses a fixed-width string into a DictionaryEntry record.
        Maintains the offset logic from the Ada START_STEM constants.
        """
        # Slicing logic strictly matches character offsets
        stems = [
            line[START_STEM_1 : START_STEM_1 + MAX_STEM_SIZE],
            line[START_STEM_2 : START_STEM_2 + MAX_STEM_SIZE],
            line[START_STEM_3 : START_STEM_3 + MAX_STEM_SIZE],
            line[START_STEM_4 : START_STEM_4 + MAX_STEM_SIZE],
        ]

        # Use dependencies to parse Part and Translation records
        part = PartEntry.from_string(line[START_PART:])
        tran = TranslationRecord.from_string(line[START_PART + 15:])
        
        # Meanings captured from end of line
        meaning = line[START_PART + 25:].strip()[:MAX_MEANING_SIZE]

        return DictionaryEntry(stems=stems, part=part, tran=tran, mean=meaning)

    def _create_esse_entry(self) -> DictionaryEntry:
        """Constructs the special entry for the verb 'to be'."""
        return DictionaryEntry(
            stems=["s".ljust(18), " ".ljust(18), "fu".ljust(18), "fut".ljust(18)],
            part=PartEntry(pofs="V", v=VerbEntry(con=(5, 1), kind="TO_BE")),
            tran=TranslationRecord(freq="A"),
            mean="be; exist; (also used to form verb perfect passive tenses) with NOM PERF PPL"
        )

    async def _write_to_stem_list(self, f: TextIO, de: DictionaryEntry, index: int) -> None:
        """
        Generates the redundant stem list used for legacy searching.
        Maps the complex conditional logic for nouns, adjectives, and verbs.
        """
        for i, stem in enumerate(de.stems, start=1):
            if stem.strip() and stem != NULL_STEM_TYPE:
                # Formatting for the STEMLIST index file
                line = f"{stem:<19} {de.part.pofs.name:<5} {i:>2} {index:>6}\n"
                f.write(line)
