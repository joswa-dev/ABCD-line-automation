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
    page_title="Pricol Industrial Intelligence",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    h1, h2, h3 { color: #0D5C75; font-family: 'Segoe UI', sans-serif; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h2 style='text-align: center; color: #0D5C75;'>🏭 PRICOL UNIT III - ENTERPRISE LINE INTELLIGENCE</h2>", unsafe_allow_html=True)
st.markdown("---")

# ---------------------------------------------------------
# 2. DYNAMIC MACHINE DATABASE SEEDING
# ---------------------------------------------------------
# Pre-configured baseline stats for different machines to show dynamic switching
machine_configs = {
    "Makino-01 (Dual Pallet)": {
        "base_pb": 200, "base_pc": 100, "base_downtime": 45, "base_scrap": 4,
        "face_mill_base": 820, "driller_base": 310,
        "timeline": [
            dict(Task="Production", Start="2026-07-27 06:00", Finish="2026-07-27 09:30", Status="Running"),
            dict(Task="Tool Change / Maintenance", Start="2026-07-27 09:30", Finish="2026-07-27 10:15", Status="Downtime"),
            dict(Task="Production", Start="2026-07-27 10:15", Finish="2026-07-27 14:00", Status="Running"),
        ]
    },
    "Makino-02 (Dual Pallet)": {
        "base_pb": 160, "base_pc": 160, "base_downtime": 20, "base_scrap": 2,
        "face_mill_base": 1100, "driller_base": 450,
        "timeline": [
            dict(Task="Production", Start="2026-07-27 06:00", Finish="2026-07-27 11:00", Status="Running"),
            dict(Task="Chip Clearance", Start="2026-07-27 11:00", Finish="2026-07-27 11:20", Status="Downtime"),
            dict(Task="Production", Start="2026-07-27 11:20", Finish="2026-07-27 14:00", Status="Running"),
        ]
    },
    "Line-B CNC": {
        "base_pb": 240, "base_pc": 0, "base_downtime": 10, "base_scrap": 1,
        "face_mill_base": 400, "driller_base": 150,
        "timeline": [
            dict(Task="Production", Start="2026-07-27 06:00", Finish="2026-07-27 13:50", Status="Running"),
            dict(Task="Minor Stop", Start="2026-07-27 13:50", Finish="2026-07-27 14:00", Status="Downtime"),
        ]
    }
}

# ---------------------------------------------------------
# 3. OPERATOR INPUT SIDEBAR (Fully Dynamic Controls)
# ---------------------------------------------------------
st.sidebar.header("🕹️ Shift Micro-Logging")
selected_machine = st.sidebar.selectbox("Select Machine", list(machine_configs.keys()))

# Get initial baseline values based on the selected machine
cfg = machine_configs[selected_machine]

pb_count = st.sidebar.number_input("Pump Body (PB 444) Count", min_value=0, value=cfg["base_pb"], key=f"pb_{selected_machine}")
pc_count = st.sidebar.number_input("Pressure Cover (PC) Count", min_value=0, value=cfg["base_pc"], key=f"pc_{selected_machine}")
downtime_mins = st.sidebar.number_input("Unplanned Downtime (Mins)", min_value=0, value=cfg["base_downtime"], key=f"dt_{selected_machine}")
rejections = st.sidebar.number_input("Rejections / Scrap", min_value=0, value=cfg["base_scrap"], key=f"sc_{selected_machine}")

# ---------------------------------------------------------
# 4. LIVE OEE MATHEMATICAL ENGINE
# ---------------------------------------------------------
shift_length_mins = 480 # 8 hour shift
operating_time = max(0, shift_length_mins - downtime_mins)
availability = (operating_time / shift_length_mins) * 100 if shift_length_mins > 0 else 0

total_parts = pb_count + pc_count
ideal_cycle_time_mins = 1.2 # 1.2 mins per cycle average
performance = min(100.0, ((total_parts * ideal_cycle_time_mins) / operating_time) * 100) if operating_time > 0 else 0

quality = ((total_parts - rejections) / total_parts * 100) if total_parts > 0 else 100
oee = (availability / 100) * (performance / 100) * (quality / 100) * 100

# ---------------------------------------------------------
# 5. KPI METRICS ROW
# ---------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Overall OEE", f"{oee:.1f}%", delta=f"{oee-75:.1f}% vs Target")
col2.metric("Availability", f"{availability:.1f}%")
col3.metric("Performance", f"{performance:.1f}%")
col4.metric("Quality Rate", f"{quality:.1f}%")

st.markdown("---")

# ---------------------------------------------------------
# 6. DYNAMIC MACHINE TIMELINE (GANTT CHART)
# ---------------------------------------------------------
st.subheader(f"⏱️ {selected_machine} Shift Timeline & State Analysis")

df_timeline = pd.DataFrame(cfg["timeline"])
fig_timeline = px.timeline(
    df_timeline, x_start="Start", x_end="Finish", y="Task", color="Status",
    color_discrete_map={"Running": "#10B981", "Downtime": "#EF4444"}
)
fig_timeline.update_yaxes(autorange="reversed")
fig_timeline.update_layout(height=200, margin=dict(l=10, r=10, t=10, b=10))
st.plotly_chart(fig_timeline, use_container_width=True, config={'displayModeBar': False})

st.markdown("---")

# ---------------------------------------------------------
# 7. DUAL-PANEL OUTPUT & PREDICTIVE TOOL EXPIRY
# ---------------------------------------------------------
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📊 Dual-Pallet Volume Breakdown")
    fig_bar = go.Figure(data=[
        go.Bar(name='Pump Body (PB 444)', x=['Shift Output'], y=[pb_count], marker_color='#0D5C75'),
        go.Bar(name='Pressure Cover (PC)', x=['Shift Output'], y=[pc_count], marker_color='#10B981')
    ])
    fig_bar.update_layout(barmode='stack', height=280, margin=dict(l=10, r=10, t=30, b=10))
    st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False})

with col_right:
    st.subheader("🛠️ Predictive Tool & Spindle Expiry")
    
    # Tool wear accumulates dynamically with inputted parts
    face_mill_used = cfg["face_mill_base"] + total_parts
    driller_used = cfg["driller_base"] + total_parts
    
    st.write("**T01 - Face Mill Spindle (Max 1200 Cycles)**")
    st.progress(min(1.0, face_mill_used / 1200))
    st.caption(f"Current Usage: {face_mill_used} / 1200 cycles ({max(0, 1200 - face_mill_used)} cycles remaining)")
    
    st.write("**T02 - Carbide Driller (Max 500 Cycles)**")
    st.progress(min(1.0, driller_used / 500))
    st.caption(f"Current Usage: {driller_used} / 500 cycles ({max(0, 500 - driller_used)} cycles remaining)")

st.markdown("---")

# ---------------------------------------------------------
# 8. INSTANT EXCEL EXPORTER
# ---------------------------------------------------------
st.subheader("💾 Instant Enterprise Excel Exporter")

buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
    summary_df = pd.DataFrame([{
        "Machine": selected_machine,
        "PB 444 Count": pb_count,
        "PC Count": pc_count,
        "Total Parts": total_parts,
        "Rejections": rejections,
        "Downtime (mins)": downtime_mins,
        "OEE (%)": round(oee, 2),
        "Availability (%)": round(availability, 2),
        "Performance (%)": round(performance, 2),
        "Quality (%)": round(quality, 2)
    }])
    summary_df.to_excel(writer, sheet_name='OEE_Daily_Report', index=False)

excel_data = buffer.getvalue()

st.download_button(
    label="📄 Download Production & OEE Report (.xlsx)",
    data=excel_data,
    file_name=f"Pricol_OEE_Report_{selected_machine.replace(' ', '_')}.xlsx",
    mime="application/vnd.ms-excel"
)
