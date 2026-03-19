from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..support_utils.developer_parameters import DeveloperParametersService

class PutStatService:
    """
    Expert migration of the Words_Engine.Put_Stat procedure to Python 3.12+.
    Provides a centralized logging utility for internal engine statistics 
    and diagnostic traces [cite: 3566-3568].
    """

    @staticmethod
    def put_stat(developer_params: DeveloperParametersService, s: str) -> None:
        """
        Implementation of procedure Put_Stat .
        
        Writes a diagnostic string to the statistics file if the engine has 
        initialized the logging stream.
        
        Logic Parity:
        1. Checks if the 'Stats' file handle is active (replicates 'Ada.Text_IO.Is_Open') .
        2. Appends the string followed by a newline (replicates 'Ada.Text_IO.Put_Line') .
        """
        # Logic: Verify that the stats stream managed by DeveloperParameters is available 
        if developer_params.stats_file and not developer_params.stats_file.closed:
            # Replicates: Ada.Text_IO.Put_Line (Stats, S) 
            developer_params.stats_file.write(f"{s}\n")
            # Ensure immediate visibility for diagnostics
            developer_params.stats_file.flush()

# --- Public API Stub (.pyi equivalent) ---

"""
from ..support_utils.developer_parameters import DeveloperParametersService

class PutStatService:
    @staticmethod
    def put_stat(developer_params: DeveloperParametersService, s: str) -> None: ...
"""
