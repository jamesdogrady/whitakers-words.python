from __future__ import annotations
from typing import TextIO, List
from pydantic import BaseModel, Field, ConfigDict

# --- Dependencies (Imported from previously migrated modules) ---
from .dictionary_package import (
    DictionaryEntry, 
    STEM_TYPE, 
    MAX_STEM_SIZE,
    PART_ENTRY_IO,
    TRANSLATION_RECORD_IO
)
from .strings_package import StringsService

# --- Logic Implementation ---

class DictionaryEntryIOService:
    """
    Expert migration of the Dictionary_Entry_IO package body.
    Handles the composite parsing and formatting of full dictionary records.
    """

    @staticmethod
    def get(input_str: str) -> DictionaryEntry:
        """
        Implementation of procedure Get (Item : out Dictionary_Entry).
        Decomposes a fixed-width string into stems, grammatical parts, and meanings.
        """
        # 1. Parse the four stems using fixed-width offsets
        # In Ada: for I in 1 .. 4 loop STEM_TYPE_IO.GET (ITEM.STEM (I)); end loop;
        stems: List[str] = []
        current_pos = 0
        for _ in range(4):
            # Each stem is followed by a space in the DICTLINE format
            stem_segment = input_str[current_pos : current_pos + MAX_STEM_SIZE]
            stems.append(stem_segment)
            current_pos += MAX_STEM_SIZE + 1

        # 2. Parse the Part of Speech metadata
        # Uses the previously migrated PART_ENTRY_IO logic
        part_segment = input_str[current_pos:]
        part = PART_ENTRY_IO.get(part_segment)
        
        # 3. Parse the translation/frequency metadata
        # The offset here is determined by the cumulative size of part-specific fields
        # Ada: TRANSLATION_RECORD_IO.GET (ITEM.TRAN);
        tran = TRANSLATION_RECORD_IO.get(part_segment[15:]) 

        # 4. Parse the meaning string
        # Ada: TEXT_IO.GET_LINE (ITEM.MEAN, ITEM.MEAN_LAST);
        # Extracts everything remaining after the structured fields
        meaning = part_segment[25:].strip()

        return DictionaryEntry(
            stems=stems,
            part=part,
            tran=tran,
            mean=meaning
        )

    @staticmethod
    def put(output: TextIO, item: DictionaryEntry) -> None:
        """
        Implementation of procedure Put (Item : in Dictionary_Entry).
        Serializes a DictionaryEntry into a standard formatted DICTLINE string.
        """
        # 1. Write the four stems
        for stem in item.stems:
            # Ensure each stem is padded to 18 characters followed by a space
            output.write(f"{stem:<{MAX_STEM_SIZE}} ")

        # 2. Write the Part Entry
        PART_ENTRY_IO.put(output, item.part)

        # 3. Write the Translation Record
        TRANSLATION_RECORD_IO.put(output, item.tran)
        
        # 4. Write the Meaning
        # Standard format adds two spaces before the meaning string
        output.write(f"  {item.mean}\n")

# --- Public API Stub (.pyi equivalent) ---

"""
from typing import TextIO
from .dictionary_package import DictionaryEntry

class DictionaryEntryIOService:
    @staticmethod
    def get(input_str: str) -> DictionaryEntry: ...
    @staticmethod
    def put(output: TextIO, item: DictionaryEntry) -> None: ...
"""
