import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Observatory Dashboard",
    page_icon="🔭",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ==========================================
# STYLING
# ==========================================

# Colours used across every chart
BG_CARD = "#FFFFFF"
ACCENT = "#6366F1"
ACCENT_2 = "#22D3EE"
ACCENT_3 = "#A78BFA"
GRID = "rgba(15, 23, 42, 0.08)"
TEXT = "#1E293B"
MUTED = "#64748B"

FLAG_COLORS = {
    "GOOD": "#10B981",
    "MISSING": "#F59E0B",
    "DUPLICATE": "#A78BFA",
    "INVALID": "#EF4444",
    "TIME_ERROR": "#F97316"
}

# Order of the three main analysis pages, used by the prev/next
# navigation arrows at the top of the page.
PAGE_ORDER = ["Dashboard", "Filtered Data", "Detailed Breakdown"]

# Used by every panel that breaks the record down by calendar month
MONTH_NAMES = {
    1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr",
    5: "May", 6: "Jun", 7: "Jul", 8: "Aug",
    9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"
}

# 3-sigma outlier threshold is fixed (not user-adjustable). Only the
# minute bucket size is configurable by the user.
SIGMA_THRESHOLD = 3.0


# Base layout applied to every plotly figure
def chart_layout(height=280, legend=False):
    return dict(
        template="plotly_white",
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=10, b=10),
        showlegend=legend,
        font=dict(color=MUTED, size=11),
        xaxis=dict(gridcolor=GRID, zeroline=False),
        yaxis=dict(gridcolor=GRID, zeroline=False),
        hoverlabel=dict(bgcolor=BG_CARD, font_size=12)
    )


st.markdown(
    """
    <style>
    /* page background */
    .stApp {
        background: #FFFFFF;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }

    /* metric cards */
    [data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        padding: 18px 20px;
    }

    [data-testid="stMetricLabel"] p {
        color: #6B7280 !important;
        font-size: 0.78rem !important;
        font-weight: 500 !important;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }

    [data-testid="stMetricValue"] {
        color: #111827 !important;
        font-size: 1.9rem !important;
        font-weight: 600 !important;
    }

    /* chart cards */
    [data-testid="stVerticalBlockBorderWrapper"]:has(> div > div > [data-testid="stPlotlyChart"]) {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        padding: 16px 18px 8px 18px;
    }

    /* headings */
    h1 {
        font-weight: 650 !important;
        letter-spacing: -0.02em;
        color: #111827 !important;
    }

    h3 {
        color: #111827 !important;
        font-size: 1.05rem !important;
        font-weight: 600 !important;
    }

    .card-title {
        color: #111827;
        font-size: 0.95rem;
        font-weight: 600;
        margin-bottom: 2px;
    }

    .card-sub {
        color: #9CA3AF;
        font-size: 0.75rem;
        margin-bottom: 10px;
    }

    /* stats line under each chart */
    .chart-stats {
        display: flex;
        gap: 18px;
        margin: 4px 0 6px 2px;
        font-size: 0.76rem;
        color: #9CA3AF;
    }

    .chart-stats b {
        color: #4B5563;
        font-weight: 500;
        margin-right: 4px;
    }

    /* section label */
    .section {
        color: #111827;
        font-size: 1.15rem;
        font-weight: 650;
        margin: 26px 0 12px 0;
        letter-spacing: -0.01em;
    }

    [data-testid="stDataFrame"] {
        border-radius: 8px;
        overflow: hidden;
        border: 1px solid #E5E7EB;
    }

    /* ---------- page nav arrows ---------- */
    .nav-page-label {
        text-align: center;
        color: #9CA3AF;
        font-size: 0.78rem;
        font-weight: 500;
        letter-spacing: 0.03em;
        padding-top: 9px;
    }

    /* ---------- step nav arrows ---------- */
    .step-nav-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
        padding: 12px 0;
    }

    .step-indicator {
        text-align: center;
        color: #6B7280;
        font-size: 0.78rem;
        font-weight: 500;
        letter-spacing: 0.03em;
    }

    /* ---------- landing screen ---------- */
    .hero {
        position: relative;
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 16px;
        padding: 52px 54px 56px 54px;
        margin-top: 6px;
        overflow: hidden;
    }

    /* very light tint so the card is not completely flat */
    .hero-glow {
        position: absolute;
        top: -170px;
        right: -110px;
        width: 440px;
        height: 440px;
        background: radial-gradient(circle,
                    rgba(79, 70, 229, 0.06) 0%,
                    rgba(255, 255, 255, 0) 70%);
        pointer-events: none;
    }

    .hero-orb {
        position: absolute;
        right: 64px;
        bottom: -70px;
        width: 180px;
        height: 180px;
        border-radius: 50%;
        background: radial-gradient(circle at 40% 30%,
                    rgba(79, 70, 229, 0.10) 0%,
                    rgba(255, 255, 255, 0) 70%);
        border-top: 1px solid #E5E7EB;
        pointer-events: none;
    }

    .hero-badge {
        position: relative;
        display: inline-block;
        color: #4B5563;
        background: #F9FAFB;
        border: 1px solid #E5E7EB;
        border-radius: 999px;
        padding: 6px 15px;
        font-size: 0.68rem;
        font-weight: 600;
        letter-spacing: 0.14em;
        margin-bottom: 20px;
    }

    .hero-title {
        position: relative;
        color: #111827;
        font-size: 3rem;
        font-weight: 700;
        line-height: 1.1;
        letter-spacing: -0.03em;
        margin-bottom: 16px;
        max-width: 620px;
    }

    .hero-sub {
        position: relative;
        color: #6B7280;
        font-size: 1rem;
        line-height: 1.65;
        max-width: 540px;
        margin-bottom: 26px;
    }

    .hero-cta {
        position: relative;
        display: inline-flex;
        align-items: center;
        gap: 6px;
        color: #6B7280;
        font-size: 0.85rem;
        font-weight: 500;
        font-style: italic;
    }

    /* the actual upload control - styled to match the cards below */
    [data-testid="stFileUploaderDropzone"] {
        background: #FFFFFF;
        border: 1.5px dashed #C7D2FE;
        border-radius: 12px;
    }

    [data-testid="stFileUploaderDropzone"]:hover {
        border-color: #6366F1;
    }

    .feature-row {
        display: flex;
        gap: 16px;
        margin-top: 18px;
    }

    .feature {
        flex: 1;
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        padding: 22px 24px;
    }

    .feature-icon {
        width: 36px;
        height: 36px;
        border-radius: 9px;
        background: #F3F4F6;
        color: #4B5563;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1rem;
        margin-bottom: 14px;
    }

    .feature-title {
        color: #111827;
        font-size: 0.98rem;
        font-weight: 600;
        margin-bottom: 7px;
    }

    .feature-text {
        color: #6B7280;
        font-size: 0.83rem;
        line-height: 1.55;
    }

    @media (max-width: 900px) {
        .feature-row { flex-direction: column; }
        .hero-title { font-size: 2.1rem; }
        .hero-orb { display: none; }
    }

    /* ---------- date range inputs (Setup > Select time period) ---------- */
    [data-testid="stDateInput"] {
        background: linear-gradient(180deg, #F5F5FF 0%, #FAFAFF 100%);
        border: 1.5px solid #E0E1FA;
        border-radius: 10px;
        padding: 6px 10px 4px 10px;
        transition: border-color 0.15s ease, box-shadow 0.15s ease;
    }

    [data-testid="stDateInput"]:hover {
        border-color: #A5A6F0;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.08);
    }

    [data-testid="stDateInput"] input {
        color: #312E81 !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
    }

    [data-testid="stDateInput"] label p {
        color: #6366F1 !important;
        font-size: 0.72rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.06em;
        text-transform: uppercase;
    }

    .date-range-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        margin-top: 12px;
        padding: 5px 14px;
        background: #EEF2FF;
        border: 1px solid #E0E1FA;
        border-radius: 999px;
        color: #4338CA;
        font-size: 0.78rem;
        font-weight: 600;
    }

    /* ---------- outlier detection (Setup > Configure outlier detection) ---------- */
    [data-testid="stNumberInput"] {
        background: linear-gradient(180deg, #F5F5FF 0%, #FAFAFF 100%);
        border: 1.5px solid #E0E1FA;
        border-radius: 10px;
        padding: 6px 10px 4px 10px;
        max-width: 260px;
        transition: border-color 0.15s ease, box-shadow 0.15s ease;
    }

    [data-testid="stNumberInput"]:hover {
        border-color: #A5A6F0;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.08);
    }

    [data-testid="stNumberInput"] input {
        color: #312E81 !important;
        font-weight: 700 !important;
        font-size: 1.05rem !important;
    }

    [data-testid="stNumberInput"] label p {
        color: #6366F1 !important;
        font-size: 0.72rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.06em;
        text-transform: uppercase;
    }

    [data-testid="stNumberInputStepUp"],
    [data-testid="stNumberInputStepDown"] {
        border-radius: 6px !important;
        color: #6366F1 !important;
    }

    .bucket-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        margin-top: 12px;
        margin-right: 8px;
        padding: 5px 14px;
        background: #EEF2FF;
        border: 1px solid #E0E1FA;
        border-radius: 999px;
        color: #4338CA;
        font-size: 0.78rem;
        font-weight: 600;
    }

    .sigma-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        margin-top: 12px;
        padding: 5px 14px;
        background: #FEF3F2;
        border: 1px solid #FBD5CE;
        border-radius: 999px;
        color: #B42318;
        font-size: 0.78rem;
        font-weight: 600;
    }

    #MainMenu, footer, header { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True
)


def card_title(title, subtitle=""):
    st.markdown(
        f'<div class="card-title">{title}</div>'
        f'<div class="card-sub">{subtitle}</div>',
        unsafe_allow_html=True
    )


def section(text):
    st.markdown(f'<div class="section">{text}</div>', unsafe_allow_html=True)


def add_stats_annotation(fig, text):
    """Small top-right in-chart annotation showing mean +/- std and a
    record count, matching the style of the reference monthly-grid
    figures (e.g. "9.2+/-4.8" / "count:549")."""
    fig.add_annotation(
        xref="paper", yref="paper",
        x=0.98, y=0.95,
        xanchor="right", yanchor="top",
        text=text,
        showarrow=False,
        align="right",
        font=dict(size=10, color=TEXT)
    )


def render_legend_row(items):
    """A single shared legend line shown above a grid of small
    multiples, instead of repeating a legend on every panel.
    items: list of (color, symbol, label) tuples.
    """
    spans = "".join(
        f'<span style="color:{color}; font-weight:600; '
        f'margin-right:20px;">{symbol} {label}</span>'
        for color, symbol, label in items
    )
    st.markdown(
        f'<div style="margin: 2px 0 10px 2px; font-size:0.78rem;">{spans}</div>',
        unsafe_allow_html=True
    )


def chart_stats(values, unit_text=""):
    """Small average / min / max line shown under a chart."""
    values = pd.Series(values).dropna()

    if len(values) == 0:
        st.markdown(
            '<div class="chart-stats">no data</div>',
            unsafe_allow_html=True
        )
        return

    average = values.mean()
    lowest = values.min()
    highest = values.max()

    st.markdown(
        '<div class="chart-stats">'
        f'<span><b>avg</b> {average:.1f}{unit_text}</span>'
        f'<span><b>min</b> {lowest:.1f}{unit_text}</span>'
        f'<span><b>max</b> {highest:.1f}{unit_text}</span>'
        '</div>',
        unsafe_allow_html=True
    )


def chart_stats_std(means, stds, unit_text=""):
    """Small average / standard deviation line - kept for optional use
    elsewhere, but the Diurnal and Daily panels now show avg/min/max
    (via chart_stats) alongside a text label on the card that states
    the shaded band itself is +/-1 standard deviation.
    """
    means = pd.Series(means).dropna()
    stds = pd.Series(stds).dropna()

    if len(means) == 0:
        st.markdown(
            '<div class="chart-stats">no data</div>',
            unsafe_allow_html=True
        )
        return

    average = means.mean()
    spread = stds.mean() if len(stds) > 0 else 0

    if pd.isna(spread):
        spread = 0

    st.markdown(
        '<div class="chart-stats">'
        f'<span><b>avg</b> {average:.1f}{unit_text}</span>'
        f'<span><b>std</b> \u00b1{spread:.1f}{unit_text}</span>'
        '</div>',
        unsafe_allow_html=True
    )


def show_controls_panel():
    """Display a collapsible Controls panel for changing selections."""
    with st.sidebar:
        with st.expander("🎛️ Controls", expanded=True):

            st.markdown("**Current Selections**")

            # Unified setup for Filtered Data and Detailed Breakdown
            combined_setup = st.session_state.selected_page != "Dashboard"

            # Display current page
            if st.session_state.page_confirmed:
                st.caption(f"📄 View: **{st.session_state.selected_page}**")
                if st.button("Change view", key="control_change_page", use_container_width=True):
                    st.session_state.page_confirmed = False
                    st.rerun()

            # Display current date range
            if st.session_state.date_range_confirmed:
                st.caption(
                    f"📅 Dates: **{st.session_state.start_date}** to **{st.session_state.end_date}**"
                )
                if combined_setup and st.button("Change setup", key="control_change_setup", use_container_width=True):
                    st.session_state.date_range_confirmed = False
                    st.session_state.parameter_confirmed = False
                    st.session_state.grouping_confirmed = False
                    st.rerun()

            # Display current parameter
            if st.session_state.parameter_confirmed:
                param_label = info.get(st.session_state.selected_parameter, {}).get("label", st.session_state.selected_parameter)
                st.caption(f"📊 Parameter: **{param_label}**")

            # Display 3-sigma settings if applicable
            if (st.session_state.grouping_confirmed and
                    st.session_state.selected_page in ("Filtered Data", "Detailed Breakdown")):
                st.caption(f"⚙️ Bucket: **{st.session_state.min_interval} min**")
                st.caption(f"⚙️ Threshold: **{st.session_state.sigma_threshold}σ (fixed)**")

            st.divider()

            # Reset everything button
            if st.button("🔄 Start over", key="control_reset_all", use_container_width=True):
                st.session_state.page_confirmed = False
                st.session_state.date_range_confirmed = False
                st.session_state.parameter_confirmed = False
                st.session_state.grouping_confirmed = False
                st.session_state.selected_page = None
                st.session_state.selected_parameter = None
                st.rerun()


def get_full_flow():
    """The complete ordered sequence of steps/pages in the app.
    Now unified: Filtered Data and Detailed Breakdown both use the same
    single "Setup" step that combines date range, parameter, and 3-sigma.
    """
    page = st.session_state.selected_page

    if page == "Dashboard":
        flow = ["Page Selection"]
    else:
        # Single unified setup page for Filtered Data and Detailed Breakdown
        flow = ["Page Selection", "Setup"]

    flow += PAGE_ORDER

    return flow


def _goto_step(step_name):
    """Update session state so that `step_name` becomes the active step."""

    if step_name == "Page Selection":
        st.session_state.page_confirmed = False

    elif step_name == "Setup":
        # Unified setup: Date Range + Parameter + 3-Sigma
        st.session_state.date_range_confirmed = False
        st.session_state.parameter_confirmed = False
        st.session_state.grouping_confirmed = False

    else:
        # One of the content pages (Dashboard / Filtered Data / Detailed Breakdown)
        st.session_state.selected_page = step_name
        st.session_state.page_confirmed = True
        st.session_state.date_range_confirmed = True
        st.session_state.parameter_confirmed = True
        st.session_state.grouping_confirmed = True


def unified_nav(current):
    """Unified back/forward navigation bar."""
    flow = get_full_flow()

    if current not in flow:
        return

    idx = flow.index(current)
    has_prev = idx > 0
    has_next = idx < len(flow) - 1

    nav_left, nav_center, nav_right = st.columns([1, 3, 1])

    with nav_left:
        if has_prev:
            prev_step = flow[idx - 1]
            prev_label = f"\u2190 {prev_step}" if current in PAGE_ORDER else "\u2190 Back"
            if st.button(prev_label, key=f"unified_nav_prev_{current}", width="stretch"):
                _goto_step(prev_step)
                st.rerun()
        else:
            st.empty()

    with nav_center:
        st.markdown(
            f'<div class="nav-page-label">Step {idx + 1} of {len(flow)} '
            f'&middot; {current}</div>',
            unsafe_allow_html=True
        )

    with nav_right:
        if has_next:
            next_step = flow[idx + 1]
            next_label = f"{next_step} \u2192" if current in PAGE_ORDER else "Next \u2192"
            if st.button(next_label, key=f"unified_nav_next_{current}", width="stretch"):
                _goto_step(next_step)
                st.rerun()
        else:
            st.empty()


# ==========================================
# COLUMN DETECTION
# ==========================================

PARAMETER_PATTERNS = {
    "dewpoint": {
        "keys": ["dew"],
        "label": "Dew Point", "unit": "\u00b0C",
        "min": -60, "max": 50, "sigma": True
    },
    "wind_direction": {
        "keys": ["dir", "wd_", "_deg", "bearing"],
        "label": "Wind Direction", "unit": "\u00b0",
        "min": 0, "max": 360, "sigma": False
    },
    "wind_speed": {
        "keys": ["wind", "wspd", "mps", "speed", "gust"],
        "label": "Wind Speed", "unit": "m/s",
        "min": 0, "max": 75, "sigma": True
    },
    "humidity": {
        "keys": ["rh", "humid"],
        "label": "Humidity", "unit": "%",
        "min": 0, "max": 100, "sigma": True
    },
    "solar": {
        "keys": ["sr_", "solar", "radiation", "wm2", "irradiance"],
        "label": "Solar Radiation", "unit": "W/m\u00b2",
        "min": 0, "max": 1400, "sigma": False
    },
    "rainfall": {
        "keys": ["rain", "precip"],
        "label": "Rainfall", "unit": "mm",
        "min": 0, "max": 500, "sigma": False
    },
    "pressure": {
        "keys": ["pressure", "hpa", "mbar", "baro"],
        "label": "Pressure", "unit": "hPa",
        "min": 500, "max": 1100, "sigma": True
    },
    "temperature": {
        "keys": ["temp", "celsius"],
        "label": "Temperature", "unit": "\u00b0C",
        "min": -50, "max": 60, "sigma": True
    },
}


def identify(column_name):
    """Match a column name to a known parameter type, or return None."""
    name = str(column_name).strip().lower()

    for kind, meta in PARAMETER_PATTERNS.items():
        for keyword in meta["keys"]:
            if keyword in name:
                return kind

    return None


def _date_str(series):
    """Turn a Date column (text, Excel datetime, or datetime.date objects)
    into 'YYYY-MM-DD' strings."""
    return pd.to_datetime(series, errors="coerce").dt.strftime("%Y-%m-%d")


def _time_str(series):
    """Turn a Time column into 'HH:MM:SS' strings.

    Excel can hand us: real datetimes, datetime.time objects, a fraction
    of a day (0.4167 = 10:00), plain hour numbers, or text.
    """
    # Real datetime values (e.g. 1900-01-01 10:00:00)
    if pd.api.types.is_datetime64_any_dtype(series):
        return series.dt.strftime("%H:%M:%S")

    # Numeric: fraction of a day, or hour number
    if pd.api.types.is_numeric_dtype(series):
        clean = series.dropna()
        if len(clean) > 0 and (clean <= 1).all():
            delta = pd.to_timedelta(series, unit="D")
        else:
            delta = pd.to_timedelta(series, unit="h")
        return (pd.Timestamp("1970-01-01") + delta).dt.strftime("%H:%M:%S")

    # Text or datetime.time objects
    return series.astype(str).str.strip()


def find_datetime(data):
    """Work out how this file stores time."""
    lower = {str(c).strip().lower(): c for c in data.columns}

    date_column = None
    time_column = None
    stamp_column = None

    for name, original in lower.items():
        if name in ("date", "day", "obs_date"):
            date_column = original
        elif name in ("time", "hour", "obs_time"):
            time_column = original
        elif name in ("timestamp", "datetime", "date_time", "utc", "time_utc"):
            stamp_column = original

    if date_column is not None and time_column is not None:
        try:
            combined = pd.to_datetime(
                _date_str(data[date_column]) + " " + _time_str(data[time_column]),
                errors="coerce"
            )
            if combined.notna().sum() > len(data) * 0.5:
                return combined, [date_column, time_column]
        except Exception:
            pass

    if stamp_column is not None:
        try:
            combined = pd.to_datetime(data[stamp_column], errors="coerce")
            if combined.notna().sum() > len(data) * 0.5:
                return combined, [stamp_column]
        except Exception:
            pass

    for column in data.columns:

        if pd.api.types.is_numeric_dtype(data[column]):
            continue

        try:
            combined = pd.to_datetime(data[column], errors="coerce")
        except Exception:
            continue

        if combined.notna().sum() <= len(data) * 0.8:
            continue

        years = combined.dt.year.dropna()

        if len(years) > 0 and years.min() >= 1950 and years.max() <= 2100:
            return combined, [column]

    return None, []


# ==========================================
# 1. BRANDING
# ==========================================

st.markdown("### 🔭 Observatory")

st.caption("Data quality & analysis")

st.markdown("---")


# ==========================================
# 1A. CONTROLS SIDEBAR (after file is uploaded)
# ==========================================

controls_placeholder = st.empty()


# ==========================================
# 1B. MAIN SCREEN - FILE UPLOAD
# ==========================================

st.markdown("#### 📤 Upload observations")

uploaded_file = st.file_uploader(
    "Drop a CSV or XLSX file here, or click to browse",
    type=["csv", "xlsx"],
    label_visibility="collapsed"
)

st.write("")

if uploaded_file is None:

    st.markdown(
        '<div class="hero"><div class="hero-glow"></div><div class="hero-orb"></div><div class="hero-badge">ATMOSPHERIC DATA QUALITY</div><div class="hero-title">Observatory Data Dashboard</div><div class="hero-sub">Upload observational data to run automated quality control, then explore diurnal, daily, monthly and seasonal patterns.</div><div class="hero-cta">&#8593; Use the upload box above to get started</div></div><div class="feature-row"><div class="feature"><div class="feature-icon">✓</div><div class="feature-title">Quality Control</div><div class="feature-text">Missing values, duplicates, physically impossible readings, broken intervals and 3&#963; outliers.</div></div><div class="feature"><div class="feature-icon">◷</div><div class="feature-title">Temporal Analysis</div><div class="feature-text">Diurnal, daily, monthly and seasonal variation for every observed parameter.</div></div><div class="feature"><div class="feature-icon">✦</div><div class="feature-title">Wind Analysis</div><div class="feature-text">Polar wind rose showing direction frequency banded by wind speed.</div></div></div>',
        unsafe_allow_html=True
    )

    st.stop()


# ==========================================
# 2. READ FILE
# ==========================================

file_name = uploaded_file.name.lower()

try:
    if file_name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)

    else:
        # openpyxl must be installed (pip install openpyxl)
        df = pd.read_excel(uploaded_file, engine="openpyxl")

except ImportError:

    st.error(
        "Reading Excel files needs the 'openpyxl' package. "
        "Install it with:  pip install openpyxl  "
        "(and add it to requirements.txt if you deploy the app)."
    )

    st.stop()

except Exception as error:

    st.error(f"Could not read this file: {error}")

    st.stop()


# Excel files often contain fully empty rows/columns - drop them
df = df.dropna(how="all")
df = df.dropna(axis=1, how="all")
df = df.reset_index(drop=True)


# ==========================================
# 3. DETECT TIME AND PARAMETERS
# ==========================================

df.columns = [str(column).strip() for column in df.columns]

timestamp_series, time_columns = find_datetime(df)


if timestamp_series is None:

    st.error(
        "Could not find a date/time column. The file needs either "
        "separate Date and Time columns, or one combined timestamp column."
    )

    st.write("Columns found:", list(df.columns))

    st.stop()


df["Timestamp"] = timestamp_series

# Rows whose timestamp could not be read cannot be analysed
df = df[df["Timestamp"].notna()].reset_index(drop=True)


parameter_columns = []

for column in df.columns:

    if column in time_columns or column == "Timestamp":
        continue

    try:
        numeric = pd.to_numeric(df[column], errors="coerce")
    except Exception:
        continue

    if numeric.notna().sum() > len(df) * 0.5:
        df[column] = numeric
        parameter_columns.append(column)


if len(parameter_columns) == 0:

    st.error("No numeric measurement columns found in this file.")

    st.stop()


# Build a description for each detected column
info = {}

for column in parameter_columns:

    kind = identify(column)

    if kind is not None:

        meta = PARAMETER_PATTERNS[kind]

        info[column] = {
            "label": meta["label"],
            "unit": meta["unit"],
            "min": meta["min"],
            "max": meta["max"],
            "sigma": meta["sigma"],
            "kind": kind
        }

    else:

        info[column] = {
            "label": column.replace("_", " "),
            "unit": "",
            "min": None,
            "max": None,
            "sigma": True,
            "kind": None
        }


original_columns = time_columns + parameter_columns


# ==========================================
# 4. TIME COLUMNS
# ==========================================

df["Hour"] = df["Timestamp"].dt.hour
df["Day"] = df["Timestamp"].dt.date
df["Month"] = df["Timestamp"].dt.month


def get_season(month):
    """Four-season scheme."""
    if month in [12, 1, 2]:
        return "Winter"
    elif month in [3, 4, 5]:
        return "Spring"
    elif month in [6, 7, 8]:
        return "Summer-Monsoon"
    else:
        return "Autumn"


df["Season"] = df["Month"].apply(get_season)


# ==========================================
# 4B. 3-SIGMA GROUPING & STATE (defaults)
# ==========================================

if "group_by" not in st.session_state:

    st.session_state.group_by = "Min"
    st.session_state.min_interval = 10
    st.session_state.sigma_threshold = SIGMA_THRESHOLD
    st.session_state.grouping_confirmed = False
    st.session_state.selected_page = None
    st.session_state.page_confirmed = False
    st.session_state.start_date = None
    st.session_state.end_date = None
    st.session_state.date_range_confirmed = False
    st.session_state.selected_parameter = None
    st.session_state.parameter_confirmed = False

group_by = st.session_state.group_by

min_interval = st.session_state.min_interval

_minutes_since_midnight = df["Timestamp"].dt.hour * 60 + df["Timestamp"].dt.minute
df["Min"] = (_minutes_since_midnight // min_interval) * min_interval



# ==========================================
# 4C. PAGE SELECTION (STEP 1)
# ==========================================

if not st.session_state.page_confirmed:

    st.markdown(
        '<div class="hero"><div class="hero-glow"></div><div class="hero-orb"></div>'
        '<div class="hero-badge">CHOOSE A VIEW</div>'
        '<div class="hero-title">What do you want to see?</div>'
        '<div class="hero-sub">Pick a view to open. You can switch to a '
        'different one at any time from the Controls panel.</div></div>',
        unsafe_allow_html=True
    )

    st.write("")

    page_options = [
        {
            "name": "Dashboard",
            "icon": "\u2726",
            "text": "Explore every record with diurnal, daily, monthly "
                    "and seasonal charts, plus the wind rose."
        },
        {
            "name": "Filtered Data",
            "icon": "\u2713",
            "text": "The same charts, restricted to records that passed "
                    "every quality check."
        },
        {
            "name": "Detailed Breakdown",
            "icon": "\u25a4",
            "text": "The full data-quality report: check counts, flagged "
                    "records, and per-parameter limits."
        }
    ]

    page_cols = st.columns(3)

    for page_col, option in zip(page_cols, page_options):

        with page_col:

            with st.container(border=True):

                st.markdown(
                    f'<div class="feature-icon">{option["icon"]}</div>'
                    f'<div class="feature-title">{option["name"]}</div>'
                    f'<div class="feature-text">{option["text"]}</div>',
                    unsafe_allow_html=True
                )

                st.write("")

                if st.button(
                    "Select",
                    key=f"open_page_{option['name']}",
                    type="primary",
                    width="stretch"
                ):

                    st.session_state.selected_page = option["name"]
                    st.session_state.page_confirmed = True

                    if option["name"] == "Dashboard":
                        st.session_state.grouping_confirmed = True
                        st.session_state.date_range_confirmed = True
                        st.session_state.start_date = df["Timestamp"].min().date()
                        st.session_state.end_date = df["Timestamp"].max().date()
                        st.session_state.parameter_confirmed = True
                        if st.session_state.selected_parameter not in parameter_columns:
                            st.session_state.selected_parameter = parameter_columns[0]

                    st.rerun()

    st.stop()


# ==========================================
# 4D. UNIFIED SETUP PAGE (STEP 2)
# ==========================================
# Combines Date Range + Parameter Selection + 3-Sigma Outlier Setup
# for both Filtered Data and Detailed Breakdown

if (
    st.session_state.selected_page != "Dashboard"
    and not (
        st.session_state.date_range_confirmed
        and st.session_state.parameter_confirmed
        and st.session_state.grouping_confirmed
    )
):

    first_day = df["Timestamp"].min().date()
    last_day = df["Timestamp"].max().date()

    show_controls_panel()

    if st.button("\u2190 Choose a view", key="setup_back_to_page_selection"):
        st.session_state.page_confirmed = False
        st.session_state.date_range_confirmed = False
        st.session_state.parameter_confirmed = False
        st.session_state.grouping_confirmed = False
        st.rerun()

    st.markdown(
        '<div class="hero"><div class="hero-glow"></div><div class="hero-orb"></div>'
        '<div class="hero-badge">SET UP ANALYSIS</div>'
        '<div class="hero-title">Configure your analysis</div>'
        '<div class="hero-sub">Choose the date range, parameter and 3\u03c3 '
        'outlier bucket size. You can adjust these anytime from the Controls panel.</div></div>',
        unsafe_allow_html=True
    )

    st.write("")

    setup_left, setup_right = st.columns([2, 1])

    with setup_left:

        # ==========================================
        # STEP 1: DATE RANGE
        # ==========================================

        with st.container(border=True):

            card_title("1. Select time period", "Choose the start and end dates for analysis")

            date_col1, date_col2 = st.columns(2)

            with date_col1:
                start_day = st.date_input(
                    "📅  FROM",
                    value=st.session_state.start_date or first_day,
                    min_value=first_day,
                    max_value=last_day,
                    key="unified_start_date"
                )

            with date_col2:
                end_day = st.date_input(
                    "📅  TO",
                    value=st.session_state.end_date or last_day,
                    min_value=first_day,
                    max_value=last_day,
                    key="unified_end_date"
                )

            if start_day <= end_day:
                span_days = (end_day - start_day).days + 1
                st.markdown(
                    f'<div class="date-range-badge">◷ {span_days:,} day'
                    f'{"s" if span_days != 1 else ""} selected</div>',
                    unsafe_allow_html=True
                )

        st.write("")

        # ==========================================
        # STEP 2: PARAMETER SELECTION
        # ==========================================

        with st.container(border=True):

            card_title("2. Select parameter", "Pick the measurement to analyse")

            default_param = (
                st.session_state.selected_parameter
                if st.session_state.selected_parameter in parameter_columns
                else parameter_columns[0]
            )

            chosen_param = st.pills(
                "Parameter",
                options=parameter_columns,
                format_func=lambda c: info[c]["label"],
                default=default_param,
                key="unified_parameter_pills",
                label_visibility="collapsed"
            )

            chosen_param = chosen_param or default_param

        st.write("")

        # ==========================================
        # STEP 3: 3-SIGMA OUTLIER SETUP
        # ==========================================

        with st.container(border=True):

            card_title(
                "3. Configure outlier detection",
                "3\u03c3 outliers are flagged against the mean and standard "
                "deviation within each time-of-day bucket. The threshold is "
                "fixed at 3\u03c3 \u2014 only the bucket size is adjustable."
            )

            # Minute Bucket Size
            st.caption(
                "Fixed-width time-of-day bucket spanning 24 hours. "
                "Higher values group readings more coarsely."
            )

            chosen_interval = st.number_input(
                "⏱️  MINUTE BUCKET SIZE",
                min_value=1,
                max_value=600,
                value=int(st.session_state.min_interval) if 1 <= st.session_state.min_interval <= 600 else 10,
                step=1,
                key="unified_min_interval"
            )

            slots_per_day = max(1, round(1440 / chosen_interval))

            st.markdown(
                f'<div class="bucket-badge">🪣 {slots_per_day} slots per day</div>'
                f'<div class="sigma-badge">🔒 {SIGMA_THRESHOLD}\u03c3 threshold (fixed)</div>',
                unsafe_allow_html=True
            )

            # Sigma threshold is fixed at 3.0 and is not user-adjustable.
            chosen_threshold = SIGMA_THRESHOLD

        st.write("")

        if start_day > end_day:
            st.error("The start date is after the end date.")
        elif st.button("Continue →", type="primary", key="unified_setup_continue", use_container_width=True):
            st.session_state.start_date = start_day
            st.session_state.end_date = end_day
            st.session_state.selected_parameter = chosen_param
            st.session_state.parameter_confirmed = True
            st.session_state.date_range_confirmed = True
            st.session_state.group_by = "Min"
            st.session_state.min_interval = chosen_interval
            st.session_state.sigma_threshold = SIGMA_THRESHOLD
            st.session_state.grouping_confirmed = True
            st.rerun()

    with setup_right:

        with st.container(border=False):

            card_title("File info", "")

            st.caption(f"Records: {len(df):,}")
            st.caption(f"Parameters: {len(parameter_columns)}")
            st.caption(f"Available: {first_day}")
            st.caption(f"to {last_day}")

            st.write("")

            card_title("Configuration", "")

            default_param = (
                st.session_state.selected_parameter
                if st.session_state.selected_parameter in parameter_columns
                else parameter_columns[0]
            )

            st.caption(f"Parameter: {info[default_param]['label']}")
            st.caption(f"Bucket: {chosen_interval} min → {slots_per_day} slots/day")
            st.caption(f"Threshold: {SIGMA_THRESHOLD}σ (fixed)")

    st.stop()


# ==========================================
# 5. QUALITY CHECKS
# ==========================================

gaps = df["Timestamp"].sort_values().diff().dropna()

if len(gaps) > 0 and gaps.mode().shape[0] > 0:
    expected_interval = gaps.mode().iloc[0]
else:
    expected_interval = pd.Timedelta(minutes=10)

expected_minutes = expected_interval.total_seconds() / 60

df["Time_Difference"] = df["Timestamp"].diff()

irregular_intervals = (
    df["Time_Difference"].notna()
    &
    (df["Time_Difference"] != expected_interval)
)


missing_values = df[parameter_columns].isnull().sum()

total_missing = int(missing_values.sum())


duplicate_rows = int(
    df.duplicated(subset=original_columns).sum()
)


physical_rows = []

invalid_row = pd.Series(False, index=df.index)


for column in parameter_columns:

    low = info[column]["min"]
    high = info[column]["max"]

    if low is None:
        continue

    bad = ((df[column] < low) | (df[column] > high)).fillna(False)

    invalid_row = invalid_row | bad

    physical_rows.append({
        "Parameter": info[column]["label"],
        "Valid range": f"{low:g} to {high:g} {info[column]['unit']}".strip(),
        "Violations": int(bad.sum())
    })


total_invalid = int(invalid_row.sum())


sigma_rows = []

total_outliers = 0

for column in parameter_columns:

    if not info[column]["sigma"]:

        sigma_rows.append({
            "Parameter": info[column]["label"],
            "Lowest limit": None,
            "Highest limit": None,
            "Outliers": 0,
            "Note": "skipped"
        })

        continue

    grouped_stats = df.groupby(group_by)[column].agg(["mean", "std"])

    row_mean = df[group_by].map(grouped_stats["mean"])

    row_std = df[group_by].map(grouped_stats["std"])

    sigma = SIGMA_THRESHOLD

    lower_limit = row_mean - sigma * row_std

    upper_limit = row_mean + sigma * row_std

    outliers = (
        (df[column] < lower_limit)
        |
        (df[column] > upper_limit)
    ).fillna(False)

    total_outliers = total_outliers + int(outliers.sum())

    sigma_rows.append({
        "Parameter": info[column]["label"],
        "Lowest limit": round(lower_limit.min(), 2)
        if lower_limit.notna().any() else None,
        "Highest limit": round(upper_limit.max(), 2)
        if upper_limit.notna().any() else None,
        "Outliers": int(outliers.sum()),
        "Note": ""
    })


df["Quality_Flag"] = "GOOD"


df.loc[irregular_intervals, "Quality_Flag"] = "TIME_ERROR"

df.loc[
    df.duplicated(subset=original_columns, keep=False),
    "Quality_Flag"
] = "DUPLICATE"

df.loc[
    df[parameter_columns].isnull().any(axis=1),
    "Quality_Flag"
] = "MISSING"

df.loc[invalid_row, "Quality_Flag"] = "INVALID"


total_records = len(df)

good_records = int((df["Quality_Flag"] == "GOOD").sum())

flagged_records = total_records - good_records

good_percentage = round(good_records / total_records * 100, 1)


# ==========================================
# 5. SET UP VARIABLES
# ==========================================

parameter = st.session_state.selected_parameter

page = st.session_state.selected_page

data_filter = "All data"

if page == "Dashboard":

    data_filter = "All data"

elif page == "Filtered Data":

    data_filter = "Good data only"

else:

    data_filter = "Good data only"

unit = info[parameter]["unit"]

label = info[parameter]["label"]


if page == "Dashboard":
    st.title("Observatory Data Dashboard")

elif page == "Filtered Data":
    st.title("Filtered Data")

elif page == "Detailed Breakdown":
    st.title("Detailed Breakdown")


# ==========================================
# 6. SET DATE RANGE FROM SESSION STATE
# ==========================================

if page in ("Dashboard", "Filtered Data"):

    start_day = st.session_state.start_date
    end_day = st.session_state.end_date

    in_range = (
        (df["Timestamp"].dt.date >= start_day)
        &
        (df["Timestamp"].dt.date <= end_day)
    )

    dated = df[in_range]

    if data_filter == "Good data only":
        view = dated[dated["Quality_Flag"] == "GOOD"]

    elif data_filter == "Flagged data only":
        view = dated[dated["Quality_Flag"] != "GOOD"]

    else:
        view = dated


# ==========================================
# CHART BLOCK
# ==========================================

def draw_charts(data, subtitle, quality_section=None):
    """Draw the six charts for whichever set of records is passed in.
    quality_section: optional zero-arg callable rendered right after the
    Overview section (used by the Filtered Data page to show the
    collapsible data-quality breakdown in that specific spot).
    """

    # Work on a copy so we never modify a slice of the main dataframe
    data = data.copy()

    section("Overview")

    main_left, main_right = st.columns([2, 1])

    with main_left:

        with st.container(border=False):

            card_title(
                label + " over time",
                subtitle
            )

            trend_data = data[["Timestamp", parameter]].dropna()

            trend_figure = go.Figure()

            trend_figure.add_trace(
                go.Scatter(
                    x=trend_data["Timestamp"],
                    y=trend_data[parameter],
                    mode="lines",
                    line=dict(color=ACCENT_2, width=1.2),
                    fill="tozeroy",
                    fillcolor="rgba(34, 211, 238, 0.10)",
                    name=label
                )
            )

            trend_figure.update_layout(
                yaxis_title=unit,
                **chart_layout(height=320)
            )

            st.plotly_chart(
                trend_figure,
                width="stretch"
            )

            chart_stats(trend_data[parameter], " " + unit)

    data["datetime"] = data["Timestamp"].dt.floor("h")
    data_h = (
        data.groupby("datetime")
        .mean(numeric_only=True)
        .reset_index()
    )
    data_h["hour"] = data_h["datetime"].dt.hour
    data_h["Day"] = data_h["datetime"].dt.date
    data_h["Month"] = data_h["datetime"].dt.month

    section("Temporal patterns")

    pattern1, pattern2, pattern3 = st.columns(3)

    with pattern1:

        with st.container(border=False):

            card_title(
                "Diurnal",
                "Average variation by hour of day • shaded band = ±1 standard deviation"
            )

            hourly = (
                data_h.groupby("hour")[parameter]
                .agg(["mean", "std"])
                .reset_index()
            )

            all_hours = pd.DataFrame({
                "hour": range(24)
            })

            hourly = all_hours.merge(
                hourly,
                on="hour",
                how="left"
            )

            diurnal_figure = go.Figure()

            diurnal_figure.add_trace(
                go.Scatter(
                    x=list(hourly["hour"]) +
                      list(hourly["hour"][::-1]),

                    y=list(hourly["mean"] + hourly["std"]) +
                      list((hourly["mean"] - hourly["std"])[::-1]),

                    fill="toself",

                    fillcolor="rgba(99, 102, 241, 0.15)",

                    line=dict(
                        color="rgba(0,0,0,0)"
                    ),

                    hoverinfo="skip",

                    showlegend=False
                )
            )

            diurnal_figure.add_trace(
                go.Scatter(
                    x=hourly["hour"],
                    y=hourly["mean"],

                    mode="lines+markers",

                    line=dict(
                        color=ACCENT,
                        width=2.5,
                        shape="spline"
                    ),

                    marker=dict(
                        size=5
                    ),

                    name="Hourly Mean"
                )
            )

            diurnal_figure.update_layout(

                xaxis=dict(
                    title="Hour of Day",

                    tickmode="array", tickangle=0,

                    tickvals=list(range(24)),

                    ticktext=[
                        str(i)
                        for i in range(1, 25)
                    ],

                    range=[-0.5, 23.5],

                    gridcolor=GRID,

                    zeroline=False
                ),

                yaxis=dict(
                    title=f"{parameter} ({unit})",
                    gridcolor=GRID,
                    zeroline=False
                ),

                **{
                    key: value
                    for key, value in chart_layout().items()
                    if key not in ["xaxis", "yaxis"]
                }
            )

            st.plotly_chart(
                diurnal_figure,
                width="stretch"
            )

            chart_stats(
                data_h[parameter].dropna(),
                " " + unit
            )

        with pattern2:

            with st.container(border=False):

                card_title("Daily", "Mean per day • shaded band = ±1 standard deviation")

                daily = data_h.groupby("Day")[parameter].agg(
                    ["mean", "std"]
                ).reset_index()

                daily["std"] = daily["std"].fillna(0)

                daily["Day"] = pd.to_datetime(daily["Day"])

                daily_figure = go.Figure()

                daily_figure.add_trace(
                    go.Scatter(
                        x=list(daily["Day"]) + list(daily["Day"][::-1]),
                        y=list(daily["mean"] + daily["std"])
                        + list((daily["mean"] - daily["std"])[::-1]),
                        fill="toself",
                        fillcolor="rgba(167, 139, 250, 0.15)",
                        line=dict(color="rgba(0,0,0,0)"),
                        hoverinfo="skip"
                    )
                )

                daily_figure.add_trace(
                    go.Scatter(
                        x=daily["Day"],
                        y=daily["mean"],
                        mode="lines",
                        line=dict(color=ACCENT_3, width=2)
                    )
                )

                daily_figure.update_layout(**chart_layout())

                st.plotly_chart(
                    daily_figure,
                    width="stretch"
                )
                chart_stats(
                    data_h[parameter].dropna(),
                    " " + unit
                )

        with pattern3:

            with st.container(border=False):

                card_title("Monthly", "Average per month")

                monthly = data_h.groupby("Month")[parameter].mean().reset_index()

                month_names = {
                    1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr",
                    5: "May", 6: "Jun", 7: "Jul", 8: "Aug",
                    9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"
                }

                monthly["Name"] = monthly["Month"].map(month_names)

                monthly_figure = go.Figure()

                monthly_figure.add_trace(
                    go.Bar(
                        x=monthly["Name"],
                        y=monthly[parameter],
                        marker=dict(
                            color=monthly[parameter],
                            colorscale=[[0, "#312E81"], [1, ACCENT_2]],
                            line=dict(width=0)
                        ),
                        hovertemplate="%{x}: %{y:.1f}<extra></extra>"
                    )
                )

                monthly_figure.update_layout(
                    bargap=0.35,
                    **chart_layout()
                )

                st.plotly_chart(
                    monthly_figure,
                    width="stretch"
                )

            chart_stats(
                data_h[parameter].dropna(),
                " " + unit
            )

    section("Distribution")

    speed_column = None
    direction_column = None

    for column in parameter_columns:
        if info[column]["kind"] == "wind_speed":
            speed_column = column
        elif info[column]["kind"] == "wind_direction":
            direction_column = column

    show_wind = (
        speed_column is not None
        and direction_column is not None
        and parameter in (speed_column, direction_column)
    )

    if show_wind:
        detail1, detail2 = st.columns(2)
    else:
        detail1 = st.columns(1)[0]

    with detail1:

        with st.container(border=False):

            card_title("Seasonal", "Spread within each season")

            season_order = [
                "Winter", "Spring", "Summer-Monsoon", "Autumn"
            ]

            seasons_present = [
                season
                for season in season_order
                if season in data["Season"].values
            ]

            seasonal_figure = px.box(
                data,
                x="Season",
                y=parameter,
                color="Season",
                category_orders={"Season": seasons_present},
                color_discrete_sequence=[
                    "#22D3EE", "#34D399", "#FBBF24", "#F472B6"
                ]
            )

            seasonal_figure.update_traces(
                marker=dict(size=3),
                line=dict(width=1.5)
            )

            seasonal_figure.update_layout(**chart_layout())

            st.plotly_chart(
                seasonal_figure,
                width="stretch"
            )

            chart_stats(data_h[parameter], " " + unit)


    if show_wind:

        with detail2:

            with st.container(border=False):

                card_title("Wind rose", "Direction and speed frequency")

                wind = data[[speed_column, direction_column]].dropna()

                wind = wind[
                    (wind[direction_column] >= 0)
                    &
                    (wind[direction_column] < 360)
                    &
                    (wind[speed_column] >= 0)
                ].copy()

                if len(wind) > 0:

                    wind["Sector"] = (
                        (wind[direction_column] + 11.25) // 22.5 % 16
                    ) * 22.5

                    wind["Band"] = pd.cut(
                        wind[speed_column],
                        bins=[0, 2, 4, 6, 8, 100],
                        labels=["0–2", "2–4", "4–6", "6–8", "8+"],
                        right=False
                    )

                    rose_data = wind.groupby(
                        ["Sector", "Band"],
                        observed=True
                    ).size().reset_index(name="Count")

                    wind_figure = px.bar_polar(
                        rose_data,
                        r="Count",
                        theta="Sector",
                        color="Band",
                        color_discrete_sequence=[
                            "#1E3A8A", "#3B82F6", "#22D3EE", "#A78BFA", "#F472B6"
                        ]
                    )

                    wind_figure.update_layout(
                        polar=dict(
                            bgcolor="rgba(0,0,0,0)",
                            radialaxis=dict(
                                showticklabels=False,
                                gridcolor=GRID
                            ),
                            angularaxis=dict(gridcolor=GRID)
                        ),
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=-0.15,
                            font=dict(size=9)
                        ),
                        **chart_layout(legend=True)
                    )

                    st.plotly_chart(
                        wind_figure,
                        width="stretch"
                    )

                    chart_stats(wind[speed_column], " m/s")

                else:

                    st.info("No valid wind data.")

    if quality_section is not None:
        quality_section()


# ==========================================
# PAGE 1 - DASHBOARD
# ==========================================

if page == "Dashboard":

    show_controls_panel()

    if st.button("\u2190 Choose a view", key="dashboard_back_to_page_selection"):
        st.session_state.page_confirmed = False
        st.session_state.date_range_confirmed = False
        st.session_state.parameter_confirmed = False
        st.session_state.grouping_confirmed = False
        st.rerun()

    if view.empty:

        st.warning("No records match this filter.")

        st.stop()

    with st.container(border=False):

        card_title(
            "Detected columns",
            "How each column in this file is being read"
        )

        st.dataframe(
            pd.DataFrame({
                "Column": parameter_columns,
                "Read as": [info[c]["label"] for c in parameter_columns],
                "Unit": [info[c]["unit"] or "-" for c in parameter_columns]
            }),
            width="stretch",
            hide_index=True
        )

    card_title("Parameter", "Click a parameter to switch what's charted below")

    clicked_parameter = st.pills(
        "Parameter",
        options=parameter_columns,
        format_func=lambda c: info[c]["label"],
        default=parameter,
        key="dashboard_parameter_pills",
        label_visibility="collapsed"
    )

    if clicked_parameter and clicked_parameter != parameter:
        st.session_state.selected_parameter = clicked_parameter
        st.rerun()

    draw_charts(
        view,
        f"{len(view):,} records • {start_day} to {end_day} • {data_filter.lower()}"
    )


# ==========================================
# PAGE 2 - FILTERED DATA
# ==========================================

elif page == "Filtered Data":

    show_controls_panel()

    if st.button("\u2190 Back to setup", key="filtered_back_to_setup"):
        st.session_state.date_range_confirmed = False
        st.session_state.parameter_confirmed = False
        st.session_state.grouping_confirmed = False
        st.rerun()

    clean = dated[dated["Quality_Flag"] == "GOOD"]

    if clean.empty:

        st.warning("No records passed the quality checks.")

        st.stop()

    removed = len(dated) - len(clean)

    st.caption(
        f"{len(clean):,} of {len(dated):,} records in the selected dates "
        f"passed every check. {removed:,} removed."
    )

    clean1, clean2, clean3, clean4 = st.columns(4)

    clean1.metric("Clean records", f"{len(clean):,}")

    clean2.metric("Removed", f"{removed:,}")

    clean3.metric(
        "Data quality",
        f"{round(len(clean) / len(dated) * 100, 1) if len(dated) else 0}%"
    )

    clean4.metric(
        label + " avg",
        f"{clean[parameter].mean():.1f} {unit}"
    )

    st.markdown(
        '<div class="chart-stats">'
        f'<span><b>missing</b> {total_missing}</span>'
        f'<span><b>duplicates</b> {duplicate_rows}</span>'
        f'<span><b>invalid</b> {total_invalid}</span>'
        f'<span><b>time errors</b> {int(irregular_intervals.sum())}</span>'
        '</div>',
        unsafe_allow_html=True
    )

    # ==========================================
    # DATA QUALITY BREAKDOWN (WITH TIME_ERROR)
    # ==========================================

    flag_order = ["GOOD", "MISSING", "DUPLICATE", "INVALID", "TIME_ERROR"]

    flag_counts = (
        dated["Quality_Flag"]
        .value_counts()
        .reindex(flag_order)
        .fillna(0)
        .astype(int)
    )

    flag_counts_present = flag_counts[flag_counts > 0]

    def _flag_table_card(title, subtitle, flag_name, accent):

        table = dated[dated["Quality_Flag"] == flag_name][
            ["Timestamp"] + parameter_columns
        ]

        with st.container(border=False):

            st.markdown(
                f'<div class="card-title">'
                f'<span style="display:inline-block;width:8px;height:8px;'
                f'border-radius:50%;background:{accent};margin-right:7px;">'
                f'</span>{title}</div>'
                f'<div class="card-sub">{subtitle}</div>',
                unsafe_allow_html=True
            )

            if table.empty:

                st.caption(f"No {title.lower()} in this date range.")

            else:

                st.dataframe(
                    table,
                    width="stretch",
                    hide_index=True,
                    height=min(38 * (len(table) + 1), 240)
                )

    def render_quality_breakdown():

        with st.expander("🔍 Data quality breakdown", expanded=False):

            with st.container(border=False):

                card_title(
                    "Flag distribution",
                    f"{len(dated):,} records in the selected dates, before filtering"
                )

                if flag_counts_present.empty:

                    st.info("No records in this date range.")

                else:

                    pie_figure = go.Figure(data=[
                        go.Pie(
                            labels=flag_counts_present.index,
                            values=flag_counts_present.values,
                            marker=dict(
                                colors=[
                                    FLAG_COLORS[f] for f in flag_counts_present.index
                                ]
                            ),
                            hole=0.55,
                            textinfo="percent+label",
                            textfont=dict(size=11),
                            sort=False
                        )
                    ])

                    pie_figure.update_layout(**chart_layout(height=300, legend=True))

                    st.plotly_chart(pie_figure, width="stretch")

            st.write("")

            grid_row1_left, grid_row1_right = st.columns(2)

            with grid_row1_left:
                _flag_table_card(
                    "Missing records",
                    f"{int(flag_counts.get('MISSING', 0)):,} rows with at least one missing value",
                    "MISSING",
                    FLAG_COLORS["MISSING"]
                )

            with grid_row1_right:
                _flag_table_card(
                    "Duplicate records",
                    f"{int(flag_counts.get('DUPLICATE', 0)):,} duplicate rows",
                    "DUPLICATE",
                    FLAG_COLORS["DUPLICATE"]
                )

            st.write("")

            grid_row2_left, grid_row2_right = st.columns(2)

            with grid_row2_left:
                _flag_table_card(
                    "Invalid records",
                    f"{int(flag_counts.get('INVALID', 0)):,} rows outside physical limits",
                    "INVALID",
                    FLAG_COLORS["INVALID"]
                )

            with grid_row2_right:
                _flag_table_card(
                    "Time errors",
                    f"{int(flag_counts.get('TIME_ERROR', 0)):,} rows with broken intervals",
                    "TIME_ERROR",
                    FLAG_COLORS["TIME_ERROR"]
                )

            st.write("")

            grid_row3_left, grid_row3_right = st.columns(2)

            with grid_row3_left:
                _flag_table_card(
                    "Good records",
                    f"{int(flag_counts.get('GOOD', 0)):,} rows that passed every check",
                    "GOOD",
                    FLAG_COLORS["GOOD"]
                )

    draw_charts(
        clean,
        f"{len(clean):,} records • {start_day} to {end_day} • quality checks passed",
        quality_section=render_quality_breakdown
    )


# ==========================================
# PAGE 3 - DETAILED BREAKDOWN
# ==========================================

elif page == "Detailed Breakdown":

    show_controls_panel()

    if st.button("\u2190 Back to setup", key="breakdown_back_to_setup"):
        st.session_state.date_range_confirmed = False
        st.session_state.parameter_confirmed = False
        st.session_state.grouping_confirmed = False
        st.rerun()

    st.caption(
        label + " broken down by day-of-month, hour-of-day, the full-record "
        "trend, and monthly/seasonal statistics. Always uses the complete "
        "file, regardless of any date filter set on the other pages."
    )

    breakdown_base = df[
        ["Timestamp", "Day", "Month", "Hour", "Season", parameter]
    ].dropna()

    if breakdown_base.empty:

        st.warning("No valid records for this parameter.")

        st.stop()


    section("By day of month")

    st.caption(
        "Every calendar month, combined across all years present in the "
        "file • x-axis is the day of the month"
    )

    render_legend_row([
        (ACCENT, "\u2014", "daily min"),
        (ACCENT_2, "\u2504", "daily max"),
        (ACCENT_3, "\u00b7", "hourly"),
        ("#EF4444", "\u2014", "daily mean ± std")
    ])

    dom_cols_per_row = 3

    for row_start in range(0, 12, dom_cols_per_row):

        row_cols = st.columns(dom_cols_per_row)

        for offset, col in enumerate(row_cols):

            m = row_start + offset + 1

            with col:

                with st.container(border=False):

                    month_df = breakdown_base[breakdown_base["Month"] == m]

                    card_title(MONTH_NAMES[m])

                    if month_df.empty:

                        st.caption("no data")

                        continue

                    day_of_month = month_df["Timestamp"].dt.day

                    daily_stats = (
                        month_df
                        .assign(DOM=day_of_month)
                        .groupby("DOM")[parameter]
                        .agg(["mean", "min", "max", "std"])
                        .reset_index()
                    )

                    dom_figure = go.Figure()

                    dom_figure.add_trace(go.Scatter(
                        x=day_of_month,
                        y=month_df[parameter],
                        mode="markers",
                        marker=dict(size=3, color=ACCENT_3, opacity=0.35),
                        name="hourly",
                        hoverinfo="skip"
                    ))

                    dom_figure.add_trace(go.Scatter(
                        x=daily_stats["DOM"],
                        y=daily_stats["min"],
                        mode="lines",
                        line=dict(color=ACCENT, width=1.3),
                        name="daily min"
                    ))

                    dom_figure.add_trace(go.Scatter(
                        x=daily_stats["DOM"],
                        y=daily_stats["max"],
                        mode="lines",
                        line=dict(color=ACCENT_2, width=1.3, dash="dot"),
                        name="daily max"
                    ))

                    dom_figure.add_trace(go.Scatter(
                        x=daily_stats["DOM"],
                        y=daily_stats["mean"],
                        mode="lines",
                        line=dict(color="#EF4444", width=2),
                        error_y=dict(
                            type="data",
                            array=daily_stats["std"].fillna(0),
                            visible=True,
                            color="#EF4444",
                            thickness=1,
                            width=0
                        ),
                        name="daily mean"
                    ))

                    dom_figure.update_layout(**chart_layout(height=220))

                    dom_figure.update_xaxes(dtick=5, title_text=None)

                    month_mean = month_df[parameter].mean()
                    month_std = month_df[parameter].std()
                    month_count = len(month_df)

                    add_stats_annotation(
                        dom_figure,
                        f"{month_mean:.1f}±{month_std:.1f}<br>"
                        f"count:{month_count}"
                    )

                    st.plotly_chart(dom_figure, width="stretch")


    section("By hour of day")

    st.caption(
        "Every calendar month, combined across all years present in the "
        "file • x-axis is the hour of the day"
    )

    render_legend_row([
        ("#10B981", "\u25bc", "diur min"),
        ("#10B981", "\u25b2", "diur max"),
        ("#EF4444", "\u2014", "diur mean ± std")
    ])

    diurnal_cols_per_row = 3

    for row_start in range(0, 12, diurnal_cols_per_row):

        row_cols = st.columns(diurnal_cols_per_row)

        for offset, col in enumerate(row_cols):

            m = row_start + offset + 1

            with col:

                with st.container(border=False):

                    month_df = breakdown_base[breakdown_base["Month"] == m]

                    card_title(MONTH_NAMES[m])

                    if month_df.empty:

                        st.caption("no data")

                        continue

                    hourly_stats = (
                        month_df
                        .groupby("Hour")[parameter]
                        .agg(["mean", "min", "max", "std"])
                        .reset_index()
                    )

                    diurnal_figure = go.Figure()

                    diurnal_figure.add_trace(go.Scatter(
                        x=hourly_stats["Hour"],
                        y=hourly_stats["min"],
                        mode="lines+markers",
                        line=dict(color="#10B981", width=1.3),
                        marker=dict(size=5, symbol="triangle-down"),
                        name="diur min"
                    ))

                    diurnal_figure.add_trace(go.Scatter(
                        x=hourly_stats["Hour"],
                        y=hourly_stats["max"],
                        mode="lines+markers",
                        line=dict(color="#10B981", width=1.3),
                        marker=dict(size=5, symbol="triangle-up"),
                        name="diur max"
                    ))

                    diurnal_figure.add_trace(go.Scatter(
                        x=hourly_stats["Hour"],
                        y=hourly_stats["mean"],
                        mode="lines+markers",
                        line=dict(color="#EF4444", width=2),
                        marker=dict(size=4),
                        error_y=dict(
                            type="data",
                            array=hourly_stats["std"].fillna(0),
                            visible=True,
                            color="#EF4444",
                            thickness=1,
                            width=0
                        ),
                        name="diur mean"
                    ))

                    diurnal_figure.update_layout(**chart_layout(height=220))

                    diurnal_figure.update_xaxes(dtick=6, title_text=None)

                    month_mean = month_df[parameter].mean()
                    month_std = month_df[parameter].std()
                    month_count = len(month_df)

                    add_stats_annotation(
                        diurnal_figure,
                        f"{month_mean:.1f}±{month_std:.1f}<br>"
                        f"count:{month_count}"
                    )

                    st.plotly_chart(diurnal_figure, width="stretch")


    section("Full record overview")

    with st.container(border=False):

        card_title(
            label + " — entire dataset",
            "Hourly and daily means with monthly min / mean / max"
        )

        daily_means = breakdown_base.groupby("Day")[parameter].mean().reset_index()

        daily_means["Day"] = pd.to_datetime(daily_means["Day"])

        month_periods = breakdown_base["Timestamp"].dt.to_period("M")

        monthly_stats = (
            breakdown_base
            .groupby(month_periods)[parameter]
            .agg(["mean", "min", "max", "std"])
            .reset_index()
        )

        monthly_stats["Timestamp"] = monthly_stats["Timestamp"].dt.to_timestamp()

        overview_figure = go.Figure()

        overview_figure.add_trace(go.Scatter(
            x=breakdown_base["Timestamp"],
            y=breakdown_base[parameter],
            mode="markers",
            marker=dict(size=2, color=ACCENT_3, opacity=0.25),
            name="hourly",
            hoverinfo="skip"
        ))

        overview_figure.add_trace(go.Scatter(
            x=daily_means["Day"],
            y=daily_means[parameter],
            mode="markers",
            marker=dict(size=3, color="#111827", opacity=0.55),
            name="daily mean"
        ))

        overview_figure.add_trace(go.Scatter(
            x=monthly_stats["Timestamp"],
            y=monthly_stats["max"],
            mode="lines+markers",
            line=dict(color=ACCENT, width=1.5),
            marker=dict(size=4),
            name="monthly max"
        ))

        overview_figure.add_trace(go.Scatter(
            x=monthly_stats["Timestamp"],
            y=monthly_stats["min"],
            mode="lines+markers",
            line=dict(color=ACCENT, width=1.5, dash="dot"),
            marker=dict(size=4),
            name="monthly min"
        ))

        overview_figure.add_trace(go.Scatter(
            x=monthly_stats["Timestamp"],
            y=monthly_stats["mean"],
            mode="lines+markers",
            line=dict(color="#EF4444", width=2.5),
            marker=dict(size=5),
            error_y=dict(
                type="data",
                array=monthly_stats["std"].fillna(0),
                visible=True,
                color="#EF4444",
                thickness=1.3
            ),
            name="monthly mean"
        ))

        overview_figure.update_layout(
            **chart_layout(height=380, legend=True)
        )

        overview_figure.update_xaxes(tickformat="%b\n%Y")

        overview_figure.update_yaxes(title_text=unit)

        overall_mean = breakdown_base[parameter].mean()
        overall_std = breakdown_base[parameter].std()
        overall_count = len(breakdown_base)

        add_stats_annotation(
            overview_figure,
            f"{overall_mean:.1f}±{overall_std:.1f}<br>"
            f"count:{overall_count}"
        )

        st.plotly_chart(overview_figure, width="stretch")


    section("Monthly & seasonal statistics")

    def _col_label(text):
        return f"{text} ({unit})" if unit else text

    def _period_stats(subset):

        events = len(subset)

        avg = subset[parameter].mean()

        std = subset[parameter].std()

        diurnal_means = subset.groupby("Hour")[parameter].mean()

        diurnal_amplitude = (
            diurnal_means.max() - diurnal_means.min()
            if len(diurnal_means) > 0 else float("nan")
        )

        v_min = subset[parameter].min()

        v_max = subset[parameter].max()

        percent_var = (std * 100 / avg) if avg else float("nan")

        return {
            "Events": events,
            _col_label("Avg ± Std"): f"{avg:.1f} ± {std:.1f}",
            _col_label("Diu Amp"): (
                round(diurnal_amplitude, 1)
                if pd.notna(diurnal_amplitude) else None
            ),
            _col_label("Min"): round(v_min, 1),
            _col_label("Max"): round(v_max, 1),
            "%Var": round(percent_var, 0) if pd.notna(percent_var) else None
        }

    stats_rows = []

    for m in range(1, 13):

        subset = breakdown_base[breakdown_base["Month"] == m]

        if subset.empty:
            continue

        stats_rows.append({"Period": MONTH_NAMES[m], **_period_stats(subset)})

    season_order = ["Winter", "Spring", "Summer-Monsoon", "Autumn"]

    season_labels = {
        "Winter": "DJF", "Spring": "MAM",
        "Summer-Monsoon": "JJA", "Autumn": "SON"
    }

    for season in season_order:

        subset = breakdown_base[breakdown_base["Season"] == season]

        if subset.empty:
            continue

        stats_rows.append({
            "Period": season_labels[season],
            **_period_stats(subset)
        })

    stats_rows.append({
        "Period": "Annual",
        **_period_stats(breakdown_base)
    })

    stats_table = pd.DataFrame(stats_rows)

    st.dataframe(
        stats_table,
        width="stretch",
        hide_index=True,
        height=min(38 * (len(stats_table) + 1), 640)
    )

    st.caption(
        "Diu Amp = difference between the highest and lowest diurnal "
        "(hour-of-day) mean within the period • %Var = std × 100 / avg"
    )