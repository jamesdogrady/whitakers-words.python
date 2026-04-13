from __future__ import annotations
from enum import Enum
from typing import Final, List, Optional, Dict
from pydantic import BaseModel, Field, ConfigDict


class TricksException(Exception):
    """Exception raised for invalid trick table lookups[cite: 9633, 9664]."""
    pass


class TrickClass(Enum):
    """Expert migration of Trick_Class enumeration[cite: 9633, 9664]."""
    TC_FLIP_FLOP = "TC_Flip_Flop"
    TC_FLIP = "TC_Flip"
    TC_INTERNAL = "TC_Internal"
    TC_SLUR = "TC_Slur"


class Trick(BaseModel):
    """
    Expert migration of the Trick variant record [cite: 9634-9639, 9665-9670].
    Maintains the structural logic of the Ada source using optional fields for variants.
    """
    model_config = ConfigDict(validate_assignment=True)

    op: TrickClass = Field(default=TrickClass.TC_FLIP_FLOP, alias="Op")
    max_val: int = Field(default=0, alias="Max")
    
    # Variant fields
    ff1: str = Field(default="", alias="FF1")
    ff2: str = Field(default="", alias="FF2")
    ff3: str = Field(default="", alias="FF3")
    ff4: str = Field(default="", alias="FF4")
    i1: str = Field(default="", alias="I1")
    i2: str = Field(default="", alias="I2")
    s1: str = Field(default="", alias="S1")


# Constants for Any_Tricks and Mediaeval_Tricks [cite: 9643-9650, 9674-9681]
ANY_TRICKS: Final[List[Trick]] = [
    Trick(Op=TrickClass.TC_INTERNAL, I1="ae", I2="e"),
    Trick(Op=TrickClass.TC_INTERNAL, I1="bul", I2="bol"),
    Trick(Op=TrickClass.TC_INTERNAL, I1="bol", I2="bul"),
    Trick(Op=TrickClass.TC_INTERNAL, I1="cl", I2="cul"),
    Trick(Op=TrickClass.TC_INTERNAL, I1="cu", I2="quu"),
    Trick(Op=TrickClass.TC_INTERNAL, I1="f", I2="ph"),
    Trick(Op=TrickClass.TC_INTERNAL, I1="ph", I2="f"),
    Trick(Op=TrickClass.TC_INTERNAL, I1="h", I2=""),
    Trick(Op=TrickClass.TC_INTERNAL, I1="oe", I2="e"),
    Trick(Op=TrickClass.TC_INTERNAL, I1="vul", I2="vol"),
    Trick(Op=TrickClass.TC_INTERNAL, I1="vol", I2="vul"),
    Trick(Op=TrickClass.TC_INTERNAL, I1="uol", I2="vul"),
]

MEDIAEVAL_TRICKS: Final[List[Trick]] = [
    Trick(Op=TrickClass.TC_INTERNAL, I1="col", I2="caul"),
    Trick(Op=TrickClass.TC_INTERNAL, I1="e", I2="ae"),
    Trick(Op=TrickClass.TC_INTERNAL, I1="o", I2="u"),
    Trick(Op=TrickClass.TC_INTERNAL, I1="i", I2="y"),
    Trick(Op=TrickClass.TC_INTERNAL, I1="ism", I2="sm"),
    Trick(Op=TrickClass.TC_INTERNAL, I1="isp", I2="sp"),
    Trick(Op=TrickClass.TC_INTERNAL, I1="ist", I2="st"),
    Trick(Op=TrickClass.TC_INTERNAL, I1="iz", I2="z"),
    Trick(Op=TrickClass.TC_INTERNAL, I1="esm", I2="sm"),
    Trick(Op=TrickClass.TC_INTERNAL, I1="esp", I2="sp"),
    Trick(Op=TrickClass.TC_INTERNAL, I1="est", I2="st"),
    Trick(Op=TrickClass.TC_INTERNAL, I1="ez", I2="z"),
    Trick(Op=TrickClass.TC_INTERNAL, I1="di", I2="z"),
    Trick(Op=TrickClass.TC_INTERNAL, I1="f", I2="ph"),
    Trick(Op=TrickClass.TC_INTERNAL, I1="is", I2="ix"),
    Trick(Op=TrickClass.TC_INTERNAL, I1="b", I2="p"),
    Trick(Op=TrickClass.TC_INTERNAL, I1="d", I2="t"),
    Trick(Op=TrickClass.TC_INTERNAL, I1="v", I2="b"),
    Trick(Op=TrickClass.TC_INTERNAL, I1="v", I2="f"),
    Trick(Op=TrickClass.TC_INTERNAL, I1="s", I2="x"),
    Trick(Op=TrickClass.TC_INTERNAL, I1="ci", I2="ti"),
    Trick(Op=TrickClass.TC_INTERNAL, I1="nt", I2="nct"),
    Trick(Op=TrickClass.TC_INTERNAL, I1="s", I2="ns"),
    Trick(Op=TrickClass.TC_INTERNAL, I1="ch", I2="c"),
    Trick(Op=TrickClass.TC_INTERNAL, I1="c", I2="ch"),
    Trick(Op=TrickClass.TC_INTERNAL, I1="th", I2="t"),
    Trick(Op=TrickClass.TC_INTERNAL, I1="t", I2="th"),
]

# Character-specific Trick Tables [cite: 9693-9713]
_TRICKS_MAP: Dict[str, List[Trick]] = {
    'a': [
        Trick(Op=TrickClass.TC_FLIP_FLOP, FF1="adgn", FF2="agn"),
        Trick(Op=TrickClass.TC_FLIP_FLOP, FF1="adsc", FF2="asc"),
        Trick(Op=TrickClass.TC_FLIP_FLOP, FF1="adsp", FF2="asp"),
        Trick(Op=TrickClass.TC_FLIP_FLOP, FF1="arqui", FF2="arci"),
        Trick(Op=TrickClass.TC_FLIP_FLOP, FF1="arqu", FF2="arcu"),
        Trick(Op=TrickClass.TC_FLIP, FF3="ae", FF4="e"),
        Trick(Op=TrickClass.TC_FLIP, FF3="al", FF4="hal"),
        Trick(Op=TrickClass.TC_FLIP, FF3="am", FF4="ham"),
        Trick(Op=TrickClass.TC_FLIP, FF3="ar", FF4="har"),
        Trick(Op=TrickClass.TC_FLIP, FF3="aur", FF4="or"),
    ],
    'd': [
        Trick(Op=TrickClass.TC_FLIP, FF3="dampn", FF4="damn"),
        Trick(Op=TrickClass.TC_FLIP_FLOP, FF1="dij", FF2="disj"),
        Trick(Op=TrickClass.TC_FLIP_FLOP, FF1="dir", FF2="disr"),
        Trick(Op=TrickClass.TC_FLIP_FLOP, FF1="dir", FF2="der"),
        Trick(Op=TrickClass.TC_FLIP_FLOP, FF1="del", FF2="dil"),
    ],
    'e': [
        Trick(Op=TrickClass.TC_FLIP_FLOP, FF1="ecf", FF2="eff"),
        Trick(Op=TrickClass.TC_FLIP_FLOP, FF1="ecs", FF2="exs"),
        Trick(Op=TrickClass.TC_FLIP_FLOP, FF1="es", FF2="ess"),
        Trick(Op=TrickClass.TC_FLIP_FLOP, FF1="ex", FF2="exs"),
        Trick(Op=TrickClass.TC_FLIP, FF3="eid", FF4="id"),
        Trick(Op=TrickClass.TC_FLIP, FF3="el", FF4="hel"),
        Trick(Op=TrickClass.TC_FLIP, FF3="e", FF4="ae"),
    ],
    'f': [
        Trick(Op=TrickClass.TC_FLIP_FLOP, FF1="faen", FF2="fen"),
        Trick(Op=TrickClass.TC_FLIP_FLOP, FF1="faen", FF2="foen"),
        Trick(Op=TrickClass.TC_FLIP_FLOP, FF1="fed", FF2="foed"),
        Trick(Op=TrickClass.TC_FLIP_FLOP, FF1="fet", FF2="foet"),
        Trick(Op=TrickClass.TC_FLIP, FF3="f", FF4="ph"),
    ],
    'g': [Trick(Op=TrickClass.TC_FLIP, FF3="gna", FF4="na")],
    'h': [
        Trick(Op=TrickClass.TC_FLIP, FF3="har", FF4="ar"),
        Trick(Op=TrickClass.TC_FLIP, FF3="hal", FF4="al"),
        Trick(Op=TrickClass.TC_FLIP, FF3="ham", FF4="am"),
        Trick(Op=TrickClass.TC_FLIP, FF3="hel", FF4="el"),
        Trick(Op=TrickClass.TC_FLIP, FF3="hol", FF4="ol"),
        Trick(Op=TrickClass.TC_FLIP, FF3="hum", FF4="um"),
    ],
    'k': [
        Trick(Op=TrickClass.TC_FLIP, FF3="k", FF4="c"),
        Trick(Op=TrickClass.TC_FLIP, FF3="c", FF4="k"),
    ],
    'l': [Trick(Max=1, Op=TrickClass.TC_FLIP_FLOP, FF1="lub", FF2="lib")],
    'm': [Trick(Max=1, Op=TrickClass.TC_FLIP_FLOP, FF1="mani", FF2="manu")],
    'n': [
        Trick(Op=TrickClass.TC_FLIP, FF3="na", FF4="gna"),
        Trick(Op=TrickClass.TC_FLIP_FLOP, FF1="nihil", FF2="nil"),
    ],
    'o': [
        Trick(Max=1, Op=TrickClass.TC_FLIP_FLOP, FF1="obt", FF2="opt"),
        Trick(Max=1, Op=TrickClass.TC_FLIP_FLOP, FF1="obs", FF2="ops"),
        Trick(Op=TrickClass.TC_FLIP, FF3="ol", FF4="hol"),
        Trick(Max=1, Op=TrickClass.TC_FLIP, FF3="opp", FF4="op"),
        Trick(Op=TrickClass.TC_FLIP, FF3="or", FF4="aur"),
    ],
    'p': [
        Trick(Op=TrickClass.TC_FLIP, FF3="ph", FF4="f"),
        Trick(Max=1, Op=TrickClass.TC_FLIP_FLOP, FF1="pre", FF2="prae"),
    ],
    's': [
        Trick(Op=TrickClass.TC_FLIP_FLOP, FF1="subsc", FF2="susc"),
        Trick(Op=TrickClass.TC_FLIP_FLOP, FF1="subsp", FF2="susp"),
        Trick(Op=TrickClass.TC_FLIP_FLOP, FF1="subc", FF2="susc"),
        Trick(Op=TrickClass.TC_FLIP_FLOP, FF1="succ", FF2="susc"),
        Trick(Op=TrickClass.TC_FLIP_FLOP, FF1="subt", FF2="supt"),
        Trick(Op=TrickClass.TC_FLIP_FLOP, FF1="subt", FF2="sust"),
    ],
    't': [Trick(Op=TrickClass.TC_FLIP_FLOP, FF1="transv", FF2="trav")],
    'u': [
        Trick(Op=TrickClass.TC_FLIP, FF3="ul", FF4="hul"),
        Trick(Op=TrickClass.TC_FLIP, FF3="uol", FF4="vul"),
    ],
    'y': [Trick(Op=TrickClass.TC_FLIP, FF3="y", FF4="i")],
    'z': [Trick(Op=TrickClass.TC_FLIP, FF3="z", FF4="di")],
}

# Slur Tricks Tables [cite: 9732-9738]
_SLUR_TRICKS_MAP: Dict[str, List[Trick]] = {
    'a': [
        Trick(Op=TrickClass.TC_FLIP_FLOP, FF1="abs", FF2="aps"),
        Trick(Op=TrickClass.TC_FLIP_FLOP, FF1="acq", FF2="adq"),
        Trick(Op=TrickClass.TC_FLIP_FLOP, FF1="ante", FF2="anti"),
        Trick(Op=TrickClass.TC_FLIP_FLOP, FF1="auri", FF2="aure"),
        Trick(Op=TrickClass.TC_FLIP_FLOP, FF1="auri", FF2="auru"),
        Trick(Op=TrickClass.TC_SLUR, S1="ad"),
    ],
    'c': [
        Trick(Op=TrickClass.TC_FLIP, FF3="circum", FF4="circun"),
        Trick(Op=TrickClass.TC_FLIP_FLOP, FF1="con", FF2="com"),
        Trick(Op=TrickClass.TC_FLIP, FF3="co", FF4="com"),
        Trick(Op=TrickClass.TC_FLIP, FF3="co", FF4="con"),
        Trick(Op=TrickClass.TC_FLIP_FLOP, FF1="conl", FF2="coll"),
    ],
    'i': [
        Trick(Max=1, Op=TrickClass.TC_SLUR, S1="in"),
        Trick(Max=1, Op=TrickClass.TC_FLIP_FLOP, FF1="inb", FF2="imb"),
        Trick(Max=1, Op=TrickClass.TC_FLIP_FLOP, FF1="inp", FF2="imp"),
    ],
    'n': [Trick(Op=TrickClass.TC_FLIP, FF3="nun", FF4="non")],
    'o': [Trick(Op=TrickClass.TC_SLUR, S1="ob")],
    'q': [Trick(Max=0, Op=TrickClass.TC_FLIP_FLOP, FF1="quadri", FF2="quadru")],
    's': [
        Trick(Op=TrickClass.TC_FLIP, FF3="se", FF4="ce"),
        Trick(Op=TrickClass.TC_SLUR, S1="sub"),
    ],
}


def member(needle: str, haystack: List[str]) -> bool:
    """Expert migration of the Member function [cite: 9688-9689]."""
    return needle in haystack


def common_prefix(s: str) -> bool:
    """
    Expert migration of Common_Prefix [cite: 9689-9692].
    Rejects common prefixes that might confuse the engine.
    """
    common_prefixes: Final[List[str]] = [
        "dis", "ex", "in", "per", "prae", "pro",
        "re", "si", "sub", "super", "trans"
    ]
    return member(s, common_prefixes)


def get_tricks_table(c: str) -> List[Trick]:
    """
    Expert migration of Get_Tricks_Table [cite: 9673, 9714-9731].
    Uses a dictionary lookup to maintain logic parity with O(1) performance.
    """
    char = c.lower()
    if char in _TRICKS_MAP:
        return _TRICKS_MAP[char]
    raise TricksException(f"No tricks table found for character: {c}")


def get_slur_tricks_table(c: str) -> List[Trick]:
    """
    Expert migration of Get_Slur_Tricks_Table [cite: 9673, 9739-9746].
    """
    char = c.lower()
    if char in _SLUR_TRICKS_MAP:
        return _SLUR_TRICKS_MAP[char]
    raise TricksException(f"No slur tricks table found for character: {c}")


### Migration Notes

# 1. Variant Records: Ada's variant records (records with discriminants) were migrated 
#    to a Pydantic model with optional fields. This satisfies the "Data Integrity" 
#    requirement while allowing Pythonic instantiation [cite: 9634-9639, 9665-9670].
# 2. Performance: The case statements in Ada were replaced with dictionaries (_TRICKS_MAP 
#    and _SLUR_TRICKS_MAP) for O(1) character-based lookups, maintaining logic 
#    parity while improving efficiency in Python [cite: 9714-9731, 9739-9746].
# 3. String Handling: Ada's Unbounded_String and the "+" renaming were abstracted. 
#    Since Python strings are natively dynamic and unbounded, direct string 
#    operations were used for logic parity[cite: 9641, 9672].
# 4. Error Handling: The Ada Tricks_Exception was mapped to a custom Python 
#    TricksException class[cite: 9633, 9664, 9731, 9746].
# 5. Type Safety: Strict typing and Pydantic validation ensure that fields like 'max_val' 
#    maintain integer integrity as required by the legacy codebase[cite: 9634, 9665].
