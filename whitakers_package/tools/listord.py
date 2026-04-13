from __future__ import annotations
from typing import Final, List, Optional, TextIO, Tuple
from pydantic import BaseModel, Field, ConfigDict
from pathlib import Path

# --- Dependencies (Simulated from previously migrated packages) ---
from .latin_utils.inflections_package import (
    DictionaryEntry, 
    PartOfSpeechType, 
    MAX_STEM_SIZE, 
    MAX_MEANING_SIZE
)
from .latin_utils.strings_package import StringsPackage

# --- Exceptions ---

class ListordError(Exception):
    """Base exception for the Listord utility [cite: 2581-2582]."""
    pass

class TextIODataError(ListordError):
    """Raised when the input file contains malformed data[cite: 2581]."""
    pass

# --- Constants and Offsets ---

# Whitaker's DICTORD output format uses specific column offsets [cite: 2556-2560]
START_STEM_1: Final[int] = 81  # Ada index 81
START_STEM_2: Final[int] = START_STEM_1 + MAX_STEM_SIZE + 1  # 100
START_STEM_3: Final[int] = START_STEM_2 + MAX_STEM_SIZE + 1  # 119
START_STEM_4: Final[int] = START_STEM_3 + MAX_STEM_SIZE + 1  # 138
START_PART:   Final[int] = START_STEM_4 + MAX_STEM_SIZE + 1  # 157

# Default width for PartOfSpeech metadata serialization in Whitaker's system
PART_ENTRY_DEFAULT_WIDTH: Final[int] = 20 

# Offset for translation flags based on POS metadata width [cite: 2560]
START_TRAN: Final[int] = START_PART + PART_ENTRY_DEFAULT_WIDTH + 1

# --- Migration Service ---

class ListordService:
    """
    Expert migration of the 'Listord' Ada procedure.
    Converts DICTORD long format entries into a human-readable 3-line "ED file" format .
    """

    def __init__(self, input_path: str = "LISTORD.IN", output_path: str = "LISTORD.OUT"):
        self.input_path = Path(input_path)
        self.output_path = Path(output_path)
        self.entry_index: int = 0

    def run(self) -> None:
        """
        Main execution loop. Processes the input file and generates the reformatted output [cite: 2565-2583].
        """
        print("LISTORD    Takes # (DICTORD) long format to ED file")
        print("(3 lines per entry so it is all on one screen)")
        print(f"{self.input_path} -> {self.output_path}")

        if not self.input_path.exists():
            raise FileNotFoundError(f"Input file {self.input_path} not found.")

        try:
            with open(self.input_path, "r", encoding="ascii") as input_file, \
                 open(self.output_path, "w", encoding="ascii") as output_file:
                
                # Replicates: while not End_Of_File (Input) loop [cite: 2565]
                for line in input_file:
                    self.entry_index += 1
                    
                    # Logic: Rejecting blank lines [cite: 2566, 2580]
                    trimmed_line = line.strip()
                    if not trimmed_line:
                        continue

                    # Pad line to 400 characters to mirror Ada fixed-length string buffer [cite: 2561-2562, 2566]
                    s = line.rstrip('\n').ljust(400)

                    try:
                        # 1. Morphological Parsing (Form_De block) [cite: 2566-2575]
                        de = self._parse_long_format_line(s)

                        # 2. Output Generation (3 lines per entry) [cite: 2576-2579]
                        
                        # Line 1: Dictionary Form (Original prefix) [cite: 2576]
                        # Ada: S (1 .. 78) -> Python line[0:78]
                        output_file.write(f"{s[0:78].strip()}\n")

                        # Line 2: Raw Stems [cite: 2576]
                        # Ada: S (Start_Stem_1 .. Start_Part - 1)
                        # Python: line[80:156]
                        output_file.write(f"{s[START_STEM_1-1 : START_PART-1].strip()}\n")

                        # Line 3: Metadata Flags and Meaning [cite: 2577-2579]
                        self._write_metadata_line(output_file, s, de)

                    except Exception as e:
                        # Replicates 'exception when others' in Form_De 
                        print(f"Exception on entry {self.entry_index}: {e}")
                        print(f"Malformed Line: {line[:100].strip()}...")
                        # In the original system, 'raise' would stop the program 
                        raise ListordError(f"Fatal error at entry {self.entry_index}") from e

            print("Migration successful.")

        except (TextIODataError, FileNotFoundError):
            # Mirroring specific exception handling [cite: 2581]
            pass
        except Exception as e:
            # Catch-all mirroring 'when others' [cite: 2582]
            raise ListordError(f"Unexpected system failure: {e}")

    def _parse_long_format_line(self, s: str) -> DictionaryEntry:
        """
        Extracts morphological data from a long-format dictionary line [cite: 2566-2574].
        """
        de = DictionaryEntry()

        # Extract 4 stems using fixed character offsets [cite: 2566-2569]
        # logic: Ada S(X..Y) -> Python s[X-1:Y]
        de.stems[0] = s[START_STEM_1-1 : START_STEM_1 + MAX_STEM_SIZE - 1]
        de.stems[1] = s[START_STEM_2-1 : START_STEM_2 + MAX_STEM_SIZE - 1]
        de.stems[2] = s[START_STEM_3-1 : START_STEM_3 + MAX_STEM_SIZE - 1]
        de.stems[3] = s[START_STEM_4-1 : START_STEM_4 + MAX_STEM_SIZE - 1]

        # Extract Part of Speech and Translation Metadata using sequential segment parsing [cite: 2570-2573]
        # Whitaker's system uses character offsets; we simulate the sequential 'Get' updates.
        
        # Segment starting at POS metadata
        remaining = s[START_PART-1 : ].strip()
        parts = remaining.split()
        
        if len(parts) >= 2:
            # Metadata flags are typically single characters grouped in the second block [cite: 2571-2573]
            flags = parts[1]
            if len(flags) >= 5:
                de.tran.age = flags[0]
                de.tran.area = flags[1]
                de.tran.geo = flags[2]
                de.tran.freq = flags[3]
                de.tran.source = flags[4]

        # Extract Meaning [cite: 2573-2574]
        # Replicates: De.Mean := Head (S (L + 2 .. Last), Max_Meaning_Size)
        # Meaning follows the metadata flags (typically starting around col 111-160+)
        de.mean = StringsPackage.head(s[START_TRAN-1:].strip(), MAX_MEANING_SIZE)

        return de

    def _write_metadata_line(self, output: TextIO, s: str, de: DictionaryEntry) -> None:
        """
        Serializes the POS metadata and translation flags into the third line of the entry [cite: 2577-2579].
        """
        # Replicates: Put (Output, S (Start_Part .. Start_Tran - 1)); Put (Output, "      "); [cite: 2577]
        pos_part = s[START_PART-1 : START_TRAN-1]
        output.write(f"{pos_part}      ")
        
        # Replicates serialization of Age, Area, Geo, Freq, Source flags [cite: 2577-2579]
        tran = de.tran
        output.write(f"{tran.age} {tran.area} {tran.geo} {tran.freq} {tran.source}\n")
        
        # Replicates: Put_Line (Output, Trim (De.Mean)); [cite: 2579]
        output.write(f"{de.mean.strip()}\n")

# --- Public API Stub (.pyi equivalent) ---

"""
class ListordService:
    def __init__(self, input_path: str = "LISTORD.IN", output_path: str = "LISTORD.OUT"): ...
    def run(self) -> None: ...
"""

# --- Execution Entry Point ---

if __name__ == "__main__":
    service = ListordService()
    try:
        service.run()
    except ListordError as error:
        print(f"Migration Failed: {error}")
