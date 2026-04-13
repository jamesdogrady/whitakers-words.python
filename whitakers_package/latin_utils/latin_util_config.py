from __future__ import annotations
import os
from typing import Final
from pydantic import BaseModel, Field, ConfigDict

# --- Dependencies (Representing the PARAMETERS package referenced in the source) ---

class ConfigParameters(BaseModel):
    """
    Holds global configuration state. 
    Enforces types for settings originally stored in the Ada Parameters package.
    """
    model_config = ConfigDict(validate_assignment=True)
    
    dictionary_path: str = Field(default="", description="Base directory for dictionary files")
    suppress_preface: bool = Field(default=False, description="Flag to silence introductory text")
    help_active: bool = Field(default=False, description="Flag to enable help output")

# --- Migration Service ---

class ConfigService:
    """
    Expert migration of the Latin_Utils.Config package to Python 3.12+.
    Provides centralized path resolution and system-wide flag access.
    """

    def __init__(self, parameters: ConfigParameters):
        self._params = parameters

    def path(self, file_name: str) -> str:
        """
        Implementation of function Path (File_Name : String) return String.
        
        Constructs a full file path by prepending the dictionary directory if configured.
        """
        # Ada: if Parameters.Dictionary_Path = "" then return File_Name;
        if not self._params.dictionary_path:
            return file_name
        
        # Ada: return Parameters.Dictionary_Path & "/" & File_Name;
        # Pythonic implementation uses os.path.join to ensure cross-platform compatibility (handling '/' vs '\')
        return os.path.join(self._params.dictionary_path, file_name)

    @property
    def suppress_preface(self) -> bool:
        """
        Implementation of function Suppress_Preface return Boolean.
        
        Directly maps to the global parameter for preface suppression.
        """
        return self._params.suppress_preface

    @property
    def help(self) -> bool:
        """
        Implementation of function Help return Boolean.
        
        Directly maps to the global parameter for help activation.
        """
        return self._params.help_active

# --- Public API Stub (.pyi equivalent) ---

"""
from pydantic import BaseModel

class ConfigParameters(BaseModel):
    dictionary_path: str
    suppress_preface: bool
    help_active: bool

class ConfigService:
    def __init__(self, parameters: ConfigParameters): ...
    def path(self, file_name: str) -> str: ...
    @property
    def suppress_preface(self) -> bool: ...
    @property
    def help(self) -> bool: ...
"""
