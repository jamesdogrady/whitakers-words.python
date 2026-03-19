import asyncio
from typing import Final
from .dictionary_package import DictionaryKind

# --- Custom Exceptions ---

class GeneralError(Exception):
    """Base exception for Latin_Utils.General operations[cite: 2539]."""
    pass

class DataError(GeneralError):
    """Raised when dictionary selection input is invalid."""
    pass

# --- Migration Service ---

class GeneralService:
    """
    Expert migration of Latin_Utils.General to Python 3.12+.
    Provides common functionality used across multiple main files that doesn't 
    fit elsewhere due to dependency graphs[cite: 2539].
    """

    @staticmethod
    async def load_dictionary() -> DictionaryKind:
        """
        Implementation of procedure Load_Dictionary.
        Interactively prompts the user to select a dictionary kind (General or Special).
        
        Returns:
            The selected DictionaryKind.
            
        Raises:
            DataError: If the user provides an invalid dictionary selection.
        """
        # Ada: Ada.Text_IO.Put ("What dictionary to use... =>"); [cite: 2548]
        prompt: Final[str] = "What dictionary to use, GENERAL or SPECIAL (Reply G or S) => "
        
        try:
            # Python's input() is blocking; in an asyncio environment, this would 
            # ideally be handled via a non-blocking stream reader, but for 
            # CLI parity with Whitaker's original tool, we use standard input.
            user_input = input(prompt).strip().lower() [cite: 2549]
            
            if not user_input:
                # Corresponds to 'if Last > 0' check in Ada 
                raise DataError("No input received.")

            # Logic: Check the first character to determine kind 
            if user_input.startswith('g'):
                return DictionaryKind.General [cite: 2549]
            
            elif user_input.startswith('s'):
                return DictionaryKind.Special [cite: 2550]
            
            else:
                # Ada: Ada.Text_IO.Put_Line ("No such dictionary"); raise Data_Error; 
                print("No such dictionary")
                raise DataError(f"Invalid dictionary selection: '{user_input}'")

        except EOFError:
            raise DataError("Input stream closed unexpectedly.")

# --- Public API Stub (.pyi equivalent) ---

"""
from .dictionary_package import DictionaryKind

class GeneralService:
    @staticmethod
    async def load_dictionary() -> DictionaryKind: ...
"""
