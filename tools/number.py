from __future__ import annotations
from typing import Final, Optional
from pydantic import BaseModel, Field, ConfigDict
from pathlib import Path

# --- Core Data Models ---

class NumberingConfig(BaseModel):
    """
    Configuration for the Numbering utility.
    Encapsulates the formatting constraints of the legacy system.
    """
    model_config = ConfigDict(validate_assignment=True)

    target_column: int = Field(default=10, ge=1, description="The column where the original text begins")
    output_filename: str = Field(default="NUMBERED.", description="The name of the generated numbered file")


# --- Migration Service ---

class NumberService:
    """
    Expert migration of the 'Number' Ada utility to Python 3.12+.
    Reads a text file and produces a new version with sequential line numbers 
    aligned to a specific column.
    """

    def __init__(self, config: Optional[NumberingConfig] = None):
        self.config = config or NumberingConfig()

    def run(self) -> None:
        """
        Main execution loop: prompts for a filename, then processes the file.
        """
        print("Takes a text file and produces a NUMBERED. file with line numbers")
        
        # 1. Get input filename from user
        try:
            input_path_str = input("What file to NUMBER? ").strip()
            if not input_path_str:
                print("No filename provided. Exiting.")
                return
            
            input_path = Path(input_path_str)
            if not input_path.exists():
                print(f"Error: {input_path_str} not found.")
                return

            # 2. Process the file
            self._process_file(input_path)

        except EOFError:
            print("\nInput stream closed.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def _process_file(self, input_path: Path) -> None:
        """
        Reads the input file and writes numbered lines to the output file.
        """
        output_path = Path(self.config.output_filename)
        line_counter = 0

        try:
            with open(input_path, "r", encoding="utf-8") as input_file, \
                 open(output_path, "w", encoding="utf-8") as output_file:
                
                for line in input_file:
                    line_counter += 1
                    original_content = line.rstrip('\n')

                    # Logic: Replicate Ada's 'Integer'Image' and 'Set_Col(10)'
                    # In Ada, Integer'Image(N) typically includes a leading space.
                    # Set_Col(10) ensures the original text starts at the 10th character (index 9).
                    
                    # Format the number with a leading space to match Ada's 'Image attribute
                    number_str = f" {line_counter}"
                    
                    # Pad the number string with spaces so the original content starts at target_column
                    # Python index 0 is column 1; target_column 10 is index 9.
                    padding_needed = self.config.target_column - 1
                    formatted_line = f"{number_str:<{padding_needed}}{original_content}\n"
                    
                    output_file.write(formatted_line)

            print(f"Successfully created {self.config.output_filename} with {line_counter} lines.")

        except Exception as e:
            print(f"Fatal error during file processing: {e}")

# --- Public API Stub (.pyi equivalent) ---

"""
class NumberService:
    def __init__(self, config: Optional[NumberingConfig] = None): ...
    def run(self) -> None: ...
"""

# --- Execution Entry Point ---

if __name__ == "__main__":
    service = NumberService()
    service.run()
