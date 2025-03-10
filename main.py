from cli import parse_arguments
from config.constants import LOCK_FILE
from services import ReservationService
from config import DATA_FILE, Action
from config import configure_logging

def main() -> None:
    logger = configure_logging()
    try:
        action, seat, count = parse_arguments()
        if not all([action, seat, count]):
            print("FAIL")
            logger.error("Invalid input arguments")
            return
        system = ReservationService(DATA_FILE, LOCK_FILE)
        success = system.book_seats(seat, count) if action == Action.BOOK else system.cancel_reservation(seat, count)
        print("SUCCESS" if success else "FAIL")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print("FAIL")

if __name__ == "__main__":
    main()