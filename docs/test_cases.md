# Test Cases & Quality Assurance Specification

**Project**: Round Robin CPU Scheduling Simulator  
**Test Suite**: `tests/test_scheduler.py` & `tests/test_metrics.py`  
**Test Framework**: `pytest` (21 unit tests implemented and passing)  

---

## Summary of Test Results

| Test Category | Total Tests | Status | Passing % |
| :--- | :---: | :---: | :---: |
| **Algorithmic Accuracy & Slices** | 10 | PASSED | 100% |
| **Edge Cases & Idle Handling** | 3 | PASSED | 100% |
| **Defensive Input Validation** | 5 | PASSED | 100% |
| **Performance Metrics Equations** | 3 | PASSED | 100% |
| **Total** | **21** | **PASSED** | **100%** |

---

## Detailed Test Matrix

### 1. Benchmark & Algorithmic Correctness Tests

#### `TC-01`: Section 11 Benchmark Verification (`test_sample_verification_case`)
- **Input**:
  - P1: AT=0, BT=5
  - P2: AT=1, BT=4
  - P3: AT=2, BT=2
  - P4: AT=4, BT=1
  - Quantum: 2
- **Expected Execution Slices**:
  - `P1`: 0 – 2
  - `P2`: 2 – 4
  - `P3`: 4 – 6 (completes)
  - `P1`: 6 – 8
  - `P4`: 8 – 9 (completes)
  - `P2`: 9 – 11 (completes)
  - `P1`: 11 – 12 (completes)
- **Expected Metrics**:
  - `P1`: CT=12, TAT=12, WT=7, RT=0
  - `P2`: CT=11, TAT=10, WT=6, RT=1
  - `P3`: CT=6, TAT=4, WT=2, RT=2
  - `P4`: CT=9, TAT=5, WT=4, RT=4
  - $\overline{WT} = 4.75$, $\overline{TAT} = 7.75$, $\overline{RT} = 1.75$, Utilization = $100.0\%$, Context Switches = $6$.
- **Result**: PASSED.

#### `TC-02`: Single Process Execution (`test_single_process`)
- **Input**: P1 (AT=0, BT=4), Quantum=2
- **Expected**: Slices: P1(0-2), P1(2-4). Total CT=4, WT=0, RT=0. Context switches = 0 (same process continues).
- **Result**: PASSED.

#### `TC-03`: Simultaneous Arrivals at $t=0$ (`test_identical_arrival_times`)
- **Input**: P1 (AT=0, BT=3), P2 (AT=0, BT=3), Quantum=2
- **Expected Slices**: P1(0-2), P2(2-4), P1(4-5), P2(5-6).
- **Result**: PASSED.

#### `TC-04`: Staggered Arrival Times Without Idle (`test_different_arrival_times`)
- **Input**: P1 (AT=0, BT=4), P2 (AT=2, BT=3), Quantum=2
- **Expected Slices**: P1(0-2), P2(2-4), P1(4-6), P2(6-7).
- **Result**: PASSED.

---

### 2. CPU Idle & Boundary Conditions

#### `TC-05`: CPU Idle Before Earliest Process Arrival (`test_cpu_idle_before_first_arrival`)
- **Input**: P1 (AT=3, BT=2), Quantum=2
- **Expected Slices**: IDLE(0-3), P1(3-5).
- **Metrics**: Total Time = 5, Busy Time = 2, Idle Time = 3, Utilization = $40.0\%$.
- **Result**: PASSED.

#### `TC-06`: CPU Idle Interval Between Processes (`test_cpu_idle_between_arrivals`)
- **Input**: P1 (AT=0, BT=2), P2 (AT=5, BT=2), Quantum=2
- **Expected Slices**: P1(0-2), IDLE(2-5), P2(5-7).
- **Metrics**: Busy Time = 4, Idle Time = 3, Utilization = $57.14\%$.
- **Result**: PASSED.

#### `TC-07`: Burst Time Smaller Than Quantum (`test_burst_smaller_than_quantum`)
- **Input**: P1 (AT=0, BT=1), P2 (AT=0, BT=1), Quantum=5
- **Expected Slices**: P1(0-1), P2(1-2). Immediate completion without requeuing.
- **Result**: PASSED.

#### `TC-08`: Burst Time Equal to Quantum (`test_burst_equal_to_quantum`)
- **Input**: P1 (AT=0, BT=3), P2 (AT=0, BT=3), Quantum=3
- **Expected Slices**: P1(0-3), P2(3-6).
- **Result**: PASSED.

#### `TC-09`: Burst Time Substantially Larger Than Quantum (`test_burst_larger_than_quantum`)
- **Input**: P1 (AT=0, BT=6), Quantum=2
- **Expected Slices**: Three consecutive slices of 2 units each.
- **Result**: PASSED.

#### `TC-10`: Quantum Larger Than All Bursts (`test_quantum_larger_than_all_burst_times`)
- **Input**: P1 (AT=0, BT=3), P2 (AT=0, BT=2), P3 (AT=0, BT=1), Quantum=10
- **Expected**: Behavior degrades to First-Come, First-Served (FCFS).
- **Result**: PASSED.

---

### 3. Defensive Input Validation Tests

| Test ID | Test Function | Input Condition | Expected Exception | Result |
| :---: | :--- | :--- | :--- | :---: |
| `TC-11` | `test_invalid_quantum` | Quantum $\le 0$ ($q=0, q=-2$) | `ValueError: Time quantum must be strictly positive` | PASSED |
| `TC-12` | `test_invalid_arrival_times` | Negative arrival time ($AT=-1$) | `ValueError: negative arrival time` | PASSED |
| `TC-13` | `test_invalid_burst_times` | Non-positive burst ($BT=0, BT=-5$) | `ValueError: non-positive burst time` | PASSED |
| `TC-14` | `test_duplicate_process_ids` | Duplicate PIDs (e.g. two `P1`s) | `ValueError: Duplicate Process ID detected` | PASSED |
| `TC-15` | `test_empty_process_list` | Empty process list `[]` | `ValueError: Process list cannot be empty` | PASSED |

---

### 4. Metrics Validation Tests

| Test ID | Test Function | Verified Property | Formula Verified | Result |
| :---: | :--- | :--- | :--- | :---: |
| `TC-16` | `test_correct_waiting_time` | Waiting Time consistency | $WT = TAT - BT$ | PASSED |
| `TC-17` | `test_correct_turnaround_time`| Turnaround Time consistency | $TAT = CT - AT$ | PASSED |
| `TC-18` | `test_correct_response_time` | Response Time non-negative | $RT = First\\ Dispatch - AT \ge 0$ | PASSED |
| `TC-19` | `test_correct_cpu_utilization` | Utilization mathematical precision | $Util = \frac{Busy}{Total} \times 100$ | PASSED |
| `TC-20` | `test_correct_gantt_chart_intervals` | Timeline continuity | $End_i == Start_{i+1}$ (No timeline gaps) | PASSED |
| `TC-21` | `test_empty_metrics` | Safe fallback handling | Zero-division guard for empty process list | PASSED |

---

## How to Re-run Test Suite

To execute all test cases locally:
```bash
pytest -v
```

Expected output:
```text
======================= 21 passed in 0.22s =======================
```
