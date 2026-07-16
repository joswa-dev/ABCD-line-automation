import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import io
from datetime import datetime

# Configure page for mobile responsiveness
st.set_page_config(
    page_title="Pricol Automation Hub", 
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

st.write("🏭 **PRICOL UNIT III – LINE AUTOMATION**")
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
    margin=dict(l=20, r=20, t=10, b=10),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    height=280
)
st.plotly_chart(fig, use_container_width=True)

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
