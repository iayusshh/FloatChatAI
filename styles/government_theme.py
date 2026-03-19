"""
FloatChat AI — Design System
Dark-mode, glassmorphism, modern data-platform aesthetic.
"""

import streamlit as st


class GovernmentTheme:
    """Central design-system for FloatChat AI."""

    # ── Token map ─────────────────────────────────────────────────────────────
    COLORS = {
        # backgrounds
        "bg":           "#070d1a",
        "bg_secondary": "#0d1526",
        "surface":      "#111827",
        "surface_raised":"#162032",
        # borders
        "border":       "rgba(255,255,255,0.07)",
        "border_strong":"rgba(255,255,255,0.14)",
        # text
        "text":         "#e2e8f0",
        "text_muted":   "#64748b",
        "text_dim":     "#94a3b8",
        # accent
        "primary":      "#3b82f6",
        "primary_glow": "rgba(59,130,246,0.25)",
        "cyan":         "#06b6d4",
        "cyan_glow":    "rgba(6,182,212,0.20)",
        "purple":       "#8b5cf6",
        "purple_glow":  "rgba(139,92,246,0.20)",
        # status
        "success":      "#10b981",
        "warning":      "#f59e0b",
        "danger":       "#ef4444",
        "success_bg":   "rgba(16,185,129,0.12)",
        "warning_bg":   "rgba(245,158,11,0.12)",
        "danger_bg":    "rgba(239,68,68,0.12)",
    }

    @classmethod
    def get_css(cls) -> str:
        c = cls.COLORS
        return f"""
        <style>
        /* ── Fonts ── */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

        /* ── Reset & base ── */
        *, *::before, *::after {{ box-sizing: border-box; }}

        :root {{
            --bg:            {c['bg']};
            --bg2:           {c['bg_secondary']};
            --surface:       {c['surface']};
            --surface-r:     {c['surface_raised']};
            --border:        {c['border']};
            --border-s:      {c['border_strong']};
            --text:          {c['text']};
            --muted:         {c['text_muted']};
            --dim:           {c['text_dim']};
            --blue:          {c['primary']};
            --blue-glow:     {c['primary_glow']};
            --cyan:          {c['cyan']};
            --cyan-glow:     {c['cyan_glow']};
            --purple:        {c['purple']};
            --purple-glow:   {c['purple_glow']};
            --success:       {c['success']};
            --warning:       {c['warning']};
            --danger:        {c['danger']};
            --font:          'Inter', system-ui, sans-serif;
            --mono:          'JetBrains Mono', monospace;
            --radius:        12px;
            --radius-sm:     8px;
            --radius-lg:     16px;
            --ease:          cubic-bezier(.4,0,.2,1);
        }}

        /* ── Hide Streamlit chrome ── */
        #MainMenu, footer, header, .stDeployButton,
        [data-testid="stToolbar"] {{ display: none !important; }}

        /* ══════════════════════════════════════════════
           SIDEBAR RADIO — style as nav list
        ══════════════════════════════════════════════ */
        [data-testid="stSidebar"] [data-testid="stRadio"] > label {{
            display: none !important;
        }}
        [data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] {{
            display: flex !important;
            flex-direction: column !important;
            gap: 2px !important;
        }}
        [data-testid="stSidebar"] [data-testid="stRadio"] label[data-baseweb="radio"] {{
            display: flex !important;
            align-items: center !important;
            padding: .5rem .75rem !important;
            border-radius: 8px !important;
            cursor: pointer !important;
            transition: background .15s var(--ease), color .15s var(--ease) !important;
            margin: 0 !important;
            background: transparent !important;
            border: none !important;
        }}
        [data-testid="stSidebar"] [data-testid="stRadio"] label[data-baseweb="radio"]:hover {{
            background: rgba(255,255,255,.05) !important;
        }}
        /* Selected nav item */
        [data-testid="stSidebar"] [data-testid="stRadio"] label[data-baseweb="radio"][aria-checked="true"] {{
            background: rgba(59,130,246,.12) !important;
            color: var(--blue) !important;
        }}
        /* Hide the actual radio circle dot */
        [data-testid="stSidebar"] [data-testid="stRadio"] [data-testid="stWidgetLabel"],
        [data-testid="stSidebar"] [data-testid="stRadio"] div[data-baseweb="radio"] div:first-child {{
            display: none !important;
        }}
        [data-testid="stSidebar"] [data-testid="stRadio"] label[data-baseweb="radio"] div:last-child p {{
            font-size: .85rem !important;
            font-weight: 500 !important;
            letter-spacing: .01em !important;
            color: inherit !important;
            margin: 0 !important;
        }}

        /* ── App shell ── */
        .stApp {{
            background: var(--bg) !important;
            font-family: var(--font) !important;
            color: var(--text) !important;
        }}
        .main .block-container {{
            padding: 1.5rem 2rem 4rem !important;
            max-width: 1400px !important;
        }}

        /* ══════════════════════════════════════════════
           SIDEBAR
        ══════════════════════════════════════════════ */
        [data-testid="stSidebar"] > div:first-child {{
            background: linear-gradient(180deg, #0a1120 0%, #070d1a 100%) !important;
            border-right: 1px solid var(--border-s) !important;
        }}
        [data-testid="stSidebar"] * {{
            color: var(--text) !important;
            font-family: var(--font) !important;
        }}
        /* Sidebar selectbox */
        [data-testid="stSidebar"] .stSelectbox > div > div {{
            background: rgba(255,255,255,.04) !important;
            border: 1px solid var(--border-s) !important;
            border-radius: var(--radius-sm) !important;
            color: var(--text) !important;
        }}
        [data-testid="stSidebar"] .stSelectbox > div > div:focus-within {{
            border-color: var(--blue) !important;
            box-shadow: 0 0 0 3px var(--blue-glow) !important;
        }}
        /* Sidebar labels */
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] .stMarkdown p {{
            color: var(--muted) !important;
            font-size: .75rem !important;
            font-weight: 600 !important;
            letter-spacing: .07em !important;
            text-transform: uppercase !important;
        }}
        /* Sidebar buttons */
        [data-testid="stSidebar"] .stButton > button {{
            background: rgba(255,255,255,.05) !important;
            border: 1px solid var(--border-s) !important;
            color: var(--dim) !important;
            border-radius: var(--radius-sm) !important;
            font-size: .82rem !important;
            font-weight: 500 !important;
            transition: all .2s var(--ease) !important;
        }}
        [data-testid="stSidebar"] .stButton > button:hover {{
            background: rgba(59,130,246,.12) !important;
            border-color: rgba(59,130,246,.4) !important;
            color: var(--blue) !important;
        }}
        /* Sidebar slider track */
        [data-testid="stSidebar"] [data-testid="stSlider"] [role="slider"] {{
            background: var(--blue) !important;
        }}
        [data-testid="stSidebar"] [data-testid="stSlider"] > div > div > div {{
            background: var(--blue) !important;
        }}
        /* Sidebar checkboxes */
        [data-testid="stSidebar"] [data-testid="stCheckbox"] label {{
            font-size: .82rem !important;
            letter-spacing: .03em !important;
            text-transform: none !important;
            color: var(--dim) !important;
        }}

        /* ══════════════════════════════════════════════
           HEADER CARD  (.app-header)
        ══════════════════════════════════════════════ */
        .app-header {{
            position: relative;
            background: linear-gradient(135deg, #0f1d35 0%, #0c2340 40%, #09263a 70%, #071e2e 100%);
            border: 1px solid rgba(59,130,246,.2);
            border-radius: var(--radius-lg);
            padding: 1.8rem 2.2rem;
            margin-bottom: 2rem;
            overflow: hidden;
            box-shadow: 0 0 40px rgba(59,130,246,.08), 0 20px 60px rgba(0,0,0,.5);
        }}
        /* Glowing orbs behind header */
        .app-header::before {{
            content: '';
            position: absolute;
            top: -60px; right: -60px;
            width: 300px; height: 300px;
            background: radial-gradient(circle, rgba(59,130,246,.18) 0%, transparent 65%);
            border-radius: 50%;
            pointer-events: none;
        }}
        .app-header::after {{
            content: '';
            position: absolute;
            bottom: -80px; left: 30%;
            width: 240px; height: 240px;
            background: radial-gradient(circle, rgba(6,182,212,.10) 0%, transparent 65%);
            border-radius: 50%;
            pointer-events: none;
        }}
        .app-header-title {{
            font-size: 2rem;
            font-weight: 800;
            color: #fff;
            letter-spacing: -.04em;
            line-height: 1.1;
            margin: 0;
            position: relative;
            background: linear-gradient(90deg, #fff 0%, rgba(147,197,253,1) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        .app-header-subtitle {{
            font-size: .875rem;
            color: rgba(148,163,184,.7);
            margin: .4rem 0 0;
            font-weight: 400;
            letter-spacing: .01em;
            position: relative;
        }}
        .app-header-meta {{
            display: flex;
            align-items: center;
            gap: .75rem;
            flex-wrap: wrap;
            position: relative;
        }}

        /* ══════════════════════════════════════════════
           STATUS PILLS
        ══════════════════════════════════════════════ */
        .status-pill {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 10px 4px 8px;
            border-radius: 999px;
            font-size: .72rem;
            font-weight: 600;
            letter-spacing: .03em;
            backdrop-filter: blur(8px);
        }}
        .status-dot {{
            width: 7px; height: 7px;
            border-radius: 50%;
            flex-shrink: 0;
        }}
        .status-online  {{ background: rgba(16,185,129,.15);  color: #34d399; border: 1px solid rgba(16,185,129,.3); }}
        .status-offline {{ background: rgba(239,68,68,.15);   color: #f87171; border: 1px solid rgba(239,68,68,.3); }}
        .status-warning {{ background: rgba(245,158,11,.15);  color: #fbbf24; border: 1px solid rgba(245,158,11,.3); }}
        .dot-online  {{ background: #10b981; box-shadow: 0 0 6px #10b981; animation: blink 2s infinite; }}
        .dot-offline {{ background: #ef4444; }}
        .dot-warning {{ background: #f59e0b; box-shadow: 0 0 6px #f59e0b; animation: blink 2s infinite; }}
        @keyframes blink {{
            0%,100% {{ opacity:1; }} 50% {{ opacity:.35; }}
        }}

        /* ══════════════════════════════════════════════
           METRIC CARDS  (.kpi-card)
        ══════════════════════════════════════════════ */
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 1rem;
            margin-bottom: 1.5rem;
        }}
        @media (max-width: 900px) {{ .kpi-grid {{ grid-template-columns: repeat(2,1fr); }} }}

        .kpi-card {{
            position: relative;
            background: var(--surface);
            border: 1px solid var(--border-s);
            border-radius: var(--radius);
            padding: 1.4rem 1.6rem 1.25rem;
            overflow: hidden;
            transition: transform .2s var(--ease), box-shadow .2s var(--ease), border-color .2s var(--ease);
        }}
        .kpi-card:hover {{
            transform: translateY(-3px);
            border-color: var(--border-strong);
            box-shadow: 0 12px 40px rgba(0,0,0,.35);
        }}
        /* Colour bar at top */
        .kpi-card::before {{
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 2px;
        }}
        .kpi-blue::before   {{ background: linear-gradient(90deg, var(--blue), var(--cyan)); box-shadow: 0 0 12px var(--blue-glow); }}
        .kpi-cyan::before   {{ background: linear-gradient(90deg, var(--cyan), #0ea5e9);    box-shadow: 0 0 12px var(--cyan-glow); }}
        .kpi-purple::before {{ background: linear-gradient(90deg, var(--purple), #ec4899);  box-shadow: 0 0 12px var(--purple-glow); }}
        .kpi-green::before  {{ background: linear-gradient(90deg, var(--success), #06b6d4); box-shadow: 0 0 12px rgba(16,185,129,.25); }}

        /* Glow blob behind value */
        .kpi-card::after {{
            content: '';
            position: absolute;
            bottom: -20px; right: -20px;
            width: 100px; height: 100px;
            border-radius: 50%;
            opacity: .07;
        }}
        .kpi-blue::after   {{ background: var(--blue); }}
        .kpi-cyan::after   {{ background: var(--cyan); }}
        .kpi-purple::after {{ background: var(--purple); }}
        .kpi-green::after  {{ background: var(--success); }}

        .kpi-label {{
            font-size: .7rem;
            font-weight: 700;
            letter-spacing: .1em;
            text-transform: uppercase;
            color: var(--muted);
            margin-bottom: .6rem;
        }}
        .kpi-value {{
            font-size: 2.2rem;
            font-weight: 800;
            color: var(--text);
            line-height: 1;
            letter-spacing: -.04em;
            font-variant-numeric: tabular-nums;
        }}
        .kpi-delta {{
            font-size: .75rem;
            font-weight: 600;
            color: var(--success);
            margin-top: .45rem;
            display: flex;
            align-items: center;
            gap: 3px;
        }}
        .kpi-delta-neg {{ color: var(--danger); }}
        .kpi-sub {{
            font-size: .72rem;
            color: var(--muted);
            margin-top: .3rem;
        }}

        /* ══════════════════════════════════════════════
           NATIVE st.metric OVERRIDE
        ══════════════════════════════════════════════ */
        [data-testid="stMetric"] {{
            background: var(--surface) !important;
            border: 1px solid var(--border-s) !important;
            border-top: 2px solid var(--blue) !important;
            border-radius: var(--radius) !important;
            padding: 1.25rem 1.5rem !important;
            transition: all .2s var(--ease) !important;
        }}
        [data-testid="stMetric"]:hover {{
            border-color: rgba(59,130,246,.4) !important;
            box-shadow: 0 0 24px var(--blue-glow) !important;
            transform: translateY(-2px);
        }}
        [data-testid="stMetricLabel"] > div {{
            font-size: .7rem !important;
            font-weight: 700 !important;
            letter-spacing: .09em !important;
            text-transform: uppercase !important;
            color: var(--muted) !important;
        }}
        [data-testid="stMetricValue"] > div {{
            font-size: 2rem !important;
            font-weight: 800 !important;
            letter-spacing: -.04em !important;
            color: var(--text) !important;
        }}
        [data-testid="stMetricDelta"] svg {{ display: none; }}

        /* ══════════════════════════════════════════════
           SECTION HEADERS
        ══════════════════════════════════════════════ */
        .section-header {{
            font-size: 1.15rem;
            font-weight: 700;
            color: var(--text);
            letter-spacing: -.025em;
            margin-bottom: 1.25rem;
            padding-bottom: .75rem;
            border-bottom: 1px solid var(--border);
            display: flex;
            align-items: center;
            gap: .6rem;
        }}
        .section-header::before {{
            content: '';
            display: inline-block;
            width: 3px;
            height: 1em;
            background: linear-gradient(180deg, var(--blue), var(--cyan));
            border-radius: 2px;
            flex-shrink: 0;
        }}

        /* ══════════════════════════════════════════════
           BUTTONS
        ══════════════════════════════════════════════ */
        .stButton > button {{
            background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 100%) !important;
            color: #fff !important;
            border: 1px solid rgba(59,130,246,.4) !important;
            border-radius: var(--radius-sm) !important;
            font-family: var(--font) !important;
            font-weight: 600 !important;
            font-size: .85rem !important;
            letter-spacing: .01em !important;
            padding: .6rem 1.4rem !important;
            transition: all .2s var(--ease) !important;
            box-shadow: 0 4px 14px rgba(37,99,235,.3) !important;
        }}
        .stButton > button:hover {{
            background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%) !important;
            box-shadow: 0 6px 20px rgba(59,130,246,.45) !important;
            transform: translateY(-1px) !important;
            border-color: rgba(59,130,246,.6) !important;
        }}
        .stButton > button:active {{
            transform: translateY(0) !important;
            box-shadow: 0 2px 8px rgba(59,130,246,.2) !important;
        }}

        /* ══════════════════════════════════════════════
           INPUTS
        ══════════════════════════════════════════════ */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea {{
            background: var(--surface) !important;
            border: 1px solid var(--border-s) !important;
            border-radius: var(--radius-sm) !important;
            color: var(--text) !important;
            font-family: var(--font) !important;
            font-size: .9rem !important;
            transition: border-color .2s var(--ease), box-shadow .2s var(--ease) !important;
        }}
        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus {{
            border-color: var(--blue) !important;
            box-shadow: 0 0 0 3px var(--blue-glow) !important;
            outline: none !important;
        }}
        .stTextInput > div > div > input::placeholder {{
            color: var(--muted) !important;
        }}

        /* ══════════════════════════════════════════════
           TABS
        ══════════════════════════════════════════════ */
        [data-testid="stTabs"] [role="tablist"] {{
            background: var(--surface) !important;
            border: 1px solid var(--border) !important;
            border-radius: var(--radius-sm) !important;
            padding: 4px !important;
            gap: 2px !important;
            border-bottom: none !important;
        }}
        [data-testid="stTabs"] [role="tab"] {{
            background: transparent !important;
            border: none !important;
            border-radius: 6px !important;
            color: var(--muted) !important;
            font-size: .82rem !important;
            font-weight: 600 !important;
            letter-spacing: .02em !important;
            padding: .45rem 1rem !important;
            transition: all .15s var(--ease) !important;
        }}
        [data-testid="stTabs"] [role="tab"]:hover {{
            color: var(--text) !important;
            background: rgba(255,255,255,.05) !important;
        }}
        [data-testid="stTabs"] [role="tab"][aria-selected="true"] {{
            background: rgba(59,130,246,.15) !important;
            color: var(--blue) !important;
            box-shadow: inset 0 0 0 1px rgba(59,130,246,.3) !important;
        }}

        /* ══════════════════════════════════════════════
           SELECTBOX / MULTISELECT
        ══════════════════════════════════════════════ */
        .stSelectbox > div > div,
        .stMultiSelect > div > div {{
            background: var(--surface) !important;
            border: 1px solid var(--border-s) !important;
            border-radius: var(--radius-sm) !important;
            color: var(--text) !important;
        }}
        .stSelectbox > div > div:focus-within,
        .stMultiSelect > div > div:focus-within {{
            border-color: var(--blue) !important;
            box-shadow: 0 0 0 3px var(--blue-glow) !important;
        }}
        /* Multiselect tags */
        [data-testid="stMultiSelect"] span[data-baseweb="tag"] {{
            background: rgba(59,130,246,.2) !important;
            border: 1px solid rgba(59,130,246,.35) !important;
            color: #93c5fd !important;
            border-radius: 4px !important;
        }}

        /* ══════════════════════════════════════════════
           EXPANDERS
        ══════════════════════════════════════════════ */
        [data-testid="stExpander"] {{
            background: var(--surface) !important;
            border: 1px solid var(--border) !important;
            border-radius: var(--radius) !important;
        }}
        [data-testid="stExpander"] summary {{
            font-size: .85rem !important;
            font-weight: 600 !important;
            color: var(--dim) !important;
        }}

        /* ══════════════════════════════════════════════
           ALERTS
        ══════════════════════════════════════════════ */
        [data-testid="stAlert"] {{
            border-radius: var(--radius-sm) !important;
            border: 1px solid !important;
        }}

        /* ══════════════════════════════════════════════
           DATAFRAME / TABLE
        ══════════════════════════════════════════════ */
        [data-testid="stDataFrame"] {{
            border: 1px solid var(--border) !important;
            border-radius: var(--radius) !important;
            overflow: hidden !important;
        }}

        /* ══════════════════════════════════════════════
           CHAT BUBBLES
        ══════════════════════════════════════════════ */
        .chat-wrap {{
            display: flex;
            flex-direction: column;
            gap: .5rem;
            padding: 1rem 0;
        }}
        .chat-row-user {{
            display: flex;
            justify-content: flex-end;
        }}
        .chat-row-ai {{
            display: flex;
            justify-content: flex-start;
        }}
        .bubble-user {{
            background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 100%);
            color: #fff;
            border-radius: 18px 18px 4px 18px;
            padding: .8rem 1.15rem;
            max-width: 72%;
            font-size: .88rem;
            line-height: 1.55;
            box-shadow: 0 4px 20px rgba(37,99,235,.35);
            word-break: break-word;
        }}
        .bubble-ai {{
            background: var(--surface-r);
            border: 1px solid var(--border-s);
            color: var(--text);
            border-radius: 18px 18px 18px 4px;
            padding: .8rem 1.15rem;
            max-width: 72%;
            font-size: .88rem;
            line-height: 1.55;
            word-break: break-word;
        }}
        .bubble-error {{
            background: rgba(239,68,68,.08) !important;
            border-color: rgba(239,68,68,.25) !important;
            color: #fca5a5 !important;
        }}
        .chat-meta {{
            font-size: .68rem;
            color: var(--muted);
            margin: 0 .4rem .15rem;
            font-weight: 500;
        }}
        .chat-meta-right {{ text-align: right; margin-right: .4rem; }}
        .chat-empty-state {{
            text-align: center;
            padding: 3rem 1rem;
            color: var(--muted);
        }}
        .chat-empty-state .icon {{
            font-size: 2.5rem;
            margin-bottom: .75rem;
            opacity: .35;
            filter: grayscale(1);
        }}
        .chat-empty-state p {{
            font-size: .9rem;
            color: var(--muted);
        }}

        /* ══════════════════════════════════════════════
           CHIP ROW (quick-action)
        ══════════════════════════════════════════════ */
        .chip-row {{
            display: flex;
            flex-wrap: wrap;
            gap: .45rem;
            margin-bottom: .75rem;
        }}

        /* ══════════════════════════════════════════════
           CHAT — backward-compat class aliases
        ══════════════════════════════════════════════ */
        .chat-message-user {{
            background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 100%);
            color: #fff;
            border-radius: 18px 18px 4px 18px;
            padding: .8rem 1.15rem;
            max-width: 72%;
            margin-left: auto;
            font-size: .88rem;
            line-height: 1.55;
            box-shadow: 0 4px 20px rgba(37,99,235,.35);
            word-break: break-word;
            margin-bottom: .25rem;
        }}
        .chat-message-ai {{
            background: var(--surface-r);
            border: 1px solid var(--border-s);
            color: var(--text);
            border-radius: 18px 18px 18px 4px;
            padding: .8rem 1.15rem;
            max-width: 72%;
            font-size: .88rem;
            line-height: 1.55;
            word-break: break-word;
            margin-bottom: .25rem;
        }}
        .chat-message-error {{
            background: rgba(239,68,68,.08) !important;
            border-color: rgba(239,68,68,.25) !important;
            color: #fca5a5 !important;
        }}
        .chat-empty {{
            text-align: center;
            padding: 3rem 1rem;
            color: var(--muted);
            font-size: .9rem;
        }}

        /* ══════════════════════════════════════════════
           FOOTER
        ══════════════════════════════════════════════ */
        .app-footer {{
            text-align: center;
            color: var(--muted);
            font-size: .72rem;
            padding: 2rem 0 .5rem;
            border-top: 1px solid var(--border);
            margin-top: 3rem;
            letter-spacing: .04em;
        }}

        /* ══════════════════════════════════════════════
           DIVIDER
        ══════════════════════════════════════════════ */
        hr {{
            border: none !important;
            border-top: 1px solid var(--border) !important;
            margin: 1.5rem 0 !important;
        }}

        /* ══════════════════════════════════════════════
           SCROLLBAR
        ══════════════════════════════════════════════ */
        ::-webkit-scrollbar {{ width: 5px; height: 5px; }}
        ::-webkit-scrollbar-track {{ background: transparent; }}
        ::-webkit-scrollbar-thumb {{ background: rgba(255,255,255,.12); border-radius: 4px; }}
        ::-webkit-scrollbar-thumb:hover {{ background: var(--blue); }}

        /* ══════════════════════════════════════════════
           MARKDOWN HEADINGS
        ══════════════════════════════════════════════ */
        [data-testid="stMarkdown"] h1,
        [data-testid="stMarkdown"] h2,
        [data-testid="stMarkdown"] h3 {{
            color: var(--text) !important;
            font-weight: 700 !important;
            letter-spacing: -.02em !important;
        }}
        [data-testid="stMarkdown"] p,
        [data-testid="stMarkdown"] li {{
            color: var(--dim) !important;
            line-height: 1.7 !important;
        }}
        </style>
        """

    @classmethod
    def apply_theme(cls) -> None:
        st.markdown(cls.get_css(), unsafe_allow_html=True)

    # ── Helper renderers ──────────────────────────────────────────────────────

    @classmethod
    def status_pill(cls, status: str, label: str) -> str:
        dot = f'<span class="status-dot dot-{status}"></span>'
        return f'<span class="status-pill status-{status}">{dot}{label}</span>'

    @classmethod
    def kpi_card(cls, label: str, value: str, color: str = "blue",
                 delta: str = "", sub: str = "") -> str:
        delta_html = (
            f'<div class="kpi-delta">{delta}</div>' if delta else ""
        )
        sub_html = f'<div class="kpi-sub">{sub}</div>' if sub else ""
        return f"""
        <div class="kpi-card kpi-{color}">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            {delta_html}{sub_html}
        </div>"""
