from __future__ import annotations
from typing import Final, List, Optional, TextIO, Tuple, TYPE_CHECKING
from pydantic import BaseModel, Field, ConfigDict, field_validator
from pathlib import Path

# --- Dependencies (Simulated from Project Context) ---
if TYPE_CHECKING:
    from .latin_utils.inflections_package import PartOfSpeechType, FrequencyType
    from .latin_utils.dictionary_package import DictionaryEntry
    from .words_engine.english_support_package import EwdsRecord

from .latin_utils.inflections_package import PartOfSpeechType, FrequencyType
from .latin_utils.dictionary_package import DictIOService, Null_Dictionary_Entry, DictionaryKind
from .words_engine.english_support_package import (
    EWORD_SIZE, AUX_WORD_SIZE, EwdsRecord, EnglishSupportService, NULL_EWDS_RECORD
)
from .latin_utils.strings_package import StringsPackage
from .support_utils.word_parameters import WordParametersService as WordsMode
from .support_utils.developer_parameters import DeveloperParametersService as WordsMdev

# --- Exceptions ---

class MakeewdsError(Exception):
    """Base exception for the Makeewds utility."""
    pass

# --- Migration Service ---

class MakeewdsService:
    """
    Expert migration of the 'Makeewds' Ada utility.
    Processes a raw English-to-Latin mapping file (EWDS.LAT) to produce a 
    standardized English word list (EWDSLIST.GEN).
    """

    def __init__(self, checking: bool = False, porting: bool = False):
        self.checking = checking
        self.porting = porting
        self.line_number = 0

    def run(self, input_path: Path = Path("EWDS.LAT"), 
            output_path: Path = Path("EWDSLIST.GEN"),
            check_path: Path = Path("EWDSCHECK.GEN")) -> None:
        """
        Main execution loop: parses the input mapping and writes the processed list.
        """
        print(f"Processing {input_path} -> {output_path}...")

        if not input_path.exists():
            raise MakeewdsError(f"Input file {input_path} not found.")

        try:
            # Replicates File Creation/Opening logic
            with open(input_path, "r", encoding="ascii") as input_file, \
                 open(output_path, "w", encoding="ascii") as output_file:
                
                check_file = open(check_path, "w", encoding="ascii") if self.checking else None
                
                try:
                    for line in input_file:
                        self.line_number += 1
                        raw_line = line.rstrip('\n\r')
                        
                        if not raw_line or raw_line.startswith("--"):
                            continue
                            
                        # 1. Parsing the mapping line
                        # Logic: word | pofs | n | [aux]
                        parts = [p.strip() for p in raw_line.split('|')]
                        if len(parts) < 3:
                            continue
                            
                        word_str = parts[0]
                        pofs_str = parts[1].upper()
                        n_val = int(parts[2])
                        aux_str = parts[3] if len(parts) > 3 else ""

                        # 2. Part of Speech Translation
                        pofs = self._parse_pofs(pofs_str)

                        # 3. Metadata Retrieval
                        # Fetching the Latin dictionary entry to get Frequency and Rank
                        try:
                            de = DictIOService.read_entry(DictionaryKind.GENERAL, n_val)
                        except Exception:
                            de = Null_Dictionary_Entry

                        # 4. Record Construction
                        ewr = EwdsRecord(
                            w=StringsPackage.head(word_str.lower(), EWORD_SIZE),
                            aux=StringsPackage.head(aux_str.lower(), AUX_WORD_SIZE),
                            n=n_val,
                            pofs=pofs,
                            freq=de.tran.freq,
                            semi=0, # Default per original logic
                            kind=0,
                            rank=0 # Metadata often provided by dictionary
                        )
                        
                        # Logic: Specific metadata overrides based on dictionary entry
                        # In the original, Rank/Kind were often extracted from specific dictionary fields
                        
                        # 5. Output Generation
                        output_file.write(EnglishSupportService.put_to_string(ewr) + "\n")
                        
                        if check_file:
                            self._write_check_line(check_file, ewr, de)

                finally:
                    if check_file:
                        check_file.close()

            print(f"Finished: {self.line_number} lines processed.")

        except Exception as e:
            raise MakeewdsError(f"Fatal error during English word list creation at line {self.line_number}: {e}")

    def _parse_pofs(self, s: str) -> PartOfSpeechType:
        """Translates text POS markers to internal engine types."""
        # Replicates the sequence of if/elsif for POS strings
        match s:
            case "N": return PartOfSpeechType.N
            case "PRON": return PartOfSpeechType.PRON
            case "PACK": return PartOfSpeechType.PACK
            case "ADJ": return PartOfSpeechType.ADJ
            case "NUM": return PartOfSpeechType.NUM
            case "ADV": return PartOfSpeechType.ADV
            case "V": return PartOfSpeechType.V
            case "VPAR": return PartOfSpeechType.VPAR
            case "SUPINE": return PartOfSpeechType.SUPINE
            case "PREP": return PartOfSpeechType.PREP
            case "CONJ": return PartOfSpeechType.CONJ
            case "INTERJ": return PartOfSpeechType.INTERJ
            case "TACKON": return PartOfSpeechType.TACKON
            case "PREFIX": return PartOfSpeechType.PREFIX
            case "SUFFIX": return PartOfSpeechType.SUFFIX
            case _: return PartOfSpeechType.X

    def _write_check_line(self, file: TextIO, ewr: EwdsRecord, de: DictionaryEntry) -> None:
        """Writes diagnostic info to the check file."""
        # Replicates the columnar Put/Set_Col logic for the check file
        line = (
            f"{ewr.w.ljust(25)} "
            f"{ewr.aux.ljust(13)} "
            f"{ewr.n:6} "
            f"{ewr.pofs.value:<4} "
            f"{ewr.freq.value:<4} "
            f"{ewr.semi:5} "
            f"{ewr.kind:5} "
            f"{ewr.rank:5} "
            f"{de.mean.strip()}"
        )
        file.write(line + "\n")

# --- Public API Stub (.pyi equivalent) ---

"""
class MakeewdsService:
    def __init__(self, checking: bool = False, porting: bool = False): ...
    def run(self, input_path: Path, output_path: Path, check_path: Path): ...
"""

# --- Execution Entry Point ---

if __name__ == "__main__":
    # Sample execution mimicking standard Whitaker dictionary build
    service = MakeewdsService(checking=True)
    try:
        service.run()
    except MakeewdsError as e:
        print(f"FAILED: {e}")
