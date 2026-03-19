from __future__ import annotations
from enum import Enum
from typing import Final, List, Optional, Tuple, TextIO, TypeAlias, Annotated, Any
from pydantic import BaseModel, Field, ConfigDict
from pathlib import Path

# --- Core Enumerations and Type Aliases ---

class PartOfSpeechType(str, Enum):
    """Grammatical Part of Speech [cite: 2330-2332, 2583-2585]."""
    X = "X"
    N = "N"
    PRON = "PRON"
    PACK = "PACK"
    ADJ = "ADJ"
    NUM = "NUM"
    ADV = "ADV"
    V = "V"
    VPAR = "VPAR"
    SUPINE = "SUPINE"
    PREP = "PREP"
    CONJ = "CONJ"
    INTERJ = "INTERJ"
    Tackon = "TACKON"
    Prefix = "PREFIX"
    Suffix = "SUFFIX"

# Whitaker's system constraints
MAX_STEM_SIZE: Final[int] = 18 [cite: 2322, 2575]
MAX_MEANING_SIZE: Final[int] = 80 [cite: 2323, 2576]

StemType: TypeAlias = str
MeaningType: TypeAlias = str
StemKeyType: TypeAlias = Annotated[int, Field(ge=0, le=9)] [cite: 2349, 2602]

# --- Support Utilities: Character and String Handling ---

class CharUtils:
    """Expert migration of Support_Utils.Char_Utils [cite: 3453-3458, 3471-3476]."""
    
    @staticmethod
    def is_punctuation(c: str) -> bool:
        """Checks if character is one of the defined punctuation marks [cite: 3482-3484]."""
        return c in " ,-;:.([{<)]}>"

    @staticmethod
    def is_alpha_etc(c: str) -> bool:
        """Checks if character is alphabetic or '.', '-' [cite: 3485-3486]."""
        return c.isalpha() or c in "-."

    @staticmethod
    def v_to_u_and_j_to_i(c: str) -> str:
        """Normalizes Latin orthography for dictionary lookups [cite: 3487-3489]."""
        match c:
            case 'V': return 'U'
            case 'v': return 'u'
            case 'J': return 'I'
            case 'j': return 'i'
            case _: return c

class StringsPackage:
    """Expert migration of Latin_Utils.Strings_Package [cite: 3013-3021, 3027-3043]."""

    @staticmethod
    def head(source: str, count: int) -> str:
        """Truncates or pads a string to exactly 'count' length[cite: 3018, 3032]."""
        return source[:count].ljust(count)

    @staticmethod
    def get_non_comment_line(file: TextIO) -> Tuple[str, int]:
        """
        Reads lines, skipping '--' comments and handling legacy CR (Val 13) [cite: 3033-3043].
        """
        for line in file:
            line = line.rstrip('\n\r')
            if not line: continue
            
            # Check for Whitaker's specific legacy file-end marker 
            if line and ord(line[0]) == 13:
                break
                
            trimmed = line.strip()
            if trimmed.startswith("--"): [cite: 3038]
                continue
                
            # Truncate inline comments [cite: 3040-3042]
            idx = line.find("--")
            result = line[:idx] if idx != -1 else line
            return result, len(result)
            
        return "", 0

# --- Addons Data Models ---

class TargetEntry(BaseModel):
    """Expert migration of variant Target_Entry record [cite: 3222-3230, 3292-3300]."""
    model_config = ConfigDict(frozen=True)
    pofs: PartOfSpeechType = PartOfSpeechType.X
    # Placeholder for specific POS sub-records (NounEntry, VerbEntry, etc.)
    data: Optional[Any] = None 

class PrefixEntry(BaseModel):
    """Transformation record for prefixes [cite: 3241-3242, 3311-3312]."""
    model_config = ConfigDict(frozen=True)
    root: PartOfSpeechType = PartOfSpeechType.X
    target: PartOfSpeechType = PartOfSpeechType.X

class SuffixEntry(BaseModel):
    """Transformation record for suffixes [cite: 3248-3250, 3318-3320]."""
    model_config = ConfigDict(frozen=True)
    root: PartOfSpeechType = PartOfSpeechType.X
    root_key: StemKeyType = 0
    target: TargetEntry = Field(default_factory=lambda: TargetEntry())
    target_key: StemKeyType = 0

class TackonItem(BaseModel):
    """Runtime item for enclitic processing [cite: 3256-3257, 3326-3327]."""
    pofs: PartOfSpeechType = PartOfSpeechType.Tackon
    tack: StemType = " " * MAX_STEM_SIZE
    entr: TargetEntry = Field(default_factory=lambda: TargetEntry())
    mnpc: int = 0

class PrefixItem(BaseModel):
    """Runtime item for prefix processing [cite: 3258-3260, 3328-3330]."""
    pofs: PartOfSpeechType = PartOfSpeechType.Prefix
    fix: StemType = " " * MAX_STEM_SIZE
    connect: str = " "
    entr: PrefixEntry = Field(default_factory=PrefixEntry)
    mnpc: int = 0

class SuffixItem(BaseModel):
    """Runtime item for suffix processing [cite: 3261-3263, 3331-3333]."""
    pofs: PartOfSpeechType = PartOfSpeechType.Suffix
    fix: StemType = " " * MAX_STEM_SIZE
    connect: str = " "
    entr: SuffixEntry = Field(default_factory=SuffixEntry)
    mnpc: int = 0

# --- Core Addons Logic ---

class AddonsPackage:
    """Expert migration of Support_Utils.Addons_Package [cite: 3352-3446]."""

    def __init__(self):
        self.tackons: List[TackonItem] = []
        self.packons: List[TackonItem] = []
        self.prefixes: List[PrefixItem] = []
        self.suffixes: List[SuffixItem] = []

    @staticmethod
    def equ(s, t) -> bool:
        """Logical equality where 'u' and 'v' are interchangeable ."""
        if len(s) != len(t): return False
        for c1, c2 in zip(s.lower(), t.lower()):
            if c2 in ('u', 'v'):
                if c1 not in ('u', 'v'): return False
            elif c1 != c2:
                return False
        return True

    @staticmethod
    def extract_fix(source: str) -> Tuple[StemType, str]:
        """Separates the prefix/suffix from its connect character [cite: 3361-3367]."""
        st = source.strip()
        if not st: return " " * MAX_STEM_SIZE, " "
        parts = st.split(None, 1)
        fix = StringsPackage.head(parts[0], MAX_STEM_SIZE)
        connect = " "
        if len(parts) > 1:
            remainder = parts[1].lstrip()
            if remainder: connect = remainder[0]
        return fix, connect

    def subtract_prefix(self, word: str, item: PrefixItem) -> StemType:
        """Removes prefix if word matches and connection is valid [cite: 3423-3428]."""
        wd = word.strip()
        fx = item.fix.strip()
        z = len(fx)
        if len(wd) > z and self.equ(wd[:z], fx): [cite: 3425]
            if item.connect == ' ' or (len(wd) > z and wd[z] == item.connect):
                return StringsPackage.head(wd[z:], MAX_STEM_SIZE) [cite: 3426]
        return StringsPackage.head(wd, MAX_STEM_SIZE)

    def subtract_suffix(self, word: str, item: SuffixItem) -> StemType:
        """Removes suffix if word matches and connection is valid [cite: 3428-3436]."""
        wd = word.strip()
        fx = item.fix.strip()
        z = len(fx)
        if len(wd) > z and self.equ(wd[-z:], fx): [cite: 3432]
            if item.connect == ' ' or (len(wd) > z and wd[-(z+1)] == item.connect):
                return StringsPackage.head(wd[:-z], MAX_STEM_SIZE) [cite: 3434]
        return StringsPackage.head(wd, MAX_STEM_SIZE)

# --- Public API Stub ---

"""
class AddonsPackage:
    def subtract_prefix(self, word: str, item: PrefixItem) -> StemType: ...
    def subtract_suffix(self, word: str, item: SuffixItem) -> StemType: ...
"""
