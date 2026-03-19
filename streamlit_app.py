"""
FloatChat AI — Streamlit Application
ARGO Oceanographic Data Visualization and Analysis Platform
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="FloatChat AI",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": None,
        "Report a bug": None,
        "About": "FloatChat AI — ARGO Oceanographic Data Platform",
    },
)

# ── Imports ───────────────────────────────────────────────────────────────────
try:
    from components.api_client import APIClient, APIException
    from components.data_transformer import DataTransformer
    from utils.dashboard_utils import init_session_state, validate_data_quality
    from dashboard_config import dashboard_config
    from components.layout_manager import DashboardLayout
    from components.chat_interface import ChatInterface
    from components.map_visualization import InteractiveMap
    from components.profile_visualizer import ProfileVisualizer
    from components.data_manager import DataManager
    from components.statistics_manager import StatisticsManager
    _imports_ok = True
except ImportError as e:
    logger.warning(f"Partial import failure: {e}")
    APIClient = DataTransformer = init_session_state = validate_data_quality = dashboard_config = None
    DashboardLayout = ChatInterface = InteractiveMap = ProfileVisualizer = None
    DataManager = StatisticsManager = None
    _imports_ok = False


# ── Session state init ────────────────────────────────────────────────────────
def _init_session():
    if init_session_state:
        init_session_state()
    else:
        defaults = {
            "initialized": True,
            "api_client": None,
            "chat_history": [],
            "selected_floats": [],
            "filter_state": {},
            "current_filters": {},
        }
        for k, v in defaults.items():
            if k not in st.session_state:
                st.session_state[k] = v


@st.cache_resource(show_spinner=False)
def _get_api_client():
    """Singleton APIClient — constructed once per process."""
    try:
        base_url = dashboard_config.API_BASE_URL if dashboard_config else "http://localhost:8000"
        return APIClient(base_url=base_url) if APIClient else None
    except Exception as e:
        logger.error(f"API client init failed: {e}")
        return None


def _init_api_client():
    if st.session_state.api_client is not None:
        return
    st.session_state.api_client = _get_api_client()


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    _init_session()
    if APIClient:
        _init_api_client()

    if DashboardLayout:
        layout = DashboardLayout()
        layout.apply_custom_styling()
        layout.render_header()
        sidebar_state = layout.render_sidebar()
        layout.render_main_content(
            active_tab=sidebar_state["selected_tab"],
            filters=sidebar_state["filters"],
        )
        layout.render_footer()
    else:
        _fallback_layout()


# ── Fallback layout ───────────────────────────────────────────────────────────
def _fallback_layout():
    """Minimal layout used when component imports are unavailable."""
    from styles.government_theme import GovernmentTheme
    GovernmentTheme.apply_theme()

    st.markdown(
        """
        <div class="app-header">
            <div class="app-header-title">FloatChat AI</div>
            <div class="app-header-subtitle">ARGO Oceanographic Data Platform</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.markdown(
            '<div style="font-size:.7rem;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:#64748b;margin-bottom:.5rem;">Navigation</div>',
            unsafe_allow_html=True,
        )
        section = st.selectbox(
            "Section",
            ["Overview", "Interactive Map", "Profile Analysis", "Chat Interface", "Data Export"],
            label_visibility="collapsed",
        )
        st.markdown("<hr style='border-color:rgba(255,255,255,.08);margin:1rem 0'>", unsafe_allow_html=True)

        # System status
        st.markdown(
            '<div style="font-size:.7rem;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:#64748b;margin-bottom:.75rem;">System</div>',
            unsafe_allow_html=True,
        )
        client = st.session_state.get("api_client")
        if client:
            try:
                health = client.health_check()
                if health.get("status") == "healthy":
                    st.success("Backend connected")
                else:
                    st.error("Backend disconnected")
            except Exception as e:
                st.warning(f"Connection error: {str(e)[:40]}")
        else:
            st.warning("API client not available")
            if APIClient:
                try:
                    st.session_state.api_client = APIClient(base_url="http://localhost:8000")
                    st.success("API client initialised")
                except Exception as e:
                    st.error(f"Init failed: {str(e)[:40]}")

    if section == "Overview":
        _fallback_overview()
    elif section == "Interactive Map":
        _fallback_map()
    elif section == "Profile Analysis":
        _fallback_profiles()
    elif section == "Chat Interface":
        _fallback_chat()
    elif section == "Data Export":
        _fallback_export()

    st.markdown(
        f'<div class="app-footer">FloatChat AI &nbsp;·&nbsp; {datetime.now().year}</div>',
        unsafe_allow_html=True,
    )


# ── Fallback tab renderers ────────────────────────────────────────────────────

def _fallback_overview():
    st.markdown('<div class="section-header">System Overview</div>', unsafe_allow_html=True)

    client = st.session_state.get("api_client")
    floats = profiles = measurements = quality = "—"
    if client:
        try:
            stats = client.get_system_statistics()
            floats       = str(stats.get("active_floats", "—"))
            profiles     = f"{stats.get('total_profiles', 0):,}"
            measurements = f"{stats.get('total_measurements', 0):,}"
            quality      = f"{stats.get('data_quality', 0):.1f}%"
        except Exception:
            pass

    from styles.government_theme import GovernmentTheme
    kpi = GovernmentTheme.kpi_card
    st.markdown(
        f"""
        <div class="kpi-grid">
            {kpi("Active Floats",   floats,       color="blue",   sub="ARGO platforms")}
            {kpi("Total Profiles",  profiles,     color="cyan",   sub="Dive cycles")}
            {kpi("Measurements",    measurements, color="purple", sub="Depth observations")}
            {kpi("Data Quality",    quality,      color="green",  sub="Good data %")}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    sample = pd.DataFrame({
        "Date":         pd.date_range("2024-01-01", periods=30, freq="D"),
        "Measurements": [100 + i * 5 + (i % 7) * 10 for i in range(30)],
    })
    _dk = dict(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color="#94a3b8", title_font_color="#e2e8f0",
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(255,255,255,0.07)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(255,255,255,0.07)"),
    )
    fig = px.area(sample, x="Date", y="Measurements",
                  title="Daily measurement count",
                  color_discrete_sequence=["#3b82f6"])
    fig.update_traces(fillcolor="rgba(59,130,246,0.10)", line_width=2)
    fig.update_layout(height=280, margin=dict(t=36, b=0, l=0, r=0), **_dk)
    st.plotly_chart(fig, use_container_width=True)


def _fallback_map():
    st.markdown('<div class="section-header">Interactive Float Map</div>', unsafe_allow_html=True)
    st.info("Connect to the API and ingest data to view live float positions.")

    sample = pd.DataFrame({
        "lat":      [10, -5, 15, 0, -15, 8, -25, 20],
        "lon":      [65, 75, 80, 70,  60, 90, 72, 85],
        "float_id": [f"ARGO_{i:04d}" for i in range(1, 9)],
        "depth":    [1800, 1500, 2000, 1200, 1750, 900, 1600, 1400],
    })
    fig = px.scatter_mapbox(
        sample, lat="lat", lon="lon", hover_name="float_id",
        color="depth", color_continuous_scale="Blues_r",
        zoom=3, height=480, title="Sample float positions",
    )
    fig.update_layout(
        mapbox_style="carto-darkmatter",
        margin=dict(t=36, b=0, l=0, r=0),
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#94a3b8", title_font_color="#e2e8f0",
    )
    st.plotly_chart(fig, use_container_width=True)


def _fallback_profiles():
    st.markdown('<div class="section-header">Profile Analysis</div>', unsafe_allow_html=True)
    st.info("Connect to the API to view live temperature/salinity profiles.")

    np.random.seed(7)
    depth = np.linspace(0, 2000, 100)
    temp  = 28 - (depth / 2000) * 26 + np.random.normal(0, 0.3, 100)
    sal   = 34.5 + (depth / 2000) * 1.2 + np.random.normal(0, 0.04, 100)
    oxy   = np.where(depth < 100, 6.5, np.where(depth < 800, 3.5 - depth/1600, 4.5))
    df    = pd.DataFrame({"depth": depth, "temperature": temp, "salinity": sal, "oxygen": oxy})

    _dk = dict(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color="#94a3b8", title_font_color="#e2e8f0",
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(255,255,255,0.07)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(255,255,255,0.07)", autorange="reversed"),
    )
    c1, c2, c3 = st.columns(3)
    with c1:
        fig = px.line(df, x="temperature", y="depth", title="Temperature (°C)",
                      color_discrete_sequence=["#3b82f6"])
        fig.update_layout(height=400, margin=dict(t=36, b=0, l=0, r=0), **_dk)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.line(df, x="salinity", y="depth", title="Salinity (PSU)",
                      color_discrete_sequence=["#06b6d4"])
        fig.update_layout(height=400, margin=dict(t=36, b=0, l=0, r=0), **_dk)
        st.plotly_chart(fig, use_container_width=True)
    with c3:
        fig = px.line(df, x="oxygen", y="depth", title="Oxygen (ml/L)",
                      color_discrete_sequence=["#10b981"])
        fig.update_layout(height=400, margin=dict(t=36, b=0, l=0, r=0), **_dk)
        st.plotly_chart(fig, use_container_width=True)


def _fallback_chat():
    st.markdown('<div class="section-header">Natural Language Query</div>', unsafe_allow_html=True)

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Chat history display
    if not st.session_state.chat_history:
        st.markdown(
            '<div class="chat-empty">Ask anything about ARGO float data.</div>',
            unsafe_allow_html=True,
        )
    else:
        for msg in st.session_state.chat_history[-20:]:
            ts = msg["timestamp"].strftime("%H:%M")
            if msg["type"] == "user":
                st.markdown(
                    f'<div class="chat-meta chat-meta-right">You &nbsp;&middot;&nbsp; {ts}</div>'
                    f'<div class="chat-message-user">{msg["content"]}</div>',
                    unsafe_allow_html=True,
                )
            else:
                extra = "chat-message-error" if msg.get("error") else ""
                st.markdown(
                    f'<div class="chat-meta">ARGO Assistant &nbsp;&middot;&nbsp; {ts}</div>'
                    f'<div class="chat-message-ai {extra}">{msg["content"]}</div>',
                    unsafe_allow_html=True,
                )

    st.markdown("---")

    col_in, col_btn = st.columns([5, 1])
    with col_in:
        query = st.text_input(
            "Query",
            placeholder="e.g.  Show salinity profiles near the equator",
            key="fallback_chat_input",
            label_visibility="collapsed",
        )
    with col_btn:
        send = st.button("Send", type="primary", use_container_width=True)

    if send and query.strip():
        client = st.session_state.get("api_client")
        st.session_state.chat_history.append({
            "type": "user", "content": query.strip(), "timestamp": datetime.now()
        })
        if client:
            with st.spinner("Processing..."):
                try:
                    response = client.query_rag_pipeline(query.strip())
                    answer = response.answer if hasattr(response, "answer") else str(response)
                    st.session_state.chat_history.append({
                        "type": "ai", "content": answer, "timestamp": datetime.now()
                    })
                except Exception as e:
                    st.session_state.chat_history.append({
                        "type": "ai", "content": f"Error: {e}",
                        "timestamp": datetime.now(), "error": True
                    })
        else:
            st.session_state.chat_history.append({
                "type": "ai",
                "content": "The backend API is not available. Start the backend server and refresh.",
                "timestamp": datetime.now(), "error": True,
            })
        st.rerun()

    if st.session_state.chat_history:
        if st.button("Clear history"):
            st.session_state.chat_history = []
            st.rerun()


def _fallback_export():
    st.markdown('<div class="section-header">Data Export</div>', unsafe_allow_html=True)
    st.markdown("Export ARGO measurement data in standard scientific formats.")

    c1, c2 = st.columns(2)
    with c1:
        fmt = st.selectbox("Format", ["CSV", "ASCII", "NetCDF"])
        float_ids_raw = st.text_input("Float IDs (comma-separated, empty = all)")
    with c2:
        max_rows = st.number_input("Max rows", 100, 100_000, 10_000, step=500)

    if st.button("Export", type="primary"):
        client = st.session_state.get("api_client")
        if not client:
            st.error("API not available. Start the backend server.")
            return
        float_ids = [f.strip() for f in float_ids_raw.split(",") if f.strip()]
        with st.spinner("Preparing export..."):
            try:
                result = client.export_data(
                    format=fmt.lower(), float_ids=float_ids or None, max_rows=max_rows
                )
                if result:
                    ext = {"csv": "csv", "ascii": "txt", "netcdf": "nc"}[fmt.lower()]
                    mime = {"csv": "text/csv", "ascii": "text/plain", "netcdf": "application/octet-stream"}[fmt.lower()]
                    st.download_button(
                        f"Download {fmt}",
                        data=result,
                        file_name=f"argo_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}",
                        mime=mime,
                    )
                else:
                    st.warning("No data returned. Check your filters.")
            except Exception as e:
                st.error(f"Export error: {e}")


if __name__ == "__main__":
    main()
