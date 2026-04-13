from __future__ import annotations
from typing import Final, List, Optional, TextIO
from pydantic import BaseModel, Field, ConfigDict
from pathlib import Path

# --- Dependencies (Simulated from Latin_Utils) ---
from .latin_utils.strings_package import StringsPackage

# --- Constants ---

# Whitaker's standard stem size
MAX_STEM_SIZE: Final[int] = 18
BLANK_STEM: Final[str] = " " * MAX_STEM_SIZE

# --- Migration Service ---

class InvStemsService:
    """
    Expert migration of the 'Invstems' Ada utility to Python 3.12+.
    Inverts the four stems of a DICTLINE form file to support reverse-dictionary lookups.
    """

    def __init__(self, input_path: str = "INVERT_S.IN", output_path: str = "INVERT_S.OUT"):
        self.input_path = Path(input_path)
        self.output_path = Path(output_path)

    @staticmethod
    def invert_stem(s: str) -> str:
        """
        Implementation of the internal function Invert (S : String).
        If the stem is not blank, it reverses the characters and re-pads to 18 characters.
        """
        # Logic: If the first character is a space, Whitaker's code treats it as a blank stem
        if not s or s[0] == ' ':
            return BLANK_STEM
        
        # Logic: Reverse the entire 18-character block
        reversed_content = s[::-1]
        
        # Logic: Trim the reversed string and pad back to 18 (using Head)
        trimmed = reversed_content.strip()
        return StringsPackage.head(trimmed, MAX_STEM_SIZE)

    def run(self) -> None:
        """
        Main execution loop: reads INVERT_S.IN and writes inverted stems to INVERT_S.OUT.
        """
        print(f"Inverts the 4 stems of a DICTLINE form file {self.input_path} -> {self.output_path}")

        if not self.input_path.exists():
            print(f"Error: {self.input_path} not found.")
            return

        try:
            with open(self.input_path, "r", encoding="ascii") as input_file, \
                 open(self.output_path, "w", encoding="ascii") as output_file:
                
                for line in input_file:
                    raw_line = line.rstrip('\n')
                    if not raw_line:
                        output_file.write("\n")
                        continue

                    # Pad line to ensure indexing parity for short lines
                    line_buf = raw_line.ljust(250)
                    
                    # 1. Extract 4 stems from fixed DICTLINE offsets
                    # Ada 1..18   -> Python 0:18
                    # Ada 20..37  -> Python 19:37
                    # Ada 39..56  -> Python 38:56
                    # Ada 58..75  -> Python 57:75
                    stems: List[str] = [
                        line_buf[0:18],
                        line_buf[19:37],
                        line_buf[38:56],
                        line_buf[57:75]
                    ]
                    
                    # 2. Invert each stem
                    inverted_stems = [self.invert_stem(st) for st in stems]
                    
                    # 3. Reconstruct the line
                    # Logic: Replaces original stems but preserves the rest of the line (metadata, meaning)
                    # Note the single space delimiters at indices 18, 37, and 56
                    new_line = (
                        f"{inverted_stems[0]} {inverted_stems[1]} "
                        f"{inverted_stems[2]} {inverted_stems[3]} "
                        f"{line_buf[75:].rstrip()}"
                    )
                    
                    output_file.write(new_line + "\n")

            print("Stem inversion complete.")

        except Exception as e:
            # Replicates Ada's catch-all exception handling for robust file processing
            print(f"Fatal error during stem inversion: {e}")

# --- Public API Stub (.pyi equivalent) ---

"""
class InvStemsService:
    def __init__(self, input_path: str = "INVERT_S.IN", output_path: str = "INVERT_S.OUT"): ...
    def run(self) -> None: ...
"""

# --- Execution Entry Point ---

if __name__ == "__main__":
    service = InvStemsService()
    service.run()
