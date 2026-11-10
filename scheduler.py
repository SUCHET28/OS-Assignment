"""
Round Robin CPU Scheduling Simulator - Core Scheduler Engine
============================================================
Author: Backend Developer (Member 1)
Branch: backend-scheduler

This module implements the deterministic Round Robin (RR) CPU scheduling algorithm,
maintaining a collections.deque ready queue, handling process arrival tie-breaking,
tracking execution intervals (slices), CPU idle periods, and capturing step-by-step
simulation snapshots for educational visualization.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from collections import deque
from typing import List, Dict, Any, Optional
import copy

from metrics import calculate_metrics


@dataclass
class Process:
    """
    Represents an input process definition.

    Attributes:
        pid: Unique process identifier (e.g. 'P1', 'P2').
        arrival_time: Arrival time of process (non-negative integer or float).
        burst_time: CPU burst time required (positive integer or float).
        priority: Optional priority attribute (default 0).
    """
    pid: str
    arrival_time: float
    burst_time: float
    priority: int = 0

    def __post_init__(self):
        self.pid = str(self.pid).strip()
        self.arrival_time = float(self.arrival_time)
        self.burst_time = float(self.burst_time)
        self.priority = int(self.priority)


@dataclass
class ProcessResult:
    """
    Represents the final scheduling results for an individual process.
    """
    pid: str
    arrival_time: float
    burst_time: float
    completion_time: float
    turnaround_time: float
    waiting_time: float
    response_time: float
    first_start_time: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "PID": self.pid,
            "Arrival Time (AT)": self.arrival_time,
            "Burst Time (BT)": self.burst_time,
            "Completion Time (CT)": self.completion_time,
            "Turnaround Time (TAT)": self.turnaround_time,
            "Waiting Time (WT)": self.waiting_time,
            "Response Time (RT)": self.response_time,
        }


@dataclass
class ExecutionSlice:
    """
    Represents a contiguous block of CPU execution (or CPU idle time).
    """
    pid: str
    start_time: float
    end_time: float
    duration: float
    is_idle: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "PID": self.pid,
            "Start": self.start_time,
            "End": self.end_time,
            "Duration": self.duration,
            "Type": "Idle" if self.is_idle else "Process",
        }


@dataclass
class SimulationStep:
    """
    Snapshot of simulator state at each scheduling slice.
    Used for step-by-step ready queue visualization.
    """
    step_number: int
    time: float
    executing_pid: str
    duration: float
    remaining_burst: float
    ready_queue_before: List[str]
    ready_queue_after: List[str]
    event_description: str
    completed: bool


@dataclass
class ScheduleResult:
    """
    Container for complete simulation outputs.
    """
    processes: List[ProcessResult]
    execution_history: List[ExecutionSlice]
    step_history: List[SimulationStep]
    total_time: float
    metrics: Dict[str, Any]
    quantum: float


class _ProcessRuntimeTracker:
    """Internal helper to track process runtime state."""
    def __init__(self, process: Process, original_order: int):
        self.process = process
        self.pid = process.pid
        self.arrival_time = process.arrival_time
        self.burst_time = process.burst_time
        self.original_order = original_order
        self.remaining_burst = process.burst_time
        self.first_start_time: Optional[float] = None
        self.completion_time: Optional[float] = None


def validate_inputs(processes: List[Process], quantum: float) -> None:
    """
    Validates input processes and time quantum.

    Raises:
        ValueError: If input violates scheduling constraints.
    """
    if quantum is None or quantum <= 0:
        raise ValueError(f"Time quantum must be strictly positive (> 0). Received: {quantum}")

    if not processes:
        raise ValueError("Process list cannot be empty. Please provide at least one process.")

    seen_pids = set()
    for p in processes:
        if not p.pid:
            raise ValueError("Process ID cannot be empty.")
        if p.pid in seen_pids:
            raise ValueError(f"Duplicate Process ID detected: '{p.pid}'. Process IDs must be unique.")
        seen_pids.add(p.pid)

        if p.arrival_time < 0:
            raise ValueError(
                f"Process '{p.pid}' has a negative arrival time ({p.arrival_time}). "
                "Arrival time must be non-negative (>= 0)."
            )

        if p.burst_time <= 0:
            raise ValueError(
                f"Process '{p.pid}' has a non-positive burst time ({p.burst_time}). "
                "Burst time must be strictly positive (> 0)."
            )


def simulate_round_robin(processes: List[Process], quantum: float) -> ScheduleResult:
    """
    Executes the Round Robin CPU Scheduling algorithm.

    Tie-breaking & Queue Convention:
    1. Arriving processes are sorted by (arrival_time, original_index).
    2. When a process finishes its quantum at time t, any new processes arriving
       at or before time t are enqueued in the ready queue BEFORE the unfinished
       running process is requeued.
    3. CPU idle intervals are captured as explicit 'IDLE' slices.

    Args:
        processes: List of Process instances.
        quantum: Positive time quantum.

    Returns:
        ScheduleResult containing process metrics, Gantt execution slices,
        step-by-step history, and global performance statistics.
    """
    validate_inputs(processes, quantum)

    # Make deep copies and initialize trackers
    trackers: List[_ProcessRuntimeTracker] = [
        _ProcessRuntimeTracker(p, idx) for idx, p in enumerate(processes)
    ]

    # Sort unarrived pool by arrival time, then original order
    unarrived = sorted(trackers, key=lambda p: (p.arrival_time, p.original_order))
    ready_queue: deque[_ProcessRuntimeTracker] = deque()

    execution_history: List[ExecutionSlice] = []
    step_history: List[SimulationStep] = []

    current_time: float = 0.0
    step_counter: int = 1

    # Check if CPU is idle before the first process arrives
    earliest_arrival = unarrived[0].arrival_time
    if earliest_arrival > current_time:
        idle_duration = earliest_arrival - current_time
        execution_history.append(
            ExecutionSlice(
                pid="IDLE",
                start_time=current_time,
                end_time=earliest_arrival,
                duration=idle_duration,
                is_idle=True,
            )
        )
        step_history.append(
            SimulationStep(
                step_number=step_counter,
                time=current_time,
                executing_pid="IDLE",
                duration=idle_duration,
                remaining_burst=0.0,
                ready_queue_before=[],
                ready_queue_after=[],
                event_description=f"CPU was IDLE from t={current_time} to t={earliest_arrival} waiting for first arrival.",
                completed=False,
            )
        )
        step_counter += 1
        current_time = earliest_arrival

    # Enqueue all processes arriving at current_time
    while unarrived and unarrived[0].arrival_time <= current_time:
        ready_queue.append(unarrived.pop(0))

    # Main scheduling loop
    while ready_queue or unarrived:
        if not ready_queue:
            # CPU is idle waiting for the next arrival
            next_arrival = unarrived[0].arrival_time
            idle_duration = next_arrival - current_time
            execution_history.append(
                ExecutionSlice(
                    pid="IDLE",
                    start_time=current_time,
                    end_time=next_arrival,
                    duration=idle_duration,
                    is_idle=True,
                )
            )
            step_history.append(
                SimulationStep(
                    step_number=step_counter,
                    time=current_time,
                    executing_pid="IDLE",
                    duration=idle_duration,
                    remaining_burst=0.0,
                    ready_queue_before=[],
                    ready_queue_after=[unarrived[0].pid],
                    event_description=f"CPU was IDLE from t={current_time} to t={next_arrival} waiting for process arrivals.",
                    completed=False,
                )
            )
            step_counter += 1
            current_time = next_arrival

            # Add arrived processes
            while unarrived and unarrived[0].arrival_time <= current_time:
                ready_queue.append(unarrived.pop(0))
            continue

        # Dispatch next process from the ready queue
        current_proc = ready_queue.popleft()
        ready_queue_before = [p.pid for p in ready_queue]

        # Record first CPU start time (for Response Time)
        if current_proc.first_start_time is None:
            current_proc.first_start_time = current_time

        # Calculate execution duration for this turn
        exec_duration = min(quantum, current_proc.remaining_burst)
        start_time = current_time
        end_time = current_time + exec_duration
        current_proc.remaining_burst -= exec_duration
        current_time = end_time

        # Record execution slice
        execution_history.append(
            ExecutionSlice(
                pid=current_proc.pid,
                start_time=start_time,
                end_time=end_time,
                duration=exec_duration,
                is_idle=False,
            )
        )

        # Enqueue new arrivals that arrived while the process was running or at end_time
        new_arrivals: List[_ProcessRuntimeTracker] = []
        while unarrived and unarrived[0].arrival_time <= current_time:
            new_arrivals.append(unarrived.pop(0))

        # Sort new arrivals by arrival_time, then original order
        new_arrivals.sort(key=lambda p: (p.arrival_time, p.original_order))
        for arrived_p in new_arrivals:
            ready_queue.append(arrived_p)

        # Re-queue running process if unfinished, or mark completion
        if current_proc.remaining_burst > 0:
            ready_queue.append(current_proc)
            is_completed = False
            desc = (
                f"{current_proc.pid} executed for {exec_duration} units "
                f"(remaining burst: {current_proc.remaining_burst}). "
            )
            if new_arrivals:
                arr_names = ", ".join(p.pid for p in new_arrivals)
                desc += f"New arrivals ({arr_names}) enqueued first. "
            desc += f"{current_proc.pid} re-added to rear of ready queue."
        else:
            is_completed = True
            current_proc.completion_time = current_time
            desc = (
                f"{current_proc.pid} executed for {exec_duration} units and "
                f"COMPLETED execution at t={current_time}."
            )
            if new_arrivals:
                arr_names = ", ".join(p.pid for p in new_arrivals)
                desc += f" New arrivals ({arr_names}) added to ready queue."

        step_history.append(
            SimulationStep(
                step_number=step_counter,
                time=start_time,
                executing_pid=current_proc.pid,
                duration=exec_duration,
                remaining_burst=current_proc.remaining_burst,
                ready_queue_before=ready_queue_before,
                ready_queue_after=[p.pid for p in ready_queue],
                event_description=desc,
                completed=is_completed,
            )
        )
        step_counter += 1

    # Build process results in original input order
    results: List[ProcessResult] = []
    # Map back by original order
    trackers_by_order = sorted(trackers, key=lambda t: t.original_order)
    for t in trackers_by_order:
        ct = t.completion_time if t.completion_time is not None else current_time
        tat = ct - t.arrival_time
        wt = tat - t.burst_time
        fst = t.first_start_time if t.first_start_time is not None else t.arrival_time
        rt = fst - t.arrival_time

        results.append(
            ProcessResult(
                pid=t.pid,
                arrival_time=t.arrival_time,
                burst_time=t.burst_time,
                completion_time=ct,
                turnaround_time=tat,
                waiting_time=wt,
                response_time=rt,
                first_start_time=fst,
            )
        )

    # Compute aggregate performance metrics
    metrics = calculate_metrics(results, execution_history)

    return ScheduleResult(
        processes=results,
        execution_history=execution_history,
        step_history=step_history,
        total_time=current_time,
        metrics=metrics,
        quantum=quantum,
    )
