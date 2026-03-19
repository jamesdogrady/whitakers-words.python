from __future__ import annotations
from typing import Final, Optional, TextIO
from pydantic import BaseModel, Field, ConfigDict

# --- Dependencies (Imported from previously migrated modules) ---
from .latin_utils.inflections_package import (
    InflectionRecord, DictionaryEntry, PartOfSpeechType, 
    PersonType, NumberType, TenseType, VoiceType, MoodType, 
    CaseType, ComparisonType, VerbKindType
)
from .latin_utils.config import ConfigurationType
from .support_utils.word_parameters import WordParametersService as WordsMode

# --- Migration Service ---

class PutExampleLineService:
    """
    Expert migration of Words_Engine.Put_Example_Line to Python 3.12+.
    Generates English grammatical examples and glosses based on Latin inflectional metadata[cite: 3427].
    """

    @staticmethod
    def put_verb_example(output: TextIO, ir: InflectionRecord, vk: VerbKindType) -> None:
        """
        Implementation of the internal procedure Put_Verb_Example [cite: 3428-3510].
        Constructs a composite English translation string using grammatical markers.
        """
        verb = ir.qual.verb
        person: Final = verb.person
        number: Final = verb.number
        tense: Final = verb.tense_voice_mood.tense
        mood: Final = verb.tense_voice_mood.mood
        voice_val: VoiceType = verb.tense_voice_mood.voice
        kind: Final = vk

        # 1. Handle Deponent/Semideponent voice shifts 
        if kind == VerbKindType.DEP:
            voice_val = VoiceType.ACTIVE
        elif kind == VerbKindType.SEMIDEP and tense in (TenseType.PERF, TenseType.PLUP, TenseType.FUTP):
            voice_val = VoiceType.ACTIVE

        # --- Internal Gloss Helpers ---

        def they() -> str:
            """Determines the English pronoun/subject [cite: 3434-3447]."""
            if kind == VerbKindType.IMPERS:
                return "it "
            if mood == MoodType.INF:
                return "to "
            if mood == MoodType.IMP and tense == TenseType.PRES and number == NumberType.P:
                return "(you) "
            if mood == MoodType.SUB and tense == TenseType.PRES and person == PersonType.P1 and number == NumberType.P:
                return "let us "
            
            match number:
                case NumberType.S:
                    match person:
                        case PersonType.P1: return "I "
                        case PersonType.P2: return "you "
                        case PersonType.P3: return "he/it "
                case NumberType.P:
                    match person:
                        case PersonType.P1: return "we "
                        case PersonType.P2: return "you "
                        case PersonType.P3: return "they "
            return ""

        def sub_marker() -> str:
            """Determines subjunctive mood markers [cite: 3505-3506]."""
            return "may/must/should " if mood == MoodType.SUB else ""

        def shall() -> str:
            """Determines future tense auxiliary markers [cite: 3448-3460]."""
            if tense in (TenseType.FUT, TenseType.FUTP):
                if mood in (MoodType.IND, MoodType.SUB):
                    return "shall " if person == PersonType.P1 else "will "
                if mood == MoodType.IMP:
                    return "will " if person == PersonType.P1 else "(shall) "
                if mood == MoodType.INF and tense == TenseType.FUT:
                    return "be about to be "
            return ""

        def have() -> str:
            """Determines perfect system auxiliary markers [cite: 3461-3469]."""
            if tense in (TenseType.PRES, TenseType.IMPF, TenseType.FUT):
                return ""
            if tense == TenseType.PERF:
                return "has " if (person == PersonType.P3 and number == NumberType.S) else "have "
            if tense == TenseType.PLUP:
                return "had" if mood == MoodType.IND else "have "
            if tense == TenseType.FUTP:
                return "have "
            return ""

        def been() -> str:
            """Determines passive voice status markers [cite: 3470-3487]."""
            if voice_val != VoiceType.PASSIVE:
                return ""
            
            match mood:
                case MoodType.IND:
                    match tense:
                        case TenseType.PRES:
                            if person == PersonType.P1 and number == NumberType.S: return "am/am being "
                            if person == PersonType.P3 and number == NumberType.S: return "is/is being "
                            return "are/are being "
                        case TenseType.IMPF:
                            if person in (PersonType.P1, PersonType.P3) and number == NumberType.S: return "was/was being "
                            return "were/were being "
                        case TenseType.FUT: return "be "
                        case TenseType.PERF:
                            if person in (PersonType.P1, PersonType.P3) and number == NumberType.S: return "been/was "
                            return "been/were "
                        case TenseType.PLUP | TenseType.FUTP: return "been "
                case MoodType.INF:
                    return "be " if tense == TenseType.PRES else "been "
                case MoodType.IMP:
                    return "be "
            return ""

        def ed_suffix() -> str:
            """Determines past/passive suffixes and punctuation [cite: 3488-3504]."""
            match mood:
                case MoodType.IMP:
                    return "!" if voice_val == VoiceType.ACTIVE else "ed!"
                case MoodType.INF:
                    return "" if voice_val == VoiceType.ACTIVE else "ed"
                case MoodType.IND:
                    if voice_val == VoiceType.ACTIVE:
                        match tense:
                            case TenseType.PRES: return "s" if (person == PersonType.P3 and number == NumberType.S) else ""
                            case TenseType.IMPF:
                                if person in (PersonType.P1, PersonType.P3) and number == NumberType.S: return "ed/was ~ing"
                                return "ed/were ~ing"
                            case TenseType.PERF | TenseType.PLUP | TenseType.FUTP: return "ed"
                    else:
                        return "ed"
                case MoodType.SUB:
                    return "ed" if tense in (TenseType.PERF, TenseType.PLUP) else ""
            return ""

        # Logic: Assemble They & Sub & Shall & Have & Been & "~" & Ed [cite: 3510]
        result = f"{they()}{sub_marker()}{shall()}{have()}{been()}~{ed_suffix()}"
        output.write(result)

    def put_example_line(self, configuration: ConfigurationType, output: TextIO, 
                         ir: InflectionRecord, de: DictionaryEntry) -> None:
        """
        Main execution logic for Put_Example_Line .
        Renders pedagogical English phrases for various Latin parts of speech.
        """
        if not WordsMode.get_flag("Do_Examples") or configuration == ConfigurationType.ONLY_MEANINGS:
            return

        match ir.qual.pofs:
            case PartOfSpeechType.N:
                # Logic: Noun case-specific examples [cite: 3511-3519]
                match ir.qual.noun.of_case:
                    case CaseType.GEN: output.write("~'s; of ~\n")
                    case CaseType.ABL: 
                        output.write("\n     from _ (separ); because of ~ (cause); than ~ (compar); of ~ (circumstance)\n")
                    case CaseType.DAT:
                        output.write("\n     for _ (purpose, reference); to ~ (w/adjectives); to ~ (double dative)\n")
                    case CaseType.LOC: output.write("at ~ (place where)\n")

            case PartOfSpeechType.ADJ:
                # Logic: Adjective comparison examples [cite: 3520-3522]
                match ir.qual.adj.comparison:
                    case ComparisonType.COMP: output.write("~er; more/too _\n")
                    case ComparisonType.SUPER: output.write("~est; most/very\n")

            case PartOfSpeechType.ADV:
                # Logic: Adverb comparison examples [cite: 3523-3525]
                match ir.qual.adv.comparison:
                    case ComparisonType.COMP: output.write("more/too ~(ly)\n")
                    case ComparisonType.SUPER: output.write("most/very ~(ly)\n")

            case PartOfSpeechType.V:
                # Logic: Standard verb examples [cite: 3527-3528]
                output.write("     ")
                self.put_verb_example(output, ir, de.part.v.kind)
                output.write("\n")

            case PartOfSpeechType.VPAR:
                # Logic: Participle system examples [cite: 3529-3543]
                match ir.qual.vpar.tense_voice_mood.tense:
                    case TenseType.PERF:
                        output.write("~ed  PERF PASSIVE PPL often used as ADJ or N (amatus => belov.ed)\n")
                    case TenseType.PRES:
                        output.write("~ing  PRES ACTIVE PPL often used as ADJ or N (lov.ing, curl.y)\n")
                    case TenseType.FUT:
                        if ir.qual.vpar.tense_voice_mood.voice == VoiceType.ACTIVE:
                            output.write("about/going/intending/destined to ~  FUT ACTIVE PPL often used as ADJ or N \n")
                        else:
                            # Gerundive/Passive Future Participle logic [cite: 3534-3543]
                            prefix = "to (/must) be ~ed  FUT PASSIVE PPL, often used as gerund or gerundive "
                            match ir.qual.vpar.of_case:
                                case CaseType.GEN: output.write(f"{prefix}(of ~ing)\n")
                                case CaseType.DAT: output.write(f"{prefix}(to/for ~ing)\n")
                                case CaseType.ABL: output.write(f"{prefix}(by/in ~ing)\n")
                                case CaseType.ACC: output.write(f"{prefix}(for ~ing/to ~)\n")
                                case _: output.write(f"{prefix}(~ing)\n")

            case PartOfSpeechType.SUPINE:
                # Logic: Supine system examples [cite: 3456-3548]
                if ir.qual.supine.of_case == CaseType.ACC:
                    output.write("to ~  expresses purpose of verb of motion; may take a direct object\n")
                elif ir.qual.supine.of_case == CaseType.ABL:
                    output.write("to ~  after ADJ indicating aspect/respect in which something is/is done\n")

# --- Public API Stub (.pyi equivalent) ---

"""
from typing import TextIO
from .latin_utils.inflections_package import InflectionRecord, DictionaryEntry
from .latin_utils.config import ConfigurationType

class PutExampleLineService:
    def put_example_line(self, configuration: ConfigurationType, output: TextIO, 
                         ir: InflectionRecord, de: DictionaryEntry) -> None: ...
"""
