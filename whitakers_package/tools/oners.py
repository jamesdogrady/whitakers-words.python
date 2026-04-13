from __future__ import annotations
from typing import Final, Optional
from pydantic import BaseModel, Field, ConfigDict
from pathlib import Path
import sys

# --- Dependencies (Simulated from Latin_Utils context) ---
# Note: Oners is a standalone utility but follows the system-wide I/O patterns.

# --- Core Data Models ---

class OnersConfig(BaseModel):
    """
    Configuration for the Oners utility.
    Encapsulates file paths and formatting constraints.
    """
    model_config = ConfigDict(validate_assignment=True)

    input_path: Path = Field(default=Path("ONERS.IN"))
    output_path: Path = Field(default=Path("ONERS.OUT"))


# --- Migration Service ---

class OnersService:
    """
    Expert migration of the 'Oners' Ada utility to Python 3.12+.
    Processes a sorted text file to deduplicate identical lines and 
    prepend a frequency count to each unique entry.
    """

    def __init__(self, config: Optional[OnersConfig] = None):
        self.config = config or OnersConfig()

    def run(self) -> None:
        """
        Main execution loop: reads the sorted input and writes unique lines with 
        counts to the output.
        """
        print("ONERS.IN -> ONERS.OUT")
        print("Takes a sorted file to produce a file having just one of each identical line.")
        print("Puts a count of how many identical lines at the beginning of each.")

        if not self.config.input_path.exists():
            print(f"Error: {self.config.input_path} not found.")
            return

        try:
            with open(self.config.input_path, "r", encoding="utf-8") as input_file, \
                 open(self.config.output_path, "w", encoding="utf-8") as output_file:
                
                # 1. Initialize the sequence
                # Replicates: Get_Line (Input, Old_Line, Old_Last);
                line_iterator = iter(input_file)
                try:
                    old_line = next(line_iterator).rstrip('\n')
                except StopIteration:
                    print("Input file is empty.")
                    return

                count = 1  # Replicates 'N : Integer := 0' and subsequent 'N := N + 1'

                # 2. Process sequential lines
                # Replicates: while not End_Of_File (Input) loop
                for line in line_iterator:
                    current_line = line.rstrip('\n')
                    
                    # Logic: Check for identity with the previous line
                    if current_line == old_line:
                        count += 1
                    else:
                        # Logic: Current line is different; write the previous group's count and content
                        # Replicates: Put (Output, N); Put_Line (Output, "  " & Old_Line);
                        # Note: Ada's Put (Integer) typically adds a leading space.
                        output_file.write(f" {count}  {old_line}\n")
                        
                        # Reset for the new group
                        old_line = current_line
                        count = 1

                # 3. Handle the final unique line
                output_file.write(f" {count}  {old_line}\n")

            print(f"Deduplication complete. Results written to {self.config.output_path}.")

        except Exception as e:
            # Replicates Ada's catch-all 'when others' error handling
            print(f"Fatal error during processing: {e}")

# --- Public API Stub (.pyi equivalent) ---

"""
class OnersService:
    def __init__(self, config: Optional[OnersConfig] = None): ...
    def run(self) -> None: ...
"""

# --- Execution Entry Point ---

if __name__ == "__main__":
    service = OnersService()
    service.run()
