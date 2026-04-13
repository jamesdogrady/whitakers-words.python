from __future__ import annotations
from typing import Final, Optional, TextIO, Tuple
from pydantic import BaseModel, Field, ConfigDict
from pathlib import Path
import sys

# --- Core Data Models ---

class DupsParameters(BaseModel):
    """
    Expert migration of parameters for the Dups utility.
    Enforces Ada-style non-negative constraints for column indices.
    """
    model_config = ConfigDict(validate_assignment=True)

    mx: int = Field(ge=1, description="Start column for duplicate check")
    nx: int = Field(ge=1, description="End column for duplicate check")


# --- Migration Service ---

class DupsService:
    """
    Expert migration of the 'Dups' Ada utility to Python 3.12+.
    Identifies duplicate entries in sorted dictionary files based on user-defined 
    column ranges.
    """

    def __init__(self, input_path: str = "DUPS.IN", output_path: str = "DUPS.OUT"):
        self.input_path = Path(input_path)
        self.output_path = Path(output_path)
        self.line_number: int = 0
        self.dup_count: int = 0

    def get_user_parameters(self) -> DupsParameters:
        """
        Implementation of procedure Get_Entry.
        Reads column bounds from standard input.
        """
        print("DUPS.IN -> DUPS.OUT    For sorted files")
        print("DUPS checks for columns MX .. NX being duplicates")
        
        try:
            # Replicates sequential Get calls in Ada
            raw_input = input("Enter MX and NX: ").split()
            if len(raw_input) < 2:
                raise ValueError("Expected two integer values for MX and NX")
            
            return DupsParameters(mx=int(raw_input[0]), nx=int(raw_input[1]))
        except (ValueError, EOFError) as e:
            print(f"Invalid input: {e}")
            sys.exit(1)

    def run(self) -> None:
        """
        Main execution loop. Processes the input file line-by-line and 
        flags sequential duplicates in the specified range.
        """
        params = self.get_user_parameters()
        
        if not self.input_path.exists():
            print(f"Error: {self.input_path} not found.")
            return

        # Indices for Python slicing (Adjusting 1-based Ada to 0-based Python)
        # Ada: Line (Mx .. Nx) -> Python: line[mx-1 : nx]
        start_idx = params.mx - 1
        end_idx = params.nx
        flag_idx = 110  # Ada column 111

        try:
            with open(self.input_path, "r") as input_file, open(self.output_path, "w") as output_file:
                old_line = ""
                
                for line in input_file:
                    self.line_number += 1
                    # Pad line to ensure indexing doesn't fail on short lines
                    current_line = line.rstrip('\n').ljust(200)
                    
                    # Logic: Check range equality and ensure line is not marked with '|'
                    # Note: Line(111) /= '|' is a Whitaker-specific check for manual overrides.
                    if (current_line[start_idx:end_idx] == old_line[start_idx:end_idx] and 
                        current_line[flag_idx] != '|' and 
                        old_line != ""):
                        
                        self.dup_count += 1
                        # Output format: Line Number + content up to NX
                        output_file.write(f"{self.line_number}  {current_line[:params.nx]}\n")
                    
                    old_line = current_line

            self._print_summary()

        except Exception as e:
            print(f"Fatal error during processing: {e}")

    def _print_summary(self) -> None:
        """Outputs statistics matching the legacy Ada format."""
        print(f"\nNumber of entries = {self.line_number}")
        print(f"Number of DUPS    = {self.dup_count}")
        if self.dup_count > 0:
            print(f"Ratio             = 1 : {self.line_number / self.dup_count:.2f}")
        else:
            print("Ratio             = 1 : 0 (No duplicates found)")

# --- Public API Stub (.pyi equivalent) ---

"""
class DupsService:
    def __init__(self, input_path: str = "DUPS.IN", output_path: str = "DUPS.OUT"): ...
    def run(self) -> None: ...
"""

# --- Execution ---

if __name__ == "__main__":
    service = DupsService()
    service.run()
