from __future__ import annotations
from enum import Enum, auto
from pathlib import Path
from typing import Final, Optional, TextIO
from pydantic import BaseModel, Field, ConfigDict, ValidationError

# --- Exceptions ---

class SlashError(Exception):
    """Base exception for the Slash utility."""
    pass

class InvalidReplyError(SlashError):
    """Raised when the user provides an invalid split type (not C or L)."""
    pass

# --- Data Models ---

class ReplyType(Enum):
    """Expert migration of Reply_Type enumeration ."""
    COLUMNS = auto()
    LINES = auto()

class SlashParams(BaseModel):
    """
    Expert migration of parameters for the Slash utility.
    Enforces non-negative constraints for line/column counts[cite: 2648].
    """
    model_config = ConfigDict(validate_assignment=True)

    input_path: Path
    first_output_path: Path
    rest_output_path: Path
    split_type: ReplyType
    split_point: int = Field(default=0, ge=0, description="N lines/columns to split at")


# --- Migration Service ---

class SlashService:
    """
    Expert migration of the 'Slash' Ada utility to Python 3.12+.
    Breaks a text file into two separate files based on a horizontal (column) 
    or vertical (line count) split point[cite: 2631, 2654].
    """

    @staticmethod
    def run_interactive() -> None:
        """
        Interactive entry point replicating the procedural I/O workflow [cite: 2655-2660].
        """
        print("Breaks a file into two, by row or column.")

        try:
            # 1. Input file resolution [cite: 2655]
            f1_name = input("What file to SLASH from => ").strip()
            print(f"=> {f1_name}")
            input_path = Path(f1_name)
            if not input_path.exists():
                raise FileNotFoundError(f"Input file {f1_name} not found.")
            print("Opened input file")

            # 2. Split type selection [cite: 2656-2657]
            reply_char = input("Do you wish to SLASH C)olumns or L)ines? => ").strip().upper()
            if not reply_char:
                raise InvalidReplyError("Empty reply.")
            
            match reply_char[0]:
                case 'C': split_type = ReplyType.COLUMNS
                case 'L': split_type = ReplyType.LINES
                case _: raise InvalidReplyError("Wrong reply. Expected C or L.")
            print()

            # 3. Split point retrieval [cite: 2657-2658]
            n_input = input("How many lines/columns to leave after SLASHing => ").strip()
            n = int(n_input)
            print(f"{n}\n")

            # 4. Output path resolution [cite: 2658-2660]
            f2_name = input("Where to put the first  => ").strip()
            print(f"=> {f2_name}")
            print("Created SLASH file first")

            f3_name = input("Where to put the rest  => ").strip()
            print(f"=> {f3_name}")
            print("Created SLASH file rest")

            params = SlashParams(
                input_path=input_path,
                first_output_path=Path(f2_name),
                rest_output_path=Path(f3_name),
                split_type=split_type,
                split_point=n
            )

            SlashService.execute(params)
            print("Done SLASHing")

        except (ValueError, ValidationError):
            print("***************** WRONG REPLY *****************\n\nTry again")
        except InvalidReplyError:
            print("***************** WRONG REPLY *****************\n\nTry again")
        except Exception as e:
            # Catch-all mirroring 'when others' block [cite: 2670-2671]
            print(f"\n\nUnexpected exception raised in SLASH: {e}")

    @staticmethod
    def execute(params: SlashParams) -> None:
        """
        Core splitting logic based on the user-defined parameters [cite: 2661-2669].
        """
        if params.split_type == ReplyType.COLUMNS:
            SlashService._split_columns(params)
        else:
            SlashService._split_lines(params)

    @staticmethod
    def _split_columns(params: SlashParams) -> None:
        """
        Implementation of the Column split logic [cite: 2661-2664].
        Splits each line at index N.
        """
        n = params.split_point
        with (
            open(params.input_path, "r", encoding="utf-8") as f1,
            open(params.first_output_path, "w", encoding="utf-8") as f2,
            open(params.rest_output_path, "w", encoding="utf-8") as f3
        ):
            for line in f1:
                clean_line = line.rstrip("\n\r")
                # Logic: Line shorter than break or runs past break [cite: 2662-2664]
                # Replicates: if Ls <= N then ... else ...
                if len(clean_line) <= n:
                    f2.write(f"{clean_line}\n")
                    f3.write("\n")
                else:
                    # Ada 1..N maps to Python :n; N+1..Last maps to n:
                    f2.write(f"{clean_line[:n]}\n")
                    f3.write(f"{clean_line[n:]}\n")

    @staticmethod
    def _split_lines(params: SlashParams) -> None:
        """
        Implementation of the Line split logic [cite: 2665-2669].
        Writes the first N lines to the first file, and the rest to the second.
        """
        n = params.split_point
        with (
            open(params.input_path, "r", encoding="utf-8") as f1,
            open(params.first_output_path, "w", encoding="utf-8") as f2,
            open(params.rest_output_path, "w", encoding="utf-8") as f3
        ):
            # 1. Process the first N lines [cite: 2665-2667]
            # Replicates: for I in 1 .. N loop
            for i, line in enumerate(f1):
                if i < n:
                    f2.write(line)
                else:
                    # 2. Process the remaining lines [cite: 2667-2669]
                    # We have already consumed the line at index N; write it to F3
                    f3.write(line)
                    # Use the file iterator to consume the rest
                    for remaining_line in f1:
                        f3.write(remaining_line)
                    break

# --- Execution Entry Point ---

if __name__ == "__main__":
    SlashService.run_interactive()
