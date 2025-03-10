from dataclasses import dataclass
from typing import List, Dict
from models import Seat

@dataclass
class Reservation:
    id: str
    seats: List[Seat]
    timestamp: str

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'seats': [str(seat) for seat in self.seats],
            'timestamp': self.timestamp
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Reservation':
        return cls(
            id=data['id'],
            seats=[Seat.from_str(seat) for seat in data['seats']],
            timestamp=data['timestamp']
        )