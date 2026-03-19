from __future__ import annotations
from typing import Final, Dict, Optional, TextIO
from pydantic import BaseModel, Field, ConfigDict
from pathlib import Path

# --- Dependencies (Imported from previously migrated modules) ---
from .latin_utils.inflections_package import (
    DictionaryEntry,
    AgeType,
    AreaType,
    GeoType,
    FrequencyType,
    SourceType,
    MAX_STEM_SIZE,
    MAX_MEANING_SIZE
)
from .latin_utils.strings_package import StringsPackage

# --- Exceptions ---

class DictFlagError(Exception):
    """Base exception for the DictFlag utility."""
    pass

# --- Migration Service ---

class DictFlagService:
    """
    Expert migration of the DictFlag Ada utility to Python 3.12+.
    Analyzes a dictionary file and aggregates statistics for metadata flags 
    (Age, Area, Geo, Frequency, Source).
    """

    def __init__(self, input_path: str = "DICTLINE.GEN", output_path: str = "DICTFLAG.OUT"):
        self.input_path = Path(input_path)
        self.output_path = Path(output_path)
        
        # Statistics Arrays (Dictionaries for O(1) lookup by Enum)
        self.age_counts: Dict[AgeType, int] = {t: 0 for t in AgeType}
        self.area_counts: Dict[AreaType, int] = {t: 0 for t in AreaType}
        self.geo_counts: Dict[GeoType, int] = {t: 0 for t in GeoType}
        self.freq_counts: Dict[FrequencyType, int] = {t: 0 for t in FrequencyType}
        self.source_counts: Dict[SourceType, int] = {t: 0 for t in SourceType}

    def run(self) -> None:
        """
        Main execution logic: parses the dictionary and generates the report.
        """
        if not self.input_path.exists():
            print(f"Error: {self.input_path} not found.")
            return

        print(f"Analyzing {self.input_path}...")
        
        try:
            with open(self.input_path, "r") as f:
                for line in f:
                    # Logic: Skips comments or empty lines
                    if not line.strip() or line.startswith("--"):
                        continue
                    
                    try:
                        # 1. Parse the entry (Simulating Dictionary_Entry_IO behavior)
                        # In Whitaker's format, metadata is stored in the Translation Record block
                        # typically located after the stems and part of speech metadata.
                        entry = self._parse_entry_metadata(line)
                        
                        # 2. Increment counters
                        tran = entry.tran
                        self.age_counts[tran.age] += 1
                        self.area_counts[tran.area] += 1
                        self.geo_counts[tran.geo] += 1
                        self.freq_counts[tran.freq] += 1
                        self.source_counts[tran.source] += 1
                        
                    except (ValueError, KeyError, IndexError):
                        # Skip malformed lines as per Whitaker's robust parser design
                        continue

            self._generate_report()
            print(f"Statistics written to {self.output_path}")

        except Exception as e:
            raise DictFlagError(f"Fatal error during dictionary analysis: {e}")

    def _parse_entry_metadata(self, line: str) -> DictionaryEntry:
        """
        Internal helper to extract metadata flags from a fixed-width DICTLINE.
        Logic matches the column offsets used in Whitaker's IO packages.
        """
        # Whitaker's DICTLINE format:
        # Stems (4 * 19) + POS (varies) + Flags (Age Area Geo Freq Source)
        # Based on previous migrations, the flags start at offset 102.
        flags_segment = line[102:110].strip().split()
        
        # This is a simplified extraction for the statistics tool logic
        # In a full system, this would call the specific IO Service.
        entry = DictionaryEntry()
        if len(flags_segment) >= 5:
            entry.tran.age = AgeType(flags_segment[0])
            entry.tran.area = AreaType(flags_segment[1])
            entry.tran.geo = GeoType(flags_segment[2])
            entry.tran.freq = FrequencyType(flags_segment[3])
            entry.tran.source = SourceType(flags_segment[4])
        
        return entry

    def _generate_report(self) -> None:
        """
        Serializes the aggregated statistics into a formatted report.
        """
        with open(self.output_path, "w") as out:
            out.write("LATIN DICTIONARY METADATA STATISTICS\n")
            out.write("====================================\n\n")

            self._write_section(out, "AGE", self.age_counts)
            self._write_section(out, "AREA", self.area_counts)
            self._write_section(out, "GEO", self.geo_counts)
            self._write_section(out, "FREQUENCY", self.freq_counts)
            self._write_section(out, "SOURCE", self.source_counts)

    def _write_section(self, file: TextIO, title: str, counts: Dict[Any, int]) -> None:
        """Replicates Ada's Set_Col and New_Line logic for report formatting."""
        file.write(f"\n{title}\n")
        file.write("-" * len(title) + "\n")
        for key, count in counts.items():
            # Matches Ada's Text_IO format: Enum_Name (Col 1) and Count (Col 10)
            file.write(f"{key.name:<10} {count:>8}\n")

# --- Execution ---

if __name__ == "__main__":
    service = DictFlagService()
    service.run()
