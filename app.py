import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# ----------------------
# Page Config & Styling
# ----------------------
st.set_page_config(
    page_title="MOL AI Replenishment Agent",
    page_icon="⛽",
    layout="wide"
)

# Initialize session state
if "feedback_log" not in st.session_state:
    st.session_state.feedback_log = []

# ----------------------
# Mock Dataset
# ----------------------
stations = {
    "Station 001: Prague Highway": {"sku_count":1520, "lead_time":3, "type":"High volume highway"},
    "Station 047: Brno City": {"sku_count":1380, "lead_time":2, "type":"Urban city station"},
    "Station 182: Ústí nad Labem Rural": {"sku_count":1100, "lead_time":4, "type":"Low volume rural"}
}

mock_skus = pd.DataFrame([
    {"sku_id":44021, "name":"Energy Drink", "current_stock":41, "forecast_7d":96, "days_cover":0.9, "shelf_cap_limit":72, "event_risk":True},
    {"sku_id":10055, "name":"Bottled Water 0.5L", "current_stock":284, "forecast_7d":120, "days_cover":4.2, "shelf_cap_limit":200, "event_risk":False},
    {"sku_id":30112, "name":"Potato Chips", "current_stock":62, "forecast_7d":45, "days_cover":2.1, "shelf_cap_limit":80, "event_risk":False},
    {"sku_id":22004, "name":"Iced Coffee", "current_stock":33, "forecast_7d":58, "days_cover":1.0, "shelf_cap_limit":50, "event_risk":True},
])

# ----------------------
# Sidebar Navigation
# ----------------------
with st.sidebar:
    st.title("⛽ MOL AI Agent")
    page = st.radio("Navigation", [
        "Dashboard Overview",
        "Station Detail",
        "Reorder Queue & AI Reasoning",
        "Feedback Learning Log",
        "Ecosystem Map"
    ])
    selected_station = st.selectbox("Select Station", list(stations.keys()))

# ----------------------
# Page 1: Dashboard Overview
# ----------------------
if page == "Dashboard Overview":
    st.header("Network Dashboard | MOL Czech 300 Filling Stations")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Product Availability", "96.2%", delta="↑5.2% vs baseline")
    col2.metric("Holding Cost per Station", "-12%", delta="↓")
    col3.metric("Auto-approved Orders", "71%", delta="")
    col4.metric("Weekly Manual Hours Saved", "114 hrs", delta="↑")

    st.subheader("Weekly Out-of-Stock Events: Before vs AI Agent")
    chart_data = pd.DataFrame({
        "Week": [1,2,3,4,5,6,7,8],
        "Manual Process": [22,24,19,25,21,23,20,26],
        "AI Agent": [18,15,12,14,11,13,10,12]
    })
    st.line_chart(chart_data, x="Week")

    st.markdown("""
    **System Summary**
    This AI agent automates two-echelon replenishment: routine reorders auto-submitted to central warehouse.
    Complex cases (local events, shelf limits, expiring stock) are escalated to category managers with transparent reasoning.
    """)

# ----------------------
# Page 2: Station Detail
# ----------------------
elif page == "Station Detail":
    st.header(f"{selected_station}")
    meta = stations[selected_station]
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total SKUs", meta["sku_count"])
    col2.metric("Warehouse Lead Time", f"{meta['lead_time']} days")
    col3.metric("Service Level This Month", "97.1%")
    col4.metric("Open Reorder Recommendations", "18")

    st.subheader("Station Profile")
    st.write(f"Station type: {meta['type']}")
    if selected_station == "Station 001: Prague Highway":
        st.info("Upcoming local event: Highway marathon next Saturday → expected demand spike.")

    st.subheader("Top SKU Inventory Snapshot")
    st.dataframe(mock_skus[["name","current_stock","days_cover"]], use_container_width=True)

# ----------------------
# Page3: Reorder Queue + AI Reasoning (Core Demo Page)
# ----------------------
elif page == "Reorder Queue & AI Reasoning":
    st.header("Reorder Recommendation Queue")

    # AI decision logic
    def ai_decision(row):
        if row["event_risk"] or row["forecast_7d"] > row["shelf_cap_limit"]:
            return "ESCALATE", "🟠"
        else:
            return "AUTO APPROVE", "🟢"

    mock_skus[["decision","tag"]] = mock_skus.apply(lambda x: pd.Series(ai_decision(x)), axis=1)
    st.dataframe(mock_skus[["name","current_stock","forecast_7d","decision"]], use_container_width=True)

    st.divider()
    st.subheader("🔍 AI Transparency Panel — Select SKU to view reasoning")
    sku_choice = st.selectbox("Choose SKU", mock_skus["name"].tolist())
    selected = mock_skus[mock_skus["name"] == sku_choice].iloc[0]

    st.markdown(f"""
    ### Recommendation: {selected["tag"]} {selected["decision"]}
    **SKU:** {selected["name"]} | Suggested order quantity: {selected["forecast_7d"]} units
    #### AI Reasoning:
    - Current stock level: {selected["current_stock"]} units, days of cover: {selected["days_cover"]}
    - 7-day demand forecast: {selected["forecast_7d"]} units
    - Shelf capacity maximum: {selected["shelf_cap_limit"]} units
    - Event / demand risk active: {selected["event_risk"]}
    """)

    if selected["decision"] == "ESCALATE":
        st.warning("Escalation reason: Complex constraint detected (event demand spike OR shelf capacity limit). Human review required.")
    else:
        st.success("No unusual constraints. This order will be automatically sent to central warehouse.")

    st.divider()
    st.subheader("👨‍💼 Manager Decision Workflow")
    action = st.radio("What action would you take?", ["Approve recommendation", "Modify quantity", "Override & reject order"])
    override_qty = st.number_input("Adjust order quantity", min_value=0, value=int(selected["forecast_7d"]))
    override_reason = st.selectbox("Reason for decision", [
        "Local event turnout lower than forecast",
        "Shelf space constraints",
        "Delivery lead time uncertainty",
        "Other (add note)"
    ])
    note = st.text_input("Optional free-text note")

    if st.button("Save Decision & Feed to AI Learning Loop"):
        new_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "sku": selected["name"],
            "ai_suggested": selected["forecast_7d"],
            "manager_decision": action,
            "final_qty": override_qty,
            "reason": override_reason,
            "note": note
        }
        st.session_state.feedback_log.append(new_entry)
        st.success("✅ Decision saved! This feedback will tune future AI recommendations.")

# ----------------------
# Page4: Feedback Learning Log (compounding feedback loop)
# ----------------------
elif page == "Feedback Learning Log":
    st.header("📚 Human Override Feedback Log — AI Learning Dataset")
    st.markdown("Every human decision/override feeds back to improve future forecasts and escalation rules. This is MOL's proprietary compounding data asset.")
    if len(st.session_state.feedback_log) ==0:
        st.info("No decisions logged yet. Go to Reorder Queue to create a manager decision.")
    else:
        log_df = pd.DataFrame(st.session_state.feedback_log)
        st.dataframe(log_df, use_container_width=True)

# ----------------------
# Page5: Ecosystem Map
# ----------------------
elif page == "Ecosystem Map":
    st.header("🌐 MOL AI Agent Ecosystem Map | MOL = Orchestrator")
    col_left, col_mid, col_right = st.columns([1,1,1])
    with col_left:
        st.subheader("Inputs / Dependencies")
        st.markdown("""
        - POS sales data
        - WMS / Central warehouse inventory
        - Station stock counts
        - Product master data (shelf life, packs)
        - Weather & local event data
        """)
    with col_mid:
        st.subheader("MOL AI Agent (Orchestrator)")
        st.markdown("""
        ML Demand Forecaster + Agentic Workflow
        ✅ Auto-routine orders
        ⚠️ Escalate complex decisions
        📝 Capture human feedback
        """)
    with col_right:
        st.subheader("Complementors / Beneficiaries")
        st.markdown("""
        - POS vendor
        - Logistics partners
        - WMS/ERP provider
        - IoT shelf sensor providers
        """)
    st.divider()
    st.subheader("Defensibility")
    st.markdown("""
    - Proprietary station-level demand patterns across MOL’s 300 Czech stations
    - Unique two-echelon paired station + warehouse inventory dataset
    - Compounding human override feedback loop
    - Deep integration with MOL internal workflows & trust from domain experts
    """)
