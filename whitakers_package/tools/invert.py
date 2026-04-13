from __future__ import annotations
from typing import Final, Optional, TextIO, Tuple
from pydantic import BaseModel, Field, ConfigDict
from pathlib import Path
import sys

# --- Dependencies (Simulated from Latin_Utils) ---
from .latin_utils.strings_package import StringsPackage

# --- Core Data Models ---

class InvertParameters(BaseModel):
    """
    Expert migration of parameters for the Invert utility.
    Enforces that column indices are positive integers.
    """
    model_config = ConfigDict(validate_assignment=True)

    n1: int = Field(ge=1, description="Start column for inversion (1-based)")
    n2: int = Field(ge=1, description="End column for inversion (1-based)")


# --- Migration Service ---

class InvertService:
    """
    Expert migration of the 'Invert' Ada utility to Python 3.12+.
    Inverts or reverses the order of specific character columns in a text file.
    Commonly used for processing dictionary data with reversed stems.
    """

    def __init__(self, input_path: str = "INVERT.IN", output_path: str = "INVERT.OUT"):
        self.input_path = Path(input_path)
        self.output_path = Path(output_path)

    @staticmethod
    def invert_string(s: str) -> str:
        """
        Implementation of the internal function Invert (S : String).
        Reverses the string content while maintaining original length via padding.
        """
        # Logic: Reverse the entire segment
        reversed_content = s[::-1]
        
        # Replicates: Head (Trim (T), S'Length)
        # This keeps the reversed text at the front and pads with spaces to the original length
        trimmed = reversed_content.strip()
        return StringsPackage.head(trimmed, len(s))

    def get_user_parameters(self) -> InvertParameters:
        """
        Interactively retrieves N1 and N2 column bounds.
        """
        print("Inverts/reverses the order of columns N1 .. N2 of INVERT.IN -> INVERT.OUT")
        try:
            raw_input = input("Give an N1 and N2 => ").split()
            if len(raw_input) < 2:
                raise ValueError("Expected two integer values for N1 and N2")
            
            return InvertParameters(n1=int(raw_input[0]), n2=int(raw_input[1]))
        except (ValueError, EOFError) as e:
            print(f"Invalid input: {e}")
            sys.exit(1)

    def run(self) -> None:
        """
        Main execution loop: reads INVERT.IN and writes the modified lines to INVERT.OUT.
        """
        params = self.get_user_parameters()
        
        if not self.input_path.exists():
            print(f"Error: {self.input_path} not found.")
            return

        # Indices for Python slicing (Adjusting 1-based Ada to 0-based Python)
        # Ada: Line (N1 .. N2) -> Python: line[n1-1 : n2]
        start_idx = params.n1 - 1
        end_idx = params.n2

        try:
            with open(self.input_path, "r", encoding="ascii") as input_file, \
                 open(self.output_path, "w", encoding="ascii") as output_file:
                
                for line in input_file:
                    raw_line = line.rstrip('\n')
                    
                    # Logic: Only invert if the line is long enough to contain the range
                    if len(raw_line) >= params.n2:
                        # Replicate slice assignment
                        segment = raw_line[start_idx:end_idx]
                        inverted_segment = self.invert_string(segment)
                        
                        # Re-assemble the line
                        new_line = (
                            raw_line[:start_idx] + 
                            inverted_segment + 
                            raw_line[end_idx:]
                        )
                    else:
                        new_line = raw_line
                    
                    output_file.write(new_line + "\n")

            print("Inversion complete.")

        except Exception as e:
            print(f"Fatal error during processing: {e}")

# --- Public API Stub (.pyi equivalent) ---

"""
class InvertService:
    def __init__(self, input_path: str = "INVERT.IN", output_path: str = "INVERT.OUT"): ...
    def run(self) -> None: ...
"""

# --- Execution Entry Point ---

if __name__ == "__main__":
    service = InvertService()
    service.run()
