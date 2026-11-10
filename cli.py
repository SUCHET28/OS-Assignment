"""
Round Robin CPU Scheduling Simulator - CLI & Automation Runner
==============================================================
Authors: V SUCHET (Backend) & PALLAVI M V (Frontend)

Provides a command-line interface for running Round Robin scheduling,
generating ASCII Gantt charts, and powering interactive GitHub Actions.
"""

from __future__ import annotations
import argparse
import sys
from typing import List

from scheduler import Process, simulate_round_robin, ScheduleResult


def parse_processes_string(proc_str: str) -> List[Process]:
    """
    Parses a string like 'P1:0:5,P2:1:4,P3:2:2,P4:4:1' into a list of Process objects.
    Format: PID:ArrivalTime:BurstTime
    """
    processes = []
    items = [item.strip() for item in proc_str.split(",") if item.strip()]
    for item in items:
        parts = item.split(":")
        if len(parts) != 3:
            raise ValueError(f"Invalid process format '{item}'. Expected 'PID:AT:BT' (e.g. 'P1:0:5')")
        pid, at, bt = parts[0].strip(), float(parts[1].strip()), float(parts[2].strip())
        processes.append(Process(pid=pid, arrival_time=at, burst_time=bt))
    return processes


def render_ascii_gantt(result: ScheduleResult) -> str:
    """Renders a clean ASCII Gantt chart timeline."""
    slices = result.execution_history
    if not slices:
        return "[No execution history]"

    top_bar = "|"
    bottom_bar = "0"

    for s in slices:
        label = f" {s.pid} "
        top_bar += label + "|"
        bottom_bar += f"{s.end_time:g}".rjust(len(label) + 1)

    chart = f"{top_bar}\n{bottom_bar}"
    return chart


def generate_markdown_summary(result: ScheduleResult) -> str:
    """Generates GitHub Actions step summary markdown."""
    m = result.metrics
    ascii_gantt = render_ascii_gantt(result)

    md = f"""## ⚡ Round Robin CPU Scheduling Simulation Report

> **Simulated via Interactive GitHub Action**  
> **Time Quantum ($q$):** `{result.quantum}` | **Total Elapsed Time:** `{m['total_elapsed_time']}`

### 📊 Performance Summary
| Metric | Value | Metric | Value |
| :--- | :--- | :--- | :--- |
| **Average Waiting Time** | `{m['average_waiting_time']}` | **CPU Utilization** | `{m['cpu_utilization']}%` |
| **Average Turnaround Time** | `{m['average_turnaround_time']}` | **Context Switches** | `{m['context_switches']}` |
| **Average Response Time** | `{m['average_response_time']}` | **Throughput** | `{m['throughput']} proc/unit` |

### ⏱️ CPU Execution Timeline (ASCII Gantt Chart)
```text
{ascii_gantt}
```

### 📋 Process Scheduling Table
| Process ID | Arrival Time (AT) | Burst Time (BT) | Completion Time (CT) | Turnaround Time (TAT) | Waiting Time (WT) | Response Time (RT) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
"""
    for p in result.processes:
        md += f"| **{p.pid}** | {p.arrival_time:g} | {p.burst_time:g} | **{p.completion_time:g}** | {p.turnaround_time:g} | {p.waiting_time:g} | {p.response_time:g} |\n"

    md += f"""
### 🔄 Execution Slices Log
| Slice # | Process ID | Start Time | End Time | Duration | Type |
| :---: | :---: | :---: | :---: | :---: | :---: |
"""
    for idx, s in enumerate(result.execution_history, start=1):
        slice_type = "Idle" if s.is_idle else "Process"
        md += f"| {idx} | `{s.pid}` | {s.start_time:g} | {s.end_time:g} | {s.duration:g} | {slice_type} |\n"

    return md


def main():
    parser = argparse.ArgumentParser(description="Round Robin Simulator CLI Runner")
    parser.add_argument("--quantum", "-q", type=float, default=2.0, help="Time Quantum (positive float)")
    parser.add_argument(
        "--preset",
        choices=["college_benchmark", "simultaneous_arrivals", "idle_gaps"],
        help="Use a pre-configured workload preset",
    )
    parser.add_argument(
        "--processes",
        "-p",
        type=str,
        help="Comma-separated process definitions 'PID:AT:BT' (e.g. 'P1:0:5,P2:1:4,P3:2:2,P4:4:1')",
    )
    parser.add_argument("--markdown", action="store_true", help="Output GitHub Actions markdown summary")

    args = parser.parse_args()

    # Determine process workload
    if args.processes:
        processes = parse_processes_string(args.processes)
    elif args.preset == "simultaneous_arrivals":
        processes = [
            Process("P1", 0, 6),
            Process("P2", 0, 4),
            Process("P3", 0, 8),
            Process("P4", 0, 3),
        ]
    elif args.preset == "idle_gaps":
        processes = [
            Process("P1", 2, 3),
            Process("P2", 8, 4),
            Process("P3", 15, 2),
        ]
    else:
        # Default: Section 11 College Benchmark
        processes = [
            Process("P1", 0, 5),
            Process("P2", 1, 4),
            Process("P3", 2, 2),
            Process("P4", 4, 1),
        ]

    result = simulate_round_robin(processes, quantum=args.quantum)

    if args.markdown:
        print(generate_markdown_summary(result))
    else:
        print("=" * 60)
        print("ROUND ROBIN CPU SCHEDULING SIMULATION")
        print("=" * 60)
        print(f"Time Quantum: {result.quantum}")
        print("\nASCII GANTT CHART:")
        print(render_ascii_gantt(result))
        print("\nPROCESS METRICS:")
        for p in result.processes:
            print(f"  {p.pid}: CT={p.completion_time:g}, TAT={p.turnaround_time:g}, WT={p.waiting_time:g}, RT={p.response_time:g}")
        m = result.metrics
        print("\nAGGREGATE SUMMARY:")
        print(f"  Avg Waiting Time:    {m['average_waiting_time']}")
        print(f"  Avg Turnaround Time: {m['average_turnaround_time']}")
        print(f"  Avg Response Time:   {m['average_response_time']}")
        print(f"  CPU Utilization:     {m['cpu_utilization']}%")
        print(f"  Context Switches:    {m['context_switches']}")
        print("=" * 60)


if __name__ == "__main__":
    main()
