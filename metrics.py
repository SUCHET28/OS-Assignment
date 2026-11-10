"""
Round Robin CPU Scheduling Simulator - Performance Metrics Engine
==================================================================
Author: Backend Developer (Member 1)
Branch: backend-scheduler

This module calculates scheduling metrics including Completion Time (CT),
Turnaround Time (TAT), Waiting Time (WT), Response Time (RT), CPU Utilization,
Idle Time, Context Switches, and Throughput.
"""

from __future__ import annotations
from typing import List, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from scheduler import ProcessResult, ExecutionSlice


def calculate_metrics(
    processes: List["ProcessResult"],
    execution_history: List["ExecutionSlice"],
) -> Dict[str, Any]:
    """
    Computes aggregate performance metrics from simulated process results
    and execution intervals.

    Context Switch Counting Convention:
    A context switch is counted whenever the CPU transitions between two
    different execution entities (e.g. from Process A to Process B, or from
    Process A to CPU IDLE, or from CPU IDLE to Process B).
    Consecutive executions of the same process do not incur a context switch.

    Args:
        processes: List of ProcessResult instances with individual timings.
        execution_history: List of ExecutionSlice representing CPU activity.

    Returns:
        Dictionary containing aggregate summary metrics.
    """
    n = len(processes)
    if n == 0:
        return {
            "num_processes": 0,
            "average_waiting_time": 0.0,
            "average_turnaround_time": 0.0,
            "average_response_time": 0.0,
            "total_busy_time": 0.0,
            "total_idle_time": 0.0,
            "total_elapsed_time": 0.0,
            "cpu_utilization": 0.0,
            "context_switches": 0,
            "total_slices": 0,
            "busy_slices": 0,
            "throughput": 0.0,
        }

    sum_wt = sum(p.waiting_time for p in processes)
    sum_tat = sum(p.turnaround_time for p in processes)
    sum_rt = sum(p.response_time for p in processes)

    avg_wt = sum_wt / n
    avg_tat = sum_tat / n
    avg_rt = sum_rt / n

    total_busy_time = sum(s.duration for s in execution_history if not s.is_idle)
    total_idle_time = sum(s.duration for s in execution_history if s.is_idle)
    total_elapsed_time = total_busy_time + total_idle_time

    if total_elapsed_time > 0:
        cpu_utilization = (total_busy_time / total_elapsed_time) * 100.0
        throughput = n / total_elapsed_time
    else:
        cpu_utilization = 0.0
        throughput = 0.0

    # Count context switches
    context_switches = 0
    prev_pid = None
    for s in execution_history:
        if prev_pid is not None and s.pid != prev_pid:
            context_switches += 1
        prev_pid = s.pid

    total_slices = len(execution_history)
    busy_slices = sum(1 for s in execution_history if not s.is_idle)

    return {
        "num_processes": n,
        "average_waiting_time": round(avg_wt, 4),
        "average_turnaround_time": round(avg_tat, 4),
        "average_response_time": round(avg_rt, 4),
        "total_busy_time": round(total_busy_time, 4),
        "total_idle_time": round(total_idle_time, 4),
        "total_elapsed_time": round(total_elapsed_time, 4),
        "cpu_utilization": round(cpu_utilization, 2),
        "context_switches": context_switches,
        "total_slices": total_slices,
        "busy_slices": busy_slices,
        "throughput": round(throughput, 4),
    }
