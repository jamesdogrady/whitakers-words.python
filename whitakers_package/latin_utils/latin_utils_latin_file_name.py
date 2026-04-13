from __future__ import annotations
from typing import Final
from pydantic import BaseModel, ConfigDict


class LatinFileNames(BaseModel):
    """
    Expert migration of the Latin_Utils.Latin_File_Names package.
    Centralizes the system-dependent external file names used by the WORDS engine .
    """
    model_config = ConfigDict(frozen=True)

    # Single files with fixed full names #[cite: 767-769]
    inflections_full_name: Final[str] = "INFLECTS.LAT"
    inflections_sections_name: Final[str] = "INFLECTS.SEC"
    uniques_full_name: Final[str] = "UNIQUES.LAT"
    addons_full_name: Final[str] = "ADDONS.LAT"

    # Engine operational and diagnostic files #[cite: 770-772]
    mode_full_name: Final[str] = "WORD.MOD"
    output_full_name: Final[str] = "WORD.OUT"
    unknowns_full_name: Final[str] = "WORD.UNK"

    # Base names for dictionary components (typically appended with extensions like .GEN, .SPE, .LOC) #[cite: 773-778]
    dictionary_file_name: Final[str] = "DICT"
    dict_file_name: Final[str] = "DICTFILE"
    dict_line_name: Final[str] = "DICTLINE"
    stem_list_name: Final[str] = "STEMLIST"
    stem_file_name: Final[str] = "STEMFILE"
    indx_file_name: Final[str] = "INDXFILE"


# Export as a singleton for system-wide access
LATIN_FILE_NAMES: Final[LatinFileNames] = LatinFileNames()
