from __future__ import annotations
from enum import Enum, auto
from typing import Final, List, Optional, Tuple, Protocol, Self
from pydantic import BaseModel, Field, ConfigDict, ValidationError
from pathlib import Path
import functools

# --- Dependencies (Simulated from Latin_Utils and Inflections context) ---
from .latin_utils.strings_package import StringsPackage
from .latin_utils.inflections_package import PartEntry, NullPartEntry

# --- Custom Exceptions ---

class SorterError(Exception):
    """Base exception for the Latin Sorter utility[cite: 2953]."""
    pass

class EntryFinishedError(SorterError):
    """Raised when user input for sort fields is complete[cite: 2953, 3027]."""
    pass

# --- Core Data Models ---

class SortType(Enum):
    """Expert migration of Sort_Type enumeration[cite: 2949]."""
    A = auto()  # Alphabetic (all case)
    C = auto()  # Case sensitive
    G = auto()  # Ignore separators
    U = auto()  # Latin orthography (u/v and i/j normalization)
    N = auto()  # Integer
    F = auto()  # Floating point
    P = auto()  # Part of speech
    S = auto()  # Section/Appendix

class WayType(Enum):
    """Expert migration of Way_Type enumeration[cite: 2950]."""
    I = auto()  # Increasing
    D = auto()  # Decreasing

class SectionType(BaseModel):
    """Logic for hierarchical document section numbering [cite: 2954-2956]."""
    model_config = ConfigDict(validate_assignment=True, frozen=True)
    first_level: int = 0
    second_level: int = 0
    third_level: int = 0
    fourth_level: int = 0
    fifth_level: int = 0

    def __lt__(self, other: SectionType) -> bool:
        """Hierarchical comparison logic ."""
        attrs = ("first_level", "second_level", "third_level", "fourth_level", "fifth_level")
        for attr in attrs:
            v1, v2 = getattr(self, attr), getattr(other, attr)
            if v1 < v2: return True
            if v1 > v2: return False
        return False

class AppendixType(Enum):
    """Enumerated appendix identifiers[cite: 2957]."""
    NONE = 0
    A = 1; B = 2; C = 3; D = 4; E = 5; F = 6; G = 7; H = 8; I = 9; J = 10
    K = 11; L = 12; M = 13; N = 14; O = 15; P = 16; Q = 17; R = 18; S = 19; T = 20
    U = 21; V = 22; W = 23; X = 24; Y = 25; Z = 26

class AppendixSectionType(BaseModel):
    """Composite model for appendix-aware sectioning [cite: 2958-2959]."""
    model_config = ConfigDict(validate_assignment=True, frozen=True)
    appendix: AppendixType = AppendixType.NONE
    section: SectionType = Field(default_factory=SectionType)

    def __lt__(self, other: AppendixSectionType) -> bool:
        """Sequential comparison of appendix then section levels ."""
        if self.appendix.value < other.appendix.value: return True
        if self.appendix.value > other.appendix.value: return False
        return self.section < other.section

class SortCriteria(BaseModel):
    """Defines a single sorting field within a line [cite: 2952-2953]."""
    model_config = ConfigDict(validate_assignment=True)
    m: int = Field(default=1, ge=0)  # Start column (1-based)
    n: int = Field(default=0, ge=0)  # End column (1-based)
    s_type: SortType = SortType.A
    way: WayType = WayType.I

# --- Migration Service ---

class LatinSorterService:
    """
    Expert migration of Whitaker's Sorter procedure.
    Supports multi-pass Latin-aware sorting on fixed-width string fields[cite: 2942, 3139].
    """
    LINE_LENGTH: Final[int] = 300

    def __init__(self):
        self.criteria: List[SortCriteria] = []

    @staticmethod
    def equ(c: str, d: str) -> bool:
        """Latin orthography equality: treats u/v and i/j as equivalent [cite: 3049-3057]."""
        if not c or not d: return c == d
        v1, v2 = c.lower(), d.lower()
        if v2 in ('u', 'v'): return v1 in ('u', 'v')
        if v2 in ('i', 'j'): return v1 in ('i', 'j')
        return c == d

    @staticmethod
    def ltu(c: str, d: str) -> bool:
        """Latin orthography 'less than' with v/j normalization [cite: 3040-3048]."""
        if not c or not d: return c < d
        v1, v2 = c.lower(), d.lower()
        if v2 == 'v': return v1 < 'u'
        if v2 == 'j': return v1 < 'i'
        return c < d

    def string_equ_latin(self, s: str, t: str) -> bool:
        """Case-insensitive Latin-aware string equality [cite: 3073-3075, 3111-3112]."""
        if len(s) != len(t): return False
        return all(self.equ(a, b) for a, b in zip(s, t))

    def string_ltu_latin(self, s: str, t: str) -> bool:
        """Case-insensitive Latin-aware string 'less than' [cite: 3067-3069, 3086-3087]."""
        for c, d in zip(s, t):
            if self.equ(c, d): continue
            return self.ltu(c, d)
        return False

    @staticmethod
    def ignore_separators(s: str) -> str:
        """Normalization that replaces hyphens/underscores between text ."""
        chars = list(s.lower())
        for i in range(1, len(chars) - 1):
            if chars[i] in ('-', '_') and chars[i-1] not in ('-', '_') and chars[i+1] not in ('-', '_'):
                chars[i] = ' '
        return "".join(chars)

    def compare_fields(self, x: str, y: str, crit: SortCriteria) -> int:
        """
        Implementation of Slt and Sort_Equal logic for a single criteria [cite: 3075-3118].
        Returns: -1 if x < y, 1 if x > y, 0 if equal.
        """
        # 1. Normalization [cite: 3078-3088, 3108-3112]
        match crit.s_type:
            case SortType.A: x_val, y_val = x.lower(), y.lower()
            case SortType.C: x_val, y_val = x, y
            case SortType.G: x_val, y_val = self.ignore_separators(x), self.ignore_separators(y)
            case SortType.U: x_val, y_val = x.lower(), y.lower()
            case _: x_val, y_val = x, y

        # 2. Logic Dispatch [cite: 3079-3102, 3108-3116]
        res = 0
        if crit.s_type == SortType.U:
            if self.string_ltu_latin(x_val, y_val): res = -1
            elif self.string_equ_latin(x_val, y_val): res = 0
            else: res = 1
        elif crit.s_type == SortType.N:
            try: res = (int(x_val) > int(y_val)) - (int(x_val) < int(y_val))
            except ValueError: res = (x_val > y_val) - (x_val < y_val)
        elif crit.s_type == SortType.F:
            try: res = (float(x_val) > float(y_val)) - (float(x_val) < float(y_val))
            except ValueError: res = (x_val > y_val) - (x_val < y_val)
        elif crit.s_type == SortType.S:
            # Section parsing placeholder logic [cite: 3099-3101, 3115-3116]
            res = (x_val > y_val) - (x_val < y_val)
        else:
            res = (x_val > y_val) - (x_val < y_val)

        # 3. Apply Direction [cite: 3079-3080, 3090-3091]
        return res if crit.way == WayType.I else -res

    def line_lt(self, left: str, right: str) -> bool:
        """Composite 'Less Than' across all defined criteria [cite: 3119-3124]."""
        for crit in self.criteria:
            if crit.n == 0: continue
            # Ada slices are 1-based inclusive; Python 0-based [cite: 3119]
            l_field = left[crit.m-1 : crit.n]
            r_field = right[crit.m-1 : crit.n]
            
            comparison = self.compare_fields(l_field, r_field, crit)
            if comparison < 0: return True
            if comparison > 0: return False
        return False

    def run(self, input_path: Path, output_path: Path) -> None:
        """
        Main execution workflow. Replaces Ada's manual on-disk Heapsort with 
        Python's optimized sorting utilizing the migrated Lt logic [cite: 3139-3175].
        """
        print(f"Sorting {input_path} -> {output_path} [cite: 3139]")
        
        if not input_path.exists():
            raise FileNotFoundError(f"Source file {input_path} not found.")

        # 1. Read and filter blank/non-graphic lines [cite: 3151-3156, 3174]
        lines = []
        with open(input_path, "r", encoding="utf-8") as f:
            for line in f:
                # Replicates: if Trim (Graphic (Line_Text))'Length > 0 [cite: 3174]
                clean = line.rstrip('\n\r')
                if clean.strip():
                    lines.append(clean)

        # 2. Sort using migrated composite comparison [cite: 3119-3124, 3157-3169]
        # Using functools.cmp_to_key to bridge Python's sort with Ada's LT logic
        def comparator(a: str, b: str) -> int:
            if self.line_lt(a, b): return -1
            if self.line_lt(b, a): return 1
            return 0

        lines.sort(key=functools.cmp_to_key(comparator))

        # 3. Write results [cite: 3172-3175]
        with open(output_path, "w", encoding="utf-8") as f:
            for line in lines:
                f.write(f"{line}\n")

        print("Sort completed successfully[cite: 3175].")

# --- Public API Stub (.pyi equivalent) ---

"""
class LatinSorterService:
    def run(self, input_path: Path, output_path: Path) -> None: ...
    def line_lt(self, left: str, right: str) -> bool: ...
    criteria: List[SortCriteria]
"""

# --- Execution Entry Point (Sample CLI flow) ---

if __name__ == "__main__":
    sorter = LatinSorterService()
    # Mocking user input for a sample Latin dictionary sort [cite: 3020-3036]
    sorter.criteria.append(SortCriteria(m=1, n=18, s_type=SortType.U, way=WayType.I))
    
    try:
        sorter.run(Path("DICTLINE.IN"), Path("DICTLINE.OUT"))
    except Exception as e:
        print(f"SORT terminated: {e} [cite: 3176-3179]")
