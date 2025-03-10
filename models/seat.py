from dataclasses import dataclass
from typing import Optional


@dataclass
class Seat:
    row: str
    position: int
    seat_type: str

    def __str__(self) -> str:
        return f"{self.row}{self.position} ({self.seat_type})"

    @classmethod
    def from_str(cls, seat_id: str) -> Optional['Seat']:
        """Parse a seat string like 'A0' into a Seat object"""
        if not seat_id or len(seat_id) < 2:
            return None

        row = seat_id[0].upper()
        try:
            position = int(seat_id[1:])
            seat_type = cls.determine_seat_type(position)
            return cls(row=row, position=position, seat_type=seat_type)
        except ValueError:
            return None

    @staticmethod
    def determine_seat_type(position: int) -> str:
        """Determine the seat type based on the position"""
        if position in [0, 7]:
            return 'window'
        elif position in [1, 2, 5, 6]:
            return 'aisle'
        else:
            return 'middle'
