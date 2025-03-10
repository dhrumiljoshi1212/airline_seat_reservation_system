#!/bin/bash

# Number of concurrent test runs
NUM_RUNS=10

# Function to run the test script
run_test() {
    python3 concurrent_booking_test.py
}

# Run multiple tests in parallel
for i in $(seq 1 $NUM_RUNS); do
    run_test &
done

# Wait for all background processes to complete
wait

echo "All concurrent tests completed."