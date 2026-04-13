import asyncio
import sys
from pathlib import Path
from typing import Final, Optional

from pydantic import BaseModel, Field, ConfigDict

# --- Dependencies (Imported from previously migrated modules) ---
from .english_support_package import EWordRecord, EnglishSupportService, EWDS_DIRECT_IO
from .latin_utils_config import LatinUtilsConfig

# --- Custom Exceptions ---

class MakeEFileError(Exception):
    """Base exception for MAKEEFIL processing errors."""
    pass

# --- Migration Service ---

class MakeEFileService:
    """
    Expert migration of the Ada MAKEEFIL procedure to Python 3.12+.
    Processes English word lists, eliminates duplicates based on priority logic, 
    and generates the binary English dictionary file.
    """

    def __init__(self):
        self.support_service = EnglishSupportService()
        self.config = LatinUtilsConfig()
        self.number_of_ewords: int = 0  # [cite: 54, 55, 57]
        self.input_name: Final[str] = "EWDSLIST.GEN"  # [cite: 46]
        self.output_name: Final[str] = "EWDSFILE.GEN"  # [cite: 46]

    async def run_conversion(self) -> None:
        """
        Main execution logic for the MAKEEFIL procedure.
        Implements the duplicate elimination and priority selection loop.
        """
        self.number_of_ewords = 0
        ewds: Optional[EWordRecord] = None  # Current record buffer [cite: 46]
        
        try:
            input_path = self.config.get_path(self.input_name)  # [cite: 46]
            
            # Open files: Input text list and Output binary direct-access file [cite: 46]
            async with self.support_service.open_ewds_list(input_path) as ewds_list, \
                       EWDS_DIRECT_IO.create(self.output_name) as ewds_file:
                
                # Main iteration loop [cite: 47]
                async for new_ewds in ewds_list.stream_records():
                    # Initial record handling
                    if ewds is None:
                        ewds = new_ewds
                        continue

                    # Eliminate doubles logic 
                    # Records match if Word (W) and Index (N) are identical
                    if ewds.w == new_ewds.w and ewds.n == new_ewds.n:
                        
                        # Priority 1: Higher KIND (Large KIND = high priority) [cite: 50, 51]
                        if ewds.kind > new_ewds.kind:
                            pass  # Keep current record
                        elif ewds.kind < new_ewds.kind:
                            ewds = new_ewds
                        
                        # Priority 2: If KIND is equal, smaller SEMI wins [cite: 52]
                        elif ewds.kind == new_ewds.kind:
                            if ewds.semi > new_ewds.semi:
                                ewds = new_ewds
                        
                        # [cite: 53]
                    else:
                        # Write the unique/winning record to binary file [cite: 53]
                        await ewds_file.write(ewds)
                        self.number_of_ewords += 1  # [cite: 54]
                        ewds = new_ewds
                
                # Write final buffered record [cite: 54]
                if ewds:
                    await ewds_file.write(ewds)
                    self.number_of_ewords += 1

            print(f"\nNUMBER_OF_EWORDS = {self.number_of_ewords}")  # [cite: 55]

        except Exception as e:
            # Ada 'when others' handler [cite: 56]
            print(f"\nMAKEEFIL terminated on an exception: {e}", file=sys.stderr)
            print(f"NUMBER_OF_EWORDS = {self.number_of_ewords}")  # [cite: 57]
            raise MakeEFileError(str(e))

# --- Public API Stubs ---

async def main():
    service = MakeEFileService()
    await service.run_conversion()

if __name__ == "__main__":
    asyncio.run(main())
