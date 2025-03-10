import unittest
from unittest.mock import patch, mock_open
from services.reservation_service import ReservationService
from models import Seat
from config.constants import DATA_FILE, LOCK_FILE
import contextlib

class TestReservationService(unittest.TestCase):
    def setUp(self):
        self.service = ReservationService(DATA_FILE, LOCK_FILE)
        self.seat = Seat(row='A', position=0, seat_type=Seat.determine_seat_type(0))

    @patch('builtins.open', new_callable=mock_open, read_data='{"reservations": {}, "seat_index": {}}')
    @patch('services.file_handler.FileHandler.save_data')
    def test_book_seats_success(self, mock_save_data, mock_open):
        with patch('services.file_handler.FileHandler.get_lock', return_value=contextlib.nullcontext()):
            result = self.service.book_seats(self.seat, 1)
            self.assertTrue(result)
            mock_save_data.assert_called_once()

    @patch('builtins.open', new_callable=mock_open, read_data='{"reservations": {}, "seat_index": {}}')
    @patch('services.file_handler.FileHandler.save_data')
    def test_book_seats_invalid_seat(self, mock_save_data, mock_open):
        invalid_seat = Seat(row='Z', position=0, seat_type='WINDOW')
        result = self.service.book_seats(invalid_seat, 1)
        self.assertFalse(result)
        mock_save_data.assert_not_called()

    @patch('builtins.open', new_callable=mock_open, read_data='{"reservations": {}, "seat_index": {}}')
    @patch('services.file_handler.FileHandler.save_data')
    def test_cancel_reservation_not_found(self, mock_save_data, mock_open):
        with patch('services.file_handler.FileHandler.get_lock', return_value=contextlib.nullcontext()):
            result = self.service.cancel_reservation(self.seat, 1)
            self.assertFalse(result)
            mock_save_data.assert_not_called()

    @patch('builtins.open', new_callable=mock_open, read_data='{"reservations": {"1234": {"seats": ["A0 (window)"], "timestamp": "2023-10-10T10:00:00"}}, "seat_index": {"A0 (window)": "1234"}}')
    @patch('services.file_handler.FileHandler.save_data')
    def test_book_seats_already_reserved(self, mock_save_data, mock_open):
        with patch('services.file_handler.FileHandler.get_lock', return_value=contextlib.nullcontext()):
            result = self.service.book_seats(self.seat, 1)
            self.assertFalse(result)
            mock_save_data.assert_not_called()

    @patch('builtins.open', new_callable=mock_open, read_data='{"reservations": {}, "seat_index": {}}')
    @patch('services.file_handler.FileHandler.save_data')
    def test_book_seats_invalid_position(self, mock_save_data, mock_open):
        invalid_seat = Seat(row='A', position=10, seat_type='WINDOW')
        result = self.service.book_seats(invalid_seat, 1)
        self.assertFalse(result)
        mock_save_data.assert_not_called()

    @patch('builtins.open', new_callable=mock_open,
           read_data='{"reservations": {"1234": {"seats": ["A0 (window)"], "timestamp": "2023-10-10T10:00:00"}}, "seat_index": {"A0 (window)": "1234"}}')
    @patch('services.file_handler.FileHandler.save_data')
    def test_cancel_reservation_success(self, mock_save_data, mock_open):
        with patch('services.file_handler.FileHandler.get_lock', return_value=contextlib.nullcontext()):
            result = self.service.cancel_reservation(self.seat, 1)
            self.assertTrue(result)
            mock_save_data.assert_called_once()


if __name__ == '__main__':
    unittest.main()