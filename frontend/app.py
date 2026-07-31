"""Farmer dashboard: upload a leaf photo, get a weather-aware treatment plan."""

import json
import os
import requests
import streamlit as st

BACKEND = os.getenv("BACKEND_URL", "http://localhost:8000")

# Color mapping for status cards & indicators
COLORS = {
    "RED": "#ef4444",
    "YELLOW": "#f59e0b",
    "GREEN": "#10b981",
    "GRAY": "#64748b"
}

STATES = [
    "Andhra Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa", "Gujarat", "Haryana",
    "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh",
    "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab",
    "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh",
    "Uttarakhand", "West Bengal", "Delhi", "Jammu and Kashmir",
]

st.set_page_config(
    page_title="AgriAI | Crop Treatment Advisor",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Injected Modern Custom CSS
st.markdown("""
<style>
    /* Dark Agronomy Background Theme */
    .stApp {
        background-color: #0b1320;
        color: #f1f5f9;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }

    /* Main Container Padding */
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2.5rem;
        max-width: 1350px;
    }

    /* Header Styling */
    .brand-header {
        background: linear-gradient(135deg, #065f46 0%, #047857 50%, #059669 100%);
        padding: 24px 30px;
        border-radius: 16px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(5, 150, 105, 0.25);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .brand-title {
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .brand-subtitle {
        font-size: 0.95rem;
        opacity: 0.9;
        margin-top: 6px;
        font-weight: 400;
    }

    /* Panel Card Design */
    .panel-box {
        background: #131f33;
        border: 1px solid #1e2d4a;
        border-radius: 14px;
        padding: 22px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }

    /* Custom Metric Cards */
    .metric-card {
        background: #18263e;
        border-radius: 12px;
        padding: 16px 20px;
        border-left: 5px solid #64748b;
        margin-bottom: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }
    .metric-title {
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #94a3b8;
    }
    .metric-value {
        font-size: 1.5rem;
        font-weight: 800;
        color: #ffffff;
        margin: 4px 0;
    }
    .metric-note {
        font-size: 0.82rem;
        color: #cbd5e1;
    }

    /* Headline Status Banner */
    .status-banner {
        padding: 18px 24px;
        border-radius: 12px;
        color: #ffffff;
        font-size: 1.15rem;
        font-weight: 700;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 12px;
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
    }

    /* Primary Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 24px !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        box-shadow: 0 4px 14px rgba(16, 185, 129, 0.3) !important;
        transition: all 0.2s ease !important;
        width: 100%;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4) !important;
    }

    /* Subheaders */
    .sub-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #38bdf8;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
</style>
""", unsafe_allow_html=True)


def render_metric_card(title, value, note, color):
    st.markdown(
        f"""
        <div class="metric-card" style="border-left-color: {color};">
            <div class="metric-title">{title}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# Top Navigation / Branding Header
st.markdown("""
<div class="brand-header">
    <div class="brand-title">🌿 AgriAI Crop Advisor</div>
    <div class="brand-subtitle">Smart Vision Diagnosis & Weather-Aware Treatment Planner</div>
</div>
""", unsafe_allow_html=True)

# Sidebar Setup
with st.sidebar:
    st.header("⚙️ Configuration")
    st.caption(f"Backend Endpoint:\n`{BACKEND}`")
    st.markdown("---")
    st.markdown("### How it works")
    st.markdown("""
    1. **Upload** affected leaf image.
    2. **Vision Model** detects disease & severity.
    3. **AI Agent** checks local weather & extension standards.
    4. **Safety Verification** tells you if it is safe to spray right now.
    """)

# Main Workspace: Split into Input and Output Panels
col_input, col_output = st.columns([1, 1.25], gap="large")

with col_input:
    st.markdown('<div class="panel-box">', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">📍 1. Farm Location</div>', unsafe_allow_html=True)
    loc1, loc2 = st.columns(2)
    city = loc1.text_input("City / Town", value="Nashik")
    state = loc2.selectbox("State", STATES, index=STATES.index("Maharashtra"))
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="panel-box">', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">📸 2. Affected Leaf Photo</div>', unsafe_allow_html=True)
    source = st.radio("Upload Method", ["Upload File", "Take Photo"], horizontal=True, label_visibility="collapsed")
    
    image = (
        st.file_uploader("Upload leaf sample", type=["png", "jpg", "jpeg"])
        if source == "Upload File"
        else st.camera_input("Capture leaf photo")
    )

    if image:
        st.image(image, use_container_width=True, caption="Selected Leaf Sample")

    analyze_btn = st.button("🚀 Analyze Leaf & Generate Plan", disabled=not (image and city))
    st.markdown('</div>', unsafe_allow_html=True)

with col_output:
    if not analyze_btn:
        st.markdown("""
        <div style="background: #131f33; border: 2px dashed #1e2d4a; border-radius: 14px; padding: 40px; text-align: center; color: #64748b;">
            <div style="font-size: 2.5rem; margin-bottom: 10px;">🩺</div>
            <div style="font-weight: 600; font-size: 1.1rem; color: #94a3b8;">Awaiting Leaf Sample</div>
            <div style="font-size: 0.88rem; margin-top: 6px;">Select your farm location, upload a clear photo of the damaged leaf, and click analyze.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        diagnosis, recommendation, trace, failed = None, None, [], None
        diag_slot = st.empty()

        with st.status("🔍 Analyzing sample and fetching local weather...", expanded=True) as status:
            try:
                resp = requests.post(
                    f"{BACKEND}/analyze/stream",
                    files={"file": (image.name, image.getvalue(), image.type)},
                    data={"city": city, "state": state},
                    stream=True,
                    timeout=300,
                )
                resp.raise_for_status()

                for line in resp.iter_lines():
                    if not line:
                        continue
                    event = json.loads(line)
                    kind = event.get("type")

                    if kind == "status":
                        status.update(label=event["message"])
                        st.write(f"⚙️ {event['message']}")

                    elif kind == "diagnosis":
                        diagnosis = event["data"]
                        msg = (f"Identified **{diagnosis.get('disease_identified')}** on "
                               f"**{diagnosis.get('crop_type')}** "
                               f"({diagnosis.get('severity_percent')}% affected area)")
                        st.write(msg)
                        with diag_slot.container():
                            st.info(f"Diagnosis Ready: {diagnosis.get('disease_identified')}")

                    elif kind == "result":
                        recommendation, trace = event["answer"], event.get("trace", [])

                    elif kind == "error":
                        failed = event["message"]

                status.update(label="Analysis Completed!", state="complete", expanded=False)
            except Exception as exc:
                failed = str(exc)
                status.update(label="Analysis Failed", state="error")

        if failed:
            st.error(f"Analysis Failed: {failed}")
            st.stop()

        if not recommendation or "error" in recommendation:
            st.error((recommendation or {}).get("error", "Failed to produce a treatment plan."))
            st.stop()

        rec, diag = recommendation, diagnosis or {}
        diag_slot.empty()

        def get_color(key, default="YELLOW"):
            return COLORS.get(str(rec.get(key, default)).upper(), COLORS["GRAY"])

        headline_color = get_color('ui_status_color')
        headline_text = rec.get('diagnostic_summary', rec.get('disease', 'Diagnosis Result'))
        
        # Summary Header Banner
        st.markdown(
            f"""<div class="status-banner" style="background-color: {headline_color};">
                📢 {headline_text}
            </div>""",
            unsafe_allow_html=True,
        )

        # Overview Metrics Grid
        m1, m2, m3 = st.columns(3)
        with m1:
            render_metric_card(
                "Disease Identified",
                rec.get("disease", "Unknown"),
                f"{diag.get('crop_type', '')} ({diag.get('confidence_score', 0)}% confidence)",
                get_color("severity_level")
            )
        with m2:
            render_metric_card(
                "Leaf Severity",
                f"{rec.get('severity_percent', 0)}%",
                diag.get("visual_evidence", "Visible leaf damage"),
                get_color("severity_level")
            )
        with m3:
            spray_status = "YES" if rec.get("spray_now") else "NO"
            render_metric_card(
                "Safe to Spray Now?",
                spray_status,
                rec.get("spray_reason", ""),
                get_color("spray_status")
            )

        # Treatment & Application Details Box
        st.markdown('<div class="panel-box">', unsafe_allow_html=True)
        st.markdown('<div class="sub-title">💊 Actionable Treatment Plan</div>', unsafe_allow_html=True)
        
        if rec.get("organic_fallback_used"):
            st.warning("⚠️ No exact chemical dosage was verified in university records. A safe generic organic fallback is provided instead.")

        t_col1, t_col2 = st.columns(2)
        with t_col1:
            st.markdown(f"**🧪 Chemical:** {rec.get('chemical', '-')}")
            st.markdown(f"**⚖️ Dosage:** {rec.get('dosage', '-')}")
            st.markdown(f"**🚿 Application Method:** {rec.get('application_method', '-')}")
            
        with t_col2:
            st.markdown(f"**⏰ Best Spray Window:** {rec.get('best_spray_window', '-')}")
            st.markdown(f"**🌤️ Weather Conditions:** {rec.get('weather_summary', '-')}")
            st.markdown(f"**🛡️ Safety Notes:** {rec.get('safety_notes', '-')}")

        if rec.get("sources"):
            st.markdown("---")
            st.caption("Trusted Extension Sources: " + " • ".join([f"[{src}]({src})" for src in rec["sources"]]))

        st.markdown('</div>', unsafe_allow_html=True)

        with st.expander("🛠️ View Agent Execution Trace & Raw Logs"):
            st.json({"diagnosis": diag, "tool_calls": trace})