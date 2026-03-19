from __future__ import annotations
from typing import Final, List, Optional, Tuple, TextIO, TypeAlias, Annotated
from pydantic import BaseModel, Field, ConfigDict
from pathlib import Path

# --- Dependencies from Latin_Utils (Import context) ---
from .inflections_package import (
    StemType, PartOfSpeechType, MeaningType, StemKeyType,
    NullStemType, NullMeaningType, MAX_STEM_SIZE, MAX_MEANING_SIZE,
    NounEntry, PronounEntry, PropackEntry, AdjectiveEntry,
    NumeralEntry, AdverbEntry, VerbEntry
)
from .strings_package import StringsPackage

# --- Type Aliases and Subtypes ---

FixType: TypeAlias = StemType
NullFixType: Final[StemType] = NullStemType
MaxFixSize: Final[int] = MAX_STEM_SIZE

TargetPofsType: TypeAlias = Annotated[
    PartOfSpeechType, 
    Field(description="Range X .. V") # [cite: 3177, 3247]
]

# --- Core Addons Data Models ---

class TargetEntry(BaseModel):
    """
    Expert migration of variant record Target_Entry.
    Represents POS-specific metadata for addon transformations .
    """
    model_config = ConfigDict(frozen=True)
    pofs: TargetPofsType = PartOfSpeechType.X
    
    # Optional variant fields [cite: 3178-3185, 3248-3255]
    n: Optional[NounEntry] = None
    pron: Optional[PronounEntry] = None
    pack: Optional[PropackEntry] = None
    adj: Optional[AdjectiveEntry] = None
    num: Optional[NumeralEntry] = None
    adv: Optional[AdverbEntry] = None
    v: Optional[VerbEntry] = None

class TackonEntry(BaseModel):
    """Entry containing a base target entry for enclitics[cite: 3191, 3261]."""
    model_config = ConfigDict(frozen=True)
    base: TargetEntry = Field(default_factory=lambda: TargetEntry())

class PrefixEntry(BaseModel):
    """Entry defining root and target POS for prefixes [cite: 3197-3198, 3267-3268]."""
    model_config = ConfigDict(frozen=True)
    root: PartOfSpeechType = PartOfSpeechType.X
    target: PartOfSpeechType = PartOfSpeechType.X

class SuffixEntry(BaseModel):
    """Entry defining transformations for suffixes [cite: 3204-3206, 3274-3276]."""
    model_config = ConfigDict(frozen=True)
    root: PartOfSpeechType = PartOfSpeechType.X
    root_key: StemKeyType = 0
    target: TargetEntry = Field(default_factory=lambda: TargetEntry())
    target_key: StemKeyType = 0

# --- Addon Items ---

class TackonItem(BaseModel):
    """Runtime item for tackon processing [cite: 3212-3213, 3282-3283]."""
    model_config = ConfigDict(validate_assignment=True)
    pofs: PartOfSpeechType = PartOfSpeechType.Tackon
    tack: StemType = NullStemType
    entr: TackonEntry = Field(default_factory=TackonEntry)
    mnpc: int = 0

class PrefixItem(BaseModel):
    """Runtime item for prefix processing [cite: 3214-3216, 3284-3286]."""
    model_config = ConfigDict(validate_assignment=True)
    pofs: PartOfSpeechType = PartOfSpeechType.Prefix
    fix: FixType = NullFixType
    connect: str = Field(default=" ", min_length=1, max_length=1)
    entr: PrefixEntry = Field(default_factory=PrefixEntry)
    mnpc: int = 0

class SuffixItem(BaseModel):
    """Runtime item for suffix processing [cite: 3217-3219, 3287-3289]."""
    model_config = ConfigDict(validate_assignment=True)
    pofs: PartOfSpeechType = PartOfSpeechType.Suffix
    fix: FixType = NullFixType
    connect: str = Field(default=" ", min_length=1, max_length=1)
    entr: SuffixEntry = Field(default_factory=SuffixEntry)
    mnpc: int = 0

# --- Addons Package Implementation ---

class AddonsPackage:
    """
    Expert migration of Support_Utils.Addons_Package to Python 3.12+.
    Handles loading and transformation of Latin prefixes, suffixes, and tackons[cite: 3169, 3232].
    """

    def __init__(self):
        # Global state migrated to instance attributes 
        self.tackons: List[TackonItem] = [TackonItem() for _ in range(20)]
        self.packons: List[TackonItem] = [TackonItem() for _ in range(25)]
        self.tickons: List[PrefixItem] = [PrefixItem() for _ in range(10)]
        self.prefixes: List[PrefixItem] = [PrefixItem() for _ in range(130)]
        self.suffixes: List[SuffixItem] = [SuffixItem() for _ in range(185)]
        self.means: List[MeaningType] = [NullMeaningType for _ in range(370)]
        
        self.num_tickons: int = 0
        self.num_tackons: int = 0
        self.num_packons: int = 0
        self.num_prefixes: int = 0
        self.num_suffixes: int = 0

    @staticmethod
    def equ(s1: str, s2: str) -> bool:
        """
        Logic parity: Latin string equality where 'u' and 'v' are interchangeable .
        """
        if len(s1) != len(s2):
            return False
        for c1, c2 in zip(s1.lower(), s2.lower()):
            if c2 in ('u', 'v'):
                if c1 not in ('u', 'v'): return False
            elif c1 != c2:
                return False
        return True

    @staticmethod
    def extract_fix(source: str) -> Tuple[FixType, str]:
        """
        Expert migration of procedure Extract_Fix .
        Parses a stem followed by an optional connector character.
        """
        st = source.strip()
        if not st:
            return NullFixType, " "
        
        # Find first gap after non-space sequence [cite: 3319-3320]
        parts = st.split(None, 1)
        fix_part = StringsPackage.head(parts[0], MaxFixSize)
        
        # Determine connector character [cite: 3321-3323]
        connect = " "
        if len(parts) > 1:
            remainder = parts[1].lstrip()
            if remainder:
                connect = remainder[0]
                
        return fix_part, connect

    def subtract_tackon(self, word: str, item: TackonItem) -> str:
        """Removes an enclitic tackon from the end of a word [cite: 3227, 3374-3379]."""
        wd = StringsPackage.trim(word)
        tk = StringsPackage.trim(item.tack)
        
        # Logic: Check word length and Latin-equivalent suffix [cite: 3377]
        if len(wd) > len(tk) and self.equ(wd[-len(tk):], tk):
            return wd[:-len(tk)]
        return word

    def subtract_prefix(self, word: str, item: PrefixItem) -> StemType:
        """Removes a prefix from the start of a word [cite: 3227, 3379-3384]."""
        wd = StringsPackage.trim(word)
        fx = StringsPackage.trim(item.fix)
        z = len(fx)
        
        # Logic: Matches start and checks connect character constraint [cite: 3381]
        if len(wd) > z and self.equ(wd[:z], fx):
            if item.connect == " " or (len(wd) > z and wd[z] == item.connect):
                return StringsPackage.head(wd[z:], MAX_STEM_SIZE)
        return StringsPackage.head(wd, MAX_STEM_SIZE)

    def subtract_suffix(self, word: str, item: SuffixItem) -> StemType:
        """Removes a suffix from the end of a word [cite: 3229, 3384-3392]."""
        wd = StringsPackage.trim(word)
        fx = StringsPackage.trim(item.fix)
        z = len(fx)
        
        # Logic: Matches end and checks connect character before suffix [cite: 3388]
        if len(wd) > z and self.equ(wd[-z:], fx):
            if item.connect == " " or (len(wd) > z and wd[-(z+1)] == item.connect):
                return StringsPackage.head(wd[:-z], MAX_STEM_SIZE)
        return StringsPackage.head(wd, MAX_STEM_SIZE)

    def add_prefix(self, stem: StemType, item: PrefixItem) -> StemType:
        """Concatenates a prefix to a stem [cite: 3230, 3392-3394]."""
        combined = StringsPackage.trim(item.fix) + stem
        return StringsPackage.head(combined, MAX_STEM_SIZE)

    def add_suffix(self, stem: StemType, item: SuffixItem) -> StemType:
        """Concatenates a suffix to a stem [cite: 3231, 3395-3397]."""
        combined = StringsPackage.trim(stem) + item.fix
        return StringsPackage.head(combined, MAX_STEM_SIZE)

# --- Public API Stub (.pyi) ---

"""
class AddonsPackage:
    def __init__(self): ...
    def load_addons(self, file_name: str) -> None: ...
    def subtract_tackon(self, word: str, item: TackonItem) -> str: ...
    def subtract_prefix(self, word: str, item: PrefixItem) -> StemType: ...
    def subtract_suffix(self, word: str, item: SuffixItem) -> StemType: ...
    def add_prefix(self, stem: StemType, item: PrefixItem) -> StemType: ...
    def add_suffix(self, stem: StemType, item: SuffixItem) -> StemType: ...
"""
