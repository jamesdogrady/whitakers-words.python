from __future__ import annotations
from typing import Final, List, Optional, TextIO
from pydantic import BaseModel, Field, ConfigDict
from pathlib import Path

# --- Dependencies (Imported from previously migrated modules) ---
from .latin_utils.inflections_package import (
    DictionaryEntry, PartEntry, AgeType, AreaType, GeoType,
    FrequencyType, SourceType, MAX_STEM_SIZE, MAX_MEANING_SIZE,
    NullDictionaryEntry
)
from .latin_utils.strings_package import StringsPackage
from .support_utils.dictionary_form import dictionary_form

# --- Constants ---

# Column offsets for fixed-width DICTLINE format [cite: 614-617]
START_STEM_1: Final[int] = 0   # Ada 1
START_STEM_2: Final[int] = 19  # Ada 20
START_STEM_3: Final[int] = 38  # Ada 39
START_STEM_4: Final[int] = 57  # Ada 58
START_PART:   Final[int] = 76  # Ada 77

# --- Migration Service ---

class DictPageService:
    """
    Expert migration of the 'Dictpage' Ada utility to Python 3.12+.
    Processes DICTLINE files to create a formatted 'paper-like' dictionary report[cite: 613].
    """

    def __init__(self, input_path: str = "DICTPAGE.IN", output_path: str = "DICTPAGE.OUT"):
        self.input_path = Path(input_path)
        self.output_path = Path(output_path)

    def run(self) -> None:
        """
        Main execution loop: reads the dictionary and generates the paper report [cite: 620-637].
        """
        if not self.input_path.exists():
            print(f"Error: {self.input_path} not found.")
            return

        print("DICTPAGE.IN -> DICTPAGE.OUT")
        print("Creating pretty dictionary display...")

        try:
            with open(self.input_path, "r") as input_file, open(self.output_path, "w") as output_file:
                for line in input_file:
                    # 1. Skip blank lines [cite: 625, 637]
                    if not line.strip():
                        continue

                    # Pad line to ensure slicing doesn't fail on legacy short lines
                    raw_line = line.rstrip('\n').ljust(400)

                    try:
                        # 2. Parse the DictionaryEntry (Logic from Form_De) 
                        de = self._parse_line_to_entry(raw_line)

                        # 3. Write pedagogical Dictionary Form [cite: 634]
                        # Replicates: Put (Output, "#" & Support_Utils.Dictionary_Form (De));
                        output_file.write(f"#{dictionary_form(de)}")

                        # 4. Write Metadata block [cite: 635-636]
                        # Replicates: [Age Area Geo Freq Source]
                        tran = de.tran
                        metadata = (
                            f" [{tran.age.value}{tran.area.value}"
                            f"{tran.geo.value}{tran.freq.value}"
                            f"{tran.source.value}]"
                        )
                        output_file.write(metadata)

                        # 5. Write Meaning with :: delimiter [cite: 636]
                        output_file.write(f" :: {de.mean.strip()}\n")

                    except Exception as e:
                        # Error recovery mirroring the 'when others' block 
                        print(f"Exception during entry processing: {e}")
                        output_file.write(f"ERROR: {raw_line[:100].strip()}\n")

            print("Report generation complete.")

        except Exception as e:
            print(f"Fatal error during file processing: {e}")

    def _parse_line_to_entry(self, s: str) -> DictionaryEntry:
        """
        Internal helper mimicking the 'Form_De' local procedure .
        Extracts stems and metadata using Whitaker's fixed-width column logic.
        """
        de = DictionaryEntry()

        # Extract 4 stems [cite: 625-628]
        # logic: S(Start..End) -> s[Start:End+1]
        de.stems[0] = s[START_STEM_1 : START_STEM_1 + MAX_STEM_SIZE]
        de.stems[1] = s[START_STEM_2 : START_STEM_2 + MAX_STEM_SIZE]
        de.stems[2] = s[START_STEM_3 : START_STEM_3 + MAX_STEM_SIZE]
        de.stems[3] = s[START_STEM_4 : START_STEM_4 + MAX_STEM_SIZE]

        # Extract Part, Age, Area, etc. using sequential segment parsing [cite: 629-631]
        # In Ada, IO.Get updates the 'L' offset. We replicate this with segment indices.
        
        # Segment after stems
        remaining = s[START_PART:].strip()
        parts = remaining.split()

        if len(parts) >= 2:
            # First non-blank is POS metadata (handled via assumed sub-IO logic in Whitaker system)
            # Second block contains the 5 single-character flags [cite: 629-631]
            flags = parts[1]
            if len(flags) >= 5:
                de.tran.age = AgeType(flags[0])
                de.tran.area = AreaType(flags[1])
                de.tran.geo = GeoType(flags[2])
                de.tran.freq = FrequencyType(flags[3])
                de.tran.source = SourceType(flags[4])

        # Meaning extraction [cite: 632]
        # Note: Whitaker places meaning at end of line (typically starting around col 111)
        de.mean = StringsPackage.head(s[110:].strip(), MAX_MEANING_SIZE)

        return de

# --- Public API Stub (.pyi equivalent) ---

"""
class DictPageService:
    def __init__(self, input_path: str = "DICTPAGE.IN", output_path: str = "DICTPAGE.OUT"): ...
    def run(self) -> None: ...
"""
