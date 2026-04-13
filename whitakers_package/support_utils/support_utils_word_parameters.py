from __future__ import annotations
from enum import IntEnum, auto
from typing import Final, List, Optional, TextIO
from pydantic import BaseModel, Field, ConfigDict
from pathlib import Path

# --- Dependencies (Imported from previously migrated modules) ---
from .latin_utils.preface import PrefaceService as Preface

# --- Core Enumerations and Constants ---

class ModeKind(IntEnum):
    """
    Expert migration of Mode_Kind enumeration.
    Defines runtime behavior flags for the Latin dictionary engine.
    """
    HAVE_OUTPUT_FILE = 0
    WRITE_UNKNOWNS_TO_FILE = auto()
    # Boundary marker for array sizing
    MODE_COUNT = auto()

class ExecutionMethod(IntEnum):
    """Mapped from Method_Type in Whitaker's system."""
    INTERACTIVE = 0
    COMMAND_LINE_INPUT = auto()
    # Other methods as defined in the legacy spec

# Whitaker's standard configuration file names
MODE_FULL_NAME: Final[str] = "WORD.MOD"
OUTPUT_FULL_NAME: Final[str] = "WORD.OUT"
UNKNOWNS_FULL_NAME: Final[str] = "WORD.UNK"

# --- Data Models ---

class WordParameters(BaseModel):
    """
    Represents the internal state of runtime mode flags.
    Replaces the global Words_Mode array in Ada.
    """
    model_config = ConfigDict(validate_assignment=True)

    # Initialized with default values
    flags: List[bool] = Field(
        default_factory=lambda: [False] * ModeKind.MODE_COUNT
    )

    def set_flag(self, kind: ModeKind, value: bool) -> None:
        self.flags[kind] = value

    def get_flag(self, kind: ModeKind) -> bool:
        return self.flags[kind]

# --- Custom Exceptions ---

class WordParametersError(Exception):
    """Base exception for word parameter operations."""
    pass

class BadModeFileError(WordParametersError):
    """Raised when the MODE file is empty or corrupted."""
    pass

# --- Migration Service ---

class WordParametersService:
    """
    Expert migration of Support_Utils.Word_Parameters to Python 3.12+.
    Handles loading, saving, and managing runtime mode state and associated files.
    """

    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = config_dir or Path(".")
        self.words_mode = WordParameters()
        self.output_file: Optional[TextIO] = None
        self.unknowns_file: Optional[TextIO] = None

    def get_modes(self) -> None:
        """
        Implementation of procedure Get_Modes.
        Reads boolean flags from the WORD.MOD file.
        """
        mode_path = self.config_dir / MODE_FULL_NAME
        if not mode_path.exists():
            raise FileNotFoundError(f"No {MODE_FULL_NAME} file found")

        try:
            with open(mode_path, "r") as f:
                content = f.read().strip()
                if not content:
                    raise BadModeFileError("MODE file is empty")
                
                # Logic: Read characters until enum bounds or EOF
                for i, char in enumerate(content[:ModeKind.MODE_COUNT]):
                    self.words_mode.set_flag(ModeKind(i), char.upper() == 'T')
        except Exception as e:
            raise BadModeFileError(f"Corrupted MODE file: {e}")

    def put_modes(self) -> None:
        """
        Implementation of procedure Put_Modes.
        Serializes current flags back to the WORD.MOD file.
        """
        mode_path = self.config_dir / MODE_FULL_NAME
        with open(mode_path, "w") as f:
            line = "".join(['T' if flag else 'F' for flag in self.words_mode.flags])
            f.write(line)

    def initialize(self, method: ExecutionMethod) -> None:
        """
        Implementation of Initialize_Word_Parameters.
        Coordinates mode loading and file handle creation.
        """
        # 1. Handle Mode File
        try:
            self.get_modes()
        except FileNotFoundError:
            # Replicates 'when Name_Error => Words_Mode := Default_Mode_Array'
            pass 
        except BadModeFileError:
            # Replicates 'when Bad_Mode_File => ...'
            Preface.put_line("MODE_FILE exists, but empty or corrupted - Default modes used")
            Preface.put_line("You can set new parameters with CHANGE PARAMETERS and save.")
        except Exception:
            Preface.put_line("MODE_FILE others ERROR")

        # 2. Open Output File
        is_output_requested = (
            method in (ExecutionMethod.INTERACTIVE, ExecutionMethod.COMMAND_LINE_INPUT) 
            and self.words_mode.get_flag(ModeKind.HAVE_OUTPUT_FILE)
        )
        if is_output_requested:
            output_path = self.config_dir / OUTPUT_FULL_NAME
            self.output_file = open(output_path, "w")
            Preface.put_line(f"{OUTPUT_FULL_NAME} Created at Initialization")

        # 3. Open Unknowns File
        if self.words_mode.get_flag(ModeKind.WRITE_UNKNOWNS_TO_FILE):
            unk_path = self.config_dir / UNKNOWNS_FULL_NAME
            self.unknowns_file = open(unk_path, "w")
            Preface.put_line(f"{UNKNOWNS_FULL_NAME} Created at Initialization")

    def __del__(self):
        """Ensures file handles are closed on cleanup."""
        if self.output_file:
            self.output_file.close()
        if self.unknowns_file:
            self.unknowns_file.close()

# --- Public API Stub (.pyi equivalent) ---

"""
class WordParametersService:
    def initialize(self, method: ExecutionMethod) -> None: ...
    def get_modes(self) -> None: ...
    def put_modes(self) -> None: ...
    words_mode: WordParameters
"""
