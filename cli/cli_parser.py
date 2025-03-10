import sys
from typing import Tuple, Optional
from models.seat import Seat
from config.constants import Action

def parse_arguments() -> Tuple[Optional[Action], Optional[Seat], Optional[int]]:
    """Parse command line arguments"""
    if len(sys.argv) != 4:
        return None, None, None

    action_str, seat_str, count_str = sys.argv[1:4]

    try:
        count = int(count_str)
        if count <= 0:
            raise ValueError
    except ValueError:
        return None, None, None

    action = Action(action_str.upper()) if action_str.upper() in Action.__members__ else None
    seat = Seat.from_str(seat_str)
    return action, seat, count