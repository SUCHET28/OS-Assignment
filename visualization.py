"""
Round Robin CPU Scheduling Simulator - Visualization Engine
============================================================
Author: Frontend Developer (PALLAVI M V)
Branch: frontend-dashboard

Provides interactive Plotly visualizations:
1. Interactive Gantt Chart with idle intervals and detailed tooltips.
2. Process performance comparison bar charts (WT, TAT, RT per process).
3. Quantum sensitivity and comparison charts (Context Switches vs Waiting Time vs TAT).
4. Step-by-step Ready Queue visual representations.
"""

from __future__ import annotations
from typing import List, Dict, Any, Tuple
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from scheduler import ExecutionSlice, ProcessResult, SimulationStep


# Sleek professional dark palette
PROCESS_COLORS = [
    "#00D2FC",  # Vibrant Cyan
    "#FF5376",  # Coral Pink
    "#2EE59D",  # Emerald Green
    "#FFC107",  # Amber Yellow
    "#9D4EDD",  # Vivid Purple
    "#FF7A00",  # Neon Orange
    "#00E5FF",  # Bright Turquoise
    "#FF007F",  # Hot Pink
    "#7000FF",  # Deep Violet
    "#00F5D4",  # Mint
]
IDLE_COLOR = "#4A5568"  # Slate Gray for CPU Idle


def create_gantt_chart(execution_history: List[ExecutionSlice]) -> go.Figure:
    """
    Constructs an interactive Plotly Gantt chart from execution slices.

    Features:
    - Dedicated visual lane for CPU execution.
    - Custom color mapping per process and distinct styling for CPU IDLE.
    - High-contrast, clean dark theme.
    - Hover information showing PID, start, end, and duration.
    """
    if not execution_history:
        fig = go.Figure()
        fig.update_layout(title="No execution data available")
        return fig

    # Map unique processes to colors
    unique_pids = []
    for s in execution_history:
        if s.pid != "IDLE" and s.pid not in unique_pids:
            unique_pids.append(s.pid)

    color_map = {pid: PROCESS_COLORS[i % len(PROCESS_COLORS)] for i, pid in enumerate(unique_pids)}
    color_map["IDLE"] = IDLE_COLOR

    fig = go.Figure()

    # Determine max time for layout
    max_time = execution_history[-1].end_time

    for s in execution_history:
        bar_color = color_map.get(s.pid, "#888888")
        opacity = 0.6 if s.is_idle else 0.95
        name_label = "CPU IDLE" if s.is_idle else f"Process {s.pid}"

        hover_text = (
            f"<b>{name_label}</b><br>"
            f"Start Time: {s.start_time:g}<br>"
            f"End Time: {s.end_time:g}<br>"
            f"Duration: {s.duration:g} unit(s)"
        )

        fig.add_trace(
            go.Bar(
                name=s.pid,
                x=[s.duration],
                y=["CPU Execution"],
                orientation="h",
                base=[s.start_time],
                marker=dict(
                    color=bar_color,
                    opacity=opacity,
                    line=dict(color="#1E293B", width=2),
                ),
                text=f"{s.pid} [{s.start_time:g}-{s.end_time:g}]" if s.duration >= 0.8 else s.pid,
                textposition="inside",
                insidetextanchor="middle",
                textfont=dict(color="#FFFFFF", size=13, family="monospace", weight="bold"),
                hovertemplate=hover_text + "<extra></extra>",
                showlegend=(s.pid not in [t.name for t in fig.data]),
            )
        )

    # Time milestones / ticks
    tick_interval = 1 if max_time <= 30 else (2 if max_time <= 60 else 5)
    tick_vals = list(range(0, int(max_time) + 1, tick_interval))
    if max_time not in tick_vals:
        tick_vals.append(max_time)

    fig.update_layout(
        title=dict(
            text="<b>CPU Execution Timeline (Gantt Chart)</b>",
            font=dict(size=18, color="#F8FAFC"),
        ),
        barmode="stack",
        height=220,
        margin=dict(l=40, r=40, t=50, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#0F172A",
        xaxis=dict(
            title=dict(text="Timeline (Time Units)", font=dict(color="#94A3B8", size=13)),
            tickmode="array",
            tickvals=tick_vals,
            tickfont=dict(color="#94A3B8", size=11),
            gridcolor="#334155",
            gridwidth=1,
            zeroline=True,
            zerolinecolor="#475569",
            range=[0, max_time + (0.5 if max_time < 20 else 1)],
        ),
        yaxis=dict(
            title="",
            tickfont=dict(color="#F8FAFC", size=14, weight="bold"),
            showgrid=False,
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.1,
            xanchor="center",
            x=0.5,
            font=dict(color="#CBD5E1", size=12),
        ),
    )

    return fig


def create_process_metrics_chart(processes: List[ProcessResult]) -> go.Figure:
    """
    Creates a grouped bar chart comparing Turnaround Time, Waiting Time,
    and Response Time across all processes.
    """
    if not processes:
        return go.Figure()

    df = pd.DataFrame([
        {
            "PID": p.pid,
            "Turnaround Time (TAT)": p.turnaround_time,
            "Waiting Time (WT)": p.waiting_time,
            "Response Time (RT)": p.response_time,
            "Burst Time (BT)": p.burst_time,
        }
        for p in processes
    ])

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df["PID"],
        y=df["Turnaround Time (TAT)"],
        name="Turnaround Time (TAT)",
        marker_color="#00D2FC",
    ))
    fig.add_trace(go.Bar(
        x=df["PID"],
        y=df["Waiting Time (WT)"],
        name="Waiting Time (WT)",
        marker_color="#FF5376",
    ))
    fig.add_trace(go.Bar(
        x=df["PID"],
        y=df["Response Time (RT)"],
        name="Response Time (RT)",
        marker_color="#FFC107",
    ))

    fig.update_layout(
        title=dict(
            text="<b>Per-Process Performance Metrics Breakdown</b>",
            font=dict(size=16, color="#F8FAFC"),
        ),
        barmode="group",
        height=360,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#0F172A",
        margin=dict(l=40, r=40, t=50, b=40),
        xaxis=dict(
            title=dict(text="Process ID", font=dict(color="#94A3B8")),
            tickfont=dict(color="#F8FAFC", size=12),
            gridcolor="#1E293B",
        ),
        yaxis=dict(
            title=dict(text="Time Units", font=dict(color="#94A3B8")),
            tickfont=dict(color="#94A3B8"),
            gridcolor="#334155",
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(color="#CBD5E1", size=12),
        ),
    )
    return fig


def create_quantum_comparison_charts(
    comparison_df: pd.DataFrame,
) -> Tuple[go.Figure, go.Figure]:
    """
    Generates two analytical charts for Time Quantum Sensitivity:
    1. Average Waiting Time & Turnaround Time vs. Quantum
    2. Context Switches vs. Quantum
    """
    # Chart 1: WT and TAT vs Quantum
    fig1 = go.Figure()
    fig1.add_trace(
        go.Scatter(
            x=comparison_df["Quantum"],
            y=comparison_df["Avg Waiting Time"],
            mode="lines+markers",
            name="Avg Waiting Time",
            line=dict(color="#FF5376", width=3),
            marker=dict(size=8),
        )
    )
    fig1.add_trace(
        go.Scatter(
            x=comparison_df["Quantum"],
            y=comparison_df["Avg Turnaround Time"],
            mode="lines+markers",
            name="Avg Turnaround Time",
            line=dict(color="#00D2FC", width=3),
            marker=dict(size=8),
        )
    )
    fig1.add_trace(
        go.Scatter(
            x=comparison_df["Quantum"],
            y=comparison_df["Avg Response Time"],
            mode="lines+markers",
            name="Avg Response Time",
            line=dict(color="#FFC107", width=2, dash="dash"),
            marker=dict(size=6),
        )
    )

    fig1.update_layout(
        title=dict(
            text="<b>Effect of Time Quantum on Waiting & Turnaround Times</b>",
            font=dict(size=15, color="#F8FAFC"),
        ),
        height=360,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#0F172A",
        margin=dict(l=40, r=40, t=50, b=40),
        xaxis=dict(
            title=dict(text="Time Quantum (q)", font=dict(color="#94A3B8")),
            tickmode="linear",
            dtick=1,
            tickfont=dict(color="#CBD5E1"),
            gridcolor="#334155",
        ),
        yaxis=dict(
            title=dict(text="Average Time Units", font=dict(color="#94A3B8")),
            tickfont=dict(color="#CBD5E1"),
            gridcolor="#334155",
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(color="#CBD5E1", size=11),
        ),
    )

    # Chart 2: Context Switches vs Quantum
    fig2 = go.Figure()
    fig2.add_trace(
        go.Bar(
            x=comparison_df["Quantum"],
            y=comparison_df["Context Switches"],
            name="Context Switches",
            marker=dict(
                color="#9D4EDD",
                line=dict(color="#C77DFF", width=1.5),
            ),
            text=comparison_df["Context Switches"],
            textposition="auto",
            textfont=dict(color="#FFFFFF", weight="bold"),
        )
    )

    fig2.update_layout(
        title=dict(
            text="<b>Context Switch Frequency vs. Time Quantum</b>",
            font=dict(size=15, color="#F8FAFC"),
        ),
        height=360,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#0F172A",
        margin=dict(l=40, r=40, t=50, b=40),
        xaxis=dict(
            title=dict(text="Time Quantum (q)", font=dict(color="#94A3B8")),
            tickmode="linear",
            dtick=1,
            tickfont=dict(color="#CBD5E1"),
            gridcolor="#334155",
        ),
        yaxis=dict(
            title=dict(text="Total Context Switches", font=dict(color="#94A3B8")),
            tickfont=dict(color="#CBD5E1"),
            gridcolor="#334155",
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(color="#CBD5E1", size=11),
        ),
    )

    return fig1, fig2


def render_ready_queue_html(queue_items: List[str], executing_pid: str) -> str:
    """
    Generates a visual HTML block displaying the CPU and the FIFO ready queue.
    """
    executing_badge = (
        f'<div style="display:inline-block; background: linear-gradient(135deg, #00D2FC, #0072FF); '
        f'color: #0F172A; font-weight: 700; padding: 10px 18px; border-radius: 8px; font-size: 16px; '
        f'box-shadow: 0 4px 14px rgba(0,210,252,0.4); text-align:center; min-width:80px;">'
        f'{executing_pid}'
        f'</div>'
        if executing_pid != "IDLE"
        else
        f'<div style="display:inline-block; background: #334155; color: #94A3B8; font-weight: 700; '
        f'padding: 10px 18px; border-radius: 8px; font-size: 16px; text-align:center; min-width:80px;">'
        f'IDLE'
        f'</div>'
    )

    if queue_items:
        queue_boxes = ""
        for idx, item in enumerate(queue_items):
            badge = (
                f'<div style="display:inline-block; background: #1E293B; border: 2px solid #38BDF8; '
                f'color: #F8FAFC; font-weight: 600; padding: 8px 14px; border-radius: 6px; '
                f'font-size: 14px; margin: 0 4px; box-shadow: 0 2px 8px rgba(0,0,0,0.3);">'
                f'{item}'
                f'</div>'
            )
            arrow = '<span style="color:#64748B; font-size:16px; margin: 0 2px;">←</span>' if idx < len(queue_items) - 1 else ''
            queue_boxes += f"{badge}{arrow}"
    else:
        queue_boxes = '<span style="color:#64748B; font-style:italic;">[ Ready Queue is currently Empty ]</span>'

    html = f"""
    <div style="background-color: #0B1120; border: 1px solid #1E293B; border-radius: 12px; padding: 18px; margin: 15px 0;">
        <div style="display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 20px;">
            <div style="flex: 1; min-width: 200px;">
                <div style="color: #94A3B8; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px;">
                    ⚡ CPU Currently Executing
                </div>
                {executing_badge}
            </div>
            <div style="flex: 2; min-width: 300px;">
                <div style="color: #94A3B8; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px;">
                    📋 Ready Queue (Front → Rear)
                </div>
                <div style="display: flex; align-items: center; flex-wrap: wrap;">
                    {queue_boxes}
                </div>
            </div>
        </div>
    </div>
    """
    return html
