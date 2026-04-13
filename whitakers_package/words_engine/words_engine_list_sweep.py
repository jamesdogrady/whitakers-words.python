from __future__ import annotations
from typing import Final, List, Optional, Tuple
from pydantic import BaseModel, Field, ConfigDict

# --- Dependencies (Imported from previously migrated modules) ---
from .latin_utils.inflections_package import (
    PartOfSpeechType, 
    InflectionRecord, 
    DictionaryKind,
    DictionaryEntry
)
from .latin_utils.dictionary_package import ParseRecord, ParseArray
from .support_utils.word_parameters import WordParametersService as WordsMode

# --- Migration Service ---

class ListSweepService:
    """
    Expert migration of Words_Engine.List_Sweep to Python 3.12+.
    Provides post-parse refinement logic to compress the parse array and 
    normalize specific morphological categories.
    """

    @staticmethod
    def list_sweep(pa: List[ParseRecord], pa_last: int) -> int:
        """
        Implementation of procedure List_Sweep.
        Iterates through the parse results to suppress duplicates and normalize 
        irregular part-of-speech markers.
        
        Args:
            pa: The list of ParseRecords to be swept/compressed.
            pa_last: The current active count of records in the list.
            
        Returns:
            The updated count of valid records (pa_last).
        """
        
        # 1. Morphological Normalization Loop
        for i in range(pa_last):
            pr = pa[i]
            
            # Logic: Destroy the artificial VAR for PRON 1 X
            if (pr.ir.qual.pofs == PartOfSpeechType.PRON and 
                pr.ir.qual.pron.decl.which == 1):
                # Using a dict update or field assignment if Pydantic model allows
                pr.ir.qual.pron.decl.var = 0

            # Logic: Fix V 3 4 to be 4th conjugation
            if pr.ir.qual.pofs == PartOfSpeechType.V:
                if pr.ir.qual.verb.con.which == 3 and pr.ir.qual.verb.con.var == 4:
                    pr.ir.qual.verb.con.which = 4
                    pr.ir.qual.verb.con.var = 1

        # 2. Compression and De-duplication Loop
        j = 0
        opr = None # Old Parse Record
        
        while j < pa_last:
            pr = pa[j]
            
            # Logic: Suppress Key Check and Duplicate Handling
            should_compress = False
            
            if WordsMode.get_flag("Trim_Output"):
                # If we are trimming, check if current record matches previous
                if opr is not None and pr.mnpc == opr.mnpc and pr.d_k == opr.d_k:
                    # Logic for Part-of-Speech specific key matching
                    if pr.ir.qual.pofs in (PartOfSpeechType.V, PartOfSpeechType.VPAR, PartOfSpeechType.SUPINE):
                        if pr.ir.key == opr.ir.key:
                            should_compress = True
                    else:
                        # General equality check for non-verb forms
                        if pr == opr:
                            should_compress = True
                
                # Logic: Suppress duplicate lines (e.g., "ludica")
                elif j + 1 < pa_last:
                    if pa[j] == pa[j + 1]:
                        should_compress = True

            if should_compress:
                # Ada: Pa (J .. Pa_Last - 1) := Pa (J + 1 .. Pa_Last)
                # Replicated via Python list deletion
                pa.pop(j)
                pa_last -= 1
                # Do not increment J, so we re-check the new item at this position
            else:
                opr = pr
                j += 1

        return pa_last

# --- Public API Stub (.pyi equivalent) ---

"""
from typing import List
from .dictionary_package import ParseRecord

class ListSweepService:
    @staticmethod
    def list_sweep(pa: List[ParseRecord], pa_last: int) -> int: ...
"""
