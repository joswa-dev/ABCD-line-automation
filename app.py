import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import io
import pptx
from pptx import Presentation
from datetime import datetime

# ---------------------------------------------------------
# 1. PAGE CONFIG & STYLING
# ---------------------------------------------------------
st.set_page_config(
    page_title="14-Makino Industrial & Presentation Hub",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    h1, h2, h3 { color: #0D5C75; font-family: 'Segoe UI', sans-serif; }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# TOP NAVIGATION SWITCHER
# ---------------------------------------------------------
nav_choice = st.radio(
    "Select Portal", 
    ["🏭 Live 14-Makino Production Hub", "📚 Executive Presentation Gallery (20 Decks)"], 
    horizontal=True
)

st.markdown("---")

# =========================================================
# MODE 1: LIVE 14-MAKINO PRODUCTION DASHBOARD
# =========================================================
if nav_choice == "🏭 Live 14-Makino Production Hub":
    st.markdown("<h2 style='text-align: center; color: #0D5C75;'>🏭 UNIT III - 14-MAKINO PRODUCTION HUB</h2>", unsafe_allow_html=True)
    st.markdown("---")

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

    st.sidebar.header("🕹️ Shift Micro-Logging")
    selected_machine = st.sidebar.selectbox("Select Machine", list(makino_fleet.keys()))
    cfg = makino_fleet[selected_machine]

    st.sidebar.markdown(f"**Architecture:** `{cfg['type']}`")
    st.sidebar.markdown("---")

    p1_count = st.sidebar.number_input(f"{cfg['p1']} Count", min_value=0, value=cfg["base_p1"], key=f"p1_{selected_machine}")
    if cfg["type"] == "Dual Pallet":
        p2_count = st.sidebar.number_input(f"{cfg['p2']} Count", min_value=0, value=cfg["base_p2"], key=f"p2_{selected_machine}")
    else:
        p2_count = 0

    downtime_mins = st.sidebar.number_input("Unplanned Downtime (Mins)", min_value=0, value=cfg["dt"], key=f"dt_{selected_machine}")
    rejections = st.sidebar.number_input("Rejections / Scrap", min_value=0, value=cfg["sc"], key=f"sc_{selected_machine}")

    shift_length_mins = 480
    operating_time = max(0, shift_length_mins - downtime_mins)
    availability = (operating_time / shift_length_mins) * 100 if shift_length_mins > 0 else 0

    total_parts = p1_count + p2_count
    ideal_cycle_time_mins = 1.2 if cfg["type"] == "Dual Pallet" else 0.9
    performance = min(100.0, ((total_parts * ideal_cycle_time_mins) / operating_time) * 100) if operating_time > 0 else 0
    quality = ((total_parts - rejections) / total_parts * 100) if total_parts > 0 else 100
    oee = (availability / 100) * (performance / 100) * (quality / 100) * 100

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Overall OEE", f"{oee:.1f}%", delta=f"{oee-75:.1f}% vs Target")
    col2.metric("Availability", f"{availability:.1f}%")
    col3.metric("Performance", f"{performance:.1f}%")
    col4.metric("Quality Rate", f"{quality:.1f}%")

    st.markdown("---")
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
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader(f"📊 {selected_machine} Volume Breakdown")
        if cfg["type"] == "Dual Pallet":
            fig_bar = go.Figure(data=[
                go.Bar(name=cfg['p1'], x=['Shift Output'], y=[p1_count], text=[f"{cfg['p1']}: {p1_count}"], textposition='auto', marker_color='#0D5C75'),
                go.Bar(name=cfg['p2'], x=['Shift Output'], y=[p2_count], text=[f"{cfg['p2']}: {p2_count}"], textposition='auto', marker_color='#10B981')
            ])
            fig_bar.update_layout(barmode='stack', height=280, margin=dict(l=10, r=10, t=30, b=10))
        else:
            fig_bar = go.Figure(data=[
                go.Bar(name=cfg['p1'], x=['Shift Output'], y=[p1_count], text=[f"{cfg['p1']}: {p1_count}"], textposition='auto', marker_color='#10B981')
            ])
            fig_bar.update_layout(height=280, margin=dict(l=10, r=10, t=30, b=10))
            
        fig_bar.update_layout(
            font=dict(color="#FFFFFF"),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(tickfont=dict(color='#FFFFFF')),
            yaxis=dict(tickfont=dict(color='#FFFFFF'))
        )
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
        file_name=f"Production_{selected_machine}_Report.xlsx",
        mime="application/vnd.ms-excel"
    )

# =========================================================
# MODE 2: EXECUTIVE PPT GALLERY (GENUINE PPTX GENERATOR)
# =========================================================
else:
    st.markdown("<h2 style='text-align: center; color: #0D5C75;'>📚 EXECUTIVE PRESENTATION & STRATEGY GALLERY</h2>", unsafe_allow_html=True)
    st.write("Browse through executive strategy decks, line automation studies, and OEE optimization reports:")
    st.markdown("---")

    ppt_catalog = {
        "PPT 01: 14-Makino Line Efficiency & OEE Master Plan": "Comprehensive breakdown of 14 Makino CNC machines, comparing Single vs Dual Pallet performance.",
        "PPT 02: Eliminating Paper Logs via Web Micro-Logging": "Transitioning shift-end logging from manual paper entries to instant cloud data entry.",
        "PPT 03: Dual-Pallet APC Cycle Math & Throughput Analysis": "How rotary table indexing doubles output without spindle downtime.",
        "PPT 04: Predictive Tool Life & Spindle Wear Modeling": "Tracking cutter impact cycles mathematically to schedule tool changes before failure.",
        "PPT 05: Non-IoT Digital Twin Architecture": "Achieving $100k industrial visibility without expensive PLC sensors or hardware modifications.",
        "PPT 06: Unplanned Downtime Root Cause Analysis": "Category breakdown of chip clearance delays, maintenance stops, and power cuts.",
        "PPT 07: Quality & Rejection Rate Optimization": "Scrap reduction techniques across Pump Body and Pressure Cover castings.",
        "PPT 08: Shop Floor Ergonomics & Shift Transition": "Reducing 10-minute shift end paperwork burden for shop operators.",
        "PPT 09: Automated Shift Report Generation": "Creating structured Excel audit logs directly from micro-log database entries.",
        "PPT 10: Executive Summary - Line Automation ROI": "Cost-benefit analysis of web dashboard vs traditional manual entry.",
        "PPT 11: Single-Pallet vs Dual-Pallet Machine Layout": "Operational comparison of Makino 01, 02, 13, 14 vs Makino 03-12.",
        "PPT 12: Production Target vs Actual Volume Variance": "Weekly metrics and gap analysis for line supervisors.",
        "PPT 13: Spindle Speed & Feed Rate Optimization": "Cutting parameter adjustments for high-speed aluminum casting milling.",
        "PPT 14: Preventive Maintenance Scheduling Framework": "Transitioning from reactive tool replacement to proactive cycle-based maintenance.",
        "PPT 15: Shift A, B, C Comparative Line Analytics": "Cross-shift efficiency and performance distribution models.",
        "PPT 16: Zero-Cost Factory Digitalization Strategy": "How web technologies bypass strict corporate IT laptop lockdown rules.",
        "PPT 17: Machine Line Heatmap & Bottleneck Identification": "Pinpointing slow cycles across all 14 CNC stations.",
        "PPT 18: Scrap Reclamation & Material Handling": "Tracking raw casting defects vs machining scrap.",
        "PPT 19: Operator User Experience & Mobile Web Integration": "Optimizing dashboard UI for Android shop-floor tablets.",
        "PPT 20: Future Roadmap - Non-Invasive Optical Sensors": "Next-level external door sensor integration for fully automated cycle counts."
    }

    selected_deck = st.selectbox("Select Presentation Deck", list(ppt_catalog.keys()))
    st.info(f"**Deck Summary:** {ppt_catalog[selected_deck]}")

    col_view, col_info = st.columns([2, 1])

    with col_view:
        st.subheader("🖼️ Interactive Deck Preview")
        st.markdown(f"""
        <div style="background-color: #1e293b; padding: 40px; border-radius: 10px; border: 1px solid #334155; text-align: center; color: white;">
            <h3>📊 {selected_deck}</h3>
            <p style="color: #94a3b8;">Slide Overview & Executive Takeaways</p>
            <div style="margin: 20px 0; padding: 20px; background-color: #0f172a; border-radius: 8px; font-family: monospace; text-align: left;">
                <b>Key Agenda & Highlights:</b><br/>
                1. Executive Summary & Shop Floor Bottlenecks<br/>
                2. Live Line Data Visualizations & OEE Metrics<br/>
                3. Operational Impact & Zero-Hardware ROI
            </div>
            <p>💡 <i>Click download on the right to grab the valid .pptx file!</i></p>
        </div>
        """, unsafe_allow_html=True)

    with col_info:
        st.subheader("💾 Actions")
        st.write("Download the complete presentation deck file below:")
        
        # ---------------------------------------------------------
        # GENERATE REAL PPTX BINARY FILE
        # ---------------------------------------------------------
        prs = Presentation()
        
        # Slide 1: Title
        title_slide_layout = prs.slide_layouts[0]
        slide1 = prs.slides.add_slide(title_slide_layout)
        title1 = slide1.shapes.title
        subtitle1 = slide1.placeholders[1]
        deck_title = selected_deck.split(':')[1].strip() if ':' in selected_deck else selected_deck
        title1.text = deck_title
        subtitle1.text = "Unit III - Executive Line Automation Strategy"
        
        # Slide 2: Bullet Highlights
        bullet_slide_layout = prs.slide_layouts[1]
        slide2 = prs.slides.add_slide(bullet_slide_layout)
        shapes2 = slide2.shapes
        title2 = shapes2.title
        body2 = shapes2.placeholders[1]
        title2.text = "Executive Key Takeaways"
        tf2 = body2.text_frame
        tf2.text = f"Overview: {ppt_catalog[selected_deck]}"
        p2 = tf2.add_paragraph()
        p2.text = "• Line Bottleneck Analysis & Current Challenges."
        p3 = tf2.add_paragraph()
        p3.text = "• Transitioning from paper log notes to real-time micro-logging."
        p4 = tf2.add_paragraph()
        p4.text = "• Predictive tool wear tracking to eliminate unplanned breakdowns."
        
        # Save to buffer
        ppt_buffer = io.BytesIO()
        prs.save(ppt_buffer)
        ppt_buffer.seek(0)

        clean_filename = selected_deck.split(':')[0].replace(' ', '_') + ".pptx"

        st.download_button(
            label=f"📥 Download {selected_deck.split(':')[0]} (.pptx)",
            data=ppt_buffer.getvalue(),
            file_name=clean_filename,
            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
        )
        
        st.markdown("---")
        st.markdown("### 📌 Quick Specs:")
        st.write("• **Format:** Genuine PowerPoint (.pptx)")
        st.write("• **Audience:** Management & Line Supervisors")
