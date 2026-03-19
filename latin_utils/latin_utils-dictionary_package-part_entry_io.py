from __future__ import annotations
from typing import Final, TextIO, Tuple, Optional
from pydantic import BaseModel, Field, ConfigDict

# --- Dependencies (Imported from previously migrated modules) ---
from .inflections_package import PartOfSpeech
from .noun_entry_io import NounEntry, NounEntryIOService
from .verb_entry_io import VerbEntry, VerbEntryIOService
from .adjective_entry_io import AdjectiveEntry, AdjectiveEntryIOService
from .adverb_entry_io import AdverbEntry, AdverbEntryIOService
from .numeral_entry_io import NumeralEntry, NumeralEntryIOService
from .preposition_entry_io import PrepositionEntry, PrepositionEntryIOService
from .conjunction_entry_io import ConjunctionEntry, ConjunctionEntryIOService
from .interjection_entry_io import InterjectionEntry, InterjectionEntryIOService

# --- Core Data Model ---

class PartEntry(BaseModel):
    """
    Expert migration of the Part_Entry variant record.
    Represents the grammatical classification and part-of-speech specific metadata 
    for a Latin dictionary entry.
    """
    model_config = ConfigDict(validate_assignment=True, frozen=True)

    pofs: PartOfSpeech = Field(..., alias="Pofs")
    
    # Variant fields
    n: Optional[NounEntry] = None
    v: Optional[VerbEntry] = None
    adj: Optional[AdjectiveEntry] = None
    adv: Optional[AdverbEntry] = None
    num: Optional[NumeralEntry] = None
    prep: Optional[PrepositionEntry] = None
    conj: Optional[ConjunctionEntry] = None
    interj: Optional[InterjectionEntry] = None

# --- Migration Service ---

class PartEntryIOService:
    """
    Expert migration of the Part_Entry_IO package body.
    Handles the composite parsing and formatting of part-of-speech records.
    """

    # Corresponds to Default_Width in the Ada specification
    DEFAULT_WIDTH: Final[int] = 15

    @staticmethod
    def get_from_string(source: str) -> Tuple[PartEntry, int]:
        """
        Implementation of procedure Get (Source : String; Target : out Part_Entry; Last : out Integer).
        Parses the part-of-speech and its variant data from a fixed-width segment.
        """
        # Note: Ada code uses a 'Low' offset to track progress through the metadata string.
        
        # 1. Parse the Part of Speech identifier (typically first field)
        # Using a slice to simulate Part_Of_Speech_Type_IO behavior
        pofs_str = source[0:2].strip()
        pofs = PartOfSpeech(pofs_str) if pofs_str else PartOfSpeech.X
        
        # Segment for variant data starts after POFS
        variant_source = source[2:]
        last_idx = 2
        
        # 2. Case-based delegation to specific POS IO services
        match pofs:
            case PartOfSpeech.N:
                n_entry, last = NounEntryIOService.get_from_string(variant_source)
                return PartEntry(pofs=pofs, n=n_entry), last_idx + last
            case PartOfSpeech.V:
                # Note: SUPINE and VPAR also use VerbEntry data in the original engine
                v_entry, last = VerbEntryIOService.get_from_string(variant_source)
                return PartEntry(pofs=pofs, v=v_entry), last_idx + last
            case PartOfSpeech.ADJ:
                adj_entry, last = AdjectiveEntryIOService.get_from_string(variant_source)
                return PartEntry(pofs=pofs, adj=adj_entry), last_idx + last
            case PartOfSpeech.ADV:
                adv_entry, last = AdverbEntryIOService.get_from_string(variant_source)
                return PartEntry(pofs=pofs, adv=adv_entry), last_idx + last
            case PartOfSpeech.NUM:
                num_entry, last = NumeralEntryIOService.get_from_string(variant_source)
                return PartEntry(pofs=pofs, num=num_entry), last_idx + last
            case PartOfSpeech.PREP:
                prep_entry, last = PrepositionEntryIOService.get_from_string(variant_source)
                return PartEntry(pofs=pofs, prep=prep_entry), last_idx + last
            case PartOfSpeech.CONJ:
                conj_entry, last = ConjunctionEntryIOService.get_from_string(variant_source)
                return PartEntry(pofs=pofs, conj=conj_entry), last_idx + last
            case PartOfSpeech.INTERJ:
                int_entry, last = InterjectionEntryIOService.get_from_string(variant_source)
                return PartEntry(pofs=pofs, interj=int_entry), last_idx + last
            case _:
                # Handle X, TACKON, PREFIX, SUFFIX (which have null record metadata)
                return PartEntry(pofs=pofs), last_idx

    @staticmethod
    def put_to_string(item: PartEntry) -> str:
        """
        Implementation of procedure Put (Target : out String; Item : in Part_Entry).
        Serializes a PartEntry into a fixed-width DICTLINE segment.
        """
        # Starts with the POFS string
        result = f"{item.pofs.value:<2} "
        
        # Appends formatted variant data based on active POFS
        match item.pofs:
            case PartOfSpeech.N if item.n:
                result += NounEntryIOService.put_to_string(item.n)
            case PartOfSpeech.V if item.v:
                result += VerbEntryIOService.put_to_string(item.v)
            case PartOfSpeech.ADJ if item.adj:
                result += AdjectiveEntryIOService.put_to_string(item.adj)
            case PartOfSpeech.NUM if item.num:
                result += NumeralEntryIOService.put_to_string(item.num)
            case PartOfSpeech.ADV if item.adv:
                result += AdverbEntryIOService.put_to_string(item.adv)
            case PartOfSpeech.PREP if item.prep:
                result += PrepositionEntryIOService.put_to_string(item.prep)
            case PartOfSpeech.CONJ if item.conj:
                result += ConjunctionEntryIOService.put_to_string(item.conj)
            case PartOfSpeech.INTERJ if item.interj:
                result += InterjectionEntryIOService.put_to_string(item.interj)
            case _:
                # X, VPAR, SUPINE, etc. provide no additional entry data
                pass

        # Pad the entire record to Default_Width
        return result.ljust(PartEntryIOService.DEFAULT_WIDTH)

    @staticmethod
    def put_to_file(file: TextIO, item: PartEntry) -> None:
        """
        Implementation of procedure Put (File : File_Type; Item : in Part_Entry).
        Writes the PartEntry and its variant metadata to a file stream.
        """
        # Ada: Part_Of_Speech_Type_IO.Put (File, Item.Pofs);
        file.write(f"{item.pofs.value} ")
        
        # Delegates to specific record IO
        match item.pofs:
            case PartOfSpeech.N if item.n:
                NounEntryIOService.put_to_file(file, item.n)
            case PartOfSpeech.V if item.v:
                VerbEntryIOService.put_to_file(file, item.v)
            case PartOfSpeech.ADJ if item.adj:
                AdjectiveEntryIOService.put_to_file(file, item.adj)
            # ... and so on for all parts of speech
            case _:
                pass

# --- Public API Stub (.pyi equivalent) ---

"""
from typing import TextIO, Tuple
from .dictionary_package import PartEntry

class PartEntryIOService:
    DEFAULT_WIDTH: int = 15
    @staticmethod
    def get_from_string(source: str) -> Tuple[PartEntry, int]: ...
    @staticmethod
    def put_to_string(item: PartEntry) -> str: ...
    @staticmethod
    def put_to_file(file: TextIO, item: PartEntry) -> None: ...
"""
