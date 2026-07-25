import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import io
from datetime import datetime
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configure page for mobile responsiveness
st.set_page_config(
    page_title="Automation Hub", 
    layout="centered", 
    initial_sidebar_state="collapsed"
)

# Custom premium styling for mobile view
st.markdown("""
    <style>
    .main { background-color: #fcfcfc; }
    h1 { color: #0d5c3a; font-family: 'Segoe UI', sans-serif; font-size: 24px !important; text-align: center; font-weight: bold; }
    h3 { color: #1e293b; font-size: 16px !important; font-weight: 600; margin-top: 15px; }
    .stButton>button { width: 100%; background-color: #0d5c3a; color: white; border-radius: 8px; font-weight: bold; border: none; height: 45px; }
    .stButton>button:hover { background-color: #09442a; color: white; }
    .css-1kyx603 { padding-top: 2rem; }
    </style>
""", unsafe_allow_html=True)

st.write("🏭 **ABCD UNIT III – LINE AUTOMATION**")
st.title("📊 Digital Production Hub")
st.markdown("---")

# ----------------------------------------------------
# 1. DIGITAL ENTRY FORM
# ----------------------------------------------------
st.subheader("📝 Live Shift Entry")
with st.form("production_form", clear_on_submit=False):
    col1, col2 = st.columns(2)
    with col1:
        date_input = st.date_input("Select Date", datetime.now())
        shift = st.selectbox("Current Shift", ["Shift A", "Shift B", "Shift C"])
    with col2:
        castings = st.number_input("Castings Processed", min_value=0, step=1, value=145)
        rejections = st.number_input("Rejections / Scrap", min_value=0, step=1, value=3)
    
    submitted = st.form_submit_button("Submit Entry to System")
    if submitted:
        efficiency = round(((castings - rejections) / castings) * 100, 2) if castings > 0 else 0
        st.success(f"✔️ Shift Data Registered! Efficiency: {efficiency}%")

st.markdown("---")

# ----------------------------------------------------
# 2. WEEKLY GRAPH FOR PPT
# ----------------------------------------------------
st.subheader("📈 Weekly Production Metrics (Ready for PPT)")

# Dynamic data simulation
days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
targets = [150, 150, 150, 150, 150, 150]
# Replace Thursday with the user's active form input dynamically
actuals = [142, 155, 138, castings, 148, 152] 

df_chart = pd.DataFrame({
    "Day": days * 2,
    "Quantity": targets + actuals,
    "Type": ["Target"] * 6 + ["Actual Production"] * 6
})

fig = px.bar(
    df_chart, 
    x="Day", 
    y="Quantity", 
    color="Type",
    barmode="group",
    color_discrete_map={"Target": "#cbd5e1", "Actual Production": "#0d5c3a"}
)

fig.update_layout(
    margin=dict(l=10, r=10, t=40, b=10),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.1,
        xanchor="center",
        x=0.5,
        title_text="" # This completely deletes the misplaced word "Type"
    ),
    height=280
)
st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

st.markdown("---")

# ----------------------------------------------------
# 3. PREDICTIVE MAINTENANCE (FOR SHOCK VALUE)
# ----------------------------------------------------
st.subheader("🔧 Live Tool Wear & Quality Metrics")
tool_df = pd.DataFrame({
    "Tool Name": ["T01 - Face Mill", "T02 - Driller", "T03 - Boring Bar"],
    "Cycle Count": ["840 / 1000", "420 / 500", "125 / 1000"],
    "Health Status": ["⚠️ Change Soon", "✅ Operational", "✅ Operational"]
})
st.dataframe(tool_df, use_container_width=True, hide_index=True)

st.markdown("---")

# ----------------------------------------------------
# 4. INSTANT EXCEL EXPORTER
# ----------------------------------------------------
st.subheader("💾 Instant Report Exporter")
st.write("Click below to export this data into a highly structured Corporate Excel Sheet:")

# Create Excel on the fly inside RAM
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
    # Sheet 1: Production
    pd.DataFrame({
        "Date": [date_input], "Shift": [shift], "Total Castings": [castings], "Rejections": [rejections]
    }).to_excel(writer, sheet_name='Daily Log', index=False)
    
    # Sheet 2: Tools
    tool_df.to_excel(writer, sheet_name='Tooling Parameters', index=False)

excel_data = buffer.getvalue()

st.download_button(
    label="📥 Generate Production Report (.xlsx)",
    data=excel_data,
    file_name=f"Pricol_Report_{date_input}.xlsx",
    mime="application/vnd.ms-excel"
)

# ---------------------------------------------------------
# 1. PAGE CONFIG & STYLING
# ---------------------------------------------------------
st.set_page_config(page_title="Pricol Enterprise Analytics", layout="wide")

st.markdown("<h2 style='text-align: center; color: #0D5C75;'>🏭 ABCD UNIT III - ENTERPRISE LINE INTELLIGENCE</h2>", unsafe_allow_html=True)
st.markdown("---")

# ---------------------------------------------------------
# 2. OPERATOR INPUT SECTION (No IoT Required)
# ---------------------------------------------------------
st.sidebar.header("🕹️ Shift Micro-Logging")
selected_machine = st.sidebar.selectbox("Select Machine", ["Makino-01 (Dual Pallet)", "Makino-02", "Line-B CNC"])
pb_count = st.sidebar.number_input("Pump Body (PB 444) Count", min_value=0, value=200)
pc_count = st.sidebar.number_input("Pressure Cover (PC) Count", min_value=0, value=100)
downtime_mins = st.sidebar.number_input("Unplanned Downtime (Minutes)", min_value=0, value=45)
rejections = st.sidebar.number_input("Rejections / Scrap", min_value=0, value=4)

# ---------------------------------------------------------
# 3. OEE MATHEMATICAL ENGINE
# ---------------------------------------------------------
shift_length_mins = 480 # 8 hour shift
operating_time = shift_length_mins - downtime_mins
availability = (operating_time / shift_length_mins) * 100

total_parts = pb_count + pc_count
ideal_cycle_time_mins = 1.2 # 1.2 mins per cycle average
performance = min(100.0, ((total_parts * ideal_cycle_time_mins) / operating_time) * 100) if operating_time > 0 else 0

quality = ((total_parts - rejections) / total_parts * 100) if total_parts > 0 else 100
oee = (availability / 100) * (performance / 100) * (quality / 100) * 100

# ---------------------------------------------------------
# 4. KPI METRICS ROW
# ---------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Overall OEE", f"{oee:.1f}%", delta=f"{oee-75:.1f}% vs Target")
col2.metric("Availability", f"{availability:.1f}%")
col3.metric("Performance", f"{performance:.1f}%")
col4.metric("Quality Rate", f"{quality:.1f}%")

st.markdown("---")

# ---------------------------------------------------------
# 5. MACHINE TIMELINE (GANTT CHART)
# ---------------------------------------------------------
st.subheader("⏱️ Machine Shift Timeline & State Analysis")

timeline_data = [
    dict(Task="Production", Start="2026-07-24 06:00", Finish="2026-07-24 09:30", Status="Running"),
    dict(Task="Tool Change / Maintenance", Start="2026-07-24 09:30", Finish="2026-07-24 10:15", Status="Downtime"),
    dict(Task="Production", Start="2026-07-24 10:15", Finish="2026-07-24 14:00", Status="Running"),
]
df_timeline = pd.DataFrame(timeline_data)
fig_timeline = px.timeline(df_timeline, x_start="Start", x_end="Finish", y="Task", color="Status", 
                           color_discrete_map={"Running": "#10B981", "Downtime": "#EF4444"})
fig_timeline.update_yaxes(autorange="reversed")
fig_timeline.update_layout(height=200, margin=dict(l=10, r=10, t=10, b=10))
st.plotly_chart(fig_timeline, use_container_width=True, config={'displayModeBar': False})

# ---------------------------------------------------------
# 6. DUAL-PANEL OUTPUT & PREDICTIVE TOOL EXPIRY
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
    
    # Calculate cycle wear
    face_mill_used = 820 + total_parts
    driller_used = 310 + total_parts
    
    st.write("**T01 - Face Mill Spindle (Max 1200 Cycles)**")
    st.progress(min(1.0, face_mill_used / 1200))
    st.caption(f"Current Usage: {face_mill_used} / 1200 cycles ({1200 - face_mill_used} cycles remaining)")
    
    st.write("**T02 - Carbide Driller (Max 500 Cycles)**")
    st.progress(min(1.0, driller_used / 500))
    st.caption(f"Current Usage: {driller_used} / 500 cycles ({500 - driller_used} cycles remaining)")
