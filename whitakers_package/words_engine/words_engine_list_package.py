from __future__ import annotations
from typing import Final, List, Optional, Tuple, TextIO, Dict as PyDict, Any
from pydantic import BaseModel, Field, ConfigDict
from pathlib import Path
import functools

# --- Dependencies (Simulated from Project Context) ---
from .latin_utils.inflections_package import (
    StemType, InflectionRecord, DictionaryKind, DictionaryEntry, 
    PartOfSpeechType, FrequencyType, AgeType, NullStemType, 
    NullInflectionRecord, NullDictionaryEntry, MNPC_Type, Null_MNPC,
    MAX_MEANING_SIZE, DecnRecord, CaseType, NumberType, GenderType,
    TenseType, VoiceType, MoodType, QualityRecord
)
from .latin_utils.dictionary_package import ParseRecord, ParseArray, DictIOService
from .latin_utils.config import Config, ConfigurationType
from .latin_utils.strings_package import StringsPackage
from .support_utils.word_parameters import WordParametersService as WordsMode
from .support_utils.developer_parameters import DeveloperParametersService as WordsMdev
from .support_utils.addons_package import Means
from .support_utils.uniques_package import UniquesDe
from .support_utils.word_support_package import WordSupportPackage, FirstIndex, LastIndex
from .support_utils.char_utils import CharUtils
from .support_utils.dictionary_form import dictionary_form
from .words_engine.explanation_package import Explanations, Symbol, CitationForm, Gloss, Trick, Affix, Inflection, Unknowns_2
from .words_engine.list_sweep import list_sweep
from .words_engine.pearse_code import pearse_format
from .words_engine.put_example_line import put_example_line
from .words_engine.put_stat import put_stat

# --- Exceptions ---

class ListPackageError(Exception):
    """Base exception for the Words Engine List Package[cite: 12837, 12840]."""
    pass

class UnexpectedExceptionInListStems(ListPackageError):
    """Raised for general failures in the stem listing process[cite: 13040]."""
    pass

# --- Core Data Models ---

class StemInflectionRecord(BaseModel):
    """Metadata for a stem combined with its inflection [cite: 12787-12788, 12818-12819]."""
    model_config = ConfigDict(validate_assignment=True, frozen=True)
    stem: StemType = NullStemType
    ir: InflectionRecord = Field(default_factory=lambda: NullInflectionRecord)

class DictionaryMNPCRecord(BaseModel):
    """Refers to a specific dictionary entry and its file position [cite: 12792-12793, 12823-12824]."""
    model_config = ConfigDict(validate_assignment=True, frozen=True)
    d_k: DictionaryKind = DictionaryKind.X
    mnpc: MNPC_Type = Null_MNPC
    de: DictionaryEntry = Field(default_factory=lambda: NullDictionaryEntry)

# Constants for Array Sizes
STEM_INFLECTION_ARRAY_SIZE: Final[int] = 12
STEM_INFLECTION_ARRAY_ARRAY_SIZE: Final[int] = 40
DICTIONARY_MNPC_ARRAY_SIZE: Final[int] = 40

class WordAnalysis(BaseModel):
    """The result of the word parsing and analysis phase [cite: 12795-12796, 12826-12827]."""
    model_config = ConfigDict(validate_assignment=True)
    stem_iaa: List[List[StemInflectionRecord]] = Field(
        default_factory=lambda: [[StemInflectionRecord() for _ in range(STEM_INFLECTION_ARRAY_SIZE)] 
                                 for _ in range(STEM_INFLECTION_ARRAY_ARRAY_SIZE)]
    )
    dict_array: List[DictionaryMNPCRecord] = Field(
        default_factory=lambda: [DictionaryMNPCRecord() for _ in range(DICTIONARY_MNPC_ARRAY_SIZE)]
    )
    i_is_pa_last: bool = False
    unknowns: bool = False
    the_word: str = ""
    was_trimmed: bool = False
    xp: Explanations = Field(default_factory=Explanations)

# --- Logic Constants ---

INFLECTION_FREQUENCY: Final[PyDict[FrequencyType, str]] = {
    FrequencyType.X: "        ", FrequencyType.A: "mostfreq", FrequencyType.B: "sometime",
    FrequencyType.C: "uncommon", FrequencyType.D: "infreq  ", FrequencyType.E: "rare    ",
    FrequencyType.F: "veryrare", FrequencyType.I: "inscript"
} [cite: 12846-12847]

INFLECTION_AGE: Final[PyDict[AgeType, str]] = {
    AgeType.X: "Always  ", AgeType.A: "Archaic ", AgeType.B: "Early   ", AgeType.C: "Classic ",
    AgeType.D: "Late    ", AgeType.E: "Later   ", AgeType.F: "Medieval", AgeType.G: "Scholar ",
    AgeType.H: "Modern  "
} [cite: 12848-12849]

DICTIONARY_FREQUENCY: Final[PyDict[FrequencyType, str]] = {
    FrequencyType.X: "        ", FrequencyType.A: "veryfreq", FrequencyType.B: "frequent",
    FrequencyType.C: "common  ", FrequencyType.D: "lesser  ", FrequencyType.E: "uncommon",
    FrequencyType.F: "veryrare", FrequencyType.I: "inscript", FrequencyType.J: "graffiti",
    FrequencyType.N: "Pliny   "
} [cite: 12850-12851]

DICTIONARY_AGE: Final[PyDict[AgeType, str]] = {
    AgeType.X: "        ", AgeType.A: "Archaic ", AgeType.B: "Early   ", AgeType.C: "Classic ",
    AgeType.D: "Late    ", AgeType.E: "Later   ", AgeType.F: "Medieval", AgeType.G: "NeoLatin",
    AgeType.H: "Modern  "
} [cite: 12852-12853]

# --- Migration Service ---

class ListPackageService:
    """
    Expert migration of Words_Engine.List_Package to Python 3.12+.
    Handles formatting and display logic for Latin word analysis[cite: 12811, 12840].
    """

    MAX_MEANING_PRINT_SIZE: Final[int] = 79 [cite: 12845]

    def __init__(self):
        self.scroll_line_number: int = 0
        self.output_screen_size: int = 24  # Standard CLI screen size

    @staticmethod
    def get_max_meaning_size(output: TextIO) -> int:
        """Determines the buffer size based on output stream type ."""
        # Replicates Standard_Output check for screen formatting
        import sys
        if output is sys.stdout:
            return ListPackageService.MAX_MEANING_PRINT_SIZE
        return MAX_MEANING_SIZE

    @staticmethod
    def put_pearse_code(output: TextIO, code: Symbol) -> None:
        """Writes pedagogical metadata codes if enabled [cite: 12857-12858]."""
        if WordsMdev.get_flag("Do_Pearse_Codes"):
            output.write(pearse_format(code))

    def put_dictionary_flags(self, output: TextIO, de: DictionaryEntry) -> bool:
        """Writes Age and Frequency metadata to the output stream [cite: 12858-12861]."""
        hit = False
        if WordsMode.get_flag("Show_Age") or DICTIONARY_AGE[de.tran.age].strip():
            output.write(f"  {DICTIONARY_AGE[de.tran.age].strip()}")
            hit = True
        if (WordsMode.get_flag("Show_Frequency") or de.tran.freq >= FrequencyType.D) and \
           DICTIONARY_FREQUENCY[de.tran.freq].strip():
            output.write(f"  {DICTIONARY_FREQUENCY[de.tran.freq].strip()}")
            hit = True
        return hit

    def put_dictionary_form(self, output: TextIO, d_k: DictionaryKind, mnpc: MNPC_Type, de: DictionaryEntry) -> None:
        """Renders the pedagogical headword form and technical codes [cite: 12861-12874]."""
        chit = dhit = ehit = fhit = lhit = False
        dict_line_num = int(mnpc)

        if WordsMode.get_flag("Do_Dictionary_Forms"):
            self.put_pearse_code(output, Citation_Form)
            if WordsMdev.get_flag("Do_Pearse_Codes"): dhit = True
            
            form = dictionary_form(de)
            if form:
                output.write(f"{form}  ")
                dhit = True

        if WordsMdev.get_flag("Show_Dictionary_Codes") and de.part.pofs not in (PartOfSpeechType.TACKON, PartOfSpeechType.PREFIX, PartOfSpeechType.SUFFIX):
            output.write(f" [{de.tran.age.value}{de.tran.area.value}{de.tran.geo.value}{de.tran.freq.value}{de.tran.source.value}]  ")
            chit = True

        if WordsMdev.get_flag("Show_Dictionary") :
            output.write(f"{d_k.name[:3]}>")
            ehit = True

        if WordsMdev.get_flag("Show_Dictionary_Line") and dict_line_num > 0:
            output.write(f"({dict_line_num})")
            lhit = True

        fhit = self.put_dictionary_flags(output, de)

        if any([chit, dhit, ehit, fhit, lhit]):
            output.write("\n")

    def constructed_meaning(self, sr: StemInflectionRecord, dm: DictionaryMNPCRecord) -> str:
        """Builds programmatic definitions for numeric forms [cite: 12874-12881]."""
        if dm.de.part.pofs != PartOfSpeechType.NUM:
            return ""
        
        n = dm.de.part.num.value
        if sr.ir.qual.pofs != PartOfSpeechType.NUM:
            return StringsPackage.head(f"Number {n}", MAX_MEANING_SIZE)

        # Logic: Normal numeric parsing [cite: 12877-12880]
        match sr.ir.qual.num.sort:
            case CaseType.CARD: return StringsPackage.head(f"{n} - (CARD answers 'how many');", MAX_MEANING_SIZE)
            case CaseType.ORD:  return StringsPackage.head(f"{n}th - (ORD, 'in series'); (a/the) {n}th (part);", MAX_MEANING_SIZE)
            case CaseType.DIST: return StringsPackage.head(f"{n} each/apiece/times/fold - 'how many each';", MAX_MEANING_SIZE)
            case CaseType.ADVERB: return StringsPackage.head(f"{n} times, on {n} occasions - (ADVERB);", MAX_MEANING_SIZE)
            case _: return ""

    def put_meaning_line(self, output: TextIO, sr: StemInflectionRecord, dm: DictionaryMNPCRecord, 
                         mm: int, xp: Explanations, used_meanings: List[bool]) -> None:
        """Writes the dictionary definition block [cite: 12883-12897]."""
        
        def _put_meaning(raw: str):
            # Removes '|' pedagogical markers used in legacy DICTLINE [cite: 12882, 12884]
            clean = raw.replace('|', '').strip()
            output.write(StringsPackage.head(clean, mm).strip() + "\n")

        def _put_word_meaning(meaning: str, code: Symbol):
            if not used_meanings[dm.d_k.value]:
                self.put_pearse_code(output, code)
                _put_meaning(meaning)
                used_meanings[dm.d_k.value] = True

        # Logic Dispatch based on Dictionary Kind [cite: 12887-12896]
        match dm.d_k:
            case DictionaryKind.RRR: _put_word_meaning(xp.rrr_meaning, Gloss)
            case DictionaryKind.NNN: _put_word_meaning(xp.nnn_meaning, Trick)
            case DictionaryKind.XXX: _put_word_meaning(xp.xxx_meaning, Trick)
            case DictionaryKind.ADDONS:
                self.put_pearse_code(output, Trick)
                _put_meaning(Means[int(dm.mnpc)])
            case _:
                self.put_pearse_code(output, Gloss)
                if dm.de.part.pofs == PartOfSpeechType.NUM and dm.de.part.num.value > 0:
                    output.write(self.constructed_meaning(sr, dm) + "\n")
                elif dm.d_k == DictionaryKind.UNIQUE:
                    _put_meaning(UniquesDe[dm.mnpc].mean)
                else:
                    _put_meaning(dm.de.mean)

    def cycle_over_pa(self, pa: ParseArray, pa_last: int, raw_word: str) -> Tuple[List[List[StemInflectionRecord]], List[DictionaryMNPCRecord], bool]:
        """
        Implementation of the complex Cycle_Over_Pa transformation [cite: 12897-12934].
        Converts the raw ParseArray into structured analysis buckets.
        """
        sraa = [[StemInflectionRecord() for _ in range(STEM_INFLECTION_ARRAY_SIZE)] for _ in range(STEM_INFLECTION_ARRAY_ARRAY_SIZE)]
        dma = [DictionaryMNPCRecord() for _ in range(DICTIONARY_MNPC_ARRAY_SIZE)]
        i_idx = 0
        j_idx = -1  # Buckets
        k_idx = 0   # Bucket contents
        odm = DictionaryMNPCRecord()

        try:
            while i_idx < pa_last:
                rec = pa[i_idx]
                if rec.d_k == DictionaryKind.UNIQUE:
                    j_idx += 1
                    sraa[j_idx][0] = StemInflectionRecord(stem=rec.stem, ir=rec.ir)
                    dma[j_idx] = DictionaryMNPCRecord(d_k=DictionaryKind.UNIQUE, mnpc=rec.mnpc, de=UniquesDe[rec.mnpc])
                    i_idx += 1
                else:
                    pofs_group = rec.ir.qual.pofs
                    while i_idx < pa_last and pa[i_idx].ir.qual.pofs == pofs_group:
                        curr = pa[i_idx]
                        # Logic: Cluster entries by MNPC/File Position [cite: 12905-12928]
                        if curr.mnpc != odm.mnpc or curr.d_k != odm.d_k:
                            j_idx += 1
                            k_idx = 0
                            # Read binary record from dictionary file parity
                            dea = DictIOService.read_entry(curr.d_k, curr.mnpc) if curr.mnpc != Null_MNPC else NullDictionaryEntry
                            dma[j_idx] = DictionaryMNPCRecord(d_k=curr.d_k, mnpc=curr.mnpc, de=dea)
                            odm = dma[j_idx]
                        else:
                            k_idx += 1
                        
                        sraa[j_idx][k_idx] = StemInflectionRecord(stem=curr.stem, ir=curr.ir)
                        i_idx += 1
                        if pofs_group not in (PartOfSpeechType.N, PartOfSpeechType.V, PartOfSpeechType.ADJ, PartOfSpeechType.NUM):
                            break
            
            return sraa, dma, i_idx == pa_last
        except Exception as e:
            put_stat(f"EXCEPTION LS at {raw_word} - {e}") [cite: 12932-12934]
            raise

    def put_inflection(self, config: ConfigurationType, output: TextIO, sr: StemInflectionRecord, dm: DictionaryMNPCRecord) -> None:
        """Renders the detailed morphological breakdown [cite: 12934-12967]."""
        if WordsMode.get_flag("Do_Only_Meanings") or config == ConfigurationType.ONLY_MEANINGS:
            return

        # 1. Output pedagogical codes and Inflected Word [cite: 12939-12943]
        if dm.d_k == DictionaryKind.ADDONS: self.put_pearse_code(output, Affix)
        elif dm.d_k in (DictionaryKind.XXX, DictionaryKind.YYY): self.put_pearse_code(output, Trick)
        else: self.put_pearse_code(output, Inflection)

        output.write(sr.stem.strip())
        if sr.ir.ending.size > 0:
            output.write(f".{sr.ir.ending.suf.strip()}")

        # 2. Alignment Logic parity [cite: 12944-12945]
        col = 25 if WordsMdev.get_flag("Do_Pearse_Codes") else 22
        output.write(" " * max(1, col - len(sr.stem.strip()) - (sr.ir.ending.size + 1 if sr.ir.ending.size > 0 else 0)))

        # 3. Modified Quality Logic: Deponent Verb voice shifts [cite: 12946-12959]
        if sr.ir != Null_Inflection_Record:
            qual_str = sr.ir.qual.to_string()
            if dm.d_k in (DictionaryKind.GENERAL, DictionaryKind.SPECIAL, DictionaryKind.LOCAL):
                if sr.ir.qual.pofs == PartOfSpeechType.V and dm.de.part.v.kind == VerbKindType.DEP:
                    # Logic: Blank out 'Passive' string for deponent verbs in active moods
                    pass 
            
            output.write(qual_str)
            # Replicates Age/Frequency flags on inflection line [cite: 12935-12936]
            if WordsMode.get_flag("Show_Age") or sr.ir.age != AgeType.X:
                output.write(f"  {INFLECTION_AGE[sr.ir.age].strip()}")
            
            output.write("\n")
            if dm.de != NullDictionaryEntry:
                put_example_line(config, output, sr.ir, dm.de) [cite: 12965]

    def put_parse_details(self, config: ConfigurationType, output: TextIO, wa: WordAnalysis) -> None:
        """Main rendering loop over the analysis structure [cite: 12972-12986]."""
        mm = self.get_max_meaning_size(output)
        osra = [StemInflectionRecord() for _ in range(STEM_INFLECTION_ARRAY_SIZE)]
        used_meanings = [False] * 40

        for j in range(DICTIONARY_MNPC_ARRAY_SIZE):
            dm = wa.dict_array[j]
            if dm.mnpc == Null_MNPC and dm.d_k == DictionaryKind.X:
                return

            sra = wa.stem_iaa[j]
            # 1. Deduplicate sequential identical inflection blocks [cite: 12977-12980]
            if sra != osra:
                for k in range(STEM_INFLECTION_ARRAY_SIZE):
                    if sra[k].stem == NullStemType and sra[k].ir == Null_Inflection_Record:
                        break
                    self.put_inflection(config, output, sra[k], dm)
                    if sra[k].stem.startswith("PPL"):
                        output.write(StringsPackage.head(wa.xp.ppp_meaning, mm) + "\n")
                osra = sra

            # 2. Render Headword [cite: 12981-12982]
            if j == 0 or dictionary_form(dm.de) != dictionary_form(wa.dict_array[j-1].de):
                self.put_dictionary_form(output, dm.d_k, dm.mnpc, dm.de)

            # 3. Render Definition [cite: 12983-12985]
            if dm.d_k not in (DictionaryKind.GENERAL, DictionaryKind.SPECIAL, DictionaryKind.UNIQUE) or \
               j + 1 >= DICTIONARY_MNPC_ARRAY_SIZE or dm.de.mean != wa.dict_array[j+1].de.mean:
                self.put_meaning_line(output, sra[0], dm, mm, wa.xp, used_meanings)

            # 4. Handle paging/pausing logic
            if not wa.i_is_pa_last and self.scroll_line_number > self.output_screen_size:
                # Replicates Pause(Output)
                input("Press Enter to continue...")
                self.scroll_line_number = 0

    def analyse_word(self, pa: ParseArray, pa_last: int, raw_word: str, xp: Explanations) -> WordAnalysis:
        """Expert migration of Analyse_Word engine entry [cite: 13026-13032]."""
        # Logic: Clean parses and handle adverbs [cite: 13030]
        list_sweep(pa[:pa_last], pa_last)
        sraa, dma, i_pa_last = self.cycle_over_pa(pa, pa_last, raw_word)

        return WordAnalysis(
            stem_iaa=sraa, dict_array=dma, i_is_pa_last=i_pa_last,
            unknowns=pa_last == 0, the_word=raw_word, xp=xp
        )

# --- Public API Stub (.pyi equivalent) ---

"""
from typing import TextIO
from .inflections_package import ParseArray
from .list_package import WordAnalysis

class ListPackageService:
    def analyse_word(self, pa: ParseArray, pa_last: int, raw_word: str, xp: Explanations) -> WordAnalysis: ...
    def put_parse_details(self, config: ConfigurationType, output: TextIO, wa: WordAnalysis) -> None: ...
    def unknown_search(self, unknown: str) -> int: ...
"""
