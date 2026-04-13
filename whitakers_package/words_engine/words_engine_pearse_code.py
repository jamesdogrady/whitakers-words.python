from __future__ import annotations
from enum import IntEnum

# --- Core Data Models ---

class Symbol(IntEnum):
    """
    Expert migration of Symbol enumeration[cite: 3248, 3263].
    These codes are named for classicist Roger Pearse and used for pedagogical metadata.
    """
    UNKNOWN = 0        # 00
    INFLECTION = 1     # 01
    CITATION_FORM = 2  # 02
    GLOSS = 3          # 03
    UNKNOWN_NAME = 4   # 04 (Mapping for Unknowns_2)
    AFFIX = 5          # 05
    TRICK = 6          # 06


# --- Migration Service ---

class PearseCodeService:
    """
    Expert migration of the Words_Engine.Pearse_Code package to Python 3.12+ [cite: 3250-3252].
    Provides standardized formatting for metadata identifiers in Whitaker's engine.
    """

    @staticmethod
    def format_code(s: Symbol) -> str:
        """
        Implementation of the Format function .
        
        Logic Parity:
        1. Ada Integer'Image(Pos(S)) creates a string with a leading space (e.g., " 1").
        2. Trim(Left) removes that space (e.g., "1").
        3. Tail(2, '0') pads to 2 digits (e.g., "01").
        4. Head(3, ' ') adds a trailing space (e.g., "01 ").
        
        Python implementation utilizes f-string formatting to achieve identical 
        bit-level alignment in a single operation.
        """
        # Formats the enum value as a 2-digit zero-padded string followed by a space 
        return f"{s.value:02} "

# --- Public API Stub (.pyi equivalent) ---

"""
from enum import IntEnum

class Symbol(IntEnum): ...

class PearseCodeService:
    @staticmethod
    def format_code(s: Symbol) -> str: ...
"""

# --- Example Usage ---
if __name__ == "__main__":
    # Test parity with Whitaker's '02 ' Citation Form marker
    print(f"'{PearseCodeService.format_code(Symbol.CITATION_FORM)}'")
