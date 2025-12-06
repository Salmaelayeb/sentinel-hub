import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time

# Configuration
API_URL = "http://django:8000/api"

st.set_page_config(page_title="Security Dashboard", layout="wide")
st.title("🛡️ Real-Time Security Dashboard")

# Auto-refresh every 30 seconds
st.markdown("""
    <meta http-equiv="refresh" content="30">
""", unsafe_allow_html=True)

def fetch_data(endpoint):
    try:
        response = requests.get(f"{API_URL}/{endpoint}", timeout=5)
        return response.json() if response.status_code == 200 else None
    except:
        return None

# --- MAIN DASHBOARD ---
col1, col2, col3, col4 = st.columns(4)

vuln_stats = fetch_data("vulnerabilities/statistics")

with col1:
    st.metric(
        "🔴 Critical Vulns",
        vuln_stats['by_severity']['critical'] if vuln_stats else 0,
        delta="ACTION REQUIRED"
    )

with col2:
    st.metric(
        "🟠 High Vulns",
        vuln_stats['by_severity']['high'] if vuln_stats else 0
    )

with col3:
    st.metric(
        "📊 Total Vulns",
        vuln_stats['total'] if vuln_stats else 0
    )

with col4:
    st.metric(
        "✅ Resolved",
        vuln_stats['by_status']['resolved'] if vuln_stats else 0
    )

st.divider()

# --- REAL-TIME ALERTS ---
st.subheader("🚨 Real-Time Alerts (Last 24h)")
alerts = fetch_data("alerts/recent")

if alerts:
    alerts_list = alerts.get('results', alerts) if isinstance(alerts, dict) else alerts
    if alerts_list:
        # Show unacknowledged alerts first (red highlight)
        unack = [a for a in alerts_list if not a.get('acknowledged')]
        ack = [a for a in alerts_list if a.get('acknowledged')]
        
        # Display critical alerts prominently
        for alert in unack[:5]:
            with st.container():
                col1, col2, col3 = st.columns([1, 3, 1])
                
                severity_color = {
                    'critical': '🔴',
                    'high': '🟠',
                    'medium': '🟡',
                    'low': '🔵'
                }
                
                with col1:
                    st.write(severity_color.get(alert['severity'], '❓'))
                
                with col2:
                    st.write(f"**{alert['alert_type']}**: {alert['message']}")
                
                with col3:
                    if st.button("Acknowledge", key=f"ack_{alert['id']}"):
                        # Call API to acknowledge
                        requests.post(f"{API_URL}/alerts/{alert['id']}/acknowledge/")
                        st.rerun()

st.divider()

# --- VULNERABILITY TIMELINE ---
st.subheader("📈 Vulnerabilities Over Time")
vulns = fetch_data("vulnerabilities")

if vulns:
    vulns_list = vulns.get('results', vulns) if isinstance(vulns, dict) else vulns
    
    if vulns_list:
        df = pd.DataFrame(vulns_list)
        df['discovered_at'] = pd.to_datetime(df['discovered_at'])
        
        # Group by day
        daily_counts = df.groupby(df['discovered_at'].dt.date).size()
        
        fig = px.line(
            x=daily_counts.index,
            y=daily_counts.values,
            labels={'x': 'Date', 'y': 'Vulnerabilities Found'},
            title='Vulnerabilities Discovered Per Day'
        )
        st.plotly_chart(fig, use_container_width=True)

# --- SCAN SCHEDULE MANAGEMENT ---
st.subheader("⏰ Automated Scan Schedules")

schedules = fetch_data("scan-schedules/active_schedules")

if schedules:
    sched_list = schedules.get('results', schedules) if isinstance(schedules, dict) else schedules
    
    for schedule in sched_list:
        with st.expander(f"📅 {schedule['tool_name']} - {schedule['target']} ({schedule['frequency']})"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write(f"**Last Run:** {schedule.get('last_run', 'Never')}")
            
            with col2:
                st.write(f"**Next Run:** {schedule.get('next_run', 'Unknown')}")
            
            with col3:
                if st.button(f"Run Now", key=f"run_{schedule['id']}"):
                    # Trigger scan immediately
                    requests.post(f"{API_URL}/scan-schedules/{schedule['id']}/run_now/")
                    st.success("Scan triggered!")

# --- ADD NEW SCHEDULE ---
st.subheader("➕ Create New Scan Schedule")

with st.form("new_schedule"):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        tool_name = st.selectbox("Tool", ["nmap", "trivy", "zap", "openvas"])
    
    with col2:
        target = st.text_input("Target", placeholder="192.168.1.0/24")
    
    with col3:
        frequency = st.selectbox("Frequency", ["daily", "weekly", "hourly", "monthly"])
    
    scan_type = st.selectbox("Scan Type", ["standard", "quick", "aggressive"])
    
    if st.form_submit_button("Create Schedule"):
        # Get tool ID
        tools = fetch_data("tools")
        tool_id = next((t['id'] for t in tools.get('results', []) if t['name'] == tool_name), None)
        
        if tool_id:
            payload = {
                "tool": tool_id,
                "target": target,
                "scan_type": scan_type,
                "frequency": frequency,
                "is_active": True
            }
            response = requests.post(f"{API_URL}/scan-schedules/", json=payload)
            if response.status_code == 201:
                st.success("Schedule created!")
                st.rerun()
            else:
                st.error(f"Error: {response.text}")