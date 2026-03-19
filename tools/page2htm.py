from __future__ import annotations
from typing import Final, Optional
from pydantic import BaseModel, Field, ConfigDict
from pathlib import Path

# --- Dependencies (Simulated from Latin_Utils context) ---
from .latin_utils.strings_package import StringsPackage

# --- Core Data Models ---

class Page2HtmConfig(BaseModel):
    """
    Configuration for the Page2htm utility.
    Encapsulates input/output paths for the HTML dictionary conversion [cite: 2512-2514].
    """
    model_config = ConfigDict(validate_assignment=True)

    input_path: Path = Field(default=Path("DICTPAGE.RAW"))
    output_path: Path = Field(default=Path("DICTPAGE.HTM"))


# --- Migration Service ---

class Page2HtmService:
    """
    Expert migration of the 'Page2htm' Ada utility to Python 3.12+.
    Converts a sorted DICTPAGE.RAW file into a formatted HTML dictionary [cite: 2512-2514].
    """

    def __init__(self, config: Optional[Page2HtmConfig] = None):
        self.config = config or Page2HtmConfig()

    def run(self) -> None:
        """
        Main execution loop: reads DICTPAGE.RAW and generates DICTPAGE.HTM [cite: 2512-2519].
        """
        print("DICTPAGE.RAW (sorted) -> DICTPAGE.HTM")
        print("For use in preparing a DICTPAGE.HTM after running DICTPAGE and sorting [cite: 2512-2513].")

        if not self.config.input_path.exists():
            print(f"Error: {self.config.input_path} not found.")
            return

        try:
            with open(self.config.input_path, "r", encoding="utf-8") as input_file, \
                 open(self.config.output_path, "w", encoding="utf-8") as output_file:
                
                # Logic: Iterate through input file line by line 
                for line in input_file:
                    raw_line = line.rstrip('\n')
                    if not raw_line:
                        continue

                    # 1. Validation: Expect pedagogical '#' marker [cite: 2515]
                    # Note: Python index 0 corresponds to Ada Line(1)
                    if not raw_line.startswith('#'):
                        print(f"BAD LINE   >{raw_line}")
                    
                    # 2. Sequential String Processing [cite: 2516-2519]
                    # Replicates the Ada loop: for I in 1 .. Last loop
                    for i in range(len(raw_line)):
                        # Look for opening bracket metadata [cite: 2516]
                        if raw_line[i] == '[':
                            # Replicates: Put (Output, "<B>" & Line (2 .. I - 1) & "</B>  ");
                            # Ada 2 .. I-1 maps to Python 1:i
                            content_head = raw_line[1:i]
                            output_file.write(f"<B>{content_head}</B>  ")
                            
                            # Replicates: Put_Line (Output, Trim (Line (I .. I + 6) & "<BR>"));
                            # Ada I .. I+6 maps to Python i:i+7
                            bracket_metadata = raw_line[i:i+7]
                            output_file.write(f"{bracket_metadata.strip()}<BR>\n")
                        
                        # Look for meaning delimiter [cite: 2518]
                        if raw_line[i:i+2] == "::":
                            # Replicates: Put_Line (Output, Trim (Line (I + 2 .. Last)) & "<BR>");
                            # Ada I + 2 .. Last maps to Python i+2:
                            meaning = raw_line[i+2:]
                            output_file.write(f"{meaning.strip()}<BR>\n")
                            # Exit inner loop after processing delimiter [cite: 2519]
                            break

            print(f"HTML generation complete. Results written to {self.config.output_path}.")

        except Exception as e:
            # Replicates Ada's catch-all error handling for file operations
            print(f"Fatal error during HTML conversion: {e}")

# --- Public API Stub (.pyi equivalent) ---

"""
class Page2HtmService:
    def __init__(self, config: Optional[Page2HtmConfig] = None): ...
    def run(self) -> None: ...
"""

# --- Execution Entry Point ---

if __name__ == "__main__":
    service = Page2HtmService()
    service.run()
