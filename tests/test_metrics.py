"""
Unit Tests for Performance Metrics Engine
=========================================
Author: Backend Developer (V SUCHET)
Branch: backend-scheduler

Tests accuracy of CT, TAT, WT, RT, CPU Utilization, and Gantt intervals.
"""

import pytest
from scheduler import Process, ProcessResult, ExecutionSlice, simulate_round_robin
from metrics import calculate_metrics


def test_correct_waiting_time():
    """Requirement 14: Correct Waiting Time calculation (WT = TAT - BT)."""
    procs = [
        Process("P1", 0, 5),
        Process("P2", 2, 3),
    ]
    res = simulate_round_robin(procs, quantum=2)
    for p in res.processes:
        assert p.waiting_time == p.turnaround_time - p.burst_time


def test_correct_turnaround_time():
    """Requirement 15: Correct Turnaround Time calculation (TAT = CT - AT)."""
    procs = [
        Process("P1", 0, 4),
        Process("P2", 1, 2),
    ]
    res = simulate_round_robin(procs, quantum=2)
    for p in res.processes:
        assert p.turnaround_time == p.completion_time - p.arrival_time


def test_correct_response_time():
    """Requirement 16: Correct Response Time calculation (RT = First Start - AT)."""
    procs = [
        Process("P1", 0, 4),
        Process("P2", 1, 2),
    ]
    res = simulate_round_robin(procs, quantum=2)
    for p in res.processes:
        assert p.response_time == p.first_start_time - p.arrival_time
        assert p.response_time >= 0


def test_correct_cpu_utilization():
    """Requirement 17: Correct CPU Utilization = Busy / Total * 100."""
    # Case with no idle
    procs = [Process("P1", 0, 5)]
    res = simulate_round_robin(procs, quantum=2)
    assert res.metrics["cpu_utilization"] == 100.0

    # Case with known idle
    procs_idle = [Process("P1", 5, 5)]
    res_idle = simulate_round_robin(procs_idle, quantum=2)
    # Total = 10, Busy = 5 -> 50%
    assert res_idle.metrics["cpu_utilization"] == 50.0
    assert res_idle.metrics["total_idle_time"] == 5.0
    assert res_idle.metrics["total_busy_time"] == 5.0


def test_correct_gantt_chart_intervals():
    """Requirement 18: Verify execution intervals are contiguous and non-overlapping."""
    procs = [
        Process("P1", 0, 4),
        Process("P2", 1, 3),
        Process("P3", 3, 1),
    ]
    res = simulate_round_robin(procs, quantum=2)
    intervals = res.execution_history
    assert len(intervals) > 0
    assert intervals[0].start_time == 0

    for i in range(len(intervals) - 1):
        # End of current slice must equal start of next slice
        assert intervals[i].end_time == intervals[i + 1].start_time
        assert intervals[i].duration == intervals[i].end_time - intervals[i].start_time


def test_empty_metrics():
    """Edge case: empty inputs to calculate_metrics."""
    res = calculate_metrics([], [])
    assert res["num_processes"] == 0
    assert res["cpu_utilization"] == 0.0
    assert res["average_waiting_time"] == 0.0
