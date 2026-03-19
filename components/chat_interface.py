"""
Chat Interface Component
Conversational AI for ARGO float data exploration via RAG pipeline
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime
import json

from dashboard_config import dashboard_config
from components.api_client import APIClient, APIException
from components.data_transformer import DataTransformer
from components.map_visualization import InteractiveMap
from components.profile_visualizer import ProfileVisualizer

logger = logging.getLogger(__name__)


SAMPLE_QUERIES: Dict[str, List[str]] = {
    "Location": [
        "Show ARGO floats in the Arabian Sea",
        "What floats are near the equator?",
        "Find measurements in the Bay of Bengal",
        "Where are the active floats located?",
    ],
    "Temperature & Salinity": [
        "Show temperature profiles near the equator in March 2023",
        "Compare salinity patterns across regions",
        "Average temperature at 500 m depth",
        "Find the warmest surface waters",
    ],
    "BGC & Water Quality": [
        "Compare BGC parameters in the Arabian Sea for the last 6 months",
        "Show oxygen levels in deep water",
        "Areas with high chlorophyll concentration",
        "pH levels near the surface",
    ],
    "Data Analysis": [
        "Summary of available ARGO data",
        "Compare data quality between floats",
        "Trends in ocean temperature over time",
        "Data coverage in the Indian Ocean",
    ],
}


class ChatInterface:
    """Conversational AI interface for ARGO data exploration"""

    def __init__(self, api_client: Optional[APIClient] = None):
        self.api_client = api_client or st.session_state.get("api_client")
        self.config = dashboard_config
        self.transformer = DataTransformer()
        self.map_viz = InteractiveMap()
        self.profile_viz = ProfileVisualizer()

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

    # ── Public entry point ────────────────────────────────────────────────────

    def render_chat_container(self) -> None:
        """Render the full chat interface."""
        st.markdown('<div class="section-header">ARGO Data Assistant</div>', unsafe_allow_html=True)

        # --- Conversation history (chronological, oldest → newest) ---
        self._render_chat_history()

        st.markdown("---")

        # --- Input bar at the bottom ---
        self._render_input_bar()

        st.markdown("---")

        # --- Collapsible sample queries ---
        self._render_sample_queries()

    # ── Input bar ─────────────────────────────────────────────────────────────

    def _render_input_bar(self) -> None:
        col_input, col_btn = st.columns([5, 1])
        with col_input:
            user_query = st.text_input(
                "Your question",
                placeholder="e.g.  Show salinity profiles near the equator in March 2023",
                key="chat_input",
                label_visibility="collapsed",
            )
        with col_btn:
            send = st.button("Send", type="primary", use_container_width=True)

        # Quick-action chips
        st.markdown(
            """
            <div class="chip-row">
                <span class="chip" id="chip-loc">Float locations</span>
                <span class="chip" id="chip-temp">Temperature profiles</span>
                <span class="chip" id="chip-sal">Salinity analysis</span>
                <span class="chip" id="chip-sum">Data summary</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("Float locations", key="qa_loc", use_container_width=True):
                self._process_query("Show me all ARGO float locations")
                st.rerun()
        with col2:
            if st.button("Temperature profiles", key="qa_temp", use_container_width=True):
                self._process_query("Show temperature profiles for recent data")
                st.rerun()
        with col3:
            if st.button("Salinity analysis", key="qa_sal", use_container_width=True):
                self._process_query("Analyze salinity patterns in the Indian Ocean")
                st.rerun()
        with col4:
            if st.button("Data summary", key="qa_sum", use_container_width=True):
                self._process_query("Give me a summary of available ARGO data")
                st.rerun()

        if send and user_query.strip():
            self._process_query(user_query.strip())
            st.rerun()

    # ── Chat history (chronological) ─────────────────────────────────────────

    def _render_chat_history(self) -> None:
        if not st.session_state.chat_history:
            st.markdown(
                '<div class="chat-empty">Start a conversation — ask anything about ARGO float data.</div>',
                unsafe_allow_html=True,
            )
            return

        # Render oldest → newest (top → bottom) — correct chat convention
        for message in st.session_state.chat_history[-20:]:
            self._render_message(message)

        # History controls
        col_clear, col_export, _ = st.columns([1, 1, 4])
        with col_clear:
            if st.button("Clear history", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()
        with col_export:
            if st.button("Export chat", use_container_width=True):
                self._export_chat_history()

    def _render_message(self, message: Dict[str, Any]) -> None:
        ts = message["timestamp"].strftime("%H:%M")
        content = message["content"]

        if message["type"] == "user":
            st.markdown(
                f'<div class="chat-meta chat-meta-right">You &nbsp;&middot;&nbsp; {ts}</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div class="chat-message-user">{content}</div>',
                unsafe_allow_html=True,
            )
        else:
            extra_cls = "chat-message-error" if message.get("error") else ""
            label = "ARGO Assistant"
            st.markdown(
                f'<div class="chat-meta">{label} &nbsp;&middot;&nbsp; {ts}</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div class="chat-message-ai {extra_cls}">{content}</div>',
                unsafe_allow_html=True,
            )

            # Compact metadata strip below AI response
            meta = message.get("metadata", {})
            if meta and not message.get("error"):
                cols = st.columns(3)
                if meta.get("data_count", 0):
                    cols[0].caption(f"Data points: {meta['data_count']}")
                if meta.get("float_ids"):
                    cols[1].caption(f"Floats: {len(meta['float_ids'])}")
                if meta.get("query_type"):
                    cols[2].caption(f"Type: {meta['query_type']}")

    # ── Sample queries ────────────────────────────────────────────────────────

    def _render_sample_queries(self) -> None:
        with st.expander("Example questions"):
            for category, queries in SAMPLE_QUERIES.items():
                st.markdown(f"**{category}**")
                cols = st.columns(2)
                for i, q in enumerate(queries):
                    with cols[i % 2]:
                        if st.button(q, key=f"sq_{hash(q)}", use_container_width=True):
                            self._process_query(q)
                            st.rerun()

    # ── Query processing ──────────────────────────────────────────────────────

    def _process_query(self, query: str) -> None:
        if not query:
            return

        st.session_state.chat_history.append({
            "type": "user",
            "content": query,
            "timestamp": datetime.now(),
        })

        with st.spinner("Processing your query..."):
            try:
                if self.api_client:
                    response = self.api_client.query_rag_pipeline(query)
                    if response:
                        ai_msg = self._build_ai_message(query, response)
                        st.session_state.chat_history.append(ai_msg)
                        self._render_visualizations(response, query)
                    else:
                        self._append_error("Could not process your query. Please try rephrasing.")
                else:
                    self._append_error(
                        "The ARGO data system is currently unavailable. Check the system status and try again."
                    )
            except APIException as e:
                self._append_error(f"API error: {e}")
            except Exception as e:
                logger.error(f"Chat processing error: {e}")
                self._append_error("An unexpected error occurred. Please try a different question.")

    def _append_error(self, text: str) -> None:
        st.session_state.chat_history.append({
            "type": "ai",
            "content": text,
            "timestamp": datetime.now(),
            "error": True,
        })

    def _build_ai_message(self, query: str, response) -> Dict[str, Any]:
        meta = self.transformer.extract_metadata_for_chat(response.__dict__)
        content = self._format_response(response.answer, meta)
        return {
            "type": "ai",
            "content": content,
            "timestamp": datetime.now(),
            "metadata": meta,
            "raw_response": response,
            "query_type": meta.get("query_type", "unknown"),
        }

    def _format_response(self, answer: str, meta: Dict[str, Any]) -> str:
        """Clean up the answer — strip redundant AI-appended annotations."""
        text = answer.strip()
        count = meta.get("data_count", 0)
        if count:
            text += f"\n\n*{count} measurements retrieved"
            if meta.get("float_ids"):
                text += f" from {len(meta['float_ids'])} float(s)"
            text += ".*"
        return text

    # ── Visualizations ────────────────────────────────────────────────────────

    def _render_visualizations(self, response, query: str) -> None:
        try:
            meta = self.transformer.extract_metadata_for_chat(response.__dict__)
            sql_results = getattr(response, "sql_results", None)
            postgres_ids = meta.get("postgres_ids", [])

            if sql_results:
                self._sql_charts(sql_results, query)
            elif postgres_ids:
                self._profile_charts(postgres_ids[:50], query)
            elif "summary" in query.lower() or "overview" in query.lower():
                self._overview_charts()
        except Exception as e:
            logger.error(f"Visualization error: {e}")

    def _sql_charts(self, sql_results: List[Dict], query: str) -> None:
        if not sql_results:
            return

        df = self.transformer.sql_results_to_dataframe(sql_results)
        if df.empty:
            return

        st.markdown("**Query results**")
        numeric = df.select_dtypes(include=["number"]).columns.tolist()

        col1, col2 = st.columns(2)

        with col1:
            if "depth" in df.columns and "avg_temperature" in df.columns:
                fig = px.scatter(
                    df, x="avg_temperature", y="depth",
                    title="Temperature vs Depth",
                    labels={"avg_temperature": "Temperature (°C)", "depth": "Depth (m)"},
                    color_discrete_sequence=["#0e6ba8"],
                )
                fig.update_yaxes(autorange="reversed")
                fig.update_layout(margin=dict(t=36, b=0, l=0, r=0), height=320)
                st.plotly_chart(fig, use_container_width=True)
            elif len(numeric) >= 2:
                fig = px.scatter(df, x=numeric[0], y=numeric[1],
                                 title=f"{numeric[1]} vs {numeric[0]}",
                                 color_discrete_sequence=["#0e6ba8"])
                fig.update_layout(margin=dict(t=36, b=0, l=0, r=0), height=320)
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            if "depth" in df.columns and "avg_salinity" in df.columns:
                fig = px.scatter(
                    df, x="avg_salinity", y="depth",
                    title="Salinity vs Depth",
                    labels={"avg_salinity": "Salinity (PSU)", "depth": "Depth (m)"},
                    color_discrete_sequence=["#00a896"],
                )
                fig.update_yaxes(autorange="reversed")
                fig.update_layout(margin=dict(t=36, b=0, l=0, r=0), height=320)
                st.plotly_chart(fig, use_container_width=True)
            elif len(numeric) >= 3:
                fig = px.bar(df.head(10), x=df.columns[0], y=numeric[2],
                             title=f"{numeric[2]} distribution",
                             color_discrete_sequence=["#00a896"])
                fig.update_layout(margin=dict(t=36, b=0, l=0, r=0), height=320)
                st.plotly_chart(fig, use_container_width=True)

        with st.expander("Raw data table"):
            st.dataframe(df, use_container_width=True)

    def _profile_charts(self, postgres_ids: List[int], query: str) -> None:
        if not self.api_client:
            st.warning("No API connection — cannot load live profile data.")
            return

        st.markdown("**Profile visualizations**")
        with st.spinner("Loading profile data..."):
            try:
                profiles = self.api_client.get_profiles_by_ids(postgres_ids[:20])
                if not profiles:
                    st.info("No profile data found for the selected measurements.")
                    return

                df = self.transformer.profiles_to_dataframe(profiles)
                if df.empty:
                    st.info("Could not process profile data.")
                    return

                c1, c2, c3 = st.columns(3)
                c1.metric("Measurements", len(df))
                c2.metric("Floats", df["float_id"].nunique() if "float_id" in df.columns else 0)
                if "depth" in df.columns:
                    c3.metric("Max depth", f"{df['depth'].max():.0f} m")

                q = query.lower()
                if any(w in q for w in ["location", "where", "map"]):
                    self._map_chart(df)
                elif any(w in q for w in ["profile", "temperature", "salinity"]):
                    self._profile_plot(df)
                else:
                    self._map_chart(df)
                    self._profile_plot(df)

            except APIException as e:
                st.error(f"API error: {e}")
            except Exception as e:
                logger.error(f"Profile fetch error: {e}")
                st.error("Could not fetch profile data.")

    def _map_chart(self, df: pd.DataFrame) -> None:
        if "latitude" not in df.columns or "longitude" not in df.columns:
            st.info("Location data not available.")
            return
        locs = df[["latitude", "longitude", "float_id"]].drop_duplicates()
        if locs.empty:
            return
        fig = px.scatter_mapbox(
            locs, lat="latitude", lon="longitude", hover_name="float_id",
            zoom=3, height=380, title="Float locations",
            color_discrete_sequence=["#0e6ba8"],
        )
        fig.update_layout(mapbox_style="open-street-map", margin=dict(t=36, b=0, l=0, r=0))
        st.plotly_chart(fig, use_container_width=True)

    def _profile_plot(self, df: pd.DataFrame) -> None:
        params = [p for p in ["temperature", "salinity", "pressure"] if p in df.columns]
        if not params or "depth" not in df.columns:
            st.info("Insufficient data for profile plot.")
            return

        float_ids = df["float_id"].unique()[:3] if "float_id" in df.columns else [None]
        for fid in float_ids:
            subset = df[df["float_id"] == fid] if fid is not None else df
            label = f"Float {fid}" if fid else "Aggregate"
            st.markdown(f"**{label}**")
            cols = st.columns(len(params))
            for j, param in enumerate(params):
                unit = {"temperature": "°C", "salinity": "PSU", "pressure": "dbar"}.get(param, "")
                fig = px.scatter(
                    subset, x=param, y="depth",
                    title=f"{param.title()} profile",
                    labels={param: f"{param.title()} ({unit})", "depth": "Depth (m)"},
                    color_discrete_sequence=["#0e6ba8"],
                )
                fig.update_yaxes(autorange="reversed")
                fig.update_layout(height=380, margin=dict(t=36, b=0, l=0, r=0))
                with cols[j]:
                    st.plotly_chart(fig, use_container_width=True)

    def _overview_charts(self) -> None:
        if not self.api_client:
            return
        try:
            stats = self.api_client.get_system_statistics()
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Active floats", stats.get("active_floats", "—"))
            c2.metric("Total profiles", stats.get("total_profiles", "—"))
            c3.metric("Measurements", f"{stats.get('total_measurements', 0):,}")
            c4.metric("Data quality", f"{stats.get('data_quality', 0):.1f}%")

            if stats.get("recent_activity"):
                act = pd.DataFrame(stats["recent_activity"])
                if not act.empty:
                    fig = px.line(act, x="date", y="count", title="Recent activity",
                                  color_discrete_sequence=["#0e6ba8"])
                    fig.update_layout(height=300, margin=dict(t=36, b=0, l=0, r=0))
                    st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            logger.error(f"Overview chart error: {e}")

    # ── Export ────────────────────────────────────────────────────────────────

    def _export_chat_history(self) -> None:
        if not st.session_state.chat_history:
            st.warning("No chat history to export.")
            return
        rows = [
            {
                "timestamp": m["timestamp"].isoformat(),
                "role": m["type"],
                "content": m["content"],
                "query_type": m.get("query_type", ""),
            }
            for m in st.session_state.chat_history
        ]
        st.download_button(
            label="Download chat history",
            data=json.dumps(rows, indent=2),
            file_name=f"argo_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
        )

    # ── Statistics helper ─────────────────────────────────────────────────────

    def get_chat_statistics(self) -> Dict[str, Any]:
        hist = st.session_state.chat_history
        if not hist:
            return {}
        user_msgs = [m for m in hist if m["type"] == "user"]
        ai_msgs = [m for m in hist if m["type"] == "ai"]
        errors = [m for m in ai_msgs if m.get("error")]
        return {
            "total": len(hist),
            "user": len(user_msgs),
            "ai": len(ai_msgs),
            "errors": len(errors),
            "success_rate": (len(ai_msgs) - len(errors)) / max(len(ai_msgs), 1) * 100,
        }
