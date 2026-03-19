from __future__ import annotations
from enum import IntEnum, auto
from typing import Final, List, Optional, TextIO
from pydantic import BaseModel, Field, ConfigDict
from pathlib import Path

# --- Core Enumerations and Constants ---

class MdevKind(IntEnum):
    """
    Expert migration of Mdev_Kind enumeration.
    Defines various developer mode flags used to control the Latin dictionary engine.
    """
    HAVE_DEBUG_FILE = 0
    HAVE_STATISTICS_FILE = auto()
    USE_TACKONS = auto()
    USE_PREFIXES = auto()
    USE_SUFFIXES = auto()
    SHOW_DICTIONARIES = auto()
    SHOW_DICTIONARY_LINE = auto()
    SHOW_DICTIONARY_CODES = auto()
    SHOW_DICTIONARY_STATISTICS = auto()
    SHOW_INFLECTIONS = auto()
    SHOW_INFLECTION_CODES = auto()
    SHOW_ORIGINAL_WORD = auto()
    SHOW_CLEAN_WORD = auto()
    DO_ONLY_STEMS = auto()
    DO_UNKNOWNS_ONLY = auto()
    DO_PLAY_WITH_STEMS = auto()
    DO_EXPERIMENTAL = auto()
    DO_LESSON = auto()
    # Boundary marker for array sizing
    MDEV_COUNT = auto()

# Whitaker's standard configuration file names
MDEV_FULL_NAME: Final[str] = "WORD.MDV"
STATS_FULL_NAME: Final[str] = "WORD.STA"

# --- Data Models ---

class DeveloperParameters(BaseModel):
    """
    Represents the internal state of developer configuration flags.
    Replaces the global Words_Mdev array in Ada.
    """
    model_config = ConfigDict(validate_assignment=True)

    # Initialized with default values matching the original system
    flags: List[bool] = Field(
        default_factory=lambda: [False] * MdevKind.MDEV_COUNT
    )

    def set_flag(self, kind: MdevKind, value: bool) -> None:
        self.flags[kind] = value

    def get_flag(self, kind: MdevKind) -> bool:
        return self.flags[kind]

# --- Custom Exceptions ---

class DeveloperParametersError(Exception):
    """Base exception for developer parameter operations."""
    pass

class BadMdevFileError(DeveloperParametersError):
    """Raised when the MDEV file is empty or corrupted."""
    pass

# --- Migration Service ---

class DeveloperParametersService:
    """
    Expert migration of Support_Utils.Developer_Parameters to Python 3.12+.
    Handles loading, saving, and managing developer mode state.
    """

    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = config_dir or Path(".")
        self.words_mdev = DeveloperParameters()
        self.stats_file: Optional[TextIO] = None

    def get_mdevs(self) -> None:
        """
        Implementation of procedure Get_Mdevs.
        Reads boolean flags from the WORD.MDV file.
        """
        mdev_path = self.config_dir / MDEV_FULL_NAME
        if not mdev_path.exists():
            raise FileNotFoundError(f"No {MDEV_FULL_NAME} file found")

        try:
            with open(mdev_path, "r") as f:
                content = f.read().strip()
                if not content:
                    raise BadMdevFileError("MDEV file is empty")
                
                # Logic: Read characters until enum bounds or EOF
                # In Whitaker's system, these are often T/F or 1/0
                for i, char in enumerate(content[:MdevKind.MDEV_COUNT]):
                    self.words_mdev.set_flag(MdevKind(i), char.upper() == 'T')
        except Exception as e:
            raise BadMdevFileError(f"Corrupted MDEV file: {e}")

    def put_mdevs(self) -> None:
        """
        Implementation of procedure Put_Mdevs.
        Serializes current flags back to the WORD.MDV file.
        """
        mdev_path = self.config_dir / MDEV_FULL_NAME
        with open(mdev_path, "w") as f:
            line = "".join(['T' if flag else 'F' for flag in self.words_mdev.flags])
            f.write(line)

    def initialize(self) -> None:
        """
        Implementation of Initialize_Developer_Parameters.
        Coordinates startup logic, file checking, and default assignment.
        """
        # Logic: Attempt to load from file; fall back to defaults on failure
        try:
            self.get_mdevs()
            print("MDEV_FILE found - Using those MDEVs and parameters")
        except (FileNotFoundError, BadMdevFileError):
            print("MDEV_FILE exists, but empty or corrupted - Default MDEVs used")
            # Defaults are already set in DeveloperParameters Pydantic model
        
        # Handle Statistics File initialization
        if self.words_mdev.get_flag(MdevKind.HAVE_STATISTICS_FILE):
            stats_path = self.config_dir / STATS_FULL_NAME
            self.stats_file = open(stats_path, "w")
            print(f"{STATS_FULL_NAME} Created at Initialization")

    def __del__(self):
        """Ensures file handles are closed on cleanup."""
        if self.stats_file:
            self.stats_file.close()

# --- Public API Stub ---

"""
class DeveloperParametersService:
    def initialize(self) -> None: ...
    def get_mdevs(self) -> None: ...
    def put_mdevs(self) -> None: ...
    words_mdev: DeveloperParameters
"""
