import unittest
from unittest.mock import patch, mock_open
from services.file_handler import FileHandler
import portalocker

class TestFileHandler(unittest.TestCase):
    def setUp(self):
        self.data_file = 'test_data.json'
        self.lock_file = 'test_lock.lock'
        self.file_handler = FileHandler(self.data_file, self.lock_file)

    @patch('builtins.open', new_callable=mock_open)
    def test_initialize_files(self, mock_open):
        self.file_handler.initialize_files()
        mock_open.assert_any_call(self.data_file, 'w')
        mock_open.assert_any_call(self.lock_file, 'w')

    @patch('builtins.open', new_callable=mock_open)
    @patch('portalocker.lock')
    @patch('portalocker.unlock')
    def test_get_lock_success(self, mock_unlock, mock_lock, mock_open):
        mock_file = mock_open.return_value
        with self.file_handler.get_lock(mock_file):
            mock_lock.assert_called_once_with(mock_file, portalocker.LOCK_EX | portalocker.LOCK_NB)
        mock_unlock.assert_called_once_with(mock_file)

    @patch('builtins.open', new_callable=mock_open)
    @patch('portalocker.lock', side_effect=portalocker.exceptions.LockException)
    def test_get_lock_timeout(self, mock_lock, mock_open):
        mock_file = mock_open.return_value
        with self.assertRaises(TimeoutError):
            with self.file_handler.get_lock(mock_file, timeout=1, interval=0.1):
                pass

    @patch('builtins.open', new_callable=mock_open, read_data='{"reservations": {}, "seat_index": {}}')
    def test_load_data_success(self, mock_open):
        mock_file = mock_open.return_value
        data = self.file_handler.load_data(mock_file)
        self.assertEqual(data, {"reservations": {}, "seat_index": {}})

    @patch('builtins.open', new_callable=mock_open, read_data='')
    def test_load_data_empty_file(self, mock_open):
        mock_file = mock_open.return_value
        data = self.file_handler.load_data(mock_file)
        self.assertEqual(data, {"reservations": {}, "seat_index": {}})


if __name__ == '__main__':
    unittest.main()