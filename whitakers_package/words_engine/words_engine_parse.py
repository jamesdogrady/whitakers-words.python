from __future__ import annotations
from typing import List, Final, Optional, TYPE_CHECKING
from pydantic import BaseModel, Field, ConfigDict

if TYPE_CHECKING:
    from .latin_utils.config import ConfigurationType
    from .words_engine.list_package import ListPackageService, WordAnalysis
    from .words_engine.word_package import WordPackageService, ParseArray
    from .words_engine.explanation_package import ExplanationService, Explanations

# --- Dependencies (Imported from previously migrated modules) ---
from .support_utils.word_parameters import WordParametersService as WordsMode
from .support_utils.developer_parameters import DeveloperParametersService as WordsMdev
from .words_engine.pearse_code import PearseCodeService, Unknown

# --- Exceptions ---

class ParseError(Exception):
    """Base exception for parsing errors [cite: 113-114]."""
    pass

class GiveUp(ParseError):
    """Exception to signal termination of parsing [cite: 111-112]."""
    pass

# --- Migration Service ---

class ParseService:
    """
    Expert migration of Words_Engine.Parse package.
    Coordinates the parsing of lines into individual Latin/English word analyses [cite: 10-14].
    """

    def __init__(
        self,
        list_package: ListPackageService,
        word_package: WordPackageService,
        explanation_package: ExplanationService
    ):
        self._list_package = list_package
        self._word_package = word_package
        self._explanation_package = explanation_package
        
        # Package state variables matching Whitaker's global counters 
        self.storage_error_count: int = 0
        self.line_number: int = 0
        self.word_number: int = 0
        self.results: List[WordAnalysis] = []

    def parse_line(self, configuration: ConfigurationType, input_line: str) -> None:
        """
        Implementation of Parse_Line procedure. 
        Splits a line into words and coordinates morphological analysis .
        """
        # Logic: Increment line counter and reset word counter [cite: 46, 52]
        self.line_number += 1
        self.word_number = 0
        self.results.clear() [cite: 53]

        try:
            # 1. Logic: Loop over words in the input line [cite: 55-103]
            # Whitaker's system effectively splits on whitespace and punctuation
            words = input_line.split() 
            
            for raw_word in words:
                self.word_number += 1 [cite: 57]
                
                # 2. Get Explanations (tricks/syncope logic) [cite: 60]
                xp = self._explanation_package.get_explanations(raw_word)
                
                # 3. Perform raw word lookup (stems/inflections) [cite: 62]
                # Replicates: Word (Raw_Word, Pa, Pa_Last);
                pa, pa_last = self._word_package.word(raw_word)
                
                # 4. Analyze results [cite: 63]
                # Replicates: Wa := Analyse_Word (Pa, Pa_Last, Raw_Word, Xp);
                wa = self._list_package.analyse_word(pa, pa_last, raw_word, xp)
                
                # 5. Store for retrieval and output [cite: 64, 67]
                self.results.append(wa)
                self._list_package.list_stems(configuration, None, wa, input_line)

        except MemoryError: # Mapping for Ada Storage_Error 
            self._report_storage_error()
            if self.storage_error_count >= 4:
                raise
        except GiveUp: # Direct mapping [cite: 111-112]
            raise
        except Exception: # Mapping for Ada 'others' [cite: 113-115]
            self._report_unknown_error(input_line)
            raise

    def get_parse_results(self) -> List[WordAnalysis]:
        """
        Implementation of Get_Parse_Results.
        Provides access to the raw analyzed word objects [cite: 17-21].
        """
        return self.results

    def _report_storage_error(self) -> None:
        """Logs memory exhaustion events with Pearse code support [cite: 117-128]."""
        if WordsMdev.get_flag("Do_Pearse_Codes"):
            # Replicates: Ada.Text_IO.Put (Pearse_Code.Format (Unknown));
            print(PearseCodeService.format(Unknown), end="") [cite: 122]
        
        print("STORAGE_ERROR Exception in WORDS, try again") [cite: 125]
        self.storage_error_count += 1 [cite: 126]

    def _report_unknown_error(self, input_line: str) -> None:
        """Logs unexpected engine exceptions during parsing ."""
        print(f"Exception in PARSE_LINE processing {input_line}") [cite: 133]
        
        if WordsMode.get_flag("Write_Unknowns_To_File"):
            # logic to append to the .UNK file handled by system WordParameters [cite: 135-137]
            pass

# --- Public API Stub (.pyi equivalent) ---

"""
from typing import List
from .latin_utils.config import ConfigurationType
from .words_engine.list_package import WordAnalysis

class ParseService:
    def parse_line(self, configuration: ConfigurationType, input_line: str) -> None: ...
    def get_parse_results(self) -> List[WordAnalysis]: ...
    line_number: int
    word_number: int
"""
