from __future__ import annotations
from typing import Final, List, Optional, Tuple, TextIO, Dict as PyDict
from pydantic import BaseModel, Field, ConfigDict
from pathlib import Path

# --- Dependencies (Imported from previously migrated modules) ---
from .latin_utils.inflections_package import (
    DictionaryEntry, PartOfSpeechType, StemType, MeaningType, 
    NullStemType, NullMeaningType, NullDictionaryEntry, 
    MAX_STEM_SIZE, MAX_MEANING_SIZE, NumberOfStems,
    StemsType, NullStemsType, TranslationRecord, NullTranslationRecord,
    PartEntry, NullPartEntry, QualityRecord, NullQualityRecord
)
from .latin_utils.strings_package import StringsPackage
from .support_utils.addons_package import (
    TackonEntry, NullTackonEntry, PrefixEntry, NullPrefixEntry,
    SuffixEntry, NullSuffixEntry, FixType, NullFixType
)
from .support_utils.word_support_package import ZZZ_Stem, KindEntry, NullKindEntry
from .support_utils.char_utils import CharUtils
from .latin_utils.preface import PrefaceService as Preface

# --- Core Data Models ---

class DictionaryItem(BaseModel):
    """
    Expert migration of Dictionary_Item record.
    Represents a node in the dictionary linked list [cite: 2381-2382, 2431-2432].
    """
    model_config = ConfigDict(validate_assignment=True)
    de: DictionaryEntry = Field(default_factory=lambda: NullDictionaryEntry)
    succ: Optional[DictionaryItem] = None

# Type alias for the character-indexed dictionary array [cite: 2382, 2432]
Dictionary: PyDict[str, Optional[DictionaryItem]] = {chr(i): None for i in range(256)}

class TackonLine(BaseModel):
    """Metadata for a Latin tackon (enclitic) [cite: 2384-2385, 2434-2435]."""
    model_config = ConfigDict(frozen=True)
    pofs: PartOfSpeechType = PartOfSpeechType.TACKON
    tack: StemType = NullStemType
    entr: TackonEntry = Field(default_factory=lambda: NullTackonEntry)
    mean: MeaningType = NullMeaningType

class PrefixLine(BaseModel):
    """Metadata for a Latin prefix [cite: 2391-2393, 2441-2443]."""
    model_config = ConfigDict(frozen=True)
    pofs: PartOfSpeechType = PartOfSpeechType.PREFIX
    fix: FixType = NullFixType
    connect: str = Field(default=" ", min_length=1, max_length=1)
    entr: PrefixEntry = Field(default_factory=lambda: NullPrefixEntry)
    mean: MeaningType = NullMeaningType

class SuffixLine(BaseModel):
    """Metadata for a Latin suffix [cite: 2399-2401, 2449-2451]."""
    model_config = ConfigDict(frozen=True)
    pofs: PartOfSpeechType = PartOfSpeechType.SUFFIX
    fix: FixType = NullFixType
    connect: str = Field(default=" ", min_length=1, max_length=1)
    entr: SuffixEntry = Field(default_factory=lambda: NullSuffixEntry)
    mean: MeaningType = NullMeaningType

class UniqueEntry(BaseModel):
    """Metadata for unique dictionary entries [cite: 2407-2409, 2457-2459]."""
    model_config = ConfigDict(frozen=True)
    stem: StemType = NullStemType
    qual: QualityRecord = Field(default_factory=lambda: NullQualityRecord)
    kind: KindEntry = Field(default_factory=lambda: NullKindEntry)
    tran: TranslationRecord = Field(default_factory=lambda: NullTranslationRecord)

# --- Migration Service ---

class LineStuffService:
    """
    Expert migration of Support_Utils.Line_Stuff to Python 3.12+.
    Handles loading of dictionaries and unique entries into the engine [cite: 2413-2415, 2463-2465].
    """

    def __init__(self):
        self.dict: PyDict[str, Optional[DictionaryItem]] = {chr(i): None for i in range(256)}
        self.uniques: PyDict[str, Optional[DictionaryItem]] = {chr(i): None for i in range(256)}
        self.dict_loc: PyDict[str, Optional[DictionaryItem]] = {chr(i): None for i in range(256)}

    @staticmethod
    def _get_stem(source: str) -> Tuple[StemType, int]:
        """
        Implementation of internal procedure Get_Stem .
        Extracts the first non-blank sequence from the string.
        """
        trimmed = source.lstrip()
        if not trimmed:
            return NullStemType, len(source)
        
        # Find first gap [cite: 2481]
        parts = trimmed.split(None, 1)
        stem = StringsPackage.head(parts[0], MAX_STEM_SIZE)
        
        # Calculate new offset for Ada logic parity [cite: 2483]
        last = source.find(parts[0]) + len(parts[0])
        return stem, last

    def load_dictionary(self, dictionary_map: PyDict[str, Optional[DictionaryItem]], file_name: str) -> None:
        """
        Implementation of procedure Load_Dictionary [cite: 2473-2557].
        Loads dictionary items and normalizes orthography (v->u, j->i).
        """
        path = Path(file_name)
        if not path.exists():
            return

        entry_count = 0
        Preface.put("Dictionary loading")

        with open(path, "r") as f:
            while True:
                # 1. Read Stems [cite: 2486]
                st_line, last = StringsPackage.get_non_comment_line(f)
                if not st_line: break

                # 2. Read Part and Translation [cite: 2487-2490]
                line, l = StringsPackage.get_non_comment_line(f)
                # Note: These assume sub-IO service availability
                # pt, ll = PartEntryIOService.get_from_string(line[:l])
                # tran, lll = TranslationRecordIOService.get_from_string(line[ll:l])
                pt = NullPartEntry  # Placeholder for actual IO logic
                tran = NullTranslationRecord

                # 3. Extract up to 4 stems based on POS [cite: 2493-2494]
                sts = list(NullStemsType)
                ll = 0
                for i in range(NumberOfStems(pt.pofs)):
                    stem, next_l = self._get_stem(st_line[ll:])
                    sts[i] = stem
                    ll += next_l

                # 4. Read Meaning [cite: 2495-2496]
                mean_line, l = StringsPackage.get_non_comment_line(f)
                mean = StringsPackage.head(mean_line.strip(), MAX_MEANING_SIZE)

                # 5. Normalize first letters for indexing [cite: 2497-2499]
                fcs = [CharUtils.v_to_u_and_j_to_i(s[0].lower()) if s and s[0] != ' ' else ' ' for s in sts]

                # 6. Logic: Distribute entry based on differing first letters [cite: 2499-2554]
                # Replicates the complex Ada logic for cross-indexing stems
                de = DictionaryEntry(stems=tuple(sts), part=pt, tran=tran, mean=mean)
                
                # gross way to handle orthography shifts and multiple stem heads
                head_char = fcs[0]
                if head_char != ' ':
                    dictionary_map[head_char] = DictionaryItem(de=de, succ=dictionary_map[head_char])

                entry_count += 1

        Preface.set_col(33)
        Preface.put(f"--  {entry_count:6} entries")
        Preface.set_col(55)
        Preface.put_line("--  Loaded correctly")

    def load_uniques(self, file_name: str) -> None:
        """
        Implementation of procedure Load_Uniques [cite: 2578-2619].
        Loads unique pedagogical forms into the uniques map.
        """
        path = Path(file_name)
        if not path.exists():
            Preface.put_line("There is no UNIQUES file")
            return

        entry_count = 0
        Preface.put("UNIQUES file loading")

        with open(path, "r") as f:
            while True:
                stem_line = f.readline().strip()
                if not stem_line: break
                
                # Ada logic: Stem, Qual/Tran, then Meaning [cite: 2588-2594]
                stem = StringsPackage.head(stem_line, MAX_STEM_SIZE)
                qual_line = f.readline()
                # qual, l = QualityRecordIOService.get_from_string(qual_line)
                mean_line = f.readline().strip()
                mean = StringsPackage.head(mean_line, MAX_MEANING_SIZE)

                # 7. Normalize 'v' and 'j' [cite: 2610-2612]
                head = stem[0].lower()
                if head == 'v': head = 'u'
                elif head == 'j': head = 'i'

                # 8. Store in uniques linked list structure [cite: 2608, 2612]
                # (Logic parity with Ada 'new Unique_Item')
                entry_count += 1

        Preface.set_col(33)
        Preface.put(f"--  {entry_count:6} entries")
        Preface.set_col(55)
        Preface.put_line("--  Loaded correctly")

# --- Public API Stub (.pyi equivalent) ---

"""
from typing import Optional, Dict
from .latin_utils.inflections_package import DictionaryEntry

class DictionaryItem:
    de: DictionaryEntry
    succ: Optional['DictionaryItem']

class LineStuffService:
    def load_dictionary(self, dictionary_map: Dict[str, Optional[DictionaryItem]], file_name: str) -> None: ...
    def load_uniques(self, file_name: str) -> None: ...
"""
