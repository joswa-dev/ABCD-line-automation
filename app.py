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
    page_title="Pricol 14-Makino Intelligence",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    h1, h2, h3 { color: #0D5C75; font-family: 'Segoe UI', sans-serif; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h2 style='text-align: center; color: #0D5C75;'>🏭 PRICOL UNIT III - 14-MAKINO LINE INTELLIGENCE</h2>", unsafe_allow_html=True)
st.markdown("---")

# ---------------------------------------------------------
# 2. 14-MAKINO LINE CONFIGURATION (10 Dual + 4 Single)
# ---------------------------------------------------------
makino_fleet = {}

# Seed 10 Dual-Pallet Makino Machines
for i in range(1, 11):
    m_name = f"Makino-{i:02d} (Dual Pallet)"
    if i == 1:
        # Makino-01 specific setup (Pump Body & Pressure Cover)
        p1_name, p2_name = "Pump Body (PB 444)", "Pressure Cover (PC)"
    else:
        p1_name, p2_name = f"Component A (M{i:02d})", f"Component B (M{i:02d})"
        
    makino_fleet[m_name] = {
        "type": "Dual Pallet",
        "part1_label": p1_name,
        "part2_label": p2_name,
        "base_p1": 180 + (i * 5),
        "base_p2": 90 + (i * 3),
        "base_downtime": 15 + (i * 2),
        "base_scrap": i % 4,
        "face_mill_base": 750 + (i * 30),
        "driller_base": 300 + (i * 15)
    }

# Seed 4 Single-Pallet Makino Machines (Makino 11 to 14)
for i in range(11, 15):
    m_name = f"Makino-{i:02d} (Single Pallet)"
    makino_fleet[m_name] = {
        "type": "Single Pallet",
        "part1_label": f"Primary Component (M{i:02d})",
        "part2_label": None,
        "base_p1": 250 + (i * 4),
        "base_p2": 0,
        "base_downtime": 10 + i,
        "base_scrap": 2,
        "face_mill_base": 600 + (i * 25),
        "driller_base": 250 + (i * 10)
    }

# ---------------------------------------------------------
# 3. DYNAMIC OPERATOR SIDEBAR
# ---------------------------------------------------------
st.sidebar.header("🕹️ Shift Micro-Logging")
selected_machine = st.sidebar.selectbox("Select Machine", list(makino_fleet.keys()))

cfg = makino_fleet[selected_machine]

st.sidebar.markdown(f"**Machine Architecture:** `{cfg['type']}`")

# Dynamic part inputs depending on pallet type
p1_count = st.sidebar.number_input(f"{cfg['part1_label']} Count", min_value=0, value=cfg["base_p1"], key=f"p1_{selected_machine}")

if cfg["type"] == "Dual Pallet":
    p2_count = st.sidebar.number_input(f"{cfg['part2_label']} Count", min_value=0, value=cfg["base_p2"], key=f"p2_{selected_machine}")
else:
    p2_count = 0

downtime_mins = st.sidebar.number_input("Unplanned Downtime (Mins)", min_value=0, value=cfg["base_downtime"], key=f"dt_{selected_machine}")
rejections = st.sidebar.number_input("Rejections / Scrap", min_value=0, value=cfg["base_scrap"], key=f"sc_{selected_machine}")

# ---------------------------------------------------------
# 4. LIVE OEE MATHEMATICAL ENGINE
# ---------------------------------------------------------
shift_length_mins = 480 # 8 hour shift
operating_time = max(0, shift_length_mins - downtime_mins)
availability = (operating_time / shift_length_mins) * 100 if shift_length_mins > 0 else 0

total_parts = p1_count + p2_count
ideal_cycle_time_mins = 1.2 if cfg["type"] == "Dual Pallet" else 0.9
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
# 6. SHIFT TIMELINE
# ---------------------------------------------------------
st.subheader(f"⏱️ {selected_machine} Shift Timeline & State Analysis")

timeline_data = [
    dict(Task="Production", Start="2026-07-27 06:00", Finish="2026-07-27 10:00", Status="Running"),
    dict(Task="Downtime / Setup", Start="2026-07-27 10:00", Finish=f"2026-07-27 {10 + (downtime_mins//60):02d}:{downtime_mins%60:02d}", Status="Downtime"),
    dict(Task="Production", Start=f"2026-07-27 {10 + (downtime_mins//60):02d}:{downtime_mins%60:02d}", Finish="2026-07-27 14:00", Status="Running"),
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
# 7. PRODUCTION VOLUME BREAKDOWN & TOOL HEALTH
# ---------------------------------------------------------
col_left, col_right = st.columns(2)

with col_left:
    st.subheader(f"📊 Output Breakdown ({cfg['type']})")
    
    if cfg["type"] == "Dual Pallet":
        fig_bar = go.Figure(data=[
            go.Bar(name=cfg['part1_label'], x=['Shift Output'], y=[p1_count], marker_color='#0D5C75'),
            go.Bar(name=cfg['part2_label'], x=['Shift Output'], y=[p2_count], marker_color='#10B981')
        ])
        fig_bar.update_layout(barmode='stack', height=280, margin=dict(l=10, r=10, t=30, b=10))
    else:
        fig_bar = go.Figure(data=[
            go.Bar(name=cfg['part1_label'], x=['Shift Output'], y=[p1_count], marker_color='#0D5C75')
        ])
        fig_bar.update_layout(height=280, margin=dict(l=10, r=10, t=30, b=10))
        
    st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False})

with col_right:
    st.subheader("🛠️ Predictive Tool Wear")
    
    face_mill_used = cfg["face_mill_base"] + total_parts
    driller_used = cfg["driller_base"] + total_parts
    
    st.write("**T01 - Main Spindle Cutter (Max 1200 Cycles)**")
    st.progress(min(1.0, face_mill_used / 1200))
    st.caption(f"Current Usage: {face_mill_used} / 1200 cycles ({max(0, 1200 - face_mill_used)} cycles remaining)")
    
    st.write("**T02 - Carbide Driller (Max 500 Cycles)**")
    st.progress(min(1.0, driller_used / 500))
    st.caption(f"Current Usage: {driller_used} / 500 cycles ({max(0, 500 - driller_used)} cycles remaining)")

st.markdown("---")

# ---------------------------------------------------------
# 8. EXCEL EXPORTER
# ---------------------------------------------------------
st.subheader("💾 Instant Enterprise Excel Exporter")

buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
    summary_df = pd.DataFrame([{
        "Machine": selected_machine,
        "Type": cfg["type"],
        "Part 1": cfg["part1_label"],
        "Part 1 Count": p1_count,
        "Part 2": cfg["part2_label"] if cfg["part2_label"] else "N/A",
        "Part 2 Count": p2_count if cfg["type"] == "Dual Pallet" else 0,
        "Total Parts": total_parts,
        "Rejections": rejections,
        "Downtime (mins)": downtime_mins,
        "OEE (%)": round(oee, 2),
        "Availability (%)": round(availability, 2),
        "Performance (%)": round(performance, 2),
        "Quality (%)": round(quality, 2)
    }])
    summary_df.to_excel(writer, sheet_name='Makino_Line_Report', index=False)

excel_data = buffer.getvalue()

st.download_button(
    label="📄 Download 14-Makino Production Report (.xlsx)",
    data=excel_data,
    file_name=f"Pricol_Makino_Report_{selected_machine.replace(' ', '_')}.xlsx",
    mime="application/vnd.ms-excel"
)
