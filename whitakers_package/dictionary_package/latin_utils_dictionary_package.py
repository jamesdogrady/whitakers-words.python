from __future__ import annotations
from enum import Enum, auto
from typing import Final, List, Optional, Dict
from pydantic import BaseModel, Field, ConfigDict

# --- Dependencies (Imported from previously migrated Inflections_Package) ---
from .inflections_package import (
    StemType, StemKeyType, MAX_STEM_SIZE, NullStemType,
    PartOfSpeech, NounKindType, PronounKindType, NumeralValueType,
    VerbKindType, ComparisonType, NumeralSortType, CaseType,
    InflectionRecord, MeaningType, NullMeaningType, NullInflectionRecord,
    DecnRecord
)

# --- Enumerations ---

class DictionaryKind(Enum):
    """Types of dictionary files used in the WORDS system[cite: 2111, 2112]."""
    X = auto()        # null
    Addons = auto()   # For FIXES
    Xxx = auto()      # TRICKS
    Yyy = auto()      # Syncope
    Nnn = auto()      # Unknown Name
    Rrr = auto()      # Roman Numerals
    Ppp = auto()      # Compounds
    General = auto()
    Special = auto()
    Local = auto()
    Unique = auto()

class AreaType(Enum):
    """Subject matter areas for vocabulary classification [cite: 2116-2118]."""
    X = "X"  # All or none
    A = "A"  # Agriculture, Flora, Fauna
    B = "B"  # Biological, Medical
    D = "D"  # Drama, Music, Theater
    E = "E"  # Ecclesiastic, Religious [cite: 2117]
    G = "G"  # Grammar, Rhetoric, Literature
    L = "L"  # Legal, Government, Political
    P = "P"  # Poetic
    S = "S"  # Science, Philosophy, Math
    T = "T"  # Technical, Architecture
    W = "W"  # War, Military, Naval [cite: 2118]
    Y = "Y"  # Mythology

class GeoType(Enum):
    """Geographical regions of Latin usage [cite: 2120-2122]."""
    X = "X"  # All
    A = "A"  # Africa
    B = "B"  # Britain
    C = "C"  # China
    D = "D"  # Scandinavia
    E = "E"  # Egypt [cite: 2121]
    F = "F"  # France, Gaul
    G = "G"  # Germany
    H = "H"  # Greece
    I = "I"  # Italy, Rome
    J = "J"  # India
    K = "K"  # Balkans
    N = "N"  # Netherlands [cite: 2122]
    P = "P"  # Persia
    Q = "Q"  # Near East
    R = "R"  # Russia
    S = "S"  # Spain, Iberia
    U = "U"  # Eastern Europe

class SourceType(Enum):
    """Citations for dictionary entries [cite: 2124-2131]."""
    X = "X"  # General/Unknown
    A = "A"
    B = "B"  # Beeson Medieval Latin
    C = "C"  # Cassell's [cite: 2124]
    D = "D"  # Adams Sexual Vocab
    E = "E"  # Stelten Eccl. Latin [cite: 2125]
    F = "F"  # Deferrari Aquinas
    G = "G"  # Gildersleeve Grammar
    H = "H"  # Collatinus
    I = "I"  # Leverett
    J = "J"  # Bracton [cite: 2125]
    K = "K"  # Calepinus Novus [cite: 2126]
    L = "L"  # Lewis Elementary
    M = "M"  # Latham Medieval
    N = "N"  # Lynn Nelson
    O = "O"  # OLD [cite: 2126]
    P = "P"  # Souter Later Latin [cite: 2127]
    Q = "Q"  # Other
    R = "R"  # Plater Grammar [cite: 2127]
    S = "S"  # Lewis and Short
    T = "T"  # Translation [cite: 2127]
    U = "U"
    V = "V"  # Blatt Saxo [cite: 2128]
    W = "W"  # Whitaker's guess
    Y = "Y"  # Temp
    Z = "Z"  # User submission [cite: 2128]

# --- Dictionary Records ---

class KindEntry(BaseModel):
    """Metadata for specific parts of speech in the dictionary [cite: 2134-2142]."""
    model_config = ConfigDict(frozen=True)
    pofs: PartOfSpeech = PartOfSpeech.X
    n_kind: NounKindType = NounKindType.X
    pron_kind: PronounKindType = PronounKindType.X
    pack_kind: PronounKindType = PronounKindType.X
    num_value: int = 0  # Numeral_Value_Type [cite: 2138]
    v_kind: VerbKindType = VerbKindType.X
    vpar_kind: VerbKindType = VerbKindType.X
    supine_kind: VerbKindType = VerbKindType.X

class TranslationRecord(BaseModel):
    """Metadata for dictionary usage and era [cite: 2151-2154]."""
    model_config = ConfigDict(frozen=True)
    age: str = "X"
    area: AreaType = AreaType.X [cite: 2152]
    geo: GeoType = GeoType.X [cite: 2153]
    freq: str = "X"
    source: SourceType = SourceType.X [cite: 2154]

class NounEntry(BaseModel):
    """Grammatical properties of a noun[cite: 2160, 2161]."""
    model_config = ConfigDict(frozen=True)
    decl: DecnRecord = Field(default_factory=lambda: DecnRecord(0, 0)) [cite: 2160]
    gender: str = "X" [cite: 2161]
    kind: NounKindType = NounKindType.X

class VerbEntry(BaseModel):
    """Grammatical properties of a verb[cite: 2198, 2199]."""
    model_config = ConfigDict(frozen=True)
    con: DecnRecord = Field(default_factory=lambda: DecnRecord(0, 0)) [cite: 2199]
    kind: VerbKindType = VerbKindType.X

class PartEntry(BaseModel):
    """Composite record for part-of-speech specific dictionary data [cite: 2222-2236]."""
    model_config = ConfigDict(frozen=True)
    pofs: PartOfSpeech = PartOfSpeech.X
    noun: Optional[NounEntry] = None [cite: 2222]
    verb: Optional[VerbEntry] = None [cite: 2228]
    # Remaining types omitted for brevity in summary, but mapped from [cite: 2223-2233]

class DictionaryEntry(BaseModel):
    """The master record for a Whitaker's WORDS dictionary entry [cite: 2243-2245]."""
    model_config = ConfigDict(frozen=True)
    stems: List[StemType] = Field(default_factory=lambda: [NullStemType] * 4) [cite: 2243]
    part: PartEntry = Field(default_factory=lambda: PartEntry(pofs=PartOfSpeech.X)) [cite: 2244]
    tran: TranslationRecord = Field(default_factory=TranslationRecord) [cite: 2244]
    mean: MeaningType = NullMeaningType [cite: 2245]

class ParseRecord(BaseModel):
    """Tracking structure used during Latin parsing [cite: 2254-2256]."""
    model_config = ConfigDict(frozen=True)
    stem: StemType = NullStemType [cite: 2254]
    ir: InflectionRecord = NullInflectionRecord [cite: 2255]
    d_k: DictionaryKind = DictionaryKind.X [cite: 2255]
    mnpc: int = 0  # MNPC_Type (Direct_IO Count) [cite: 2256]

# --- Global Constants & Utility Logic ---

ZZZ_STEM: Final[StemType] = "zzz" + (" " * (MAX_STEM_SIZE - 3)) [cite: 2109]

def number_of_stems(part: PartOfSpeech) -> int:
    """Returns the expected number of stems for a given POS ."""
    match part:
        case PartOfSpeech.N | PartOfSpeech.PRON | PartOfSpeech.PACK:
            return 2 [cite: 2438, 2439]
        case PartOfSpeech.ADJ | PartOfSpeech.NUM | PartOfSpeech.V:
            return 4 [cite: 2440, 2441]
        case PartOfSpeech.ADV:
            return 3 [cite: 2441]
        case PartOfSpeech.PREP | PartOfSpeech.CONJ | PartOfSpeech.INTERJ:
            return 1 [cite: 2443, 2444]
        case _:
            return 0 [cite: 2442, 2444, 2445]

# --- Migration Services ---

class DictionaryPackageService:
    """
    Coordinates global initialization and metadata for the dictionary package.
    Equivalent to the package body initialization .
    """
    
    # Mapping for file extensions [cite: 2114]
    EXTENSIONS: Final[Dict[DictionaryKind, str]] = {
        DictionaryKind.X: "X  ", DictionaryKind.Addons: "ADD",
        DictionaryKind.Xxx: "XXX", DictionaryKind.Yyy: "YYY",
        DictionaryKind.Nnn: "NNN", DictionaryKind.Rrr: "RRR",
        DictionaryKind.Ppp: "PPP", DictionaryKind.General: "GEN",
        DictionaryKind.Special: "SPE", DictionaryKind.Local: "LOC",
        DictionaryKind.Unique: "UNI"
    }

    @staticmethod
    def area_less_than_or_equal(left: AreaType, right: AreaType) -> bool:
        """Implements the overriding function for Area context[cite: 2466, 2467]."""
        return right == left or right == AreaType.X [cite: 2466]
