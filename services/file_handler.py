import os
import json
import tempfile
import logging
import time
import portalocker
import contextlib
from typing import Dict, Any, Generator

logger = logging.getLogger('airline_reservation')

class FileHandler:
    def __init__(self, data_file: str, lock_file: str):
        self.data_file = data_file
        self.lock_file = lock_file

    def initialize_files(self) -> None:
        """Initialize the data file if it doesn't exist"""
        if not os.path.exists(self.data_file):
            with open(self.data_file, 'w') as f:
                json.dump({'reservations': {}, 'seat_index': {}}, f)
        if not os.path.exists(self.lock_file):
            with open(self.lock_file, 'w') as f:
                pass

    @contextlib.contextmanager
    def get_lock(self, file_handle, timeout: int = 20, interval: float = 0.1) -> Generator[None, Any, None]:
            """Context manager for file locking."""
            start_time = time.time()
            end_time = start_time + timeout
            while time.time() < end_time:
                try:
                    portalocker.lock(file_handle, portalocker.LOCK_EX | portalocker.LOCK_NB)
                    logger.info("Successfully acquired file lock")
                    try:
                        yield
                    finally:
                        portalocker.unlock(file_handle)
                        logger.info("Successfully released file lock")
                    return
                except portalocker.exceptions.LockException:
                    logger.debug("File is locked, retrying in %.1f seconds...", interval)
                    time.sleep(interval)
            logger.error("Timeout while trying to acquire file lock after %d seconds", timeout)
            raise TimeoutError("Could not acquire file lock within the specified timeout")

    @staticmethod
    def load_data(file_handle) -> Dict:
        """Load reservation data from file"""
        file_handle.seek(0)
        try:
            data = json.load(file_handle)
            return data
        except json.JSONDecodeError:
            # If the file is empty or corrupt, initialize with empty data
            return {'reservations': {}, 'seat_index': {}}

    def save_data(self, data: Dict) -> None:
        """Save reservation data to file using a temporary file to avoid corruption"""
        temp_file = None
        try:
            temp_dir = os.path.dirname(self.data_file)
            with tempfile.NamedTemporaryFile('w', dir=temp_dir, delete=False) as temp_file:
                json.dump(data, temp_file, indent=2)
                temp_file.flush()
                os.fsync(temp_file.fileno())
            # Atomically replace the original file with the temporary file
            os.replace(temp_file.name, self.data_file)
        except Exception as e:
            logger.error(f"Error saving data: {e}", exc_info=True)
            if temp_file:
                os.remove(temp_file.name)
            raise
        finally:
            if temp_file and os.path.exists(temp_file.name):
                os.remove(temp_file.name)