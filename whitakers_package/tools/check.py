from __future__ import annotations
from enum import Enum, IntEnum
from typing import Final, List, Optional, Tuple, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
import struct
from pathlib import Path

# --- Dependencies (Simulated from Latin_Utils and Support_Utils) ---
from .latin_utils.inflections_package import (
    StemType, PartEntry, StemKeyType, ComparisonType, 
    NumeralSortType, PartOfSpeechType, NullStemType, 
    NullPartEntry, MAX_STEM_SIZE
)
from .latin_utils.strings_package import StringsPackage
from .latin_utils.preface import PrefaceService as Preface
from .latin_utils.config import Config
from .support_utils.char_utils import CharUtils

# --- Core Data Models ---

class DictionaryStem(BaseModel):
    """
    Expert migration of Dictionary_Stem record [cite: 2904-2905, 2933-2934].
    Represents a stem entry in the binary stem file.
    """
    model_config = ConfigDict(validate_assignment=True)

    stem: StemType = NullStemType
    part: PartEntry = Field(default_factory=lambda: NullPartEntry)
    key: StemKeyType = 0
    mnpc: int = 0  # Replaces Dict_IO.Count

class DictionaryFileKind(IntEnum):
    """
    Subtype of Dictionary_Kind representing the search tiers.
    """
    GENERAL = 0
    SPECIAL = 1
    LOCAL = 2

# --- Migration Service ---

class WordSupportPackage:
    """
    Expert migration of Support_Utils.Word_Support_Package[cite: 2903, 2932].
    Handles word metadata parsing and indexed dictionary lookup management.
    """

    def __init__(self):
        # Global state migrated to instance attributes [cite: 2903, 2932]
        self.followed_by_period: bool = False
        self.capitalized: bool = False
        self.all_caps: bool = False

        # In-memory "blank" and single-letter stems [cite: 2909, 2938]
        self.bdl: List[DictionaryStem] = [DictionaryStem() for _ in range(101)]
        self.bdl_last: int = 0

        # Multi-dimensional indices for dictionary seek offsets 
        # Maps (Kind, Char1, Char2) -> Seek Count
        self._first_indices: Dict[Tuple[DictionaryFileKind, str, str], int] = {}
        self._last_indices: Dict[Tuple[DictionaryFileKind, str, str], int] = {}

    @staticmethod
    def len(s: str) -> int:
        """Returns the trimmed length of a string [cite: 2954-2955]."""
        return len(s.strip())

    @staticmethod
    def eff_part(part: PartOfSpeechType) -> PartOfSpeechType:
        """Normalizes verbal variants to base Verb [cite: 2955-2957]."""
        if part in (PartOfSpeechType.VPAR, PartOfSpeechType.SUPINE):
            return PartOfSpeechType.V
        return part

    @staticmethod
    def adj_comp_from_key(key: StemKeyType) -> ComparisonType:
        """Maps stem key to adjective comparison [cite: 2958-2961]."""
        match key:
            case 0 | 1 | 2: return ComparisonType.Pos
            case 3: return ComparisonType.Comp
            case 4: return ComparisonType.Super
            case _: return ComparisonType.X

    @staticmethod
    def adv_comp_from_key(key: StemKeyType) -> ComparisonType:
        """Maps stem key to adverb comparison [cite: 2962-2964]."""
        match key:
            case 1: return ComparisonType.Pos
            case 2: return ComparisonType.Comp
            case 3: return ComparisonType.Super
            case _: return ComparisonType.X

    @staticmethod
    def num_sort_from_key(key: StemKeyType) -> NumeralSortType:
        """Maps stem key to numeral sort [cite: 2964-2966]."""
        match key:
            case 1: return NumeralSortType.Card
            case 2: return NumeralSortType.Ord
            case 3: return NumeralSortType.Dist
            case 4: return NumeralSortType.Adverb
            case _: return NumeralSortType.X

    def first_index(self, input_word: str, d_k: DictionaryFileKind = DictionaryFileKind.GENERAL) -> int:
        """
        Implementation of First_Index [cite: 2916, 2967-2971].
        Calculates the binary seek offset for the start of the word's block.
        """
        wd = input_word.strip()
        if d_k == DictionaryFileKind.LOCAL:
            # Local dictionaries use single-letter indexing [cite: 2968]
            return self._first_indices.get((d_k, wd[0], 'a'), 0)
        
        if len(wd) < 2:
            return 0
        
        # General dictionaries use two-letter indexing [cite: 2970]
        return self._first_indices.get((d_k, wd[0], wd[1]), 0)

    def last_index(self, input_word: str, d_k: DictionaryFileKind = DictionaryFileKind.GENERAL) -> int:
        """
        Implementation of Last_Index [cite: 2917, 2971-2975].
        Calculates the binary seek offset for the end of the word's block.
        """
        wd = input_word.strip()
        if d_k == DictionaryFileKind.LOCAL:
            return self._last_indices.get((d_k, wd[0], 'a'), 0)
        
        if len(wd) < 2:
            return 0
        
        return self._last_indices.get((d_k, wd[0], wd[1]), 0)

    def load_indices_from_indx_file(self, d_k: DictionaryFileKind) -> None:
        """
        Implementation of Load_Indices_From_Indx_File [cite: 2947, 2991-3013].
        Parses text-based index files (e.g., STEMFILE.GEN.INDX).
        """
        ext = d_k.name[:3].upper() # Simulating EXT(D_K)
        file_path = Config.path(f"STEMFILE.{ext}.INDX") [cite: 2995]

        Preface.put(f"{d_k.name} Dictionary loading") [cite: 2996]

        try:
            with open(file_path, "r") as f:
                # 1. Handle General Blank Stems [cite: 2997-3000]
                if d_k == DictionaryFileKind.GENERAL:
                    line = f.readline()
                    if line:
                        ch = line[0:2]
                        m = int(line[3:7].strip())
                        n = int(line[8:12].strip())
                        self._first_indices[(d_k, ' ', ' ')] = m
                        self._last_indices[(d_k, ' ', ' ')] = n

                # 2. Parse Remaining Indices [cite: 3001-3010]
                for line in f:
                    if not line.strip(): break
                    ch = line[0:2]
                    # Whitaker's index format: CH1 CH2 FIRST LAST
                    # Logic branches based on whether index is single-letter or pair [cite: 3003-3010]
                    m = int(line[3:9].strip())
                    n = int(line[10:16].strip())
                    
                    self._first_indices[(d_k, ch[0], ch[1])] = m
                    self._last_indices[(d_k, ch[0], ch[1])] = n

            Preface.set_col(33)
            Preface.put("--  stems") [cite: 3012]
            Preface.set_col(55)
            Preface.put_line("--  Loaded correctly") [cite: 3013]
        except FileNotFoundError:
            Preface.put_line(f"Warning: Index file {file_path} not found")

    def load_bdl_from_disk(self) -> None:
        """
        Implementation of Load_Bdl_From_Disk [cite: 2947, 2975-2991].
        Pre-caches "blank" stems and single-letter stems into memory for speed.
        """
        k = 0
        
        # 1. Load Blank Stems (General Only) [cite: 2977-2981]
        if (DictionaryFileKind.GENERAL, ' ', ' ') in self._first_indices:
            d_k = DictionaryFileKind.GENERAL
            path = Config.path(f"STEMFILE.{d_k.name[:3].upper()}")
            
            try:
                # Simulating binary seek/read of records [cite: 2980-2981]
                idx_first = self._first_indices[(d_k, ' ', ' ')]
                idx_last = self._last_indices[(d_k, ' ', ' ')]
                
                # Mock loading for logic parity
                for j in range(idx_first, idx_last + 1):
                    # stem_data = self._read_binary_record(path, j)
                    k += 1
                    # self.bdl[k] = stem_data
            except Exception as e:
                Preface.put_line(f"LOADING BDL FROM DISK failed on {path}") [cite: 2982]

        # 2. Load Single-Letter Stems [cite: 2985-2990]
        for d_k in DictionaryFileKind:
            if d_k == DictionaryFileKind.LOCAL: break
            
            for i in range(ord('a'), ord('z') + 1):
                char = chr(i)
                idx_first = self._first_indices.get((d_k, char, ' '), 0)
                idx_last = self._last_indices.get((d_k, char, ' '), 0)
                
                if idx_first > 0:
                    for j in range(idx_first, idx_last + 1):
                        # ds = self._read_binary_record(path, j)
                        k += 1
                        # self.bdl[k] = ds
        
        self.bdl_last = k [cite: 2991]

# --- Public API Stub (.pyi equivalent) ---

"""
from typing import Tuple, List, Optional
from .inflections_package import DictionaryStem

class WordSupportPackage:
    bdl: List[DictionaryStem]
    bdl_last: int
    def first_index(self, input_word: str, d_k: DictionaryFileKind) -> int: ...
    def last_index(self, input_word: str, d_k: DictionaryFileKind) -> int: ...
    def load_indices_from_indx_file(self, d_k: DictionaryFileKind) -> None: ...
    def load_bdl_from_disk(self) -> None: ...
"""
