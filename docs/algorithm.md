# Round Robin CPU Scheduling Algorithm Specification

**Course**: Operating Systems (CS / IT Engineering)  
**Topic**: CPU Scheduling Algorithms - Preemptive Round Robin (RR)  
**Engine Implementation**: `scheduler.py` & `metrics.py`  

---

## 1. Introduction to Round Robin Scheduling

**Round Robin (RR)** is one of the oldest, simplest, fairest, and most widely used CPU scheduling algorithms, specifically designed for time-sharing systems.

### Key Characteristics:
1. **Preemptive**: The operating system allocates the CPU to a process for a fixed interval called a **Time Quantum** (or time slice). If the process has not completed within this slice, it is preempted, and the CPU is allocated to the next ready process.
2. **Circular FIFO Ready Queue**: Processes waiting for CPU execution reside in a First-In, First-Out (FIFO) queue. New or preempted processes are added to the tail (rear) of the queue.
3. **Starvation-Free**: Because CPU time is divided cyclically among ready processes, no process can monopolize the CPU, guaranteeing that every process makes steady progress.

---

## 2. Core Scheduling Rules & Invariants

### 2.1 Ready Queue Management
In our implementation, the ready queue is instantiated using Python's `collections.deque`:
- `popleft()`: Removes the process at the head of the queue in $O(1)$ time to dispatch it to the CPU.
- `append()`: Appends newly arrived or preempted processes to the rear of the queue in $O(1)$ time.

### 2.2 Deterministic Tie-Breaking Convention
When multiple events coincide at time $t$, order of operations is strictly deterministic:
1. **Arrival Priority**: Any unarrived processes whose arrival time $AT \le t$ (including those arriving during the slice or at the exact completion time $t$) are enqueued **BEFORE** the currently running process is requeued.
2. **Same Arrival Time Tie-Break**: If multiple processes arrive at the exact same arrival time, they are ordered deterministically by their original input sequence (or PID alphanumeric sorting).
3. **Preemption Requeue**: If the running process still has remaining burst time ($BT_{rem} > 0$), it is appended to the rear of the ready queue **AFTER** all newly arrived processes have entered.
4. **Completion**: If the running process completes ($BT_{rem} == 0$), its completion time is recorded as $CT = t$, and it leaves the scheduling loop.

### 2.3 CPU Idle Time Handling
- **Pre-arrival Idle**: If the earliest process arrives at $t > 0$, the CPU sits IDLE from $t=0$ to $t=AT_{min}$. This idle duration is logged as an explicit slice `ExecutionSlice(pid="IDLE", start_time=0, end_time=AT_min, is_idle=True)`.
- **Inter-arrival Idle**: If the ready queue becomes empty but unarrived processes remain in the system, the CPU enters an IDLE state from the current time to the arrival time of the next earliest process.

---

## 3. Mathematical Formulas

| Metric | Symbol | Formula | Explanation |
| :--- | :---: | :--- | :--- |
| **Completion Time** | $CT$ | Time when process completes execution | Timestamp when remaining burst becomes 0. |
| **Turnaround Time** | $TAT$ | $TAT = CT - AT$ | Total time from process submission to completion. |
| **Waiting Time** | $WT$ | $WT = TAT - BT$ | Total time the process spent waiting in the ready queue. |
| **Response Time** | $RT$ | $RT = First\\ CPU\\ Dispatch - AT$ | Time taken from arrival until the process first gets CPU time. |
| **Average Waiting Time** | $\overline{WT}$ | $\frac{1}{n}\sum_{i=1}^{n} WT_i$ | Arithmetic mean of waiting times across all $n$ processes. |
| **Average Turnaround Time** | $\overline{TAT}$ | $\frac{1}{n}\sum_{i=1}^{n} TAT_i$ | Arithmetic mean of turnaround times across all $n$ processes. |
| **Average Response Time** | $\overline{RT}$ | $\frac{1}{n}\sum_{i=1}^{n} RT_i$ | Arithmetic mean of response times across all $n$ processes. |
| **CPU Utilization** | $\%Util$ | $\frac{\text{Total Busy Time}}{\text{Total Elapsed Time}} \times 100\%$ | Ratio of active execution time to total simulation time. |
| **Throughput** | $TP$ | $\frac{n}{\text{Total Elapsed Time}}$ | Rate of processes completed per unit time. |

---

## 4. Context Switch Counting Convention

A **Context Switch** is the operational overhead where the operating system saves the state of the currently executing process and loads the context of the next process.

### Simulator Rule:
- A context switch is recorded whenever the CPU transitions from one entity to another (e.g. Process A $\to$ Process B, Process A $\to$ IDLE, or IDLE $\to$ Process B).
- If a process finishes its time slice but is the **only** process in the ready queue, it immediately continues into its next time slice without a context switch ($A \to A$).

---

## 5. Walkthrough of College Assignment Benchmark

Consider the 4-process workload with Time Quantum $q = 2$:

| Process | Arrival Time (AT) | Burst Time (BT) |
| :---: | :---: | :---: |
| **P1** | 0 | 5 |
| **P2** | 1 | 4 |
| **P3** | 2 | 2 |
| **P4** | 4 | 1 |

### Execution Timeline:
1. **$t = 0$**: P1 arrives ($AT=0$). Ready Queue: `[P1]`.
   - P1 executes from $t=0$ to $t=2$.
   - Remaining BT for P1 = $5 - 2 = 3$.
   - During $[0, 2]$, P2 arrives at $t=1$, and P3 arrives at $t=2$.
   - New arrivals enqueued: `[P2, P3]`.
   - Unfinished P1 is requeued: `[P2, P3, P1]`.
2. **$t = 2$**: P2 dispatched. Executes from $t=2$ to $t=4$.
   - Remaining BT for P2 = $4 - 2 = 2$.
   - At $t=4$, P4 arrives.
   - Ready queue before requeue: `[P3, P1, P4]`.
   - P2 requeued: `[P3, P1, P4, P2]`.
3. **$t = 4$**: P3 dispatched. Executes from $t=4$ to $t=6$.
   - Remaining BT for P3 = $2 - 2 = 0$.
   - **P3 finishes at $t=6$!** ($CT=6$).
   - Ready Queue: `[P1, P4, P2]`.
4. **$t = 6$**: P1 dispatched. Executes from $t=6$ to $t=8$.
   - Remaining BT for P1 = $3 - 2 = 1$.
   - P1 requeued: `[P4, P2, P1]`.
5. **$t = 8$**: P4 dispatched. Remaining BT is 1, which is $\le q=2$.
   - P4 executes from $t=8$ to $t=9$.
   - **P4 finishes at $t=9$!** ($CT=9$).
   - Ready Queue: `[P2, P1]`.
6. **$t = 9$**: P2 dispatched. Executes from $t=9$ to $t=11$.
   - Remaining BT for P2 = $2 - 2 = 0$.
   - **P2 finishes at $t=11$!** ($CT=11$).
   - Ready Queue: `[P1]`.
7. **$t = 11$**: P1 dispatched. Remaining BT is 1.
   - P1 executes from $t=11$ to $t=12$.
   - **P1 finishes at $t=12$!** ($CT=12$).
   - Ready Queue: `[]`. Simulation terminates at $t=12$.

### Final Results:
| PID | AT | BT | First Start | CT | TAT (CT - AT) | WT (TAT - BT) | RT (Start - AT) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **P1** | 0 | 5 | 0 | 12 | 12 | 7 | 0 |
| **P2** | 1 | 4 | 2 | 11 | 10 | 6 | 1 |
| **P3** | 2 | 2 | 4 | 6 | 4 | 2 | 2 |
| **P4** | 4 | 1 | 8 | 9 | 5 | 4 | 4 |

- **Average Waiting Time**: $\frac{7 + 6 + 2 + 4}{4} = \mathbf{4.75}$
- **Average Turnaround Time**: $\frac{12 + 10 + 4 + 5}{4} = \mathbf{7.75}$
- **Average Response Time**: $\frac{0 + 1 + 2 + 4}{4} = \mathbf{1.75}$
- **CPU Utilization**: $\frac{12}{12} \times 100\% = \mathbf{100.0\%}$
- **Context Switches**: $6$ switches (P1 $\to$ P2 $\to$ P3 $\to$ P1 $\to$ P4 $\to$ P2 $\to$ P1).
