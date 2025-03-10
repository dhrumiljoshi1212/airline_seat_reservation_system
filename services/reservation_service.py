import logging
from typing import List, Optional, Set
from uuid import uuid4
from datetime import datetime
from models import Seat, Reservation
from services import FileHandler
from config.constants import ROWS, ROW_LAYOUT

logger = logging.getLogger('airline_reservation')

class ReservationService:
    def __init__(self, data_file: str, lock_file):
        self.file_handler = FileHandler(data_file, lock_file)
        self.file_handler.initialize_files()

    def _load_reserved_seats(self) -> Set[str]:
        with open(self.file_handler.data_file, 'r') as f:
            data = self.file_handler.load_data(f)
            return set(data['seat_index'].keys())

    @staticmethod
    def is_valid_seat(seat: Seat) -> bool:
        if seat.row < 'A' or seat.row > chr(ord('A') + ROWS - 1):
            return False
        return seat.position in ROW_LAYOUT

    def is_seat_reserved(self, seat: Seat, data=None) -> bool:
        if data is None:
            with open(self.file_handler.data_file, 'r') as f:
                data = self.file_handler.load_data(f)
        return str(seat) in data['seat_index']

    @staticmethod
    def get_consecutive_seats(start_seat: Seat, count: int) -> List[Seat]:
        row = start_seat.row
        try:
            start_idx = ROW_LAYOUT.index(start_seat.position)
        except ValueError:
            return []
        if start_idx + count > len(ROW_LAYOUT):
            return []
        return [
            Seat(row=row, position=ROW_LAYOUT[i], seat_type=Seat.determine_seat_type(ROW_LAYOUT[i]))
            for i in range(start_idx, start_idx + count)
        ]

    def book_seats(self, start_seat: Seat, count: int) -> Optional[bool]:
        try:
            seats_to_book = self.get_consecutive_seats(start_seat, count)
            if len(seats_to_book) != count:
                return False
            for seat in seats_to_book:
                if not self.is_valid_seat(seat):
                    return False
            with open(self.file_handler.lock_file, 'r+') as lock_file:
                with self.file_handler.get_lock(lock_file):
                    with open(self.file_handler.data_file, 'r+') as f:
                        data = self.file_handler.load_data(f)
                        for seat in seats_to_book:
                            if self.is_seat_reserved(seat, data):
                                return False
                        data = self.file_handler.load_data(f)
                        reservation_id = str(uuid4())
                        timestamp = datetime.now().isoformat()
                        reservation = Reservation(
                            id=reservation_id,
                            seats=seats_to_book,
                            timestamp=timestamp
                        )
                        data['reservations'][reservation_id] = reservation.to_dict()
                        for seat in seats_to_book:
                            data['seat_index'][str(seat)] = reservation_id
                        self.file_handler.save_data(data)
                        logger.info(f"Booked seats: {[str(seat) for seat in seats_to_book]} with reservation ID: {reservation_id}")
                        return True
        except Exception as e:
            logger.error(f"Booking error: {e}", exc_info=True)
            return False

    def cancel_reservation(self, start_seat: Seat, count: int) -> Optional[bool]:
        try:
            seats_to_cancel = self.get_consecutive_seats(start_seat, count)
            if len(seats_to_cancel) != count:
                logger.warning(f"Failed to find {count} consecutive seats from {start_seat}")
                return False

            seats_to_cancel_str = [str(seat) for seat in seats_to_cancel]

            with open(self.file_handler.lock_file, 'r+') as lock_file:
               with self.file_handler.get_lock(lock_file):
                   with open(self.file_handler.data_file, 'r+') as f:
                        data = self.file_handler.load_data(f)

                        # Group seats by their reservation ID
                        reservation_seats = {}
                        for seat_str in seats_to_cancel_str:
                            reservation_id = data['seat_index'].get(seat_str)
                            if reservation_id:
                                if reservation_id not in reservation_seats:
                                    reservation_seats[reservation_id] = []
                                reservation_seats[reservation_id].append(seat_str)
                            else:
                                logger.warning(f"No reservation found for seat: {seat_str}")
                                return False

                        # Remove seats from their respective reservations
                        for reservation_id, seats in reservation_seats.items():
                            reservation = data['reservations'][reservation_id]
                            remaining_seats = [seat for seat in reservation['seats'] if seat not in seats]

                            if not remaining_seats:
                                # If no seats are left in the reservation, remove the entire reservation
                                del data['reservations'][reservation_id]
                            else:
                                # Otherwise, update the reservation with the remaining seats
                                reservation['seats'] = remaining_seats
                                data['reservations'][reservation_id] = reservation

                            # Remove the seats from the seat_index
                            for seat in seats:
                                del data['seat_index'][seat]

                        self.file_handler.save_data(data)
                        logger.info(f"Cancelled seats: {seats_to_cancel_str}")
                        return True
        except Exception as e:
            logger.error(f"Cancellation error: {e}", exc_info=True)
            return False