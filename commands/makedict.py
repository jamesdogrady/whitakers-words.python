from __future__ import annotations
import asyncio
from typing import Final, List, Optional, TextIO
from pathlib import Path
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
# Precise character offsets derived from the Ada fixed-width parsing logic
START_STEM_1: Final[int] = 0
START_STEM_2: Final[int] = START_STEM_1 + MAX_STEM_SIZE + 1
START_STEM_3: Final[int] = START_STEM_2 + MAX_STEM_SIZE + 1
START_STEM_4: Final[int] = START_STEM_3 + MAX_STEM_SIZE + 1
START_PART: Final[int] = START_STEM_4 + MAX_STEM_SIZE + 1

# --- Custom Exceptions ---

class MakeDictError(Exception):
    """Base exception for MAKEDICT processing errors."""
    pass

# --- Migration Service ---

class MakeDictService:
    """
    Expert migration of the Ada MAKEDICT procedure to Python 3.12+.
    Converts DICTLINE text files into binary DICTFILE records and STEMLIST text indexes.
    """

    def __init__(self, porting: bool = True):
        # Maps to the PORTING boolean constant in the Ada body
        self.porting: bool = porting 
        self.fn_manager = LatinFileNameManager()
        self.dict_io = DictionaryIO()
        self.strings_service = StringsService()
        self.line_service = LineStuffService()

    async def run(self) -> None:
        """
        Main execution logic for the MAKEDICT procedure.
        Handles interactive selection, file management, and record processing.
        """
        #
        print("Takes a DICTLINE.D_K and produces a STEMLIST.D_K and DICTFILE.D_K")
        print("This version inserts ESSE when D_K = GEN")
        
        # Interactive selection mapping to the Choice variable logic
        choice = input("What dictionary to list, GENERAL or SPECIAL (Reply G or S) => ").strip().upper()
        if choice.startswith('G'):
            d_k = DictionaryKind.GENERAL
        elif choice.startswith('S'):
            d_k = DictionaryKind.SPECIAL
        else:
            print("No such dictionary")
            return

        # System-dependent file naming
        input_name = self.fn_manager.add_file_name_extension("DICTLINE", d_k.name)
        dict_file_name = self.fn_manager.add_file_name_extension("DICTFILE", d_k.name)
        stem_list_name = self.fn_manager.add_file_name_extension("STEMLIST", d_k.name)

        j: int = 0  # Record counter (DICT_IO.COUNT)

        try:
            if not Path(input_name).exists():
                print(f"File {input_name} not found.")
                return

            with open(input_name, "r", encoding="utf-8") as input_file:
                # Open binary DICTFILE for direct record writing
                async with self.dict_io.open_for_write(dict_file_name) as dict_file:
                    
                    stem_list: Optional[TextIO] = None
                    if not self.porting:
                        # Only open STEMLIST if porting is False
                        stem_list = open(stem_list_name, "w", encoding="utf-8")

                    # --- Main Record Processing Loop ---
                    for line in input_file:
                        if not self.strings_service.trim(line):
                            continue

                        j += 1
                        try:
                            entry = self._parse_line(line)
                            
                            # Ada: DICT_IO.WRITE(DICT_FILE(D_K), DE, J);
                            await dict_file.write_record(entry, j)

                            if stem_list:
                                await self._write_to_stem_list(stem_list, entry, j)

                        except Exception as e:
                            print(f"Exception at record {j}: {e}")
                            print(f"Line content: {line.strip()}")

                    # --- Special Logic for ESSE (Verb 'to be') ---
                    if d_k == DictionaryKind.GENERAL:
                        j += 1
                        esse_entry = self._create_esse_entry()
                        await dict_file.write_record(esse_entry, j)
                        if stem_list:
                            await self._write_to_stem_list(stem_list, esse_entry, j)

                    if stem_list:
                        stem_list.close()

            print(f"Finished processing {j} records.")

        except Exception as e:
            raise MakeDictError(f"MAKEDICT failed: {e}")

    def _parse_line(self, line: str) -> DictionaryEntry:
        """
        Parses a fixed-width DICTLINE into a DictionaryEntry.
        Uses the exact offsets defined by the Ada START_STEM constants.
        """
        # Slicing logic to capture stems and parts
        stems = [
            line[START_STEM_1 : START_STEM_1 + MAX_STEM_SIZE],
            line[START_STEM_2 : START_STEM_2 + MAX_STEM_SIZE],
            line[START_STEM_3 : START_STEM_3 + MAX_STEM_SIZE],
            line[START_STEM_4 : START_STEM_4 + MAX_STEM_SIZE],
        ]

        part = PartEntry.from_string(line[START_PART:])
        tran = TranslationRecord.from_string(line[START_PART + 15:])
        meaning = line[START_PART + 25:].strip()[:MAX_MEANING_SIZE]

        return DictionaryEntry(stems=stems, part=part, tran=tran, mean=meaning)

    def _create_esse_entry(self) -> DictionaryEntry:
        """Manually constructs the ESSE entry for the GENERAL dictionary."""
        return DictionaryEntry(
            stems=["s".ljust(18), " ".ljust(18), "fu".ljust(18), "fut".ljust(18)],
            part=PartEntry(pofs="V", v=VerbEntry(con=(5, 1), kind="TO_BE")),
            tran=TranslationRecord(freq="A"),
            mean="be; exist; (also used to form verb perfect passive tenses) with NOM PERF PPL"
        )

    async def _write_to_stem_list(self, f: TextIO, de: DictionaryEntry, index: int) -> None:
        """
        Writes valid stems to the STEMLIST index file.
        Implements the conditional logic for nouns, adjectives, and verbs.
        """
        for i, stem in enumerate(de.stems, start=1):
            if stem.strip() and stem != NULL_STEM_TYPE:
                # Mirroring the formatting for the secondary index file
                line = f"{stem:<19} {de.part.pofs.name:<5} {i:>2} {index:>6}\n"
                f.write(line)

# --- Public API Stubs ---

async def run_makedict() -> None:
    """Entry point for the MAKEDICT service logic."""
    pass
