from __future__ import annotations
from typing import Final, List, Optional, TextIO, Tuple, TYPE_CHECKING
from pydantic import BaseModel, Field, ConfigDict
from pathlib import Path

# --- Dependencies (Simulated from Project Context) ---
if TYPE_CHECKING:
    from .latin_utils.inflections_package import PartOfSpeechType, DictionaryKind, GenderType, VerbKindType
    from .latin_utils.dictionary_package import DictionaryEntry
    from .words_engine.english_support_package import EwdsRecord

from .latin_utils.inflections_package import PartOfSpeechType, DictionaryKind, FrequencyType
from .latin_utils.strings_package import StringsPackage
from .support_utils.word_parameters import WordParametersService as WordsMode
from .support_utils.developer_parameters import DeveloperParametersService as WordsMdev
from .words_engine.english_support_package import EWORD_SIZE, EwdsRecord, Null_Ewds_Record
from .latin_utils.dictionary_package import Null_Dictionary_Entry, DictIOService
from .support_utils.dictionary_form import dictionary_form

# --- Exceptions ---

class SearchEnglishError(Exception):
    """Base exception for English search operations [cite: 12198-12199]."""
    pass

# --- Migration Service ---

class SearchEnglishService:
    """
    Expert migration of Words_Engine.Search_English procedure.
    Performs binary search on English-to-Latin mappings and formats output[cite: 12144].
    """

    ONE_SCREEN: Final[int] = 6

    def __init__(self):
        self.output_array: List[EwdsRecord] = [Null_Ewds_Record for _ in range(500)]
        self.number_of_hits: int = 0
        self.trimmed: bool = False
        self.scroll_line_number: int = 0

    def load_output_array(self, ewds: EwdsRecord, input_pofs: PartOfSpeechType) -> None:
        """Collects hits matching the part-of-speech filter [cite: 12149-12150]."""
        if ewds.pofs.value <= input_pofs.value:
            if self.number_of_hits < 500:
                self.output_array[self.number_of_hits] = ewds
                self.number_of_hits += 1

    def sort_output_array(self) -> None:
        """
        Implementation of Bubble Sort for hit results .
        Orders by Rank (desc), then Frequency (asc), then Semantic index (asc).
        """
        # Note: Using Python's sorted() with a key for performance while maintaining logic parity
        relevant_hits = self.output_array[:self.number_of_hits]
        
        # Sort key: (-Rank, Frequency, Semantic) 
        # Negative Rank achieves descending order 
        relevant_hits.sort(key=lambda x: (-x.rank, x.freq.value, x.semi))
        
        self.output_array[:self.number_of_hits] = relevant_hits

    def dump_output_array(self, output: TextIO) -> None:
        """Formats and displays the search results [cite: 12159-12181]."""
        if self.number_of_hits == 0:
            output.write("No Match\n") [cite: 12161]
            return

        self.sort_output_array() [cite: 12162]
        self.trimmed = False

        number_to_show = self.number_of_hits
        if WordsMode.get_flag("Trim_Output"): [cite: 12163]
            if self.number_of_hits > self.ONE_SCREEN:
                number_to_show = self.ONE_SCREEN
                self.trimmed = True
            else:
                number_to_show = self.number_of_hits

        for i in range(number_to_show):
            output.write("\n") [cite: 12165]
            
            # Paging logic parity [cite: 12166-12167]
            # (Note: In a true Python CLI, this would interact with a pager)

            ewds = self.output_array[i]
            try:
                # Read Latin entry corresponding to English word mapping [cite: 12167]
                de = DictIOService.read_entry(DictionaryKind.GENERAL, ewds.n)
            except Exception:
                continue

            # Display Dictionary Form [cite: 12168]
            output.write(f"{dictionary_form(de)}   ")

            # POS Specific Metadata Formatting [cite: 12169-12172]
            if de.part.pofs == PartOfSpeechType.N:
                output.write(f"  {de.part.n.decl.to_string()}  {de.part.n.gender.name}  ")
            elif de.part.pofs == PartOfSpeechType.V:
                output.write(f"  {de.part.v.con.to_string()}")
                if de.part.v.kind.value >= 1: # Equivalent to Gen..Perfdef
                    output.write(f"  {de.part.v.kind.name}  ")

            # Technical Metadata Brackets [cite: 12173-12175]
            if WordsMdev.get_flag("Show_Dictionary_Codes"):
                output.write(f" [{de.tran.age.value}{de.tran.area.value}{de.tran.geo.value}{de.tran.freq.value}{de.tran.source.value}]  ")

            if WordsMdev.get_flag("Show_Dictionary"):
                output.write(f"{DictionaryKind.GENERAL.name[:3]}>") [cite: 12176]

            if WordsMdev.get_flag("Show_Dictionary_Line"):
                output.write(f"({ewds.n})") [cite: 12177]

            output.write("\n")
            output.write(f"{de.mean.strip()}\n") [cite: 12178]

        if self.trimmed:
            output.write("*\n") [cite: 12179]

    def search_english(self, input_english_word: str, pofs: PartOfSpeechType = PartOfSpeechType.X, output: Optional[TextIO] = None) -> None:
        """
        Main binary search execution loop [cite: 12181-12197].
        """
        input_word = StringsPackage.head(input_english_word.lower(), EWORD_SIZE)
        self.number_of_hits = 0
        
        # Binary Search Initialization [cite: 12181-12183]
        # In this migration, we assume Ewds_File is handled by EnglishSupportService
        from .words_engine.english_support_package import EnglishSupportService
        file_size = EnglishSupportService.get_file_size()
        
        j1, j2 = 1, file_size
        first_try = second_try = True
        
        while True:
            # Termination logic parity 
            if (j1 == j2 - 1) or (j1 == j2):
                if first_try:
                    j = j1
                    first_try = False
                elif second_try:
                    j = j2
                    second_try = False
                else:
                    break
            else:
                j = (j1 + j2) // 2

            # Read record at index j [cite: 12187]
            ewds = EnglishSupportService.read_record(j)
            
            # String comparison (Direct binary search, not Latin-aware) [cite: 12188-12190]
            if ewds.w.lower() < input_word:
                j1 = j
            elif ewds.w.lower() > input_word:
                j2 = j
            else:
                # Range scan for multiple hits [cite: 12190-12196]
                # Backward scan
                for i in range(j, j1 - 1, -1):
                    rec = EnglishSupportService.read_record(i)
                    if rec.w.lower() == input_word:
                        self.load_output_array(rec, pofs)
                    else:
                        break
                # Forward scan
                for i in range(j + 1, j2 + 1):
                    rec = EnglishSupportService.read_record(i)
                    if rec.w.lower() == input_word:
                        self.load_output_array(rec, pofs)
                    else:
                        break
                break

        # Render Results 
        import sys
        target_output = output or sys.stdout
        self.dump_output_array(target_output)

# --- Public API Stub (.pyi equivalent) ---

"""
from .latin_utils.inflections_package import PartOfSpeechType

class SearchEnglishService:
    def search_english(self, input_english_word: str, pofs: PartOfSpeechType = PartOfSpeechType.X) -> None: ...
"""
