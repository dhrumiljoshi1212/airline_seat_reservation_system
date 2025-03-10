import unittest
from unittest.mock import patch
from cli.cli_parser import parse_arguments
from config.constants import Action
from models.seat import Seat

class TestCLIParser(unittest.TestCase):

    @patch('sys.argv', ['program', 'BOOK', 'A1', '2'])
    def test_parse_arguments_valid(self):
        action, seat, count = parse_arguments()
        self.assertEqual(action, Action.BOOK)
        self.assertEqual(seat, Seat(row='A', position=1, seat_type='aisle'))
        self.assertEqual(count, 2)

    @patch('sys.argv', ['program', 'INVALID', 'A1', '2'])
    def test_parse_arguments_invalid_action(self):
        action, seat, count = parse_arguments()
        self.assertIsNone(action)
        self.assertEqual(seat, Seat(row='A', position=1, seat_type='aisle'))
        self.assertEqual(count, 2)

    @patch('sys.argv', ['program', 'BOOK', 'A1', '-1'])
    def test_parse_arguments_invalid_count(self):
        action, seat, count = parse_arguments()
        self.assertIsNone(action)
        self.assertIsNone(seat)
        self.assertIsNone(count)

    @patch('sys.argv', ['program', 'BOOK', 'A1'])
    def test_parse_arguments_missing_arguments(self):
        action, seat, count = parse_arguments()
        self.assertIsNone(action)
        self.assertIsNone(seat)
        self.assertIsNone(count)

if __name__ == '__main__':
    unittest.main()