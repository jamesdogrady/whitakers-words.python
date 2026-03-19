import asyncio
import sys
from typing import List, NoReturn

# --- Dependencies (Imported from previously migrated modules) ---
from .config import ConfigurationType, ConfigurationMode, ExecutionMethod
from .word_parameters import WordParametersService
from .developer_parameters import DeveloperParametersService
from .preface import PrefaceService, PrefaceConfig
from .banner import BannerService
from .process_input import ProcessInputService
from .parse import ParseService
from .dictionary_package import DictionaryIO

# --- Custom Exceptions ---

class WordsMainError(Exception):
    """Base exception for the WORDS_MAIN top-level procedure."""
    pass

# --- Logic Implementation ---

class WordsMainService:
    """
    Expert migration of the Ada WORDS_MAIN procedure to Python 3.12+.
    Serves as the primary entry point controller for the Latin dictionary engine.
    """

    def __init__(self, args: List[str]):
        self.args = args[1:]  # Exclude script name (sys.argv[0])
        self.config = PrefaceConfig(suppress_preface=False)
        self.preface = PrefaceService(self.config)
        
        # Core Engine Services
        self.dev_params = DeveloperParametersService()
        self.word_params = WordParametersService(self.args)
        self.dict_io = DictionaryIO()
        self.parse_service = ParseService()
        self.banner = BannerService(self.preface)
        
        # Input Processor
        self.processor = ProcessInputService(
            preface=self.preface,
            parse_service=self.parse_service,
            word_params=self.word_params,
            dev_params=self.dev_params,
            dict_io=self.dict_io,
            banner=self.banner
        )

    async def run(self, configuration: ConfigurationType = ConfigurationMode.USER_VERSION) -> NoReturn:
        """
        Main execution flow mapping to 'procedure WORDS_MAIN'.
        Coordinates initialization and hands off to the input processor.
        """
        try:
            # 1. Initialization Phase
            # Ada: INITIALIZE_WORD_PARAMETERS(METHOD, COMMAND_LINE);
            await self.word_params.initialize_word_parameters()
            
            # Ada: INITIALIZE_DEVELOPER_PARAMETERS;
            await self.dev_params.initialize_developer_parameters()

            # 2. Input Processing Phase
            # Ada: PROCESS_INPUT(CONFIGURATION, COMMAND_LINE);
            await self.processor.process_input(
                configuration=configuration,
                command_line=self.word_params.command_line_string
            )

        except Exception as e:
            # Ada: exception when others => PUT_LINE("WORDS_MAIN terminated...");
            self.preface.put_line(f"\nWORDS_MAIN terminated on an exception: {e}")
            sys.exit(1)
        
        sys.exit(0)

# --- Public API / Entry Point ---

async def main():
    """Execution entry point for the standalone WORDS application."""
    service = WordsMainService(sys.argv)
    
    # Default to USER_VERSION as per original procedure spec
    await service.run(ConfigurationMode.USER_VERSION)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # Graceful exit for interactive users
        sys.exit(0)
