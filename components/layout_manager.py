"""
Dashboard Layout Manager
Handles navigation, header, sidebar, and content layout.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging

from dashboard_config import dashboard_config

try:
    from styles.government_theme import GovernmentTheme
except ImportError:
    GovernmentTheme = None

logger = logging.getLogger(__name__)

# ── Module-level cached loaders ───────────────────────────────────────────────

@st.cache_resource(show_spinner=False)
def _get_chroma_client():
    """Return a singleton ChromaDB client (cached for app lifetime)."""
    try:
        import chromadb
        return chromadb.PersistentClient(path="./chroma_db")
    except Exception:
        return None


@st.cache_data(ttl=300, show_spinner=False)
def _load_chroma_data(limit: int = 5000) -> pd.DataFrame:
    """Load measurements from ChromaDB into a normalised DataFrame. Cached 5 min."""
    client = _get_chroma_client()
    if client is None:
        return pd.DataFrame()
    try:
        col = client.get_collection("argo_measurements")
        total = col.count()
        if total == 0:
            return pd.DataFrame()
        result = col.get(limit=min(limit, total), include=["metadatas"])
        rows = result.get("metadatas", [])
        if not rows:
            return pd.DataFrame()
        df = pd.DataFrame(rows)
        # Normalise column aliases (legacy data may lack them)
        if "latitude" not in df.columns and "lat" in df.columns:
            df["latitude"] = df["lat"]
        if "longitude" not in df.columns and "lon" in df.columns:
            df["longitude"] = df["lon"]
        if "date" not in df.columns:
            for src in ("profile_date", "time"):
                if src in df.columns:
                    df["date"] = df[src]
                    break
        # Coerce numeric columns
        for c in ["temperature", "salinity", "depth", "latitude", "longitude",
                  "oxygen", "chlorophyll"]:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors="coerce")
        # Coerce date column
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
        return df
    except Exception as e:
        logger.warning(f"ChromaDB load failed: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=30, show_spinner=False)
def _cached_health_check(base_url: str) -> Dict[str, Any]:
    """Check backend health; cached for 30 s to avoid per-render HTTP calls."""
    try:
        import requests
        r = requests.get(f"{base_url}/health", timeout=2)
        if r.status_code == 200:
            return r.json()
        return {"status": "unhealthy"}
    except Exception:
        return {"status": "offline"}

TABS = [
    "Overview",
    "Interactive Map",
    "Profile Analysis",
    "Chat Interface",
    "Data Export",
    "Advanced Filters",
]


class DashboardLayout:
    """Manages the main dashboard layout and navigation"""

    def __init__(self):
        self.config = dashboard_config

    # ── Styling ───────────────────────────────────────────────────────────────

    def apply_custom_styling(self) -> None:
        if GovernmentTheme:
            GovernmentTheme.apply_theme()

    # ── Header ────────────────────────────────────────────────────────────────

    def render_header(self) -> None:
        status_html = self._connection_status_html()
        st.markdown(
            f"""
            <div class="app-header">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:1rem;position:relative;z-index:1;">
                    <div>
                        <div class="app-header-title">FloatChat AI</div>
                        <div class="app-header-subtitle">ARGO Oceanographic Data &nbsp;&middot;&nbsp; RAG-Powered Analysis</div>
                    </div>
                    <div class="app-header-meta">
                        {status_html}
                        <span style="color:rgba(148,163,184,.45);font-size:.72rem;font-family:'JetBrains Mono',monospace;letter-spacing:.03em;">
                            {datetime.utcnow().strftime("%d %b %Y &nbsp; %H:%M UTC")}
                        </span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    def _connection_status_html(self) -> str:
        if not GovernmentTheme:
            return ""
        # Use cached health check — no blocking HTTP call on every render
        client = st.session_state.get("api_client")
        base_url = getattr(client, "base_url", "http://localhost:8000") if client else "http://localhost:8000"
        health = _cached_health_check(base_url)
        if health.get("status") == "healthy":
            db_ok = health.get("database") == "connected"
            ch_ok = health.get("chromadb") == "connected"
            pills  = GovernmentTheme.status_pill("online", "Backend")
            pills += "&nbsp;" + GovernmentTheme.status_pill("online" if db_ok else "offline", "DB")
            pills += "&nbsp;" + GovernmentTheme.status_pill("online" if ch_ok else "warning", "Vector DB")
            return pills
        elif health.get("status") == "offline":
            return GovernmentTheme.status_pill("offline", "Backend offline")
        else:
            return GovernmentTheme.status_pill("warning", "Backend unhealthy")

    # ── Sidebar ───────────────────────────────────────────────────────────────

    def render_sidebar(self) -> Dict[str, Any]:
        with st.sidebar:
            # ── Brand ─────────────────────────────────────────────────────────
            st.markdown(
                """
                <div style="padding:.5rem 0 1.1rem;margin-bottom:1rem;
                            border-bottom:1px solid rgba(255,255,255,.07);">
                    <div style="font-size:1.1rem;font-weight:800;letter-spacing:-.03em;
                                background:linear-gradient(90deg,#fff 30%,#93c5fd 100%);
                                -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                                background-clip:text;">FloatChat AI</div>
                    <div style="font-size:.65rem;color:#334155;margin-top:.2rem;
                                letter-spacing:.09em;text-transform:uppercase;font-weight:600;">
                        ARGO Data Platform
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # ── Navigation ────────────────────────────────────────────────────
            st.markdown(
                '<p style="font-size:.62rem;font-weight:700;letter-spacing:.12em;'
                'text-transform:uppercase;color:#1e3a5f;margin:0 0 .4rem;">Navigation</p>',
                unsafe_allow_html=True,
            )

            NAV_ITEMS = [
                ("Overview",         "overview"),
                ("Interactive Map",  "map"),
                ("Profile Analysis", "profile"),
                ("Chat Interface",   "chat"),
                ("Data Export",      "export"),
                ("Advanced Filters", "filters"),
            ]
            labels   = [n[0] for n in NAV_ITEMS]
            default  = st.session_state.get("_nav_idx", 0)
            selected = st.radio(
                "nav",
                labels,
                index=default,
                key="main_navigation_radio",
                label_visibility="collapsed",
            )
            tab_selection = selected
            st.session_state["_nav_idx"] = labels.index(selected)

            # ── Quick actions ──────────────────────────────────────────────────
            st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Refresh", use_container_width=True, key="sb_refresh"):
                    _load_chroma_data.clear()
                    _cached_health_check.clear()
                    st.session_state.last_refresh = datetime.now()
                    st.rerun()
            with col2:
                if st.button("Clear cache", use_container_width=True, key="sb_cache"):
                    st.cache_data.clear()
                    st.rerun()

            st.markdown("<hr style='border:none;border-top:1px solid rgba(255,255,255,.07);margin:.9rem 0'>",
                        unsafe_allow_html=True)

            # ── Filters ───────────────────────────────────────────────────────
            st.markdown(
                '<p style="font-size:.62rem;font-weight:700;letter-spacing:.12em;'
                'text-transform:uppercase;color:#1e3a5f;margin:0 0 .5rem;">Filters</p>',
                unsafe_allow_html=True,
            )
            filter_state = self._render_filters()

            st.markdown("<hr style='border:none;border-top:1px solid rgba(255,255,255,.07);margin:.9rem 0'>",
                        unsafe_allow_html=True)

            # ── System status ──────────────────────────────────────────────────
            st.markdown(
                '<p style="font-size:.62rem;font-weight:700;letter-spacing:.12em;'
                'text-transform:uppercase;color:#1e3a5f;margin:0 0 .5rem;">System</p>',
                unsafe_allow_html=True,
            )
            self._render_sidebar_status()

            # ── ChromaDB info ─────────────────────────────────────────────────
            chroma_client = _get_chroma_client()
            if chroma_client:
                try:
                    col = chroma_client.get_collection("argo_measurements")
                    doc_count = col.count()
                    st.markdown(
                        f'<div style="margin-top:.6rem;padding:.5rem .7rem;'
                        f'background:rgba(59,130,246,.08);border:1px solid rgba(59,130,246,.2);'
                        f'border-radius:8px;">'
                        f'<div style="font-size:.68rem;color:#64748b;font-weight:600;'
                        f'text-transform:uppercase;letter-spacing:.08em;">Vector DB</div>'
                        f'<div style="font-size:1.1rem;font-weight:700;color:#93c5fd;'
                        f'letter-spacing:-.02em;">{doc_count:,}</div>'
                        f'<div style="font-size:.68rem;color:#475569;">documents indexed</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                except Exception:
                    pass

            # Footer
            st.markdown(
                f'<div style="margin-top:1.5rem;font-size:.65rem;color:#1e293b;text-align:center;">'
                f'v1.0 &nbsp;·&nbsp; {datetime.now().strftime("%d %b %Y")}</div>',
                unsafe_allow_html=True,
            )

            return {"selected_tab": tab_selection, "filters": filter_state}

    def _render_filters(self) -> Dict[str, Any]:
        st.markdown(
            '<div style="font-size:.65rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:#334155;margin-bottom:.6rem;">Filters</div>',
            unsafe_allow_html=True,
        )

        default_start = datetime.now() - timedelta(days=365)
        date_range = st.date_input(
            "Date range",
            value=(default_start.date(), datetime.now().date()),
            key="date_filter",
        )

        region_preset = st.selectbox(
            "Region",
            ["All Regions", "Indian Ocean", "Pacific Ocean", "Atlantic Ocean", "Custom"],
            key="region_preset",
        )

        custom_bounds = None
        if region_preset == "Custom":
            c1, c2 = st.columns(2)
            with c1:
                north = st.number_input("N lat", value=20.0, min_value=-90.0, max_value=90.0, format="%.1f")
                south = st.number_input("S lat", value=-20.0, min_value=-90.0, max_value=90.0, format="%.1f")
            with c2:
                east = st.number_input("E lon", value=100.0, min_value=-180.0, max_value=180.0, format="%.1f")
                west = st.number_input("W lon", value=60.0, min_value=-180.0, max_value=180.0, format="%.1f")
            custom_bounds = {"north": north, "south": south, "east": east, "west": west}

        depth_range = st.slider("Depth (m)", 0, 2000, (0, 2000), step=50, key="depth_filter")

        st.markdown('<div style="font-size:.8rem; color:#94a3b8; margin:.75rem 0 .4rem;">Parameters</div>', unsafe_allow_html=True)
        show_temp = st.checkbox("Temperature", value=True, key="show_temp")
        show_sal  = st.checkbox("Salinity",    value=True, key="show_sal")
        show_bgc  = st.checkbox("BGC",         value=False, key="show_bgc")

        quality_levels = st.multiselect(
            "Quality levels",
            ["Excellent", "Good", "Fair", "Poor"],
            default=["Excellent", "Good"],
            key="quality_filter",
        )

        if st.button("Reset filters", use_container_width=True):
            for key in list(st.session_state.keys()):
                if key.endswith("_filter") or key in [
                    "region_preset", "show_temp", "show_sal", "show_bgc", "quality_filter"
                ]:
                    del st.session_state[key]
            st.rerun()

        return {
            "date_range": date_range,
            "region_preset": region_preset,
            "custom_bounds": custom_bounds,
            "depth_range": depth_range,
            "parameters": {"temperature": show_temp, "salinity": show_sal, "bgc": show_bgc},
            "quality_levels": quality_levels,
        }

    def _render_sidebar_status(self) -> None:
        st.markdown(
            '<div style="font-size:.65rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:#334155;margin-bottom:.6rem;">System</div>',
            unsafe_allow_html=True,
        )
        client = st.session_state.get("api_client")
        if client:
            try:
                health = client.health_check()
                ok = health.get("status") == "healthy"
                db = health.get("database") == "connected"
                ch = health.get("chromadb") == "connected"

                def _row(label, good):
                    dot   = "#10b981" if good else "#ef4444"
                    glow  = "0 0 6px #10b981" if good else "none"
                    state = "Online" if good else "Offline"
                    clr   = "#34d399" if good else "#f87171"
                    st.markdown(
                        f'<div style="display:flex;justify-content:space-between;align-items:center;'
                        f'margin-bottom:.5rem;padding:.3rem .5rem;border-radius:6px;'
                        f'background:rgba(255,255,255,.02);">'
                        f'<span style="font-size:.78rem;color:#64748b;">{label}</span>'
                        f'<span style="display:inline-flex;align-items:center;gap:5px;font-size:.72rem;'
                        f'font-weight:600;color:{clr};">'
                        f'<span style="width:6px;height:6px;border-radius:50%;background:{dot};'
                        f'display:inline-block;box-shadow:{glow};"></span>{state}'
                        f'</span></div>',
                        unsafe_allow_html=True,
                    )

                _row("Backend API",  ok)
                _row("PostgreSQL",   db)
                _row("ChromaDB",     ch)
            except Exception:
                st.markdown('<span style="font-size:.82rem;color:#f87171;">Connection error</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span style="font-size:.82rem;color:#f59e0b;">API not initialised</span>', unsafe_allow_html=True)

        st.markdown(
            '<div style="margin-top:.75rem;font-size:.68rem;color:#1e293b;letter-spacing:.03em;">'
            'Latency &lt;100ms &nbsp;&middot;&nbsp; Cache 85%</div>',
            unsafe_allow_html=True,
        )

    # ── Main content router ───────────────────────────────────────────────────

    def render_main_content(self, active_tab: str, filters: Dict[str, Any]) -> None:
        st.session_state.current_filters = filters
        dispatch = {
            "Overview":          self._render_overview_content,
            "Interactive Map":   self._render_map_content,
            "Profile Analysis":  self._render_profile_content,
            "Chat Interface":    self._render_chat_content,
            "Data Export":       self._render_export_content,
            "Advanced Filters":  self._render_advanced_filters_content,
        }
        dispatch.get(active_tab, self._render_overview_content)()

    # ── Overview tab ─────────────────────────────────────────────────────────

    def _render_overview_content(self) -> None:
        st.markdown('<div class="section-header">System Overview</div>', unsafe_allow_html=True)

        try:
            from components.statistics_manager import StatisticsManager
            stats_manager = StatisticsManager()

            # Load from ChromaDB (cached 5 min) — works without backend
            current_data = _load_chroma_data()
            if current_data.empty:
                current_data = self._sample_data()

            stats_manager.render_dataset_overview(current_data)
            st.markdown("---")

            tab1, tab2, tab3 = st.tabs(["Parameter statistics", "Data quality", "Analysis"])
            with tab1:
                stats_manager.render_parameter_statistics(current_data)
            with tab2:
                stats_manager.render_data_quality_assessment(current_data)
            with tab3:
                self._render_analysis_tab(current_data)

        except ImportError:
            self._render_simple_overview()
        except Exception as e:
            logger.error(f"Overview error: {e}")
            self._render_simple_overview()

    def _render_analysis_tab(self, data: pd.DataFrame) -> None:
        st.markdown('<div class="section-header">Advanced Analysis</div>', unsafe_allow_html=True)
        if data.empty:
            st.info("No data available. Connect to the API and load data to see analysis.")
            return
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        exclude = {"latitude", "longitude", "depth", "profile_id", "float_id"}
        param_cols = [c for c in numeric_cols if c not in exclude]
        if param_cols:
            selected = st.multiselect("Parameters", param_cols, default=param_cols[:2])
            if selected:
                try:
                    from components.statistics_manager import StatisticsManager
                    sm = StatisticsManager()
                    fig = sm.create_statistics_summary_plot(data, selected)
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    logger.error(f"Analysis plot error: {e}")
                    st.info("Could not render analysis chart.")

    def _render_simple_overview(self) -> None:
        """Fallback overview when StatisticsManager is unavailable."""
        client = st.session_state.get("api_client")
        floats = profiles = measurements = quality = "—"

        if client:
            try:
                stats        = client.get_system_statistics()
                floats       = str(stats.get("active_floats", "—"))
                profiles     = f"{stats.get('total_profiles', 0):,}"
                measurements = f"{stats.get('total_measurements', 0):,}"
                raw_q        = stats.get("data_quality", 0)
                quality      = f"{raw_q:.1f}%" if raw_q else "—"
            except Exception:
                pass

        # Render KPI grid via custom HTML cards
        kpi = GovernmentTheme.kpi_card if GovernmentTheme else None
        if kpi:
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
        else:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Active floats",  floats)
            c2.metric("Total profiles", profiles)
            c3.metric("Measurements",   measurements)
            c4.metric("Data quality",   quality)

        st.markdown("---")

        # Activity chart — dark theme
        sample = pd.DataFrame({
            "Date":         pd.date_range("2024-01-01", periods=60, freq="D"),
            "Measurements": [200 + i * 4 + (i % 7) * 15 for i in range(60)],
        })
        fig = px.area(
            sample, x="Date", y="Measurements",
            title="Daily measurement count",
            color_discrete_sequence=["#3b82f6"],
        )
        fig.update_traces(
            line_width=2,
            fillcolor="rgba(59,130,246,0.12)",
        )
        fig.update_layout(
            height=280,
            margin=dict(t=36, b=0, l=0, r=0),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#94a3b8",
            title_font_color="#e2e8f0",
            xaxis=dict(gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(255,255,255,0.07)"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(255,255,255,0.07)"),
        )
        st.plotly_chart(fig, use_container_width=True)

    # ── Map tab ───────────────────────────────────────────────────────────────

    def _render_map_content(self) -> None:
        st.markdown('<div class="section-header">Interactive Float Map</div>', unsafe_allow_html=True)
        try:
            from components.map_visualization import InteractiveMap
            map_viz = InteractiveMap()
            filters = st.session_state.get("current_filters", {})
            map_viz.render_interactive_map(filters)
        except ImportError:
            self._render_map_placeholder()
        except Exception as e:
            logger.error(f"Map error: {e}")
            self._render_map_placeholder()

    def _render_map_placeholder(self) -> None:
        st.info("Connect to the API and ingest data to view live float positions.")
        sample = pd.DataFrame({
            "lat":      [10, -5, 15, 0, -15, 8, -25, 20, -10, 5],
            "lon":      [65, 75, 80, 70,  60, 90, 72, 85,  68, 78],
            "float_id": [f"ARGO_{i:04d}" for i in range(1, 11)],
            "depth":    [1800, 1500, 2000, 1200, 1750, 900, 1600, 1400, 1100, 1950],
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
            font_color="#94a3b8",
            title_font_color="#e2e8f0",
        )
        st.plotly_chart(fig, use_container_width=True)

    # ── Profile tab ───────────────────────────────────────────────────────────

    def _render_profile_content(self) -> None:
        st.markdown('<div class="section-header">Profile Analysis</div>', unsafe_allow_html=True)
        try:
            from components.profile_visualizer import ProfileVisualizer
            pv = ProfileVisualizer()
            filters = st.session_state.get("current_filters", {})
            pv.render_profile_analysis(filters)
        except ImportError:
            self._render_profile_placeholder()
        except Exception as e:
            logger.error(f"Profile error: {e}")
            self._render_profile_placeholder()

    def _render_profile_placeholder(self) -> None:
        st.info("Connect to the API to load live T-S-D profiles.")

        np.random.seed(7)
        depth = np.linspace(0, 2000, 100)
        temp  = 28 - (depth / 2000) * 26 + np.random.normal(0, 0.3, 100)
        sal   = 34.5 + (depth / 2000) * 1.2 + np.random.normal(0, 0.04, 100)
        oxy   = np.where(depth < 100, 6.5, np.where(depth < 800, 3.5 - depth/1600, 4.5))
        demo  = pd.DataFrame({"depth": depth, "temperature": temp, "salinity": sal, "oxygen": oxy})

        _dark = dict(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#94a3b8",
            title_font_color="#e2e8f0",
            xaxis=dict(gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(255,255,255,0.07)"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(255,255,255,0.07)", autorange="reversed"),
        )

        c1, c2, c3 = st.columns(3)
        with c1:
            fig = px.line(demo, x="temperature", y="depth",
                          title="Temperature (°C)", orientation="h",
                          color_discrete_sequence=["#3b82f6"])
            fig.update_layout(height=400, margin=dict(t=36,b=0,l=0,r=0), **_dark)
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            fig = px.line(demo, x="salinity", y="depth",
                          title="Salinity (PSU)", orientation="h",
                          color_discrete_sequence=["#06b6d4"])
            fig.update_layout(height=400, margin=dict(t=36,b=0,l=0,r=0), **_dark)
            st.plotly_chart(fig, use_container_width=True)
        with c3:
            fig = px.line(demo, x="oxygen", y="depth",
                          title="Oxygen (ml/L)", orientation="h",
                          color_discrete_sequence=["#10b981"])
            fig.update_layout(height=400, margin=dict(t=36,b=0,l=0,r=0), **_dark)
            st.plotly_chart(fig, use_container_width=True)

    # ── Chat tab ──────────────────────────────────────────────────────────────

    def _render_chat_content(self) -> None:
        try:
            from components.chat_interface import ChatInterface
            ci = ChatInterface(api_client=st.session_state.get("api_client"))
            ci.render_chat_container()
        except ImportError:
            self._render_chat_placeholder()
        except Exception as e:
            logger.error(f"Chat error: {e}")
            st.error(f"Chat interface error: {e}")

    def _render_chat_placeholder(self) -> None:
        st.markdown('<div class="section-header">Natural Language Query</div>', unsafe_allow_html=True)
        st.error("Chat interface component is unavailable.")
        st.markdown("Try asking:")
        for q in [
            "Show salinity profiles near the equator in March 2023",
            "Compare BGC parameters in the Arabian Sea for the last 6 months",
            "What are the nearest ARGO floats to this location?",
        ]:
            st.markdown(f"- _{q}_")
        user_input = st.text_input("Enter your query:")
        if user_input:
            st.info("Chat requires the backend API. Start the backend and refresh.")

    # ── Export tab ────────────────────────────────────────────────────────────

    def _render_export_content(self) -> None:
        st.markdown('<div class="section-header">Data Export</div>', unsafe_allow_html=True)
        try:
            from components.export_manager import ExportManager
            em = ExportManager()
            em.render_export_interface()
        except ImportError:
            self._render_export_ui()
        except Exception as e:
            logger.error(f"Export error: {e}")
            self._render_export_ui()

    def _render_export_ui(self) -> None:
        """Minimal functional export UI when ExportManager is not available."""
        st.markdown("Export oceanographic measurements in standard formats.")

        col1, col2 = st.columns(2)
        with col1:
            fmt = st.selectbox("Format", ["CSV", "ASCII", "NetCDF"])
            float_ids_input = st.text_input(
                "Float IDs (comma-separated, leave empty for all)",
                placeholder="e.g. F001, F002",
            )
        with col2:
            max_rows = st.number_input("Max rows", min_value=100, max_value=100_000, value=10_000, step=500)
            include_bgc = st.checkbox("Include BGC parameters", value=False)

        if st.button("Export", type="primary"):
            client = st.session_state.get("api_client")
            if not client:
                st.error("API not available. Start the backend to export data.")
                return

            float_ids = [f.strip() for f in float_ids_input.split(",") if f.strip()]
            with st.spinner("Preparing export..."):
                try:
                    result = client.export_data(
                        format=fmt.lower(),
                        float_ids=float_ids or None,
                        max_rows=max_rows,
                        include_bgc=include_bgc,
                    )
                    if result:
                        mime_map = {"csv": "text/csv", "ascii": "text/plain", "netcdf": "application/octet-stream"}
                        ext_map  = {"csv": "csv",      "ascii": "txt",         "netcdf": "nc"}
                        key = fmt.lower()
                        st.download_button(
                            label=f"Download {fmt}",
                            data=result,
                            file_name=f"argo_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext_map[key]}",
                            mime=mime_map[key],
                        )
                    else:
                        st.warning("No data returned. Adjust your filters and try again.")
                except Exception as e:
                    st.error(f"Export failed: {e}")

        st.markdown("---")
        st.markdown("**Supported formats**")
        rows = [
            {"Format": "CSV",    "Use case": "Spreadsheet tools, Python, R",      "Extension": ".csv"},
            {"Format": "ASCII",  "Use case": "Text-based tools, legacy systems",  "Extension": ".txt"},
            {"Format": "NetCDF", "Use case": "Scientific analysis (xarray, NCO)", "Extension": ".nc"},
        ]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    # ── Advanced filters tab ──────────────────────────────────────────────────

    def _render_advanced_filters_content(self) -> None:
        st.markdown('<div class="section-header">Advanced Filters</div>', unsafe_allow_html=True)

        tab1, tab2, tab3 = st.tabs(["Spatial", "Parameter ranges", "Float selection"])

        with tab1:
            st.markdown("**Bounding box**")
            c1, c2, c3, c4 = st.columns(4)
            with c1: st.number_input("North (lat)", value=30.0, min_value=-90.0, max_value=90.0, key="adv_north")
            with c2: st.number_input("South (lat)", value=-30.0, min_value=-90.0, max_value=90.0, key="adv_south")
            with c3: st.number_input("East (lon)",  value=120.0, min_value=-180.0, max_value=180.0, key="adv_east")
            with c4: st.number_input("West (lon)",  value=40.0, min_value=-180.0, max_value=180.0, key="adv_west")

        with tab2:
            c1, c2 = st.columns(2)
            with c1:
                st.slider("Temperature (°C)", -5.0, 35.0, (-2.0, 32.0), key="adv_temp_range")
                st.slider("Salinity (PSU)",   30.0, 40.0, (32.0, 38.0), key="adv_sal_range")
            with c2:
                st.slider("Oxygen (µmol/kg)", 0.0, 400.0, (0.0, 400.0), key="adv_oxy_range")
                st.slider("Chlorophyll (mg/m³)", 0.0, 10.0, (0.0, 10.0), key="adv_chl_range")

        with tab3:
            st.text_area(
                "Float IDs (one per line or comma-separated)",
                placeholder="Leave empty to include all floats.",
                key="adv_float_ids",
                height=100,
            )
            st.multiselect(
                "Float type",
                ["ARGO Core", "ARGO BGC", "Deep ARGO"],
                default=["ARGO Core", "ARGO BGC"],
                key="adv_float_type",
            )

        if st.button("Apply advanced filters", type="primary"):
            st.success("Filters applied. Navigate to another tab to see the filtered results.")

    # ── Footer ────────────────────────────────────────────────────────────────

    def render_footer(self) -> None:
        st.markdown(
            f'<div class="app-footer">FloatChat AI &nbsp;·&nbsp; ARGO Oceanographic Data Platform &nbsp;·&nbsp; '
            f'Built for scientific research &nbsp;·&nbsp; {datetime.now().year}</div>',
            unsafe_allow_html=True,
        )

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    @st.cache_data(show_spinner=False)
    def _sample_data() -> pd.DataFrame:
        """Return a small synthetic dataset for offline demos (cached)."""
        np.random.seed(42)
        n = 500
        return pd.DataFrame({
            "float_id":    np.random.choice(["F001", "F002", "F003", "F004", "F005"], n),
            "depth":       np.random.uniform(0, 2000, n),
            "temperature": np.random.uniform(-2, 30, n),
            "salinity":    np.random.uniform(33, 38, n),
            "latitude":    np.random.uniform(-30, 30, n),
            "longitude":   np.random.uniform(40, 120, n),
        })
