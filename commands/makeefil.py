from __future__ import annotations
from typing import Final, Optional, TextIO, BinaryIO
from pydantic import BaseModel, Field, ConfigDict
from pathlib import Path

# --- Dependencies (Imported from previously migrated modules) ---
from .latin_utils.inflections_package import PartOfSpeechType, FrequencyType
from .words_engine.english_support_package import (
    EwdsRecord, 
    NULL_EWDS_RECORD, 
    EnglishSupportService
)

# --- Exceptions ---

class MakeefilError(Exception):
    """Base exception for the Makeefil utility."""
    pass

# --- Migration Service ---

class MakeefilService:
    """
    Expert migration of the 'Makeefil' Ada utility to Python 3.12+.
    Processes a sorted English word list (EWDSLIST.GEN) to produce a binary 
    direct-access file (EWDSFILE.GEN), eliminating duplicates based on 
    priority rules.
    """

    def __init__(self, input_path: str = "EWDSLIST.GEN", output_path: str = "EWDSFILE.GEN"):
        self.input_path = Path(input_path)
        self.output_path = Path(output_path)
        self.number_of_ewords: int = 0

    def run(self) -> None:
        """
        Main execution loop: reads the text list and writes the optimized 
        binary direct-access file.
        """
        print(f"Processing {self.input_path} -> {self.output_path}...")

        if not self.input_path.exists():
            raise MakeefilError(f"Input file {self.input_path} not found.")

        try:
            # Replicates: Ewds_Direct_Io.Create (Ewds_File, Out_File, "EWDSFILE.GEN")
            with open(self.input_path, "r", encoding="ascii") as ewds_list, \
                 open(self.output_path, "wb") as ewds_file:
                
                # Initialization
                current_ewds = NULL_EWDS_RECORD
                
                # Logic: Read the first record to prime the loop
                # Replicates: Ewds_Record_Io.Get (Ewds_List, Ewds)
                line = ewds_list.readline()
                if line:
                    current_ewds, _ = EnglishSupportService.get_from_string(line)

                # Replicates: while not Ada.Text_IO.End_Of_File (Ewds_List) loop
                for line in ewds_list:
                    new_ewds, _ = EnglishSupportService.get_from_string(line)
                    
                    # Logic: Eliminate doubles/duplicates based on Word and Line Number
                    if current_ewds.w == new_ewds.w and current_ewds.n == new_ewds.n:
                        # Priority Rules:
                        # 1. Higher Kind value has priority
                        if current_ewds.kind < new_ewds.kind:
                            current_ewds = new_ewds
                        # 2. If Kind is equal, lower Semi value has priority
                        elif current_ewds.kind == new_ewds.kind:
                            if current_ewds.semi > new_ewds.semi:
                                current_ewds = new_ewds
                        # Otherwise (current_ewds.kind > new_ewds.kind), keep current
                    else:
                        # Word changed: Write the finalized record to the binary file
                        # Replicates: Write (Ewds_File, Ewds)
                        self._write_record(ewds_file, current_ewds)
                        current_ewds = new_ewds
                        self.number_of_ewords += 1

                # Write the final pending record
                if current_ewds != NULL_EWDS_RECORD:
                    self._write_record(ewds_file, current_ewds)
                    self.number_of_ewords += 1

            print(f"Finished: {self.number_of_ewords} English word records created.")

        except Exception as e:
            raise MakeefilError(f"Fatal error during English file creation: {e}")

    def _write_record(self, file: BinaryIO, record: EwdsRecord) -> None:
        """
        Helper to write a record in a format compatible with Direct_IO expectation.
        Delegates serialization to the EnglishSupportService.
        """
        # Note: Whitaker's direct files are often fixed-width text records 
        # that are read via Direct_IO as fixed-length strings.
        record_str = EnglishSupportService.put_to_string(record)
        file.write((record_str + "\n").encode("ascii"))

# --- Public API Stub (.pyi equivalent) ---

"""
class MakeefilService:
    def __init__(self, input_path: str = "EWDSLIST.GEN", output_path: str = "EWDSFILE.GEN"): ...
    def run(self) -> None: ...
"""

# --- Execution Entry Point ---

if __name__ == "__main__":
    try:
        service = MakeefilService()
        service.run()
    except MakeefilError as error:
        print(f"Error: {error}")
