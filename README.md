# Round Robin CPU Scheduling Simulator

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-FF4B4B.svg)](https://streamlit.io/)
[![Plotly](https://img.shields.io/badge/Plotly-Interactive-3F4F75.svg)](https://plotly.com/)
[![Tests](https://img.shields.io/badge/Tests-21%20Passed-brightgreen.svg)]()

**Description**: An interactive Operating Systems engineering group project demonstrating the preemptive **Round Robin (RR) CPU Scheduling Algorithm** using Python, Streamlit, and Plotly.

**Objective**: Develop an interactive, mathematically rigorous simulator that demonstrates round-robin scheduling, visualizes execution timelines via Gantt charts, renders step-by-step ready queue state transitions, and evaluates time quantum sensitivity.

---

## 1. Problem Statement & Background

In time-sharing operating systems, CPU scheduling determines the allocation of processor time among competing concurrent processes. 

The **Round Robin (RR)** algorithm is a foundational preemptive scheduling technique where each ready process is assigned a fixed execution slice called the **Time Quantum ($q$)**. While Round Robin guarantees fairness and prevents starvation, selecting an optimal time quantum is critical:
- An excessively small time quantum incurs high context switching overhead.
- An excessively large time quantum degrades into First-Come, First-Served (FCFS), harming interactive responsiveness.

This simulator allows students, educators, and engineers to observe, step through, and analyze this scheduling behavior interactively.

---

## 2. Key Features

- **Dynamic Process Configuration**: Add, remove, and modify process IDs, Arrival Times (AT), and Burst Times (BT) via an interactive table editor.
- **Built-in Benchmark Presets**: Includes the standard college assignment verification benchmark, simultaneous arrivals ($t=0$), and workloads with CPU idle gaps.
- **Interactive Plotly Gantt Chart**: Color-coded horizontal timeline displaying process execution slices, time boundaries, hover tooltips, and explicit CPU idle periods.
- **Step-by-Step Ready Queue Inspection**: Trace CPU scheduling decisions slice by slice with visual diagrams illustrating the circular FIFO Ready Queue (Front $\to$ Rear).
- **Comprehensive Performance Metrics**: Automatic calculation of Completion Time (CT), Turnaround Time (TAT), Waiting Time (WT), Response Time (RT), CPU Utilization, and Context Switch counts.
- **Time Quantum Sensitivity Analysis**: Compare scheduling performance across a spectrum of quantum values ($q$) with dual-axis comparative graphs.
- **Data Export (CSV)**: Export scheduling tables, execution intervals, and quantum sensitivity comparison results with a single click.
- **Defensive Input Validation**: Robust guards against negative arrival times, zero/negative burst times, invalid quanta, and duplicate process IDs.

---

## 3. Technology Stack

- **Core Language**: Python 3.10+
- **Web UI & Dashboard**: [Streamlit](https://streamlit.io/)
- **Data Structures**: `collections.deque` (FIFO Ready Queue)
- **Data Handling**: [Pandas](https://pandas.pydata.org/) & [NumPy](https://numpy.org/)
- **Visualizations**: [Plotly](https://plotly.com/) & [Matplotlib](https://matplotlib.org/)
- **Testing**: [pytest](https://pytest.org/) (21 unit tests covering all algorithmic scenarios)
- **Version Control**: Git & GitHub with a multi-branch team collaboration workflow

---

## 4. Project Folder Structure

```text
round-robin-cpu-scheduling-simulator/
│
├── app.py                     # Streamlit frontend dashboard application
├── scheduler.py               # Core Round Robin scheduling engine & queue logic
├── metrics.py                 # Performance metrics & context switch calculator
├── visualization.py           # Plotly Gantt chart & visual ready queue components
├── requirements.txt           # Project dependencies
├── README.md                  # Complete project documentation and guide
├── .gitignore                 # Git ignore file for Python cache & bytecode
│
├── tests/                     # Automated unit test suite
│   ├── __init__.py
│   ├── test_scheduler.py      # Scheduler algorithm & edge case test suite
│   └── test_metrics.py        # Metrics calculations & interval continuity tests
│
└── docs/                      # Technical documentation
    ├── architecture.md        # System architecture, data flow & component contracts
    ├── algorithm.md           # Theoretical specification & mathematical formulas
    └── test_cases.md          # Complete QA test matrix and validation records
```

---

## 5. Team Distribution & GitHub Branch Strategy

This project was built through a collaborative two-member team division:

| Team Member | Role | Assigned Branch | Primary Responsibilities |
| :--- | :--- | :--- | :--- |
| **Member 1** | **Backend Developer** | `backend-scheduler` | `scheduler.py`, `metrics.py`, `collections.deque` ready queue, slice recording, context switch counting, unit tests (`test_scheduler.py`, `test_metrics.py`). |
| **Member 2** | **Frontend Developer** | `frontend-dashboard` | `app.py`, `visualization.py`, dark-themed dashboard, Plotly Gantt charts, step-by-step queue visualizer, CSV export. |
| **Joint Team** | **Integration & QA** | `testing-documentation` | Architecture specifications, technical documentation, requirements, end-to-end integration, demo verification. |

### Branch Structure:
- `main`: Production-ready integrated release.
- `backend-scheduler`: Reserved for Member 1 backend logic and unit testing.
- `frontend-dashboard`: Reserved for Member 2 UI components and Plotly charts.
- `testing-documentation`: Shared branch for documentation, integration, and final testing.

---

## 6. Installation & Execution Guide

### Prerequisites
- Python 3.10, 3.11, 3.12, 3.13, or 3.14 installed on your system.
- Git.

### 1. Clone or Open the Repository
```bash
git clone https://github.com/SUCHET28/OS-Assignment.git
cd OS-Assignment
```

### 2. (Optional) Create a Virtual Environment
```bash
python -m venv venv

# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Launch the Streamlit Application
```bash
streamlit run app.py
```

The simulator will launch automatically in your default browser at `http://localhost:8501`.

---

## 7. Mathematical Formulas & Concepts

| Metric | Formula | Description |
| :--- | :--- | :--- |
| **Turnaround Time (TAT)** | $TAT = CT - AT$ | Elapsed time from submission to complete execution. |
| **Waiting Time (WT)** | $WT = TAT - BT$ | Total duration spent waiting in the ready queue. |
| **Response Time (RT)** | $RT = First\\ Dispatch\\ Time - AT$ | Time elapsed from arrival to the very first CPU execution. |
| **Average Waiting Time** | $\overline{WT} = \frac{1}{n} \sum WT$ | Mean waiting time over all $n$ processes. |
| **Average Turnaround Time** | $\overline{TAT} = \frac{1}{n} \sum TAT$ | Mean turnaround time over all $n$ processes. |
| **Average Response Time** | $\overline{RT} = \frac{1}{n} \sum RT$ | Mean response time over all $n$ processes. |
| **CPU Utilization** | $\frac{\text{Total Busy Time}}{\text{Total Elapsed Time}} \times 100\%$ | Proportion of time the CPU was actively executing processes. |

### Context Switch Convention:
A context switch is counted whenever the CPU transitions between two different processes (or between a process and CPU IDLE). Consecutive executions of the same process do not trigger a context switch.

---

## 8. Sample Verification Benchmark

### Input Data
- **Time Quantum ($q$)**: `2`

| Process ID | Arrival Time (AT) | Burst Time (BT) |
| :---: | :---: | :---: |
| **P1** | 0 | 5 |
| **P2** | 1 | 4 |
| **P3** | 2 | 2 |
| **P4** | 4 | 1 |

### Execution Slices (Gantt Order)
$$\text{P1 (0-2)} \to \text{P2 (2-4)} \to \text{P3 (4-6)} \to \text{P1 (6-8)} \to \text{P4 (8-9)} \to \text{P2 (9-11)} \to \text{P1 (11-12)}$$

### Expected Outputs
| PID | AT | BT | Completion Time (CT) | Turnaround Time (TAT) | Waiting Time (WT) | Response Time (RT) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **P1** | 0 | 5 | **12** | **12** | **7** | **0** |
| **P2** | 1 | 4 | **11** | **10** | **6** | **1** |
| **P3** | 2 | 2 | **6** | **4** | **2** | **2** |
| **P4** | 4 | 1 | **9** | **5** | **4** | **4** |

- **Average Waiting Time**: **4.75**
- **Average Turnaround Time**: **7.75**
- **Average Response Time**: **1.75**
- **CPU Utilization**: **100.0%**
- **Context Switches**: **6**

---

## 9. Running Automated Tests

The backend engine has an extensive test suite verifying 21 distinct scenarios including single processes, simultaneous arrivals, CPU idle gaps, burst time edge cases, invalid inputs, and interval continuity.

To execute the test suite:
```bash
pytest -v
```

Expected output:
```text
============================= test session starts =============================
collected 21 items

tests/test_metrics.py::test_correct_waiting_time PASSED                  [  4%]
tests/test_metrics.py::test_correct_turnaround_time PASSED               [  9%]
tests/test_metrics.py::test_correct_response_time PASSED                 [ 14%]
tests/test_metrics.py::test_correct_cpu_utilization PASSED               [ 19%]
tests/test_metrics.py::test_correct_gantt_chart_intervals PASSED         [ 23%]
tests/test_metrics.py::test_empty_metrics PASSED                         [ 28%]
tests/test_scheduler.py::test_sample_verification_case PASSED            [ 33%]
tests/test_scheduler.py::test_single_process PASSED                      [ 38%]
tests/test_scheduler.py::test_identical_arrival_times PASSED             [ 42%]
tests/test_scheduler.py::test_different_arrival_times PASSED             [ 47%]
tests/test_scheduler.py::test_cpu_idle_before_first_arrival PASSED       [ 52%]
tests/test_scheduler.py::test_cpu_idle_between_arrivals PASSED           [ 57%]
tests/test_scheduler.py::test_burst_smaller_than_quantum PASSED          [ 61%]
tests/test_scheduler.py::test_burst_equal_to_quantum PASSED              [ 66%]
tests/test_scheduler.py::test_burst_larger_than_quantum PASSED           [ 71%]
tests/test_scheduler.py::test_quantum_larger_than_all_burst_times PASSED [ 76%]
tests/test_scheduler.py::test_invalid_quantum PASSED                     [ 80%]
tests/test_scheduler.py::test_invalid_arrival_times PASSED               [ 85%]
tests/test_scheduler.py::test_invalid_burst_times PASSED                 [ 90%]
tests/test_scheduler.py::test_duplicate_process_ids PASSED               [ 95%]
tests/test_scheduler.py::test_empty_process_list PASSED                  [100%]

======================= 21 passed in 0.22s =======================
```

---

## 10. Future Enhancements

- Multi-Level Feedback Queue (MLFQ) extension.
- Priority-based Round Robin scheduling.
- Configurable context switch overhead penalty in calculation formulas.
- Real-time animation playback mode with variable speed controls.
