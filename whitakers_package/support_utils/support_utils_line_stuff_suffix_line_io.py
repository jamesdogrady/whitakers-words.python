from __future__ import annotations
from typing import Final, List, Optional, Tuple, Any
from pydantic import BaseModel, Field, ConfigDict
from .latin_utils.strings_package import StringsPackage
from .latin_utils.inflections_package import (
    PartOfSpeechType, GenderType, CaseType, VerbKindType,
    DictionaryEntry, DecnRecord, ComparisonType,
    NumeralSortType, NullStemType
)

# --- Exceptions ---

class DictionaryFormError(Exception):
    """Base exception for DictionaryForm operations."""
    pass

class NotFoundError(DictionaryFormError):
    """Raised when a declension or POS pattern is not found[cite: 19]."""
    pass

# --- Constants and Helpers ---

NULL_OX: Final[str] = " " * 24 [cite: 15]
FST: Final[dict[int, str]] = {
    1: "1st", 2: "2nd", 3: "3rd", 4: "4th", 5: "5th"
} [cite: 18]

def add(stem: str, infl: str) -> str:
    """Helper to combine stem and inflection with legacy 24-char limit [cite: 19-20]."""
    combined = stem.strip() + infl.strip()
    return StringsPackage.head(combined, 24)

# --- Core Logic ---

def dictionary_form(de: Optional[DictionaryEntry]) -> str:
    """
    Expert migration of Support_Utils.Dictionary_Form to Python 3.12+.
    Produces the pedagogical 'dictionary form' string for a Latin entry .
    """
    # 0. Null Parity Check [cite: 22-23]
    if de is None:
        return ""

    # 1. Initialization [cite: 16-17]
    ox: List[str] = [NULL_OX] * 5  # Using index 1..4 for logical parity
    form: str = " " * 100

    def add_up(factor: str) -> None:
        nonlocal form
        # Implementation of Add_Up [cite: 20-21]
        form = StringsPackage.head(form.strip() + factor.strip(), 100)

    def add_to(factor: str) -> None:
        nonlocal form
        # Implementation of Add_To [cite: 21-22]
        form = StringsPackage.head(form.strip() + factor, 100)

    pofs = de.part.pofs

    # 2. Preposition Shortcut [cite: 23-24]
    if pofs == PartOfSpeechType.PREP:
        return f"{de.stems[0].strip()}  {pofs.value}  {de.part.prep.obj.value}"

    # 3. Invariants / Simple Form Check [cite: 24-26]
    # Check if stems 2-4 are unused and no complex metadata exists
    stems_2_to_4_empty = all(s == NullStemType for s in de.stems[1:4])
    is_complex_metadata = (
        (pofs == PartOfSpeechType.N and de.part.n.decl.which == 9) or
        (pofs == PartOfSpeechType.ADJ and (de.part.adj.decl.which == 9 or de.part.adj.co != ComparisonType.POS)) or
        (pofs == PartOfSpeechType.V and (de.part.v.con.which == 9 and de.part.v.con.var in (8, 9)))
    )

    if stems_2_to_4_empty and not is_complex_metadata:
        return f"{de.stems[0].strip()}  {pofs.value}"

    # 4. Inflectional Endings Logic
    try:
        match pofs:
            case PartOfSpeechType.N:  # [cite: 27-54]
                n_rec = de.part.n
                match n_rec.decl.which:
                    case 1:
                        match n_rec.decl.var:
                            case 1: ox[1], ox[2] = add(de.stems[0], "a"), add(de.stems[1], "ae") [cite: 27-28]
                            case 6: ox[1], ox[2] = add(de.stems[0], "e"), add(de.stems[1], "es") [cite: 28-29]
                            case 7: ox[1], ox[2] = add(de.stems[0], "es"), add(de.stems[1], "ae") [cite: 29-30]
                            case 8: ox[1], ox[2] = add(de.stems[0], "as"), add(de.stems[1], "ae") [cite: 30-31]
                    case 2:
                        match n_rec.decl.var:
                            case 1: ox[1], ox[2] = add(de.stems[0], "us"), add(de.stems[1], "i") [cite: 32-33]
                            case 2: ox[1], ox[2] = add(de.stems[0], "um"), add(de.stems[1], "i") [cite: 33-34]
                            case 3: ox[1], ox[2] = add(de.stems[0], ""), add(de.stems[1], "i") [cite: 34-35]
                            case 4:
                                ox[1] = add(de.stems[0], "um" if n_rec.gender == GenderType.N else "us") [cite: 35-37]
                                ox[2] = add(de.stems[1], "(i)") [cite: 37]
                            case 5: ox[1], ox[2] = add(de.stems[0], "us"), add(de.stems[1], "") [cite: 37-38]
                            case 6 | 7: ox[1], ox[2] = add(de.stems[0], "os"), add(de.stems[1], "i") [cite: 38-40]
                            case 8: ox[1], ox[2] = add(de.stems[0], "on"), add(de.stems[1], "i") [cite: 40-41]
                            case 9: ox[1], ox[2] = add(de.stems[0], "us"), add(de.stems[1], "i") [cite: 41-42]
                    case 3:
                        ox[1] = add(de.stems[0], "") [cite: 43]
                        ox[2] = add(de.stems[1], "os/is" if n_rec.decl.var in (7, 9) else "is") [cite: 44-46]
                    case 4:
                        match n_rec.decl.var:
                            case 1: ox[1], ox[2] = add(de.stems[0], "us"), add(de.stems[1], "us") [cite: 46-47]
                            case 2: ox[1], ox[2] = add(de.stems[0], "u"), add(de.stems[1], "us") [cite: 47-48]
                            case 3: ox[1], ox[2] = add(de.stems[0], "us"), add(de.stems[1], "u") [cite: 48-49]
                    case 5:
                        ox[1], ox[2] = add(de.stems[0], "es"), add(de.stems[1], "ei") [cite: 50-51]
                    case 9:
                        if n_rec.decl.var == 8: ox[1], ox[2] = add(de.stems[0], "."), add(NULL_OX, "abb.") [cite: 51-52]
                        elif n_rec.decl.var == 9: ox[1], ox[2] = add(de.stems[0], ""), add(NULL_OX, "undeclined") [cite: 52-53]
                    case _: raise NotFoundError() [cite: 54]

            case PartOfSpeechType.PRON:  # [cite: 55-68]
                p_rec = de.part.pron
                match p_rec.decl.which:
                    case 3:
                        ox[1], ox[2] = add(de.stems[0], "ic"), add(de.stems[0], "aec") [cite: 55-56]
                        ox[3] = add(de.stems[0], "oc" if p_rec.decl.var == 1 else "uc") [cite: 56-58]
                    case 4:
                        if p_rec.decl.var == 1: ox[1], ox[2], ox[3] = add(de.stems[0], "s"), add(de.stems[1], "a"), add(de.stems[0], "d") [cite: 58-59]
                        elif p_rec.decl.var == 2: ox[1], ox[2], ox[3] = add(de.stems[0], "dem"), add(de.stems[1], "adem"), add(de.stems[0], "dem") [cite: 60-61]
                    case 6:
                        ox[1], ox[2] = add(de.stems[0], "e"), add(de.stems[0], "a") [cite: 62-63]
                        ox[3] = add(de.stems[0], "ud" if p_rec.decl.var == 1 else "um") [cite: 63-65]
                    case 9:
                        if p_rec.decl.var == 8: ox[1], ox[2] = add(de.stems[0], "."), add(NULL_OX, "abb.") [cite: 65-66]
                        elif p_rec.decl.var == 9: ox[1], ox[2] = add(de.stems[0], ""), add(NULL_OX, "undeclined") [cite: 66-67]
                    case _: raise NotFoundError() [cite: 67]

            case PartOfSpeechType.ADJ:  # [cite: 69-121]
                a_rec = de.part.adj
                match a_rec.co:
                    case ComparisonType.COMP:
                        ox[1], ox[2], ox[3] = add(de.stems[0], "or"), add(de.stems[0], "or"), add(de.stems[0], "us") [cite: 69-70]
                    case ComparisonType.SUPER:
                        ox[1], ox[2], ox[3] = add(de.stems[0], "mus"), add(de.stems[0], "ma"), add(de.stems[0], "mum") [cite: 71-72]
                    case ComparisonType.POS:
                            if a_rec.decl.which == 1:
                                match a_rec.decl.var:
                                    case 1: ox[1], ox[2], ox[3] = add(de.stems[0], "us"), add(de.stems[1], "a"), add(de.stems[1], "um") [cite: 73-74]
                                    case 2: ox[1], ox[2], ox[3] = add(de.stems[0], ""), add(de.stems[1], "a"), add(de.stems[1], "um") [cite: 75-76]
                                    case 3: ox[1], ox[2], ox[3] = add(de.stems[0], "us"), add(de.stems[1], "a"), add(de.stems[1], "um (gen -ius)") [cite: 77-78]
                                    case 4: ox[1], ox[2], ox[3] = add(de.stems[0], ""), add(de.stems[1], "a"), add(de.stems[1], "um") [cite: 79-80]
                                    case 5: ox[1], ox[2], ox[3] = add(de.stems[0], "us"), add(de.stems[1], "a"), add(de.stems[1], "ud") [cite: 81-82]
                                    case _: raise NotFoundError() [cite: 83]
                            elif a_rec.decl.which == 2:
                                match a_rec.decl.var:
                                    case 1: ox[1], ox[2], ox[3] = add(NULL_OX, "-"), add(de.stems[0], "e"), add(NULL_OX, "-") [cite: 84-85]
                                    case 2: ox[1], ox[2], ox[3] = add(NULL_OX, "-"), add(NULL_OX, "a"), add(NULL_OX, "-") [cite: 86-87]
                                    case 3: ox[1], ox[2], ox[3] = add(de.stems[0], "es"), add(de.stems[0], "es"), add(de.stems[0], "es") [cite: 88-89]
                                    case 6: ox[1], ox[2], ox[3] = add(de.stems[0], "os"), add(de.stems[0], "os"), add(NULL_OX, "-") [cite: 90-91]
                                    case 7: ox[1], ox[2], ox[3] = add(de.stems[0], "os"), add(NULL_OX, "-"), add(NULL_OX, "-") [cite: 92-93]
                                    case 8: ox[1], ox[2], ox[3] = add(NULL_OX, "-"), add(NULL_OX, "-"), add(de.stems[1], "on") [cite: 94-95]
                            elif a_rec.decl.which == 3:
                                match a_rec.decl.var:
                                    case 1: ox[1], ox[2], ox[3] = add(de.stems[0], ""), add(NULL_OX, "(gen.)"), add(de.stems[1], "is") [cite: 96-97]
                                    case 2: ox[1], ox[2], ox[3] = add(de.stems[0], "is"), add(de.stems[1], "is"), add(de.stems[1], "e") [cite: 98-99]
                                    case 3: ox[1], ox[2], ox[3] = add(de.stems[0], ""), add(de.stems[1], "is"), add(de.stems[1], "e") [cite: 100-101]
                                    case 6: ox[1], ox[2], ox[3] = add(de.stems[0], ""), add(NULL_OX, "(gen.)"), add(de.stems[1], "os") [cite: 102-103]
                            elif a_rec.decl == DecnRecord(which=9, var=8): ox[1], ox[2] = add(de.stems[0], "."), add(NULL_OX, "abb.") [cite: 104-105]
                            elif a_rec.decl == DecnRecord(which=9, var=9): ox[1], ox[2] = add(de.stems[0], ""), add(NULL_OX, "undeclined") [cite: 105-106]
                            else: raise NotFoundError() [cite: 106]
                    case ComparisonType.X:
                        match a_rec.decl.which:
                            case 1:
                                ox[1] = add(de.stems[0], "us" if a_rec.decl.var == 1 else "") [cite: 107-109]
                                ox[2], ox[3], ox[4] = add(de.stems[1], "a -um"), add(de.stems[2], "or -or -us"), add(de.stems[3], "mus -a -um") [cite: 108-111]
                            case 3:
                                match a_rec.decl.var:
                                    case 1: ox[1], ox[2] = add(de.stems[0], ""), add(de.stems[1], "is (gen.)") [cite: 112-113]
                                    case 2: ox[1], ox[2] = add(de.stems[0], "is"), add(de.stems[1], "e") [cite: 114-115]
                                    case 3: ox[1], ox[2] = add(de.stems[0], ""), add(de.stems[1], "is -e") [cite: 116-117]
                                ox[3], ox[4] = add(de.stems[2], "or -or -us"), add(de.stems[3], "mus -a -um") [cite: 113-118]
                            case 9:
                                ox[1], ox[2] = add(de.stems[0], ""), add(NULL_OX, "undeclined") [cite: 119-120]
                                ox[3], ox[4] = add(de.stems[2], "or -or -us"), add(de.stems[3], "mus -a -um") [cite: 120-121]
                            case _: raise NotFoundError() [cite: 121]

            case PartOfSpeechType.ADV if de.part.adv.co == ComparisonType.X: # [cite: 122-123]
                ox[1], ox[2], ox[3] = add(de.stems[0], ""), add(de.stems[1], ""), add(de.stems[2], "")

            case PartOfSpeechType.V:  # [cite: 124-180]
                v_rec = de.part.v
                if v_rec.kind == VerbKindType.DEP: [cite: 124]
                    ox[3], ox[4] = add(NULL_OX, "DEP"), add(de.stems[3], "us sum") [cite: 124-125]
                    match v_rec.con.which:
                        case 1: ox[1], ox[2] = add(de.stems[0], "or"), add(de.stems[1], "ari") [cite: 126-127]
                        case 2: ox[1], ox[2] = add(de.stems[0], "eor"), add(de.stems[1], "eri") [cite: 127-128]
                        case 3:
                            ox[1] = add(de.stems[0], "or") [cite: 128]
                            ox[2] = add(de.stems[1], "iri" if v_rec.con.var == 4 else "i") [cite: 129-130]
                        case _: raise NotFoundError() [cite: 131]
                elif v_rec.kind == VerbKindType.PERFDEF: [cite: 132]
                    ox[1], ox[2], ox[3] = add(de.stems[2], "i"), add(de.stems[2], "isse"), add(de.stems[3], "us") [cite: 132-133]
                    ox[4] = NULL_OX [cite: 133]
                elif v_rec.kind == VerbKindType.IMPERS and de.stems[0][:3] == "zzz" and de.stems[1][:3] == "zzz": [cite: 134]
                    ox[1], ox[2], ox[3] = add(de.stems[2], "it"), add(de.stems[2], "isse"), add(de.stems[3], "us est") [cite: 134-135]
                else:
                    if v_rec.kind == VerbKindType.IMPERS: [cite: 137]
                        match v_rec.con.which:
                            case 1: ox[1] = add(de.stems[0], "at") [cite: 137-138]
                            case 2: ox[1] = add(de.stems[0], "et") [cite: 138]
                            case 3:
                                if v_rec.con.var == 2: ox[1] = add(de.stems[0], "t") [cite: 139]
                                else: ox[1] = add(de.stems[0], "t" if de.stems[0].strip().endswith('i') else "it") [cite: 140-141]
                            case 5 if v_rec.con.var == 1: ox[1] = add(de.stems[0], "est") [cite: 142]
                            case 7 if v_rec.con.var in (1, 2): ox[1] = add(de.stems[0], "t") [cite: 143]
                    else:
                        if v_rec.con.which == 2: ox[1] = add(de.stems[0], "eo") [cite: 144-145]
                        elif v_rec.con.which == 5: ox[1] = add(de.stems[0], "um") [cite: 145]
                        elif v_rec.con == DecnRecord(which=7, var=2): ox[1] = add(de.stems[0], "am") [cite: 146]
                        else: ox[1] = add(de.stems[0], "o") [cite: 147]

                    match v_rec.con.which: [cite: 148]
                        case 1: ox[2] = add(de.stems[1], "are") [cite: 148]
                        case 2: ox[2] = add(de.stems[1], "ere") [cite: 149]
                        case 3:
                            match v_rec.con.var:
                                case 2: ox[2] = add(de.stems[1], "re") [cite: 150]
                                case 3: ox[2] = add(de.stems[1], "ieri" if de.stems[1].strip() == "f" else "eri") [cite: 151-153]
                                case 4: ox[2] = add(de.stems[1], "ire") [cite: 154]
                                case _: ox[2] = add(de.stems[1], "ere") [cite: 155]
                        case 5:
                            if v_rec.con.var == 1: ox[2] = add(de.stems[1], "esse") [cite: 157]
                            elif v_rec.con.var == 2: ox[2] = add(de.stems[0], "e") [cite: 158]
                        case 6: ox[2] = add(de.stems[1], "re" if v_rec.con.var == 1 else "le") [cite: 160-161]
                        case 7 if v_rec.con.var == 3: ox[2] = add(de.stems[1], "se") [cite: 162]
                        case 8:
                            match v_rec.con.var:
                                case 1: ox[2] = add(de.stems[1], "are") [cite: 163]
                                case 2 | 3 | 5: ox[2] = add(de.stems[1], "ere") [cite: 164-165, 167]
                                case 4: ox[2] = add(de.stems[1], "ire") [cite: 166]
                        case 9:
                            if v_rec.con.var == 8: ox[1], ox[2] = add(de.stems[0], "."), add(NULL_OX, "abb.") [cite: 168-169]
                            elif v_rec.con.var == 9: ox[1], ox[2] = add(de.stems[0], ""), add(NULL_OX, "undeclined") [cite: 169-170]

                    if v_rec.kind == VerbKindType.IMPERS:
                        if ox[3][:7] != "PERFDEF": ox[3] = add(de.stems[2], "it") [cite: 171-172]
                        ox[4] = add(de.stems[3], "us est") [cite: 172]
                    elif v_rec.kind == VerbKindType.SEMIDEP: ox[4] = add(de.stems[3], "us sum") [cite: 173]
                    elif v_rec.con == DecnRecord(which=5, var=1): ox[3], ox[4] = add(de.stems[2], "i"), add(de.stems[3], "urus") [cite: 174-175]
                    elif v_rec.con.which == 8: ox[3], ox[4] = add("", "additional"), add("", "forms") [cite: 175-176]
                    elif v_rec.con.which == 9: ox[3], ox[4] = add(NULL_OX, "BLANK"), add(NULL_OX, "BLANK") [cite: 176-178]
                    else: ox[3], ox[4] = add(de.stems[2], "i"), add(de.stems[3], "us") [cite: 178-179]

                if v_rec.con == DecnRecord(which=6, var=1): ox[3] = add(ox[3], " (ii)") [cite: 180]

            case PartOfSpeechType.NUM:  # [cite: 181-206]
                n_rec = de.part.num
                match n_rec.sort:
                    case NumeralSortType.X:
                        if n_rec.decl.which == 1:
                            match n_rec.decl.var:
                                case 1: ox[1], ox[2], ox[3] = add(de.stems[0], "us -a -um"), add(de.stems[1], "us -a -um"), add(de.stems[2], "i -ae -a") [cite: 181-182]
                                case 2: ox[1], ox[2], ox[3] = add(de.stems[0], "o -ae o"), add(de.stems[1], "us -a -um"), add(de.stems[2], "i -ae -a") [cite: 183-184]
                                case 3: ox[1], ox[2], ox[3] = add(de.stems[0], "es -es -ia"), add(de.stems[1], "us -a -um"), add(de.stems[2], "i -ae -a") [cite: 185-186]
                                case 4: ox[1], ox[2], ox[3], ox[4] = add(de.stems[0], "i -ae -a"), add(de.stems[1], "us -a -um"), add(de.stems[2], "i -ae -a"), add(de.stems[3], "ie (n)s") [cite: 187-189]
                        elif n_rec.decl.which == 2:
                            ox[1], ox[2], ox[3], ox[4] = add(de.stems[0], ""), add(de.stems[1], "us -a -um"), add(de.stems[2], "i -ae -a"), add(de.stems[3], "ie (n)s") [cite: 190-192]
                    case NumeralSortType.CARD:
                        if n_rec.decl.which == 1:
                            match n_rec.decl.var:
                                case 1: ox[1], ox[2], ox[3] = add(de.stems[0], "us"), add(de.stems[0], "a"), add(de.stems[0], "um") [cite: 193-194]
                                case 2: ox[1], ox[2], ox[3] = add(de.stems[0], "o"), add(de.stems[0], "ae"), add(de.stems[0], "o") [cite: 195-196]
                                case 3: ox[1], ox[2], ox[3] = add(de.stems[0], "es"), add(de.stems[0], "es"), add(de.stems[0], "ia") [cite: 197-198]
                                case 4: ox[1], ox[2], ox[3] = add(de.stems[0], "i"), add(de.stems[0], "ae"), add(de.stems[0], "a") [cite: 199-200]
                        elif n_rec.decl.which == 2: ox[1] = add(de.stems[0], "") [cite: 201]
                    case NumeralSortType.ORD:
                        ox[1], ox[2], ox[3] = add(de.stems[0], "us"), add(de.stems[0], "a"), add(de.stems[0], "um") [cite: 202-203]
                    case NumeralSortType.DIST:
                        ox[1], ox[2], ox[3] = add(de.stems[0], "i"), add(de.stems[0], "ae"), add(de.stems[0], "a") [cite: 204-205]
                    case _: ox[1] = add(de.stems[0], "") [cite: 206]

            case _: ox[1] = add(de.stems[0], "") [cite: 206]

    except (NotFoundError, ValueError, KeyError, IndexError):
        return "" [cite: 227-228]

    # 5. Result Assembly [cite: 208-220]
    if ox[1][:3] == "zzz": add_up(" - ") [cite: 208]
    elif ox[1] != NULL_OX: add_up(ox[1]) [cite: 209]

    if ox[2][:3] == "zzz": add_up(", - ") [cite: 210]
    elif ox[2] != NULL_OX: add_up(f", {ox[2]}") [cite: 211]

    if ox[3][:3] == "zzz": add_up(", - ") [cite: 212]
    elif ox[3][:3] == "DEP": pass [cite: 213]
    elif ox[3][:7] == "PERFDEF": pass [cite: 214]
    elif ox[3][:5] == "BLANK": pass [cite: 215]
    elif ox[3] != NULL_OX: add_up(f", {ox[3]}") [cite: 216]

    if ox[4][:3] == "zzz": add_up(", - ") [cite: 217]
    elif ox[4][:5] == "BLANK": pass [cite: 218]
    elif ox[4] != NULL_OX: add_up(f", {ox[4]}") [cite: 219]

    # 6. Metadata Markers [cite: 220-226]
    add_to(f"  {pofs.value}  ") [cite: 220]
    
    if pofs == PartOfSpeechType.N:
        n_p = de.part.n
        if 1 <= n_p.decl.which <= 5 and 1 <= n_p.decl.var <= 5:
            add_to(f" ({FST[n_p.decl.which]})") [cite: 221]
        add_to(f" {n_p.gender.value}  ") [cite: 222]
    
    if pofs == PartOfSpeechType.V:
        v_p = de.part.v
        if 1 <= v_p.con.which <= 3:
            if v_p.con.var == 1: add_to(f" ({FST[v_p.con.which]})") [cite: 223]
            elif v_p.con == DecnRecord(which=3, var=4): add_to(" (4th)") [cite: 224]
        if VerbKindType.GEN.value <= v_p.kind.value <= VerbKindType.PERFDEF.value:
            add_to(f" {v_p.kind.value}  ") [cite: 225]

    return form.strip() [cite: 226]

# --- Public API Stub (.pyi equivalent) ---

"""
from typing import Optional
from .latin_utils.inflections_package import DictionaryEntry

def dictionary_form(de: Optional[DictionaryEntry]) -> str: ...
"""
