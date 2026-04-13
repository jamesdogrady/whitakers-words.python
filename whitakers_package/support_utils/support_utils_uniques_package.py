from __future__ import annotations
from typing import Dict, Final, List, Optional
from pydantic import BaseModel, Field, ConfigDict

# --- Dependencies (Imported from previously migrated modules) ---
from ..inflections_package import (
    StemType, QualityRecord,
    NullStemType 
)
from ..dictionary_package import (
     KindEntry
)
from ..dictionary_package.latin_utils_dictionary_package_dictionary_entry_io import DictionaryEntry


# --- Core Data Models ---

class UniqueItem(BaseModel):
    """
    Expert migration of Unique_Item record.
    Represents a node in the linked list of unique/irregular Latin words.
    """
    model_config = ConfigDict(validate_assignment=True)

    stem: StemType = Field(default=NullStemType, alias="Stem")
    qual: QualityRecord = Field(default_factory=QualityRecord, alias="Qual")
    kind: KindEntry = Field(default_factory=KindEntry, alias="Kind")
    mnpc: int = Field(default=0 , alias="MNPC")
    succ: Optional[UniqueItem] = Field(default=None, alias="Succ")


# --- Migration Service ---

class UniquesPackage:
    """
    Expert migration of Support_Utils.Uniques_Package.
    Manages the lookup tables for unique Latin stems and their corresponding 
    dictionary entries.
    """

    def __init__(self):
        # Maps 'a'..'z' to the head of a UniqueItem linked list
        # Replicates: type Latin_Uniques is array (Character range 'a' .. 'z') of Unique_List;
        self.unq: Dict[str, Optional[UniqueItem]] = {
            chr(i): None for i in range(ord('a'), ord('z') + 1)
        }

        # Fixed-size array of dictionary entries for unique words
        # Replicates: Uniques_De : Uniques_De_Array (1 .. 100);
        self.uniques_de: List[DictionaryEntry] = [
            DictionaryEntry() for _ in range(101) # 1-based indexing parity
        ]

    def get_unique_list(self, char: str) -> Optional[UniqueItem]:
        """Retrieves the list of unique entries for a specific starting character."""
        return self.unq.get(char.lower())

# --- Public API Stub (.pyi equivalent) ---

"""
from typing import Dict, List, Optional
from .inflections_package import StemType, QualityRecord, KindEntry
from .dictionary_package import MNPC_Type, DictionaryEntry

class UniqueItem:
    stem: StemType
    qual: QualityRecord
    kind: KindEntry
    mnpc: int
    succ: Optional[UniqueItem]

class UniquesPackage:
    unq: Dict[str, Optional[UniqueItem]]
    uniques_de: List[DictionaryEntry]
    def get_unique_list(self, char: str) -> Optional[UniqueItem]: ...
"""
