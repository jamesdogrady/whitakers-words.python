from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict
from ..latin_utils.inflections_package import Meaning_Type, Null_Meaning_Type

# --- Core Data Models ---

class Explanations(BaseModel):
    """
    Expert migration of the Words_Engine.Explanation_Package record.
    Captures additional explanatory metadata generated during specific morphological 'tricks' 
    and specialized parsing paths (Syncope, Roman Numerals, etc.).
    """
    model_config = ConfigDict(validate_assignment=True)

    # Meaning text for orthographic 'tricks' (e.g., spelling variations)
    xxx_meaning: Meaning_Type = Field(default=Null_Meaning_Type, alias="Xxx_Meaning")
    
    # Meaning text for syncopated perfect forms (contracted vowels)
    yyy_meaning: Meaning_Type = Field(default=Null_Meaning_Type, alias="Yyy_Meaning")
    
    # Meaning text for unidentified or variant proper names
    nnn_meaning: Meaning_Type = Field(default=Null_Meaning_Type, alias="Nnn_Meaning")
    
    # Meaning text for Roman numerals found in text
    rrr_meaning: Meaning_Type = Field(default=Null_Meaning_Type, alias="Rrr_Meaning")
    
    # Meaning text for compounded words (e.g., prepositions joined to nouns)
    ppp_meaning: Meaning_Type = Field(default=Null_Meaning_Type, alias="Ppp_Meaning")


# --- Public API Stub (.pyi equivalent) ---

"""
from pydantic import BaseModel
from ..latin_utils.inflections_package import Meaning_Type

class Explanations(BaseModel):
    xxx_meaning: Meaning_Type
    yyy_meaning: Meaning_Type
    nnn_meaning: Meaning_Type
    rrr_meaning: Meaning_Type
    ppp_meaning: Meaning_Type
"""
