from __future__ import annotations
from pathlib import Path
from typing import Final, Optional
from pydantic import BaseModel, Field, ConfigDict, ValidationError

# --- Exceptions ---

class PatchError(Exception):
    """Base exception for the Patch utility[cite: 2587]."""
    pass


# --- Data Models ---

class PatchParams(BaseModel):
    """
    Expert migration of parameters for the Patch utility.
    Enforces non-negative constraints for padding to ensure valid gap size[cite: 2573].
    """
    model_config = ConfigDict(validate_assignment=True)

    input_path_1: Path
    input_path_2: Path
    output_path: Path
    n_blanks: int = Field(default=0, ge=0, description="Number of blank columns between files [cite: 2570, 2581]")


# --- Migration Service ---

class PatchService:
    """
    Expert migration of the 'Patch' Ada utility to Python 3.12+.
    Processes two files in parallel, joining corresponding lines into columns 
    with a user-defined spacing [cite: 2575-2576].
    """

    @staticmethod
    def run_interactive() -> None:
        """
        Interactive entry point replicating the procedural I/O workflow [cite: 2577-2583].
        """
        print("Takes in two files and produces a third which is the pair")
        print("as columns with N blanks between")
        print("Does this while there are corresponding lines in both files")

        try:
            # Input prompts matching Ada Put/Get_Line sequence [cite: 2577-2580]
            f1_name = input("What is first file to PATCH from => ").strip()
            print(f"=> {f1_name}")
            
            f2_name = input("What is second file to PATCH from => ").strip()
            print(f"=> {f2_name}")

            # Retrieving gap width [cite: 2581]
            n_input = input("How many blank columns to leave between => ").strip()
            n = int(n_input)
            print(f"{n}\n")

            # Output file resolution [cite: 2582-2583]
            out_name = input("Where to put the resulting PATCHed file => ").strip()
            print(f"=> {out_name}")

            params = PatchParams(
                input_path_1=Path(f1_name),
                input_path_2=Path(f2_name),
                output_path=Path(out_name),
                n_blanks=n
            )

            PatchService.execute(params)
            print("Finished PATCH [cite: 2586]")

        except (ValueError, ValidationError) as e:
            print(f"Invalid input or parameter constraint violation: {e}")
        except PatchError as e:
            print(f"Patch operation failed: {e}")
        except Exception:
            # Catch-all mirroring 'when others' block [cite: 2587]
            print("Unexpected exception in PATCH")

    @staticmethod
    def execute(params: PatchParams) -> None:
        """
        Core logic for side-by-side file patching [cite: 2584-2586].
        Iterates through files while lines exist in both.
        """
        if not params.input_path_1.exists():
            raise PatchError(f"First input file not found: {params.input_path_1}")
        if not params.input_path_2.exists():
            raise PatchError(f"Second input file not found: {params.input_path_2}")

        try:
            # Parallel file processing using context managers
            with (
                open(params.input_path_1, "r", encoding="utf-8") as f1,
                open(params.input_path_2, "r", encoding="utf-8") as f2,
                open(params.output_path, "w", encoding="utf-8") as out
            ):
                # Replicates logic: while not End_Of_File (F1) and not End_Of_File (F2) 
                # Python's zip handles the simultaneous termination logic natively.
                gap = " " * params.n_blanks
                for line1, line2 in zip(f1, f2):
                    # Replicate line concatenation logic [cite: 2585]
                    # We strip original newlines to control the output format precisely.
                    clean_l1 = line1.rstrip("\n\r")
                    clean_l2 = line2.rstrip("\n\r")
                    out.write(f"{clean_l1}{gap}{clean_l2}\n")

        except Exception as e:
            # Exception safety parity with Whitaker's catch-all [cite: 2587]
            raise PatchError(f"Unexpected error during file processing: {e}")

if __name__ == "__main__":
    PatchService.run_interactive()
