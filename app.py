"""
Round Robin CPU Scheduling Simulator - Interactive Streamlit Application
========================================================================
Author: Frontend Developer (PALLAVI M V) & Integrated Team
Branch: frontend-dashboard

An interactive web-based simulator for exploring Round Robin CPU Scheduling.
Designed for engineering college demonstrations, lab assignments, and vivas.
"""

from __future__ import annotations
import streamlit as st
import pandas as pd
import numpy as np
from typing import List, Dict, Any

from scheduler import Process, simulate_round_robin, ScheduleResult
from visualization import (
    create_gantt_chart,
    create_process_metrics_chart,
    create_quantum_comparison_charts,
    render_ready_queue_html,
)

# Page configuration
st.set_page_config(
    page_title="Round Robin CPU Scheduling Simulator",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Dark Theme CSS Injection
st.markdown(
    """
    <style>
    /* Global background and fonts */
    .stApp {
        background-color: #090D16;
        color: #F1F5F9;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #F8FAFC !important;
        font-weight: 700;
    }
    
    /* Metric Cards */
    div[data-testid="stMetric"] {
        background: linear-gradient(145deg, #131D31, #0F172A);
        border: 1px solid #1E293B;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        border-color: #38BDF8;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 13px !important;
        color: #94A3B8 !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    div[data-testid="stMetricValue"] {
        font-size: 26px !important;
        color: #38BDF8 !important;
        font-weight: 800 !important;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #0284C7, #0369A1);
        color: #FFFFFF;
        font-weight: 600;
        border: none;
        border-radius: 8px;
        padding: 8px 18px;
        transition: all 0.2s ease;
        box-shadow: 0 4px 12px rgba(2, 132, 199, 0.3);
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #0EA5E9, #0284C7);
        box-shadow: 0 6px 18px rgba(14, 165, 233, 0.4);
        transform: translateY(-1px);
    }
    
    /* Cards and Containers */
    .info-card {
        background: #0F172A;
        border: 1px solid #1E293B;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #0B1120;
        border-right: 1px solid #1E293B;
    }
    
    /* Dataframe / Tables */
    div[data-testid="stDataFrame"] {
        border: 1px solid #1E293B;
        border-radius: 8px;
        overflow: hidden;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Default test dataset (Section 11)
DEFAULT_PROCESSES = [
    {"PID": "P1", "Arrival Time": 0.0, "Burst Time": 5.0},
    {"PID": "P2", "Arrival Time": 1.0, "Burst Time": 4.0},
    {"PID": "P3", "Arrival Time": 2.0, "Burst Time": 2.0},
    {"PID": "P4", "Arrival Time": 4.0, "Burst Time": 1.0},
]

# Initialize Session State
if "process_data" not in st.session_state:
    st.session_state.process_data = pd.DataFrame(DEFAULT_PROCESSES)

if "time_quantum" not in st.session_state:
    st.session_state.time_quantum = 2.0

if "simulation_result" not in st.session_state:
    st.session_state.simulation_result = None

if "current_step_idx" not in st.session_state:
    st.session_state.current_step_idx = 0


def load_preset(preset_name: str):
    """Loads standardized presets into the session state."""
    if preset_name == "Section 11 Sample":
        st.session_state.process_data = pd.DataFrame([
            {"PID": "P1", "Arrival Time": 0.0, "Burst Time": 5.0},
            {"PID": "P2", "Arrival Time": 1.0, "Burst Time": 4.0},
            {"PID": "P3", "Arrival Time": 2.0, "Burst Time": 2.0},
            {"PID": "P4", "Arrival Time": 4.0, "Burst Time": 1.0},
        ])
        st.session_state.time_quantum = 2.0
    elif preset_name == "Simultaneous Arrivals (t=0)":
        st.session_state.process_data = pd.DataFrame([
            {"PID": "P1", "Arrival Time": 0.0, "Burst Time": 6.0},
            {"PID": "P2", "Arrival Time": 0.0, "Burst Time": 4.0},
            {"PID": "P3", "Arrival Time": 0.0, "Burst Time": 8.0},
            {"PID": "P4", "Arrival Time": 0.0, "Burst Time": 3.0},
        ])
        st.session_state.time_quantum = 3.0
    elif preset_name == "CPU Idle Intervals":
        st.session_state.process_data = pd.DataFrame([
            {"PID": "P1", "Arrival Time": 2.0, "Burst Time": 3.0},
            {"PID": "P2", "Arrival Time": 8.0, "Burst Time": 4.0},
            {"PID": "P3", "Arrival Time": 15.0, "Burst Time": 2.0},
        ])
        st.session_state.time_quantum = 2.0


# -------------------------------------------------------------
# SIDEBAR: CONFIGURATION & WORKLOAD SETUP
# -------------------------------------------------------------
with st.sidebar:
    st.image("https://raw.githubusercontent.com/feathericons/feather/master/icons/cpu.svg", width=42)
    st.title("CPU Scheduler")
    st.caption("College OS Mini-Project · Two-Member Collaboration")
    st.divider()

    st.subheader("⚙️ Workload Presets")
    col_pre1, col_pre2 = st.columns(2)
    with col_pre1:
        if st.button("Sample Data", width="stretch", help="Load Section 11 Benchmark"):
            load_preset("Section 11 Sample")
            st.rerun()
    with col_pre2:
        if st.button("Idle Gaps", width="stretch", help="Load Workload with CPU Idle Gaps"):
            load_preset("CPU Idle Intervals")
            st.rerun()

    if st.button("Simultaneous (t=0)", width="stretch"):
        load_preset("Simultaneous Arrivals (t=0)")
        st.rerun()

    st.divider()

    st.subheader("⏱️ Time Quantum (q)")
    quantum_val = st.number_input(
        "Time Quantum",
        min_value=0.5,
        max_value=100.0,
        value=float(st.session_state.time_quantum),
        step=0.5,
        help="Maximum time slice allocated to each process per round in CPU",
    )
    st.session_state.time_quantum = quantum_val

    st.divider()

    st.subheader("👥 Project Credits")
    st.markdown(
        """
        - **V SUCHET (Backend Developer)**:
          `scheduler.py`, `metrics.py`, Unit Tests
        - **PALLAVI M V (Frontend Developer)**:
          `app.py`, `visualization.py`, UI/UX
        """
    )
    st.caption("Branch Model: `backend-scheduler` & `frontend-dashboard`")


# -------------------------------------------------------------
# MAIN CONTENT HEADER
# -------------------------------------------------------------
st.title("⚡ Round Robin CPU Scheduling Simulator")
st.markdown(
    "A comprehensive, interactive demonstration of preemptive **Round Robin (RR)** CPU scheduling, "
    "evaluating performance metrics, ready queue transitions, and time quantum sensitivity."
)

tab_sim, tab_steps, tab_analysis, tab_theory = st.tabs([
    "📊 Simulator & Results",
    "🔄 Step-by-Step Ready Queue",
    "📈 Quantum Sensitivity Analysis",
    "📖 Algorithm & Theory Guide",
])

# -------------------------------------------------------------
# TAB 1: SIMULATOR & RESULTS
# -------------------------------------------------------------
with tab_sim:
    st.markdown("### 1. Process Configuration")
    st.markdown(
        "Edit the table below to configure process IDs, arrival times (AT), and burst times (BT). "
        "You can add or remove rows directly."
    )

    edited_df = st.data_editor(
        st.session_state.process_data,
        num_rows="dynamic",
        width="stretch",
        column_config={
            "PID": st.column_config.TextColumn("Process ID", required=True),
            "Arrival Time": st.column_config.NumberColumn("Arrival Time (AT)", min_value=0.0, step=1.0, required=True),
            "Burst Time": st.column_config.NumberColumn("Burst Time (BT)", min_value=0.1, step=1.0, required=True),
        },
    )
    st.session_state.process_data = edited_df

    col_btn1, col_btn2, _ = st.columns([2, 2, 4])
    with col_btn1:
        run_sim = st.button("🚀 Run Simulation", width="stretch", type="primary")
    with col_btn2:
        if st.button("🔄 Reset Table", width="stretch"):
            load_preset("Section 11 Sample")
            st.rerun()

    # Simulation execution
    has_error = False
    process_list: List[Process] = []

    if run_sim or st.session_state.simulation_result is None:
        try:
            if edited_df.empty:
                st.error("Error: The process table cannot be empty. Please add at least one process.")
                has_error = True
            else:
                for _, row in edited_df.iterrows():
                    pid_str = str(row["PID"]).strip()
                    if not pid_str:
                        raise ValueError("Process ID cannot be empty.")
                    at = float(row["Arrival Time"])
                    bt = float(row["Burst Time"])
                    process_list.append(Process(pid=pid_str, arrival_time=at, burst_time=bt))

                # Run backend scheduling engine
                res = simulate_round_robin(process_list, float(st.session_state.time_quantum))
                st.session_state.simulation_result = res
                st.session_state.current_step_idx = 0
        except Exception as e:
            st.error(f"⚠️ Validation Error: {e}")
            has_error = True

    # Render Simulation Results
    if not has_error and st.session_state.simulation_result is not None:
        res: ScheduleResult = st.session_state.simulation_result
        metrics = res.metrics

        st.divider()
        st.markdown("### 2. Performance Summary")

        mcol1, mcol2, mcol3, mcol4, mcol5, mcol6 = st.columns(6)
        mcol1.metric("Avg Waiting Time", f"{metrics['average_waiting_time']:.2f}")
        mcol2.metric("Avg Turnaround Time", f"{metrics['average_turnaround_time']:.2f}")
        mcol3.metric("Avg Response Time", f"{metrics['average_response_time']:.2f}")
        mcol4.metric("CPU Utilization", f"{metrics['cpu_utilization']:.1f}%")
        mcol5.metric("Context Switches", f"{metrics['context_switches']}")
        mcol6.metric("Total Elapsed Time", f"{metrics['total_elapsed_time']:.1f}")

        st.divider()
        st.markdown("### 3. CPU Execution Timeline (Gantt Chart)")
        gantt_fig = create_gantt_chart(res.execution_history)
        st.plotly_chart(gantt_fig, width="stretch")

        st.divider()
        col_res1, col_res2 = st.columns([1, 1])

        with col_res1:
            st.markdown("### 4. Process Scheduling Table")
            res_df = pd.DataFrame([p.to_dict() for p in res.processes])
            st.dataframe(res_df, width="stretch", hide_index=True)

            # CSV Download
            csv_data = res_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download Scheduling Results (CSV)",
                data=csv_data,
                file_name="round_robin_scheduling_results.csv",
                mime="text/csv",
            )

        with col_res2:
            st.markdown("### 5. Metrics Comparison Breakdown")
            metrics_chart = create_process_metrics_chart(res.processes)
            st.plotly_chart(metrics_chart, width="stretch")

        st.divider()
        st.markdown("### 6. Execution Interval Details")
        slices_df = pd.DataFrame([s.to_dict() for s in res.execution_history])
        col_s1, col_s2 = st.columns([2, 1])
        with col_s1:
            st.dataframe(slices_df, width="stretch", hide_index=True)
        with col_s2:
            st.markdown(
                f"""
                <div class="info-card">
                    <b>Execution Summary:</b><br>
                    • <b>Time Quantum:</b> {res.quantum}<br>
                    • <b>Total Slices:</b> {metrics['total_slices']}<br>
                    • <b>Busy Slices:</b> {metrics['busy_slices']}<br>
                    • <b>CPU Idle Time:</b> {metrics['total_idle_time']} units<br>
                    • <b>Throughput:</b> {metrics['throughput']:.4f} proc/unit
                </div>
                """,
                unsafe_allow_html=True,
            )
            csv_slices = slices_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download Execution Slices (CSV)",
                data=csv_slices,
                file_name="round_robin_execution_slices.csv",
                mime="text/csv",
            )


# -------------------------------------------------------------
# TAB 2: STEP-BY-STEP READY QUEUE VISUALIZATION
# -------------------------------------------------------------
with tab_steps:
    st.markdown("### 🔄 Step-by-Step Ready Queue Simulation")
    st.markdown(
        "Trace each CPU dispatch decision, examine the state of the FIFO Ready Queue, "
        "and observe how processes are preempted or completed at each time slice."
    )

    if st.session_state.simulation_result is not None:
        res: ScheduleResult = st.session_state.simulation_result
        steps = res.step_history
        total_steps = len(steps)

        if total_steps > 0:
            step_idx = st.slider(
                "Navigate Execution Step",
                min_value=1,
                max_value=total_steps,
                value=st.session_state.current_step_idx + 1,
                help="Move slider to inspect intermediate states of the ready queue.",
            )
            st.session_state.current_step_idx = step_idx - 1

            col_nav1, col_nav2, _ = st.columns([1, 1, 4])
            with col_nav1:
                if st.button("⬅️ Previous Step") and st.session_state.current_step_idx > 0:
                    st.session_state.current_step_idx -= 1
                    st.rerun()
            with col_nav2:
                if st.button("Next Step ➡️") and st.session_state.current_step_idx < total_steps - 1:
                    st.session_state.current_step_idx += 1
                    st.rerun()

            current_step = steps[st.session_state.current_step_idx]

            # Render Visual Ready Queue
            st.markdown(
                render_ready_queue_html(
                    queue_items=current_step.ready_queue_after,
                    executing_pid=current_step.executing_pid,
                ),
                unsafe_allow_html=True,
            )

            # Step Details Grid
            col_d1, col_d2, col_d3, col_d4 = st.columns(4)
            col_d1.metric("Current Time", f"t = {current_step.time:g}")
            col_d2.metric("Executing Process", current_step.executing_pid)
            col_d3.metric("Duration Executed", f"{current_step.duration:g} units")
            col_d4.metric("Remaining Burst", f"{current_step.remaining_burst:g} units")

            st.info(f"**Event Log:** {current_step.event_description}")

            # All Steps History Table
            with st.expander("📋 View Complete Step Execution Log"):
                step_log_df = pd.DataFrame([
                    {
                        "Step": s.step_number,
                        "Time": s.time,
                        "Process": s.executing_pid,
                        "Duration": s.duration,
                        "Remaining BT": s.remaining_burst,
                        "Ready Queue (After)": ", ".join(s.ready_queue_after) if s.ready_queue_after else "[Empty]",
                        "Completed": "Yes" if s.completed else "No",
                        "Description": s.event_description,
                    }
                    for s in steps
                ])
                st.dataframe(step_log_df, width="stretch", hide_index=True)
    else:
        st.info("Run the simulation in the 'Simulator & Results' tab first to enable step-by-step inspection.")


# -------------------------------------------------------------
# TAB 3: QUANTUM SENSITIVITY ANALYSIS
# -------------------------------------------------------------
with tab_analysis:
    st.markdown("### 📈 Time Quantum (q) Sensitivity Analysis")
    st.markdown(
        "Evaluate how varying the Time Quantum impacts Average Waiting Time, "
        "Turnaround Time, Response Time, and Context Switch Overhead for your workload."
    )

    col_q1, col_q2 = st.columns(2)
    with col_q1:
        min_q = st.number_input("Minimum Quantum to Test", min_value=1.0, max_value=20.0, value=1.0, step=1.0)
    with col_q2:
        max_q = st.number_input("Maximum Quantum to Test", min_value=2.0, max_value=50.0, value=10.0, step=1.0)

    if min_q >= max_q:
        st.warning("Minimum Quantum must be strictly less than Maximum Quantum.")
    else:
        # Run comparative simulations
        comparison_records = []
        q_range = np.arange(min_q, max_q + 1, 1.0)

        for test_q in q_range:
            try:
                # Reconstruct process list
                test_procs = [
                    Process(pid=str(row["PID"]).strip(), arrival_time=float(row["Arrival Time"]), burst_time=float(row["Burst Time"]))
                    for _, row in st.session_state.process_data.iterrows()
                ]
                sim_res = simulate_round_robin(test_procs, quantum=float(test_q))
                m = sim_res.metrics
                comparison_records.append({
                    "Quantum": float(test_q),
                    "Avg Waiting Time": m["average_waiting_time"],
                    "Avg Turnaround Time": m["average_turnaround_time"],
                    "Avg Response Time": m["average_response_time"],
                    "Context Switches": m["context_switches"],
                    "CPU Utilization (%)": m["cpu_utilization"],
                    "Total Slices": m["total_slices"],
                })
            except Exception:
                continue

        if comparison_records:
            comp_df = pd.DataFrame(comparison_records)

            fig_wt, fig_cs = create_quantum_comparison_charts(comp_df)
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                st.plotly_chart(fig_wt, width="stretch")
            with col_c2:
                st.plotly_chart(fig_cs, width="stretch")

            st.markdown("#### Comparison Summary Table")
            st.dataframe(comp_df, width="stretch", hide_index=True)

            # CSV Download
            csv_comp = comp_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download Quantum Comparison (CSV)",
                data=csv_comp,
                file_name="quantum_comparison_analysis.csv",
                mime="text/csv",
            )

            st.markdown(
                """
                > **Operating Systems Insight:**
                > - **Small Time Quantum (q → 0)**: Enhances interactive responsiveness (lowers response time). However, it drastically increases context switching overhead, wasting CPU cycles on saving/restoring register states.
                > - **Large Time Quantum (q → ∞)**: Context switches decrease, but the scheduler degenerates into First-Come, First-Served (FCFS), leading to the *convoy effect* and elevated waiting times for shorter jobs.
                > - **Conclusion**: No single quantum is universally optimal; the ideal quantum typically encompasses 80% of CPU bursts in production systems.
                """
            )


# -------------------------------------------------------------
# TAB 4: ALGORITHM & THEORY GUIDE
# -------------------------------------------------------------
with tab_theory:
    st.markdown("### 📖 Round Robin CPU Scheduling Theory & Formulas")
    
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.markdown(
            """
            #### 1. Core Concepts
            - **Type**: Preemptive scheduling algorithm.
            - **Data Structure**: Circular First-In, First-Out (FIFO) Ready Queue.
            - **Time Slice (Quantum)**: Fixed duration of CPU time granted to each process.
            - **Preemption Rule**: When a process runs for its quantum without completing, the CPU is preempted and the process is returned to the back of the ready queue.
            - **Starvation-Free**: Every ready process receives CPU time periodically.
            """
        )
    with col_t2:
        st.markdown(
            """
            #### 2. Mathematical Formulas
            - **Turnaround Time (TAT)**:
              $$TAT = Completion\\ Time (CT) - Arrival\\ Time (AT)$$
            - **Waiting Time (WT)**:
              $$WT = Turnaround\\ Time (TAT) - Burst\\ Time (BT)$$
            - **Response Time (RT)**:
              $$RT = First\\ CPU\\ Dispatch\\ Time - Arrival\\ Time (AT)$$
            - **CPU Utilization**:
              $$\\text{Utilization} = \\frac{\\text{Total Busy Time}}{\\text{Total Elapsed Time}} \\times 100\\%$$
            """
        )

    st.divider()
    st.markdown(
        """
        #### 3. Context Switch Counting Convention
        In this simulator:
        - A context switch is recorded whenever the CPU switches between different execution contexts (e.g., from Process A to Process B, or between a process and CPU IDLE).
        - If a single process is the only one in the ready queue and executes consecutive time slices, **no context switch** is incurred.
        """
    )
