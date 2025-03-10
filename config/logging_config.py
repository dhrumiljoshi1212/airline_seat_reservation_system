import logging
import os
def configure_logging():
    root_dir = os.path.abspath(os.path.dirname(__file__))
    parent_dir = os.path.abspath(os.path.join(root_dir, os.pardir))
    log_file = os.path.join(parent_dir, 'reservation.log')

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        filename=log_file
    )
    return logging.getLogger('airline_reservation')