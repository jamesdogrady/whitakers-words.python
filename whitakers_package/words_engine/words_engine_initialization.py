from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Dependency services assumed to follow the established project migration pattern
    from .support_utils.word_parameters import WordParametersService
    from .support_utils.developer_parameters import DeveloperParametersService
    from .words_engine.word_package import WordPackageService

class InitializationService:
    """
    Expert migration of Words_Engine.Initialization to Python 3.12+.
    Coordinates the engine-wide setup by triggering the initialization 
    sequences for word parameters, developer settings, and the core lookup package.
    """

    def __init__(
        self,
        word_params: WordParametersService,
        developer_params: DeveloperParametersService,
        word_package: WordPackageService
    ):
        """
        Dependency injection for the component initialization services.
        """
        self._word_params = word_params
        self._developer_params = developer_params
        self._word_package = word_package

    def initialize_engine(self) -> None:
        """
        Implementation of procedure Initialize_Engine.
        Sequentially executes the three core setup routines defined in the 
        Ada package body.
        """
        # 1. Initialize Word Parameters
        # Replicates call to Support_Utils.Word_Parameters.Initialize_Word_Parameters
        self._word_params.initialize()

        # 2. Initialize Developer Parameters
        # Replicates call to Support_Utils.Developer_Parameters.Initialize_Developer_Parameters
        self._developer_params.initialize()

        # 3. Initialize Word Package logic
        # Replicates call to Words_Engine.Word_Package.Initialize_Word_Package
        self._word_package.initialize()

# --- Public API Stub (.pyi equivalent) ---

"""
from .support_utils.word_parameters import WordParametersService
from .support_utils.developer_parameters import DeveloperParametersService
from .words_engine.word_package import WordPackageService

class InitializationService:
    def __init__(self, 
                 word_params: WordParametersService, 
                 developer_params: DeveloperParametersService, 
                 word_package: WordPackageService): ...
    def initialize_engine(self) -> None: ...
"""
