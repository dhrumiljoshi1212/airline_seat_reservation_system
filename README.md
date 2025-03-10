# Airline Reservation System

## Dependencies
- Python 3.12+
- [Poetry 1.8.3](https://python-poetry.org/)

## Run using shell script:
    ```zsh
     chmod +x run.sh
    ./run.sh book a0 1
    ./run.sh cancel a0 1
    ```
### Using Poetry
1. Install project dependencies:
    ```zsh
    poetry install
    ```
2. Run the server in Poetry shell environment:
    ```zsh
    poetry run airline BOOK A0 1
    poetry run airline CANCEL A0 1
    ```

### Without Poetry
1. Install dependencies manually with pip: 
    ```zsh
    pip install portalocker
    pip install coverage
    ```

2. Run the server:
    ```zsh
    python3 main.py BOOK A0 1
    python3 main.py CANCEL A0 1
    ```

## Running Integration Tests
1. Run concurrency tests with Poetry:
    ```zsh
    poetry run concurrent_booking_test
    poetry run concurrent_cancellation_test
    ```
   OR without Poetry:
    ```zsh
    python3 concurrent_booking_test.py
    python3 concurrent_cancellation_test.py
    ```

2. Run parallel tests:
    ```zsh
    ./parallel_booking_test.sh
    ./parallel_cancellation_test.sh
    ```