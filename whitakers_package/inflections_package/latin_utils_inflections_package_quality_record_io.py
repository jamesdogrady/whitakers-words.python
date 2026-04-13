from __future__ import annotations
from enum import Enum, auto
from typing import Final, List, Optional, Tuple, TextIO, Any
from pydantic import BaseModel, Field, ConfigDict

# --- Core Enumerations and Constants (Dictionary Package Context) ---

class DictionaryKind(Enum):
    """Mapped from Dictionary_Kind enum [cite: 2064-2065]."""
    X = "X  "
    Addons = "ADD"
    Xxx = "XXX"
    Yyy = "YYY"
    Nnn = "NNN"
    Rrr = "RRR"
    Ppp = "PPP"
    General = "GEN"
    Special = "SPE"
    Local = "LOC"
    Unique = "UNI"

class PartOfSpeech(Enum):
    """Grammatical Part of Speech [cite: 1782, 2391-2398]."""
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
    PREFIX = "PREFIX"
    SUFFIX = "SUFFIX"
    TACKON = "TACKON"
    X = "X"

# --- Data Models (Implementing Ada Records) ---

class DecnRecord(BaseModel):
    """Declension/Conjugation and variant[cite: 2113, 2559]."""
    model_config = ConfigDict(frozen=True)
    which: int = Field(default=0, ge=0)
    var: int = Field(default=0, ge=0)

    def to_string(self) -> str:
        return f"{self.which} {self.var}"

class TranslationRecord(BaseModel):
    """Usage metadata: Age, Area, Geography, Frequency, Source [cite: 2104-2107]."""
    model_config = ConfigDict(frozen=True)
    age: str = "X"
    area: str = "X"
    geo: str = "X"
    freq: str = "X"
    source: str = "X"

class KindEntry(BaseModel):
    """Variant record for POS-specific properties [cite: 2087-2095]."""
    model_config = ConfigDict(frozen=True)
    pofs: PartOfSpeech = PartOfSpeech.X
    n_kind: Optional[int] = None
    pron_kind: Optional[int] = None
    pack_kind: Optional[int] = None
    num_value: Optional[int] = None
    v_kind: Optional[int] = None
    vpar_kind: Optional[int] = None
    supine_kind: Optional[int] = None

class NounEntry(BaseModel):
    """Noun-specific dictionary metadata [cite: 2113-2114]."""
    model_config = ConfigDict(frozen=True)
    decl: DecnRecord = Field(default_factory=DecnRecord)
    gender: str = "X"
    kind: str = "X"

class VerbEntry(BaseModel):
    """Verb-specific dictionary metadata[cite: 2152]."""
    model_config = ConfigDict(frozen=True)
    con: DecnRecord = Field(default_factory=DecnRecord)
    kind: str = "X"

class PartEntry(BaseModel):
    """Master variant record for the 'PART' segment of a dictionary record [cite: 2175-2188]."""
    model_config = ConfigDict(frozen=True)
    pofs: PartOfSpeech = PartOfSpeech.X
    n: Optional[NounEntry] = None
    v: Optional[VerbEntry] = None
    num: Optional[Any] = None  # NumeralEntry
    adj: Optional[Any] = None  # AdjectiveEntry
    adv: Optional[Any] = None  # AdverbEntry
    prep: Optional[Any] = None # PrepositionEntry
    conj: Optional[Any] = None # ConjunctionEntry
    interj: Optional[Any] = None

# --- I/O Service Implementation ---

class DictionaryIOService:
    """
    Expert migration of various Record_IO packages into a unified service.
    Handles the column-based parsing required by Whitaker's WORDS [cite: 2423-2434].
    """

    @staticmethod
    def get_kind_entry(source: str, pofs: PartOfSpeech) -> Tuple[KindEntry, int]:
        """Parses Kind_Entry metadata based on POFS [cite: 1622-1641]."""
        # Logic: POFS determines which kind of integer or null space to read.
        # This mirrors the 'case POFS is' logic in Ada [cite: 1563-1579].
        val_str = source[:2].strip()
        val = int(val_str) if val_str.isdigit() else 0
        
        match pofs:
            case PartOfSpeech.N: return KindEntry(pofs=pofs, n_kind=val), 2
            case PartOfSpeech.PRON: return KindEntry(pofs=pofs, pron_kind=val), 2
            case PartOfSpeech.PACK: return KindEntry(pofs=pofs, pack_kind=val), 2
            case PartOfSpeech.NUM: return KindEntry(pofs=pofs, num_value=val), 2
            case PartOfSpeech.V: return KindEntry(pofs=pofs, v_kind=val), 2
            case _: return KindEntry(pofs=pofs), 2

    @staticmethod
    def get_translation_record(source: str) -> Tuple[TranslationRecord, int]:
        """Parses Translation_Record using fixed widths and spacers [cite: 2009-2014]."""
        # Age (1) + Spacer (1) + Area (1) + Spacer (1) + Geo (1) + Spacer (1) + Freq (1) + Spacer (1) + Source (1)
        # Total parsed: 9 characters [cite: 2433]
        parts = source[:9].replace(" ", "X").ljust(9, "X")
        return TranslationRecord(
            age=parts[0],
            area=parts[2],
            geo=parts[4],
            freq=parts[6],
            source=parts[8]
        ), 9

    @staticmethod
    def get_noun_entry(source: str) -> Tuple[NounEntry, int]:
        """Parses Noun_Entry: Declension (3) + Spacer + Gender (1) + Spacer + Kind (1) [cite: 1679-1682]."""
        # DecnRecord uses split logic for its internal Which/Var [cite: 2579-2581].
        # Simulated parsing based on Whitaker's standard DICTLINE offsets:
        return NounEntry(
            decl=DecnRecord(which=int(source[0:1]), var=int(source[2:3])),
            gender=source[4:5],
            kind=source[6:7]
        ), 8

    @staticmethod
    def put_part_entry_to_string(item: PartEntry, width: int = 15) -> str:
        """Serializes PartEntry to fixed-width string [cite: 1888-1905]."""
        # Start with POFS identifier [cite: 1890]
        result = f"{item.pofs.value:<4} "
        
        # Add POS-specific record data [cite: 1891-1903]
        if item.pofs == PartOfSpeech.N and item.n:
            result += f"{item.n.decl.to_string()} {item.n.gender} {item.n.kind}"
        elif item.pofs == PartOfSpeech.V and item.v:
            result += f"{item.v.con.to_string()} {item.v.kind}"
        # ... other POS variants ...

        # Fill remainder of target string with spaces [cite: 1905]
        return result.ljust(width)

# --- General System Utilities ---

class GeneralService:
    """Migration of Latin_Utils.General [cite: 2465-2470]."""
    
    @staticmethod
    async def load_dictionary_selection() -> DictionaryKind:
        """Interactively determines dictionary kind from user input [cite: 2466-2468]."""
        prompt = "What dictionary to use, GENERAL or SPECIAL (Reply G or S) => "
        # In modern Python, we'd use an async console reader or standard input
        user_choice = input(prompt).strip().upper()
        if user_choice.startswith("G"):
            return DictionaryKind.General
        elif user_choice.startswith("S"):
            return DictionaryKind.Special
        else:
            raise ValueError("No such dictionary [cite: 2469]")

def number_of_stems(part: PartOfSpeech) -> int:
    """Returns the expected number of stems for a given POS [cite: 2391-2398]."""
    mapping = {
        PartOfSpeech.N: 2, PartOfSpeech.PRON: 2, PartOfSpeech.PACK: 2,
        PartOfSpeech.ADJ: 4, PartOfSpeech.NUM: 4, PartOfSpeech.ADV: 3, PartOfSpeech.V: 4,
        PartOfSpeech.PREP: 1, PartOfSpeech.CONJ: 1, PartOfSpeech.INTERJ: 1
    }
    return mapping.get(part, 0)
