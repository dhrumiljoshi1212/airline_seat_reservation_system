import subprocess
import time
import os
import sys
import random
import json
import datetime
from concurrent.futures import ThreadPoolExecutor
from typing import Tuple, List, Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class CancelResult:
    seat_id: str
    seat_num: int
    return_code: int
    output: str
    timestamp: float = 0.0

    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()


def run_cancel_command(row: str, seat: int, seat_num: int) -> Tuple[int, str]:
    main_script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "main.py"))

    cmd = [
        sys.executable,  # Use the current Python interpreter
        main_script_path,
        'CANCEL',
        f'{row}{seat}',
        str(seat_num)
    ]

    # Use context manager for better resource handling
    with subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True  # More modern than universal_newlines
    ) as process:
        stdout, _ = process.communicate()
        return process.returncode, stdout.strip()


def cancel_seat_task(row: str, seat: int, seat_num: int) -> CancelResult:
    """Wrapper function for canceling that returns structured results"""
    return_code, output = run_cancel_command(row, seat, seat_num)
    return CancelResult(
        seat_id=f"{row}{seat}",
        seat_num=seat_num,
        return_code=return_code,
        output=output
    )


def concurrent_cancel_test() -> Dict[str, Any]:
    print("\nConcurrent Cancel Test")
    print("----------------------")

    # Define cancel attempts
    cancel_attempts = [
        ('A', 1, 1),  # First attempt to cancel A1
        ('A', 1, 1),  # Second attempt to cancel A1 (should fail)
        ('A', 2, 1),  # Cancel A2
        ('A', 0, 2),  # Cancel consecutive seats A0-A1
        ('A', 0, 2)  # Try canceling same consecutive seats again
    ]

    start_time = time.time()
    results: List[CancelResult] = []

    # Use ThreadPoolExecutor for better thread management
    with ThreadPoolExecutor(max_workers=len(cancel_attempts)) as executor:
        # Submit all tasks and get futures
        futures = [
            executor.submit(cancel_seat_task, row, seat, seat_num)
            for row, seat, seat_num in cancel_attempts
        ]

        # Collect results as they complete
        for future in futures:
            results.append(future.result())

    duration = time.time() - start_time

    # Print results
    print("\nCancel Attempts Results:")
    for result in results:
        print(f"Seat {result.seat_id} ({result.seat_num} seat(s)): {result.output}")

    print(f"\nTotal test duration: {duration:.4f} seconds")

    return {
        "test_type": "concurrent_cancel",
        "start_time": start_time,
        "duration": duration,
        "num_attempts": len(cancel_attempts),
        "results": results
    }


def stress_test(num_attempts: int = 50) -> Dict[str, Any]:
    print("\nStress Test")
    print("-----------")

    # Generate all cancellation attempts ahead of time
    cancel_tasks = [
        (chr(ord('A') + random.randint(0, 19)), random.randint(0, 7), 1)
        for _ in range(num_attempts)
    ]

    start_time = time.time()
    results: List[CancelResult] = []

    # Use ThreadPoolExecutor for better performance and resource management
    with ThreadPoolExecutor(max_workers=min(32, num_attempts)) as executor:
        # Map the function across all generated tasks
        for result in executor.map(
                lambda args: cancel_seat_task(*args),
                cancel_tasks
        ):
            results.append(result)

    # Analyze results
    successes = sum(1 for result in results if result.output == 'SUCCESS')
    failures = sum(1 for result in results if result.output == 'FAIL')
    duration = time.time() - start_time

    # Print summary
    print(f"Total attempts: {num_attempts}")
    print(f"Successful cancellations: {successes}")
    print(f"Failed cancellations: {failures}")
    print(f"Total test duration: {duration:.4f} seconds")

    return {
        "test_type": "stress_test",
        "start_time": start_time,
        "duration": duration,
        "attempts": num_attempts,
        "successes": successes,
        "failures": failures,
        "results": results
    }


def save_results_to_file(results: Dict[str, Any], filename: str = None) -> str:
    if filename is None:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        nanoseconds = time.perf_counter_ns()  # Higher resolution than microseconds
        filename = f"cancel_test_results_{timestamp}_{nanoseconds}.json"

    # Convert dataclass objects to dictionaries
    serializable_results = results.copy()

    # Handle nested CancelResult objects in each test result
    for test_key, test_data in serializable_results.items():
        if isinstance(test_data, dict) and "results" in test_data:
            test_data["results"] = [asdict(r) for r in test_data["results"]]

    # Create the results directory if it doesn't exist
    results_dir = os.path.join(os.path.dirname(__file__), "cancellation_results")
    os.makedirs(results_dir, exist_ok=True)

    # Save to file
    filepath = os.path.join(results_dir, filename)
    with open(filepath, 'w') as f:
        json.dump(serializable_results, f, indent=2)

    print(f"\nResults saved to: {filepath}")
    return filepath


def main() -> None:
    # Run tests and collect results
    all_results = {
        "timestamp": datetime.datetime.now().isoformat(),
        "system_info": {
            "python_version": sys.version,
            "platform": sys.platform
        }
    }

    # Run concurrent cancel test
    concurrent_results = concurrent_cancel_test()
    all_results["concurrent_test"] = concurrent_results

    # Run stress test
    stress_results = stress_test(num_attempts=50)
    all_results["stress_test"] = stress_results

    # Save results to file
    save_results_to_file(all_results)


if __name__ == '__main__':
    main()