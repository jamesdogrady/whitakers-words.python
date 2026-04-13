from __future__ import annotations
from typing import Final, Optional, TextIO
from pydantic import BaseModel, Field, ConfigDict
from pathlib import Path

# --- Dependencies (Imported from previously migrated modules) ---
from .latin_utils.strings_package import StringsPackage

# --- Exceptions ---

class FixordError(Exception):
    """Base exception for the Fixord utility."""
    pass

class InputFileNotFoundError(FixordError):
    """Raised when the input file FIXORD.IN is missing."""
    pass

# --- Core Data Models ---

class FixordConfig(BaseModel):
    """
    Configuration for the Fixord utility.
    Enforces Whitaker's legacy string buffer limits.
    """
    model_config = ConfigDict(validate_assignment=True)

    max_line_length: int = Field(default=400, ge=1)
    comment_character: str = Field(default="#", min_length=1, max_length=1)


# --- Migration Service ---

class FixordService:
    """
    Expert migration of the 'Fixord' Ada utility to Python 3.12+.
    Cleans dictionary listing files by removing pedagogical '#' markers to 
    produce a raw 3-line entry format suitable for editing.
    """

    def __init__(
        self, 
        input_path: str = "FIXORD.IN", 
        output_path: str = "FIXORD.OUT",
        config: Optional[FixordConfig] = None
    ):
        self.input_path = Path(input_path)
        self.output_path = Path(output_path)
        self.config = config or FixordConfig()

    def run(self) -> None:
        """
        Main execution loop: reads FIXORD.IN and writes the cleaned format to FIXORD.OUT.
        """
        print(f"{self.input_path} -> {self.output_path}")
        print("Makes a clean (no #) 3 line ED format from LISTORD output")

        if not self.input_path.exists():
            raise InputFileNotFoundError(f"No {self.input_path} file to process")

        try:
            with open(self.input_path, "r", encoding="ascii") as input_file, \
                 open(self.output_path, "w", encoding="ascii") as output_file:
                
                # Replicates: while not End_Of_File (Input) loop
                for line in input_file:
                    # Logic: Replicate Whitaker's blank line rejection
                    trimmed_line = line.strip()
                    if not trimmed_line:
                        continue
                    
                    # Logic: Skip lines starting with '#' pedagogical marker
                    # Replicates: if S (1) /= '#' then
                    if not line.startswith(self.config.comment_character):
                        # Replicates: Put_Line (Output, S (1 .. Last))
                        output_file.write(line)

            print("Cleaning complete.")

        except Exception as e:
            # Replicates Ada's catch-all 'when others' error handling
            raise FixordError(f"Fatal error during dictionary file cleaning: {e}")

# --- Public API Stub (.pyi equivalent) ---

"""
class FixordService:
    def __init__(self, input_path: str = "FIXORD.IN", output_path: str = "FIXORD.OUT"): ...
    def run(self) -> None: ...
"""

# --- Execution Entry Point ---

if __name__ == "__main__":
    try:
        service = FixordService()
        service.run()
    except FixordError as e:
        print(f"Error: {e}")
