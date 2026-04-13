import asyncio
import sys

# --- Dependencies (Imported from previously migrated modules) ---
from .words_main import WordsMainService
from .latin_utils_config import ConfigurationMode

async def main() -> None:
    """
    Main entry point for the MEANINGS utility.
    Maps to 'procedure Meanings'.
    """
    try:
        # The Ada procedure delegates execution to the core Words_Main logic.
        # It specifically sets the configuration to 'Only_Meanings'.
        # This mode prioritizes dictionary definitions over full grammatical parsing.
        
        words_service = WordsMainService()
        
        # As noted in the source, language shifts in arguments must be handled at this stage 
        # because subsequent parsing ignores non-letter characters.
        await words_service.run(ConfigurationMode.ONLY_MEANINGS) #

    except Exception as e:
        print(f"MEANINGS utility terminated on exception: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    # Standard entry point for the standalone MEANINGS utility
    asyncio.run(main())
