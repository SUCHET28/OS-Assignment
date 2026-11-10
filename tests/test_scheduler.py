"""
Unit Tests for Round Robin Scheduler Engine
===========================================
Author: Backend Developer (Member 1)
Branch: backend-scheduler

Tests all algorithmic requirements, edge cases, and deterministic execution sequences.
"""

import pytest
from scheduler import Process, simulate_round_robin, validate_inputs


def test_sample_verification_case():
    """
    Validates Section 11 College Assignment Sample Test Data:
    P1: AT=0, BT=5
    P2: AT=1, BT=4
    P3: AT=2, BT=2
    P4: AT=4, BT=1
    Quantum = 2
    """
    procs = [
        Process("P1", 0, 5),
        Process("P2", 1, 4),
        Process("P3", 2, 2),
        Process("P4", 4, 1),
    ]
    res = simulate_round_robin(procs, quantum=2)

    # 1. Check Execution Slices
    expected_slices = [
        ("P1", 0, 2),
        ("P2", 2, 4),
        ("P3", 4, 6),
        ("P1", 6, 8),
        ("P4", 8, 9),
        ("P2", 9, 11),
        ("P1", 11, 12),
    ]
    actual_slices = [(s.pid, s.start_time, s.end_time) for s in res.execution_history]
    assert actual_slices == expected_slices, f"Expected {expected_slices}, got {actual_slices}"

    # 2. Check Individual Process Metrics
    p_map = {p.pid: p for p in res.processes}
    assert p_map["P1"].completion_time == 12
    assert p_map["P1"].turnaround_time == 12
    assert p_map["P1"].waiting_time == 7
    assert p_map["P1"].response_time == 0

    assert p_map["P2"].completion_time == 11
    assert p_map["P2"].turnaround_time == 10
    assert p_map["P2"].waiting_time == 6
    assert p_map["P2"].response_time == 1

    assert p_map["P3"].completion_time == 6
    assert p_map["P3"].turnaround_time == 4
    assert p_map["P3"].waiting_time == 2
    assert p_map["P3"].response_time == 2

    assert p_map["P4"].completion_time == 9
    assert p_map["P4"].turnaround_time == 5
    assert p_map["P4"].waiting_time == 4
    assert p_map["P4"].response_time == 4

    # 3. Check Aggregate Metrics
    assert res.metrics["average_waiting_time"] == 4.75
    assert res.metrics["average_turnaround_time"] == 7.75
    assert res.metrics["average_response_time"] == 1.75
    assert res.metrics["cpu_utilization"] == 100.0
    assert res.metrics["total_idle_time"] == 0.0
    assert res.metrics["total_busy_time"] == 12.0
    assert res.metrics["context_switches"] == 6


def test_single_process():
    """Requirement 1: Single process simulation."""
    procs = [Process("P1", 0, 4)]
    res = simulate_round_robin(procs, quantum=2)
    assert len(res.processes) == 1
    p = res.processes[0]
    assert p.completion_time == 4
    assert p.turnaround_time == 4
    assert p.waiting_time == 0
    assert p.response_time == 0
    assert res.metrics["cpu_utilization"] == 100.0
    # Two slices of P1: 0-2 and 2-4 -> no context switch since same process
    assert res.metrics["context_switches"] == 0


def test_identical_arrival_times():
    """Requirement 2: Multiple processes with identical arrival times (t=0)."""
    procs = [
        Process("P1", 0, 3),
        Process("P2", 0, 3),
    ]
    res = simulate_round_robin(procs, quantum=2)
    # Execution: P1(0-2), P2(2-4), P1(4-5), P2(5-6)
    slices = [(s.pid, s.start_time, s.end_time) for s in res.execution_history]
    assert slices == [("P1", 0, 2), ("P2", 2, 4), ("P1", 4, 5), ("P2", 5, 6)]
    assert res.processes[0].completion_time == 5
    assert res.processes[1].completion_time == 6


def test_different_arrival_times():
    """Requirement 3: Different arrival times without idle."""
    procs = [
        Process("P1", 0, 4),
        Process("P2", 2, 3),
    ]
    res = simulate_round_robin(procs, quantum=2)
    # t=0: P1 runs [0-2], P2 arrives at 2
    # P1 requeued -> queue [P2, P1]
    # P2 runs [2-4] -> queue [P1, P2]
    # P1 runs [4-6] -> finishes
    # P2 runs [6-7] -> finishes
    slices = [(s.pid, s.start_time, s.end_time) for s in res.execution_history]
    assert slices == [("P1", 0, 2), ("P2", 2, 4), ("P1", 4, 6), ("P2", 6, 7)]


def test_cpu_idle_before_first_arrival():
    """Requirement 4: CPU idle before first process arrives (e.g. AT > 0)."""
    procs = [Process("P1", 3, 2)]
    res = simulate_round_robin(procs, quantum=2)
    assert res.execution_history[0].is_idle is True
    assert res.execution_history[0].start_time == 0
    assert res.execution_history[0].end_time == 3
    assert res.execution_history[1].pid == "P1"
    assert res.execution_history[1].start_time == 3
    assert res.execution_history[1].end_time == 5
    assert res.metrics["total_idle_time"] == 3.0
    assert res.metrics["total_busy_time"] == 2.0
    # 2 / 5 * 100 = 40%
    assert res.metrics["cpu_utilization"] == 40.0


def test_cpu_idle_between_arrivals():
    """Requirement 5: CPU idle gap between processes."""
    procs = [
        Process("P1", 0, 2),
        Process("P2", 5, 2),
    ]
    res = simulate_round_robin(procs, quantum=2)
    slices = [(s.pid, s.start_time, s.end_time, s.is_idle) for s in res.execution_history]
    assert slices == [
        ("P1", 0, 2, False),
        ("IDLE", 2, 5, True),
        ("P2", 5, 7, False),
    ]
    assert res.metrics["total_idle_time"] == 3.0
    assert res.metrics["total_busy_time"] == 4.0
    # 4 / 7 * 100 = 57.14%
    assert res.metrics["cpu_utilization"] == pytest.approx(57.14, 0.01)


def test_burst_smaller_than_quantum():
    """Requirement 6: Burst time smaller than quantum (finishes early)."""
    procs = [
        Process("P1", 0, 1),
        Process("P2", 0, 1),
    ]
    res = simulate_round_robin(procs, quantum=5)
    slices = [(s.pid, s.start_time, s.end_time) for s in res.execution_history]
    assert slices == [("P1", 0, 1), ("P2", 1, 2)]


def test_burst_equal_to_quantum():
    """Requirement 7: Burst time exactly equal to quantum."""
    procs = [
        Process("P1", 0, 3),
        Process("P2", 0, 3),
    ]
    res = simulate_round_robin(procs, quantum=3)
    slices = [(s.pid, s.start_time, s.end_time) for s in res.execution_history]
    assert slices == [("P1", 0, 3), ("P2", 3, 6)]
    assert res.processes[0].completion_time == 3
    assert res.processes[1].completion_time == 6


def test_burst_larger_than_quantum():
    """Requirement 8: Burst time significantly larger than quantum."""
    procs = [Process("P1", 0, 6)]
    res = simulate_round_robin(procs, quantum=2)
    # Slices: 0-2, 2-4, 4-6
    assert len(res.execution_history) == 3
    assert res.processes[0].completion_time == 6


def test_quantum_larger_than_all_burst_times():
    """Requirement 9: Quantum larger than all bursts behaves like FCFS."""
    procs = [
        Process("P1", 0, 3),
        Process("P2", 0, 2),
        Process("P3", 0, 1),
    ]
    res = simulate_round_robin(procs, quantum=10)
    slices = [(s.pid, s.start_time, s.end_time) for s in res.execution_history]
    assert slices == [("P1", 0, 3), ("P2", 3, 5), ("P3", 5, 6)]


def test_invalid_quantum():
    """Requirement 10: Zero or negative time quantum."""
    with pytest.raises(ValueError, match="Time quantum must be strictly positive"):
        simulate_round_robin([Process("P1", 0, 2)], quantum=0)

    with pytest.raises(ValueError, match="Time quantum must be strictly positive"):
        simulate_round_robin([Process("P1", 0, 2)], quantum=-2)


def test_invalid_arrival_times():
    """Requirement 11: Negative arrival time."""
    with pytest.raises(ValueError, match="negative arrival time"):
        simulate_round_robin([Process("P1", -1, 3)], quantum=2)


def test_invalid_burst_times():
    """Requirement 12: Zero or negative burst time."""
    with pytest.raises(ValueError, match="non-positive burst time"):
        simulate_round_robin([Process("P1", 0, 0)], quantum=2)

    with pytest.raises(ValueError, match="non-positive burst time"):
        simulate_round_robin([Process("P1", 0, -5)], quantum=2)


def test_duplicate_process_ids():
    """Requirement 13: Duplicate process IDs."""
    with pytest.raises(ValueError, match="Duplicate Process ID"):
        simulate_round_robin([Process("P1", 0, 3), Process("P1", 1, 2)], quantum=2)


def test_empty_process_list():
    """Empty list validation."""
    with pytest.raises(ValueError, match="Process list cannot be empty"):
        simulate_round_robin([], quantum=2)
