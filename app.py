import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import io
from datetime import datetime

# ---------------------------------------------------------
# 1. PAGE CONFIG & STYLING
# ---------------------------------------------------------
st.set_page_config(
    page_title="Pricol 14-Makino Platform",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    h1, h2, h3 { color: #0D5C75; font-family: 'Segoe UI', sans-serif; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h2 style='text-align: center; color: #0D5C75;'>🏭 PRICOL UNIT III - 14-MAKINO PRODUCTION HUB</h2>", unsafe_allow_html=True)
st.markdown("---")

# ---------------------------------------------------------
# 2. EXACT 14-MAKINO MAPPING & MATERIAL DEFINITIONS
# ---------------------------------------------------------
makino_fleet = {
    # SINGLE PALLET MACHINES (1, 2, 13, 14)
    "Makino-01": {"type": "Single Pallet", "p1": "Oil Pump Housing", "p2": None, "base_p1": 210, "base_p2": 0, "dt": 15, "sc": 2, "fm": 850, "dr": 320},
    "Makino-02": {"type": "Single Pallet", "p1": "Water Pump Body", "p2": None, "base_p1": 195, "base_p2": 0, "dt": 25, "sc": 3, "fm": 910, "dr": 400},
    
    # DUAL PALLET MACHINES (3 to 12)
    "Makino-03": {"type": "Dual Pallet", "p1": "Pump Body (PB 444)", "p2": "Pressure Cover (PC)", "base_p1": 180, "base_p2": 90, "dt": 30, "sc": 4, "fm": 820, "dr": 310},
    "Makino-04": {"type": "Dual Pallet", "p1": "Transmission Case A", "p2": "Transmission Cap B", "base_p1": 160, "base_p2": 160, "dt": 20, "sc": 1, "fm": 650, "dr": 280},
    "Makino-05": {"type": "Dual Pallet", "p1": "Fuel Line Flange", "p2": "Fuel Line Valve Seat", "base_p1": 220, "base_p2": 110, "dt": 10, "sc": 2, "fm": 740, "dr": 350},
    "Makino-06": {"type": "Dual Pallet", "p1": "Manifold Intake A", "p2": "Manifold Cover B", "base_p1": 140, "base_p2": 140, "dt": 40, "sc": 5, "fm": 1050, "dr": 480},
    "Makino-07": {"type": "Dual Pallet", "p1": "Engine Mount L", "p2": "Engine Mount R", "base_p1": 175, "base_p2": 175, "dt": 15, "sc": 2, "fm": 530, "dr": 210},
    "Makino-08": {"type": "Dual Pallet", "p1": "Coolant Elbow A", "p2": "Coolant Base B", "base_p1": 200, "base_p2": 100, "dt": 0, "sc": 1, "fm": 400, "dr": 150},
    "Makino-09": {"type": "Dual Pallet", "p1": "Gearbox Side Cover", "p2": "Gearbox Plug", "base_p1": 155, "base_p2": 155, "dt": 35, "sc": 3, "fm": 980, "dr": 420},
    "Makino-10": {"type": "Dual Pallet", "p1": "Thermostat Housing", "p2": "Thermostat Cap", "base_p1": 190, "base_p2": 95, "dt": 20, "sc": 2, "fm": 790, "dr": 330},
    "Makino-11": {"type": "Dual Pallet", "p1": "Brake Bracket L", "p2": "Brake Bracket R", "base_p1": 130, "base_p2": 130, "dt": 50, "sc": 6, "fm": 1120, "dr": 470},
    "Makino-12": {"type": "Dual Pallet", "p1": "Filter Head A", "p2": "Filter Adapter B", "base_p1": 170, "base_p2": 85, "dt": 15, "sc": 1, "fm": 600, "dr": 260},
    
    # SINGLE PALLET MACHINES (13, 14)
    "Makino-13": {"type": "Single Pallet", "p1": "Heavy Flywheel Ring", "p2": None, "base_p1": 280, "base_p2": 0, "dt": 10, "sc": 1, "fm": 450, "dr": 190},
    "Makino-14": {"type": "Single Pallet", "p1": "Main Standoff Casting", "p2": None, "base_p1": 240, "base_p2": 0, "dt": 5, "sc": 0, "fm": 320, "dr": 140},
}

# ---------------------------------------------------------
# 3. DYNAMIC SIDEBAR CONTROL
# ---------------------------------------------------------
st.sidebar.header("🕹️ Shift Micro-Logging")
selected_machine = st.sidebar.selectbox("Select Machine", list(makino_fleet.keys()))

cfg = makino_fleet[selected_machine]

st.sidebar.markdown(f"**Architecture:** `{cfg['type']}`")
st.sidebar.markdown("---")

# Dynamic Input Fields
p1_count = st.sidebar.number_input(f"{cfg['p1']} Count", min_value=0, value=cfg["base_p1"], key=f"p1_{selected_machine}")

if cfg["type"] == "Dual Pallet":
    p2_count = st.sidebar.number_input(f"{cfg['p2']} Count", min_value=0, value=cfg["base_p2"], key=f"p2_{selected_machine}")
else:
    p2_count = 0

downtime_mins = st.sidebar.number_input("Unplanned Downtime (Mins)", min_value=0, value=cfg["dt"], key=f"dt_{selected_machine}")
rejections = st.sidebar.number_input("Rejections / Scrap", min_value=0, value=cfg["sc"], key=f"sc_{selected_machine}")

# ---------------------------------------------------------
# 4. LIVE OEE CALCULATOR
# ---------------------------------------------------------
shift_length_mins = 480
operating_time = max(0, shift_length_mins - downtime_mins)
availability = (operating_time / shift_length_mins) * 100 if shift_length_mins > 0 else 0

total_parts = p1_count + p2_count
ideal_cycle_time_mins = 1.2 if cfg["type"] == "Dual Pallet" else 0.9
performance = min(100.0, ((total_parts * ideal_cycle_time_mins) / operating_time) * 100) if operating_time > 0 else 0

quality = ((total_parts - rejections) / total_parts * 100) if total_parts > 0 else 100
oee = (availability / 100) * (performance / 100) * (quality / 100) * 100

# ---------------------------------------------------------
# 5. KPI DISPLAY
# ---------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Overall OEE", f"{oee:.1f}%", delta=f"{oee-75:.1f}% vs Target")
col2.metric("Availability", f"{availability:.1f}%")
col3.metric("Performance", f"{performance:.1f}%")
col4.metric("Quality Rate", f"{quality:.1f}%")

st.markdown("---")

# ---------------------------------------------------------
# 6. SHIFT TIMELINE
# ---------------------------------------------------------
st.subheader(f"⏱️ {selected_machine} ({cfg['type']}) Shift Timeline")

dt_end_hour = 10 + (downtime_mins // 60)
dt_end_min = downtime_mins % 60

timeline_data = [
    dict(Task="Production", Start="2026-07-27 06:00", Finish="2026-07-27 10:00", Status="Running"),
    dict(Task="Downtime / Setup", Start="2026-07-27 10:00", Finish=f"2026-07-27 {dt_end_hour:02d}:{dt_end_min:02d}", Status="Downtime"),
    dict(Task="Production", Start=f"2026-07-27 {dt_end_hour:02d}:{dt_end_min:02d}", Finish="2026-07-27 14:00", Status="Running"),
]
df_timeline = pd.DataFrame(timeline_data)
fig_timeline = px.timeline(
    df_timeline, x_start="Start", x_end="Finish", y="Task", color="Status",
    color_discrete_map={"Running": "#10B981", "Downtime": "#EF4444"}
)
fig_timeline.update_yaxes(autorange="reversed")
fig_timeline.update_layout(height=200, margin=dict(l=10, r=10, t=10, b=10))
st.plotly_chart(fig_timeline, use_container_width=True, config={'displayModeBar': False})

st.markdown("---")

# ---------------------------------------------------------
# 7. OUTPUT BREAKDOWN & TOOL HEALTH
# ---------------------------------------------------------
col_left, col_right = st.columns(2)

with col_left:
    st.subheader(f"📊 {selected_machine} Volume Breakdown")
    
    if cfg["type"] == "Dual Pallet":
        fig_bar = go.Figure(data=[
            go.Bar(name=cfg['p1'], x=['Shift Output'], y=[p1_count], marker_color='#0D5C75'),
            go.Bar(name=cfg['p2'], x=['Shift Output'], y=[p2_count], marker_color='#10B981')
        ])
        fig_bar.update_layout(barmode='stack', height=280, margin=dict(l=10, r=10, t=30, b=10))
    else:
        fig_bar = go.Figure(data=[
            go.Bar(name=cfg['p1'], x=['Shift Output'], y=[p1_count], marker_color='#0D5C75')
        ])
        fig_bar.update_layout(height=280, margin=dict(l=10, r=10, t=30, b=10))
        
    st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False})

with col_right:
    st.subheader(f"🛠️ {selected_machine} Tool Life")
    
    face_mill_used = cfg["fm"] + total_parts
    driller_used = cfg["dr"] + total_parts
    
    st.write("**T01 - Main Spindle Cutter (Max 1200 Cycles)**")
    st.progress(min(1.0, face_mill_used / 1200))
    st.caption(f"Usage: {face_mill_used} / 1200 cycles ({max(0, 1200 - face_mill_used)} remaining)")
    
    st.write("**T02 - Carbide Driller (Max 500 Cycles)**")
    st.progress(min(1.0, driller_used / 500))
    st.caption(f"Usage: {driller_used} / 500 cycles ({max(0, 500 - driller_used)} remaining)")

st.markdown("---")

# ---------------------------------------------------------
# 8. EXCEL REPORT EXPORTER
# ---------------------------------------------------------
st.subheader("💾 Instant Enterprise Excel Exporter")

buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
    summary_df = pd.DataFrame([{
        "Machine": selected_machine,
        "Type": cfg["type"],
        "Material 1": cfg["p1"],
        "Material 1 Count": p1_count,
        "Material 2": cfg["p2"] if cfg["p2"] else "N/A (Single Pallet)",
        "Material 2 Count": p2_count,
        "Total Output": total_parts,
        "Scrap": rejections,
        "Downtime (mins)": downtime_mins,
        "OEE (%)": round(oee, 2),
        "Availability (%)": round(availability, 2),
        "Performance (%)": round(performance, 2),
        "Quality (%)": round(quality, 2)
    }])
    summary_df.to_excel(writer, sheet_name='Makino_Report', index=False)

excel_data = buffer.getvalue()

st.download_button(
    label="📄 Download Production & OEE Report (.xlsx)",
    data=excel_data,
    file_name=f"Pricol_{selected_machine}_Report.xlsx",
    mime="application/vnd.ms-excel"
)
