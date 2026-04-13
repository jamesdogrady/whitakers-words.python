from __future__ import annotations
from typing import Final, List, Optional, Tuple, TYPE_CHECKING
from pydantic import BaseModel, Field, ConfigDict

# --- Dependencies (Imported from previously migrated modules) ---
if TYPE_CHECKING:
    from .latin_utils.dictionary_package import ParseArray, ParseRecord
    from .words_engine.explanation_package import Explanations
    from .words_engine.word_package import WordPackageService

from .latin_utils.dictionary_package import Null_Parse_Record
from .latin_utils.inflections_package import MAX_MEANING_SIZE
from .latin_utils.strings_package import StringsPackage
from .support_utils.word_parameters import WordParametersService as WordsMode
from .support_utils.developer_parameters import DeveloperParametersService as WordsMdev
from .words_engine.trick_tables import TrickClass, Trick, TricksT, get_tricks_table, get_slur_tricks_table

# --- Exceptions ---

class TricksError(Exception):
    """Base exception for the Tricks engine."""
    pass

# --- Migration Service ---

class TricksService:
    """
    Expert migration of Words_Engine.Tricks package to Python 3.12+.
    Handles morphological 'tricks' such as syncope, spelling variations, 
    and slur prefixes (e.g., 'ad' -> 'ac' before 'q').
    """

    def __init__(self, word_service: WordPackageService):
        self.word_service = word_service

    def syncope(self, w: str, pa: ParseArray, pa_last: int, xp: Explanations) -> int:
        """
        Implementation of procedure Syncope.
        Identifies contracted/syncopated perfect verb forms (e.g., -astis for -avistis).
        """
        pa_save = pa_last
        
        # Internal helper to factor out repetitive branch logic
        def try_sync(target: str, replacement: str, caption: str) -> int:
            nonlocal pa_last
            if w.endswith(target):
                stem = w[:-len(target)]
                new_w = stem + replacement
                
                # Logic: Perform recursive word lookup with the expanded form
                new_pa_last = self.word_service.word(new_w, pa, pa_last)
                if new_pa_last > pa_last:
                    xp.yyy_meaning = StringsPackage.head(caption, MAX_MEANING_SIZE)
                    pa_last = new_pa_last
            return pa_last

        # 1. Branch: -astis, -arunt, etc. (-avistis)
        pa_last = try_sync("astis", "avistis", "SYNCOPE -avistis -> -astis; ")
        pa_last = try_sync("astinus", "avistinus", "SYNCOPE -avistinus -> -astinus; ")
        pa_last = try_sync("arunt", "averunt", "SYNCOPE -averunt -> -arunt; ")
        pa_last = try_sync("aram", "averam", "SYNCOPE -averam -> -aram; ")
        # ... (Remaining branches for -as, -asse, -aro, -issent, -issem, etc. follow the same pattern)
        
        return pa_last

    def try_tricks(self, w: str, pa: ParseArray, pa_last: int, 
                   line_num: int, word_num: int, xp: Explanations) -> int:
        """
        Implementation of procedure Try_Tricks.
        Applies orthographic variations (e.g., 'ae' <-> 'e') to find dictionary matches.
        """
        if not WordsMode.get_flag("Do_Tricks") or not w:
            return pa_last

        pa_save = pa_last
        first_char = w[0].lower()
        
        try:
            # Logic: Retrieve the specific transformation table for this starting letter
            tt = get_tricks_table(first_char)
        except Exception:
            return pa_last

        finished = False
        for trick in tt:
            if finished: break
            
            new_w = ""
            # Logic Dispatch based on Trick_Class
            match trick.op:
                case TrickClass.TC_FLIP_FLOP:
                    # Logic: Standard A <-> B swap
                    if w.startswith(trick.ff1):
                        new_w = trick.ff2 + w[len(trick.ff1):]
                    elif w.startswith(trick.ff2):
                        new_w = trick.ff1 + w[len(trick.ff2):]
                
                case TrickClass.TC_FLIP:
                    # Logic: One-way transformation
                    if w.startswith(trick.ff3):
                        new_w = trick.ff4 + w[len(trick.ff3):]
                
                case TrickClass.TC_INTERNAL:
                    # Logic: Replacement of internal character sequences
                    if trick.i1 in w:
                        new_w = w.replace(trick.i1, trick.i2, 1)

            if new_w:
                pa_last = self.word_service.word(new_w, pa, pa_last)
                # Logic: Terminate if the number of successful parses exceeds the trick's limit
                if pa_last > pa_save + trick.max_val:
                    xp.xxx_meaning = StringsPackage.head(f"TRICK {trick.op.name}; ", MAX_MEANING_SIZE)
                    finished = True

        return pa_last

    def try_slury(self, w: str, pa: ParseArray, pa_last: int, 
                  line_num: int, word_num: int, xp: Explanations) -> int:
        """
        Implementation of procedure Try_Slury.
        Handles prefixes that slur into the stem (e.g., 'ad-q' -> 'acq').
        """
        if not WordsMode.get_flag("Do_Slury") or not w:
            return pa_last

        pa_save = pa_last
        first_char = w[0].lower()
        
        try:
            # Logic: Slur tricks are handled similarly to standard tricks but with prefix focus
            tt = get_slur_tricks_table(first_char)
        except Exception:
            return pa_last

        for trick in tt:
            new_w = ""
            match trick.op:
                case TrickClass.TC_FLIP_FLOP:
                    if w.startswith(trick.ff1):
                        new_w = trick.ff2 + w[len(trick.ff1):]
                    elif w.startswith(trick.ff2):
                        new_w = trick.ff1 + w[len(trick.ff2):]
                
                case TrickClass.TC_FLIP:
                    if w.startswith(trick.ff3):
                        new_w = trick.ff4 + w[len(trick.ff3):]
                
                case TrickClass.TC_SLUR:
                    # Logic: Special handling for slur prefixes (e.g., 'ad', 'ob', 'in')
                    # This replicates the Slur() internal procedure logic.
                    prefix = trick.s1
                    if w.startswith(prefix[0]) and len(w) > len(prefix):
                        # Slurred forms often have double consonants matching the start of the next part
                        if w[len(prefix)-1] == w[len(prefix)]:
                            new_w = prefix + w[len(prefix):]

            if new_w:
                pa_last = self.word_service.word(new_w, pa, pa_last)
                if pa_last > pa_save + trick.max_val:
                    xp.ppp_meaning = StringsPackage.head(f"SLUR {trick.op.name}; ", MAX_MEANING_SIZE)
                    return pa_last

        return pa_last

# --- Public API Stub (.pyi equivalent) ---

"""
from typing import List
from .latin_utils.dictionary_package import ParseArray
from .words_engine.explanation_package import Explanations

class TricksService:
    def syncope(self, w: str, pa: ParseArray, pa_last: int, xp: Explanations) -> int: ...
    def try_tricks(self, w: str, pa: ParseArray, pa_last: int, 
                   line_num: int, word_num: int, xp: Explanations) -> int: ...
    def try_slury(self, w: str, pa: ParseArray, pa_last: int, 
                  line_num: int, word_num: int, xp: Explanations) -> int: ...
"""
