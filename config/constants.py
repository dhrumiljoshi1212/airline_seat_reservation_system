from enum import Enum
import os

ROWS = 20
SEATS_PER_ROW = 8
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
PARENT_DIR = os.path.abspath(os.path.join(ROOT_DIR, os.pardir))
DATA_FILE = os.path.join(PARENT_DIR, 'reservation_data.json')
LOCK_FILE = os.path.join(PARENT_DIR, 'reservation_data.lock')
ROW_LAYOUT = [0, 1, 2, 3, 4, 5, 6, 7]

class Action(Enum):
    BOOK = "BOOK"
    CANCEL = "CANCEL"