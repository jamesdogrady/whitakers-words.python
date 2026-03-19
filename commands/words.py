import sys
import asyncio
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict

# --- Dependencies (Imported from previously migrated modules) ---
from .config import ConfigurationMode, ExecutionMethod
from .words_main import WordsMainService
from .word_parameters import WordParametersService
from .developer_parameters import DeveloperParametersService

# --- Custom Exceptions ---

class WordsSystemError(Exception):
    """Base exception for the WORDS top-level procedure."""
    pass

class AdaNameError(WordsSystemError):
    """Equivalent to Ada.Text_IO.NAME_ERROR."""
    pass

# --- State Management ---

class WordsState(BaseModel):
    """
    Maintains the global execution state for the WORDS system.
    Enforces constraints found in the Ada source.
    """
    model_config = ConfigDict(validate_assignment=True)

    configuration: ConfigurationMode = ConfigurationMode.USER_VERSION
    method: Optional[ExecutionMethod] = None
    suppress_preface: bool = False
    input_line: str = Field(default="", max_length=250)
    change_language_character: str = "^"

# --- Main System Service ---

class WordsService:
    """
    Expert migration of the 'procedure WORDS' entry point to Python 3.12+.
    Coordinates between interactive, file-based, and command-line input modes.
    """

    def __init__(self, args: List[str]):
        self.args = args[1:]  # Exclude script name (sys.argv[0])
        self.state = WordsState()
        self.arg_count = len(self.args)
        self.arguments_start = 0
        self.main_engine = WordsMainService(args)

    async def run(self) -> None:
        """
        Main execution flow mapping to the Ada 'WORDS' procedure.
        Handles the logic for determining how the program was invoked.
        """
        try:
            # 1. Logic based on argument count
            # No arguments implies interactive keyboard mode.
            if self.arg_count == 0:
                await self._execute_interactive_mode()
            else:
                await self._execute_command_line_mode()

        except Exception as e:
            # Ada: exception when others => PUT_LINE("WORDS terminated...");
            print(f"WORDS terminated on exception: {e}", file=sys.stderr)
            sys.exit(1)

    async def _execute_interactive_mode(self) -> None:
        """Handles simple execution with no parameters."""
        self.state.method = ExecutionMethod.INTERACTIVE
        self.state.suppress_preface = False
        
        # Invoke the core engine with default user configuration
        await self.main_engine.run(ConfigurationMode.USER_VERSION)

    async def _execute_command_line_mode(self) -> None:
        """
        Handles execution with file names or direct word input.
        Maps the complex logic for argument interpretation.
        """
        self.state.suppress_preface = True  # Default for non-interactive

        # Handle Language Shift (e.g., ^E for English)
        if self.arg_count > 0 and self.args[0].startswith(self.state.change_language_character):
            if len(self.args[0]) > 1:
                # Actual logic for shifting dictionary context resides in WordParametersService
                self.arguments_start = 1
            self.state.method = ExecutionMethod.COMMAND_LINE_INPUT

        # One Argument: Could be a file to process or a word to translate
        if self.arg_count == 1:
            arg = self.args[0].strip()
            try:
                # Check if the argument refers to a valid file path
                if Path(arg).exists():
                    self.state.method = ExecutionMethod.COMMAND_LINE_FILES
                else:
                    raise AdaNameError
            except (AdaNameError, OSError):
                # If not a file, treat as a single word/phrase
                self.state.method = ExecutionMethod.COMMAND_LINE_INPUT

        # Multiple Arguments: Check if the first is a file
        elif self.arg_count >= 2:
            try:
                if Path(self.args[0]).exists():
                    self.state.method = ExecutionMethod.COMMAND_LINE_FILES
                else:
                    self.state.method = ExecutionMethod.COMMAND_LINE_INPUT
            except (AdaNameError, OSError):
                self.state.method = ExecutionMethod.COMMAND_LINE_INPUT

        # Final dispatch to the engine
        await self.main_engine.run(ConfigurationMode.USER_VERSION)

# --- Entry Point ---

async def main():
    service = WordsService(sys.argv)
    await service.run()

if __name__ == "__main__":
    asyncio.run(main())
