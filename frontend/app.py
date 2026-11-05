import html
import importlib
import math
import sys
from contextlib import ExitStack
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import geopandas as gpd
import pytz
import streamlit as st
import streamlit.components.v1 as components

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from config import CAMPUS_POINT, CAMPUS_RADIUS, DATA_DIR

fetch_graph = importlib.import_module("scripts.01_fetch_graph")
fetch_buildings = importlib.import_module("scripts.02_fetch_buildings")
fetch_trees = importlib.import_module("scripts.03_fetch_trees")
project_shadows = importlib.import_module("scripts.05_project_shadows")
apply_shade = importlib.import_module("scripts.06_apply_shade")
calculate_weights = importlib.import_module("scripts.07_calculate_heat_score")
route_finder = importlib.import_module("scripts.08_route_finder")
route_visualizer = importlib.import_module("scripts.09_visualize_route")
sun_position = importlib.import_module("scripts.sun_position")

IST = pytz.timezone("Asia/Kolkata")

st.set_page_config(
    page_title="ShadeRoute | Campus route planner",
    page_icon="🌤️",
    layout="wide",
)

header_col, theme_col = st.columns([5, 1], vertical_alignment="center")
with theme_col:
    theme_mode = st.segmented_control(
        "Appearance",
        options=["Light", "Dark"],
        default="Light",
        label_visibility="collapsed",
        key="theme_mode",
    )

if theme_mode == "Dark":
    page_bg = "#101714"
    surface_bg = "#17211c"
    field_bg = "#111a16"
    primary_text = "#edf5ef"
    secondary_text = "#a9b9ae"
    border_color = "#2b3931"
    accent = "#70d6a5"
    soft_accent = "#1e382b"
    shadow = "0 16px 38px rgba(0, 0, 0, .22)"
else:
    page_bg = "#f3f6f2"
    surface_bg = "#ffffff"
    field_bg = "#fbfdfb"
    primary_text = "#18271f"
    secondary_text = "#63746a"
    border_color = "#dfe7df"
    accent = "#147a55"
    soft_accent = "#eaf4ed"
    shadow = "0 14px 34px rgba(27, 55, 39, .07)"

st.markdown(
    f"""
    <style>
    :root {{
        color-scheme: {"dark" if theme_mode == "Dark" else "light"};
        --page-bg: {page_bg};
        --surface-bg: {surface_bg};
        --field-bg: {field_bg};
        --primary-text: {primary_text};
        --secondary-text: {secondary_text};
        --border-color: {border_color};
        --accent: {accent};
        --soft-accent: {soft_accent};
    }}
    .stApp, [data-testid="stAppViewContainer"] {{
        background: var(--page-bg);
        color: var(--primary-text);
    }}
    [data-testid="stHeader"] {{ background: transparent; }}
    .block-container {{ max-width: 1120px; padding: 2.2rem 2rem 4rem; }}
    .hero {{
        position: relative; overflow: hidden;
        padding: 1.8rem 2rem; border: 1px solid {border_color};
        border-radius: 22px; color: {primary_text}; background: {surface_bg};
        box-shadow: {shadow};
    }}
    .hero::after {{
        content: ""; position: absolute; width: 220px; height: 220px;
        right: -54px; top: -110px; border-radius: 50%;
        background: radial-gradient(circle, {soft_accent}, transparent 70%);
    }}
    .hero-kicker {{
        margin: 0 0 .45rem; color: {accent}; font-size: .73rem;
        font-weight: 750; letter-spacing: .16em; text-transform: uppercase;
    }}
    .hero h1 {{ margin: 0; color: {primary_text}; font-size: 2.35rem; letter-spacing: -.045em; }}
    .hero p {{ margin: .5rem 0 0; color: {secondary_text}; font-size: 1rem; }}
    [data-testid="stSegmentedControl"] {{
        padding: .3rem; border: 1px solid var(--border-color);
        border-radius: 13px; background: var(--surface-bg);
    }}
    [role="radiogroup"][aria-label="Appearance"] [role="radio"] {{
        border: 1px solid transparent; border-radius: 9px;
        background: var(--surface-bg); color: var(--secondary-text);
    }}
    [role="radiogroup"][aria-label="Appearance"] [role="radio"][aria-checked="true"] {{
        border-color: var(--accent) !important;
        background: var(--soft-accent) !important;
        color: var(--accent) !important;
    }}
    [data-testid="stForm"] {{
        padding: 1.5rem 1.6rem; border: 1px solid var(--border-color);
        border-radius: 20px; background: var(--surface-bg); box-shadow: {shadow};
    }}
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stCaptionContainer"] {{ color: var(--secondary-text); }}
    [data-testid="stMarkdownContainer"] h3 {{
        margin: 1.2rem 0 .9rem; padding-bottom: .55rem;
        border-bottom: 1px solid var(--border-color);
        color: var(--primary-text); font-size: 1.08rem; letter-spacing: -.015em;
    }}
    [data-testid="stWidgetLabel"] p {{ color: var(--secondary-text); font-weight: 550; }}
    [data-testid="stNumberInputContainer"],
    [data-testid="stDateInputField"],
    [data-testid="stTimeInputTimeDisplay"] {{
        border: 1px solid var(--border-color) !important;
        border-radius: 11px !important;
        background: var(--field-bg) !important;
        color: var(--primary-text) !important;
    }}
    [data-testid="stNumberInputContainer"] input {{
        background: transparent !important;
        color: var(--primary-text) !important;
    }}
    [data-testid="stNumberInputStepDown"],
    [data-testid="stNumberInputStepUp"],
    [data-testid="stDateInputCalendarButton"] {{
        background: transparent !important;
        color: var(--secondary-text) !important;
    }}
    div[data-baseweb="input"] > div,
    div[data-baseweb="select"] > div {{
        border-color: var(--border-color); border-radius: 11px;
        background: var(--field-bg); color: var(--primary-text);
    }}
    input, textarea {{ color: var(--primary-text) !important; }}
    button[kind="primary"] {{
        min-height: 3rem; border: 0; border-radius: 12px;
        background: {accent}; color: {"#102019" if theme_mode == "Dark" else "#ffffff"};
        font-weight: 700; transition: filter .2s ease, transform .2s ease;
    }}
    button[kind="primary"]:hover {{ filter: brightness(1.08); transform: translateY(-1px); }}
    [data-testid="stMetric"] {{
        padding: 1rem 1.15rem; border: 1px solid var(--border-color);
        border-radius: 15px; background: var(--surface-bg);
    }}
    [data-testid="stMetricLabel"] p {{ color: var(--secondary-text); }}
    [data-testid="stMetricValue"] {{ color: var(--primary-text); }}
    [data-testid="stAlert"] {{ border-radius: 12px; }}
    [data-testid="stIFrame"] {{
        overflow: hidden; border: 1px solid var(--border-color);
        border-radius: 18px; box-shadow: {shadow};
    }}
    @media (max-width: 700px) {{
        .block-container {{ padding: 1rem 1rem 2.5rem; }}
        .hero {{ padding: 1.35rem; border-radius: 17px; }}
        .hero h1 {{ font-size: 1.9rem; }}
        [data-testid="stForm"] {{ padding: 1rem; }}
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

with header_col:
    st.markdown(
        f"""
        <div class="hero">
          <div class="hero-kicker">Campus walking guide</div>
          <h1>ShadeRoute</h1>
          <p>Find the comfortable way there, planned around your place and time.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
st.markdown(
    "<div style='height:.35rem'></div>"
    "<p style='margin:0 0 1.1rem'>Set your map area, choose two points, and pick when you plan to travel. "
    "Times are shown in <strong>India Standard Time (IST)</strong>.</p>",
    unsafe_allow_html=True,
)

now_ist = datetime.now(IST)
with st.form("route_inputs"):
    st.markdown("### 01 &nbsp; Map area", unsafe_allow_html=True)
    center_col, radius_col = st.columns([2, 1])
    with center_col:
        lat_col, lon_col = st.columns(2)
        center_lat = lat_col.number_input(
            "Center latitude",
            min_value=-90.0,
            max_value=90.0,
            value=float(CAMPUS_POINT[0]),
            format="%.6f",
        )
        center_lon = lon_col.number_input(
            "Center longitude",
            min_value=-180.0,
            max_value=180.0,
            value=float(CAMPUS_POINT[1]),
            format="%.6f",
        )
    with radius_col:
        radius = st.number_input(
            "Fetch radius (meters)",
            min_value=100,
            max_value=10000,
            value=int(CAMPUS_RADIUS),
            step=100,
        )

    st.markdown("### 02 &nbsp; Route endpoints", unsafe_allow_html=True)
    start_col, end_col = st.columns(2)
    with start_col:
        st.markdown("**START · Origin**")
        start_lat_col, start_lon_col = st.columns(2)
        start_lat = start_lat_col.number_input(
            "Start latitude",
            min_value=-90.0,
            max_value=90.0,
            value=20.268645,
            format="%.6f",
        )
        start_lon = start_lon_col.number_input(
            "Start longitude",
            min_value=-180.0,
            max_value=180.0,
            value=85.840747,
            format="%.6f",
        )
    with end_col:
        st.markdown("**END · Destination**")
        end_lat_col, end_lon_col = st.columns(2)
        end_lat = end_lat_col.number_input(
            "End latitude",
            min_value=-90.0,
            max_value=90.0,
            value=20.275596,
            format="%.6f",
        )
        end_lon = end_lon_col.number_input(
            "End longitude",
            min_value=-180.0,
            max_value=180.0,
            value=85.834382,
            format="%.6f",
        )

    st.markdown("### 03 &nbsp; Travel time", unsafe_allow_html=True)
    date_col, time_col = st.columns(2)
    travel_date = date_col.date_input("Date (year-month-day)", value=now_ist.date())
    travel_clock = time_col.time_input(
        "Time (hour:minute)",
        value=now_ist.time().replace(second=0, microsecond=0, tzinfo=None),
    )
    submitted = st.form_submit_button(
        "Fetch map and generate route",
        type="primary",
        use_container_width=True,
    )


def distance_in_meters(point_a, point_b):
    earth_radius = 6_371_000
    lat_a, lat_b = math.radians(point_a[0]), math.radians(point_b[0])
    delta_lat = lat_b - lat_a
    delta_lon = math.radians(point_b[1] - point_a[1])
    haversine = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat_a) * math.cos(lat_b) * math.sin(delta_lon / 2) ** 2
    )
    return 2 * earth_radius * math.asin(math.sqrt(haversine))


if submitted:
    center = (center_lat, center_lon)
    start = (start_lat, start_lon)
    end = (end_lat, end_lon)
    travel_time = IST.localize(datetime.combine(travel_date, travel_clock))
    for key in ("route_map_html", "route_time", "sun_position"):
        st.session_state.pop(key, None)

    outside_points = [
        label
        for label, point in (("Start", start), ("End", end))
        if distance_in_meters(center, point) > radius
    ]
    if outside_points:
        st.error(
            f"{' and '.join(outside_points)} point must be within the selected "
            f"{int(radius)} m fetch radius."
        )
    else:
        try:
            with st.spinner(
                "Fetching map data and calculating the shade-aware route..."
            ):
                DATA_DIR.mkdir(parents=True, exist_ok=True)
                graph_file = DATA_DIR / "campus_graph.graphml"
                map_file = DATA_DIR / "route_comparison.html"

                with ExitStack() as stack:
                    for module, attribute, value in (
                        (fetch_graph, "CAMPUS_POINT", center),
                        (fetch_graph, "CAMPUS_RADIUS", int(radius)),
                        (fetch_graph, "GRAPH_FILE", graph_file),
                        (fetch_buildings, "CAMPUS_POINT", center),
                        (fetch_buildings, "CAMPUS_RADIUS", int(radius)),
                        (fetch_buildings, "DATA_DIR", DATA_DIR),
                        (fetch_trees, "CAMPUS_POINT", center),
                        (fetch_trees, "CAMPUS_RADIUS", int(radius)),
                        (fetch_trees, "DATA_DIR", DATA_DIR),
                        (project_shadows, "DATA_DIR", DATA_DIR),
                        (apply_shade, "GRAPH_FILE", graph_file),
                        (apply_shade, "DATA_DIR", DATA_DIR),
                        (calculate_weights, "DATA_DIR", DATA_DIR),
                        (route_finder, "DATA_DIR", DATA_DIR),
                        (route_visualizer, "DATA_DIR", DATA_DIR),
                        (sun_position, "CAMPUS_POINT", center),
                    ):
                        stack.enter_context(patch.object(module, attribute, value))

                    fetch_graph.fetch_campus()
                    fetch_buildings.fetch_buildings()
                    fetch_trees.fetch_trees()

                    altitude, azimuth, _ = sun_position.get_sun_position(
                        travel_time.year,
                        travel_time.month,
                        travel_time.day,
                        travel_time.hour,
                        travel_time.minute,
                    )
                    shadows = project_shadows.calculate_shadows(altitude, azimuth)
                    if shadows is None:
                        empty_shadows = gpd.GeoDataFrame(
                            geometry=[],
                            crs="EPSG:4326",
                        )
                        empty_shadows.to_file(
                            DATA_DIR / "campus_shadows.geojson",
                            driver="GeoJSON",
                        )

                    apply_shade.apply_shade_to_graph()
                    calculate_weights.calculate_final_weights()
                    route_finder.find_best_routes(
                        start[0], start[1], end[0], end[1]
                    )
                    route_visualizer.generate_route_map(
                        start[0], start[1], end[0], end[1]
                    )

                map_html = map_file.read_text(encoding="utf-8")
                map_details = f"""
                <div style="position:fixed;top:12px;left:50px;z-index:9999;
                            background:{surface_bg};color:{primary_text};
                            border:1px solid {border_color};padding:11px 15px;
                            border-radius:11px;box-shadow:0 4px 16px #0003;
                            font:13px/1.65 sans-serif">
                  Travel time: {html.escape(travel_time.strftime("%Y-%m-%d %H:%M IST"))}<br>
                  Sun altitude: {altitude:.1f}° · Azimuth: {azimuth:.1f}°<br>
                  Start: {start[0]:.6f}, {start[1]:.6f} ·
                  End: {end[0]:.6f}, {end[1]:.6f}
                </div>
                """
                map_html = map_html.replace("</body>", map_details + "</body>")

            st.session_state["route_map_html"] = map_html
            st.session_state["route_time"] = travel_time.strftime(
                "%Y-%m-%d %H:%M IST"
            )
            st.session_state["sun_position"] = (altitude, azimuth)
        except Exception as error:
            st.error(f"Could not generate the route: {error}")
            st.exception(error)

if "route_map_html" in st.session_state:
    st.markdown("### 04 &nbsp; Your route", unsafe_allow_html=True)
    altitude, azimuth = st.session_state["sun_position"]
    st.caption(
        f"Travel time: {st.session_state['route_time']} · "
        f"Sun altitude: {altitude:.1f}° · Azimuth: {azimuth:.1f}°"
    )
    st.markdown(
        """
        <div style="display:flex;gap:1.2rem;align-items:center;margin:.3rem 0 1rem;
                    font:600 .83rem sans-serif">
          <span><i style="display:inline-block;width:10px;height:10px;border-radius:50%;
                         background:#e05252;margin-right:7px"></i>Shortest route</span>
          <span><i style="display:inline-block;width:10px;height:10px;border-radius:50%;
                         background:#3788df;margin-right:7px"></i>Shade-aware route</span>
          <span style="color:#178052">● Start</span>
          <span style="color:#69756d">● Destination</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    components.html(st.session_state["route_map_html"], height=680, scrolling=False)
