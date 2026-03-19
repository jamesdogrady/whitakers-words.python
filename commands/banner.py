from __future__ import annotations
import asyncio
from typing import Final
from pydantic import BaseModel, ConfigDict

# --- Dependencies (Imported from previously migrated modules) ---
from .preface import PrefaceService

# --- Constants ---

VERSION: Final[str] = "1.97ED"  #

# --- Custom Exceptions ---

class BannerError(Exception):
    """Base exception for banner display operations."""
    pass

# --- Migration Service ---

class BannerService:
    """
    Expert migration of the Ada BANNER package to Python 3.12+.
    Provides standardized header output for all 'WORDS' system utilities.
    """

    def __init__(self, preface: PrefaceService):
        self.preface = preface

    async def banner_words(self) -> None:
        """Displays the main WORDS program banner."""
        self.preface.new_line(2)  #
        self.preface.set_col(10)  #
        self.preface.put_line(f"WORDS {VERSION}")  #
        self.preface.set_col(10)  #
        self.preface.put_line("Latin Dictionary Program")  #
        self._put_attribution()

    async def banner_meanings(self) -> None:
        """Displays the MEANINGS utility banner."""
        self.preface.new_line(2)  #
        self.preface.set_col(10)  #
        self.preface.put_line(f"MEANINGS {VERSION}")  #
        self.preface.set_col(10)  #
        self.preface.put_line("Latin Dictionary Program")  #
        self._put_attribution()

    async def banner_makedict(self) -> None:
        """Displays the MAKEDICT utility banner."""
        self.preface.new_line(2)  #
        self.preface.set_col(10)  #
        self.preface.put_line(f"MAKEDICT {VERSION}")  #
        self.preface.set_col(10)  #
        self.preface.put_line("Latin Dictionary Program - Dictionary Maintenance")  #
        self._put_attribution()

    async def banner_makeinfl(self) -> None:
        """Displays the MAKEINFL utility banner."""
        self.preface.new_line(2)  #
        self.preface.set_col(10)  #
        self.preface.put_line(f"MAKEINFL {VERSION}")  #
        self.preface.set_col(10)  #
        self.preface.put_line("Latin Dictionary Program - Inflection Maintenance")  #
        self._put_attribution()

    async def banner_makestem(self) -> None:
        """Displays the MAKESTEM utility banner."""
        self.preface.new_line(2)  #
        self.preface.set_col(10)  #
        self.preface.put_line(f"MAKESTEM {VERSION}")  #
        self.preface.set_col(10)  #
        self.preface.put_line("
