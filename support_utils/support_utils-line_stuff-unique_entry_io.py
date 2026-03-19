from typing import TextIO, Annotated, Tuple, Final
from pydantic import BaseModel, Field, StringConstraints, ConfigDict

# --- Types & Constants ---
# Assuming these constants based on the Ada package specifications
MAX_STEM_SIZE: Final[int] = 19
MAX_MEANING_SIZE: Final[int] = 80
QUALITY_WIDTH: Final[int] = 12
KIND_WIDTH: Final[int] = 10

class UniqueEntryError(Exception):
    """Base exception for UniqueEntry IO operations."""
    pass

class QualityRecord(BaseModel):
    model_config = ConfigDict(frozen=True)
    pofs: str = Field(..., description="Part of speech")
    data: str = "" # Placeholder for internal QualityRecord fields

class UniqueEntry(BaseModel):
    model_config = ConfigDict(validate_assignment=True)
    
    stem: Annotated[str, StringConstraints(min_length=0, max_length=MAX_STEM_SIZE)]
    qual: QualityRecord
    kind: str
    tran: Annotated[str, StringConstraints(min_length=0, max_length=MAX_MEANING_SIZE)]

# --- Mocking external IO logic mentioned in Ada 'use' clauses ---
# In a real migration, these would be imported from separate modules.
class QualityRecordIO:
    DEFAULT_WIDTH: int = QUALITY_WIDTH
    
    @staticmethod
    def get(source: TextIO | str) -> QualityRecord:
        # Implementation depends on Quality_Record_IO spec
        return QualityRecord(pofs="N", data="example")

class KindEntryIO:
    DEFAULT_WIDTH: int = KIND_WIDTH

# --- Main IO Module ---

def get_from_file(file: TextIO) -> UniqueEntry:
    """
    Translates 'procedure Get (F : in File_Type; P : out Unique_Entry)'
    """
    try:
        # Ada: Get (F, Ue.Stem)
        stem = file.read(MAX_STEM_SIZE).strip()
        file.read(1)  # Spacer
        
        # In Ada, Qual, Kind, and Tran have their own Get procedures
        # This implementation follows the sequence of the Ada body
        qual = QualityRecordIO.get(file)
        file.read(1)  # Spacer
        
        # Ada: Get (F, Ue.Qual.Pofs, Ue.Kind)
        # Mocking the dual-parameter get
        pofs_and_kind = file.read(KIND_WIDTH).strip().split()
        kind = pofs_and_kind[0] if pofs_and_kind else ""
        file.read(1)  # Spacer
        
        tran = file.read(MAX_MEANING_SIZE).strip()
        
        return UniqueEntry(
            stem=stem,
            qual=qual,
            kind=kind,
            tran=tran
        )
    except Exception as e:
        raise UniqueEntryError(f"Failed to read UniqueEntry from file: {e}")

def put_to_file(file: TextIO, entry: UniqueEntry) -> None:
    """
    Translates 'procedure Put (F : in File_Type; P : in Unique_Entry)'
    """
    try:
        file.write(f"{entry.stem:<{MAX_STEM_SIZE}} ")
        # In Ada, these calls would be delegated to specific IO packages
        file.write(f"{entry.qual.pofs:<{QUALITY_WIDTH}} ")
        file.write(f"{entry.kind:<{KIND_WIDTH}} ")
        file.write(f"{entry.tran}")
    except Exception as e:
        raise UniqueEntryError(f"Failed to write UniqueEntry to file: {e}")

def get_from_string(buffer: str) -> Tuple[UniqueEntry, int]:
    """
    Translates 'procedure Get (S : in String; P : out Unique_Entry; Last : out Integer)'
    Returns the parsed object and the 'Last' index.
    """
    try:
        l_idx = 0
        
        # Stem parsing
        m_idx = l_idx + MAX_STEM_SIZE
        stem = buffer[l_idx:m_idx].strip()
        
        # Quality parsing (Simulation of: Get (S (L + 1 .. S'Last), P.Qual, L))
        l_idx = m_idx + 1
        qual_str = buffer[l_idx : l_idx + QUALITY_WIDTH]
        qual = QualityRecord(pofs=qual_str.strip())
        
        # Kind parsing
        l_idx += QUALITY_WIDTH + 1
        kind = buffer[l_idx : l_idx + KIND_WIDTH].strip()
        
        # Translation parsing
        l_idx += KIND_WIDTH + 1
        tran = buffer[l_idx : l_idx + MAX_MEANING_SIZE].strip()
        
        last = l_idx + MAX_MEANING_SIZE
        
        entry = UniqueEntry(stem=stem, qual=qual, kind=kind, tran=tran)
        return entry, last
    except (IndexError, ValueError) as e:
        raise UniqueEntryError(f"String buffer parsing failed: {e}")

def put_to_string(entry: UniqueEntry) -> str:
    """
    Translates 'procedure Put (S : out String; P : in Unique_Entry)'
    Pythonic approach returns the formatted string.
    """
    # Ada version uses fixed-width buffers and slices
    # Here we use f-string padding to ensure data integrity/alignment
    parts = [
        f"{entry.stem:<{MAX_STEM_SIZE}}",
        f"{entry.qual.pofs:<{QUALITY_WIDTH}}",
        f"{entry.kind:<{KIND_WIDTH}}",
        f"{entry.tran:<{MAX_MEANING_SIZE}}"
    ]
    return " ".join(parts)
