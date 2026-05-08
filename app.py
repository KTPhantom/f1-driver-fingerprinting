"""
F1 Analytics Dashboard — Main Application.

Sidebar-driven navigation with 5 sections:
Home · Driver · Team · Track · ML Fingerprinting

Author: Kshitij Tripathi
"""
import streamlit as st
import pandas as pd
import logging, sys, os

sys.path.insert(0, os.path.dirname(__file__))
from config import (ALL_CIRCUITS, DEFAULT_CIRCUITS, DRIVER_FULL_NAMES,
    TRAIN_CIRCUITS, TEST_CIRCUITS, TARGET_DRIVERS, TEAMS)
from src.data_loader import (load_session, load_session_results,
    load_lap_data, load_track_map, extract_driver_telemetry, load_all_data)
from src.feature_engineering import build_feature_matrix
from src.clustering import ClusteringPipeline
from src.fingerprint import DriverFingerprinter
from src.pages import render_home, render_driver, render_team, render_track, render_ml

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s")

st.set_page_config(page_title="F1 Analytics Dashboard", page_icon="🏎️",
    layout="wide", initial_sidebar_state="expanded")

# ─── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: linear-gradient(135deg, #0E1117 0%, #151921 50%, #0E1117 100%); }
.metric-card {
    background: linear-gradient(145deg, #1A1D23, #22262E);
    border: 1px solid #2A2D35; border-radius: 16px;
    padding: 1.2rem; text-align: center;
    transition: transform 0.2s, box-shadow 0.2s;
    margin-bottom: 0.5rem;
}
.metric-card:hover { transform: translateY(-2px); box-shadow: 0 8px 32px rgba(0,212,255,0.12); }
.metric-value {
    font-size: 2rem; font-weight: 700;
    background: linear-gradient(135deg, #00D4FF, #7B61FF);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.metric-label { font-size: 0.8rem; color: #8B92A5; margin-top: 0.2rem; }
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #12151B, #0E1117);
    border-right: 1px solid #2A2D35;
}
.stTabs [data-baseweb="tab-list"] { gap: 8px; }
.stTabs [data-baseweb="tab"] { background: #1A1D23; border-radius: 10px; border: 1px solid #2A2D35; }
.stTabs [aria-selected="true"] { background: linear-gradient(135deg, rgba(0,212,255,0.2), rgba(123,97,255,0.2)); border-color: #00D4FF; }
.nav-item { padding: 0.7rem 1rem; border-radius: 10px; margin: 4px 0; cursor: pointer;
    border: 1px solid transparent; transition: all 0.2s; }
.nav-active { background: linear-gradient(135deg, rgba(0,212,255,0.15), rgba(123,97,255,0.15));
    border-color: rgba(0,212,255,0.4); }
</style>
""", unsafe_allow_html=True)


# ─── Data Loading (cached, lazy per circuit) ──────────────────────────────────
@st.cache_data(show_spinner=False, ttl=3600)
def load_circuit_data(circuit_name, year=2024):
    """Load all data for a single circuit: results, laps, telemetry, track map."""
    try:
        session = load_session(circuit_name, "R", year)
        results = load_session_results(session)
        laps = load_lap_data(session)
        track_map = load_track_map(session)
        # Raw telemetry for available drivers
        drivers = list(results["Driver"].unique()) if not results.empty else []
        raw_parts = []
        for d in drivers[:15]:  # Cap at 15 drivers
            tel = extract_driver_telemetry(session, d, max_laps=8)
            if tel is not None:
                raw_parts.append(tel)
        raw = pd.concat(raw_parts, ignore_index=True) if raw_parts else pd.DataFrame()
        return {"results": results, "laps": laps, "track_map": track_map, "raw": raw,
                "circuit": circuit_name}
    except Exception as e:
        st.warning(f"Could not load {circuit_name}: {e}")
        return None


@st.cache_data(show_spinner=False, ttl=3600)
def run_ml_pipeline(drivers_tuple, max_laps):
    """Run the full ML fingerprinting pipeline."""
    train_seg, train_raw = load_all_data(
        [tuple(c) for c in TRAIN_CIRCUITS], list(drivers_tuple), max_laps)
    test_seg, test_raw = load_all_data(
        [tuple(c) for c in TEST_CIRCUITS], list(drivers_tuple), max_laps)
    if not train_seg: return None
    train_feat = build_feature_matrix(train_seg)
    test_feat = build_feature_matrix(test_seg) if test_seg else pd.DataFrame()
    pipe = ClusteringPipeline()
    train_cl = pipe.fit(train_feat)
    cluster_met = pipe.evaluate(train_cl)
    cross, profiles = {}, pd.DataFrame()
    if not test_feat.empty:
        test_cl = pipe.transform_new(test_feat)
        fp = DriverFingerprinter(); fp.fit(train_cl)
        cross = fp.evaluate(test_cl, "knn")
        cent = fp.evaluate(test_cl, "centroid")
        cross["centroid_accuracy"] = cent["overall_accuracy"]
        profiles = fp.get_all_profiles(train_cl)
    return {"train_clustered": train_cl, "test_clustered": test_feat,
            "cluster_metrics": cluster_met, "cross_track": cross, "profiles": profiles}


# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""<div style="text-align:center;margin-bottom:1rem;">
        <span style="font-size:2rem;">🏎️</span>
        <div style="font-size:1.3rem;font-weight:800;
            background:linear-gradient(135deg,#00D4FF,#7B61FF,#FF4BCD);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
            F1 Analytics</div>
        <div style="font-size:0.75rem;color:#555;">2024 Season Dashboard</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("---")
    page = st.radio("Navigation", ["🏠 Home", "🧑‍✈️ Driver", "🏎️ Car / Team",
        "🏁 Track", "🧬 ML Fingerprinting"], label_visibility="collapsed")

    st.markdown("---")
    st.markdown("### 📡 Load Data")
    circuit_options = [c[1] for c in ALL_CIRCUITS]
    selected_circuits = st.multiselect("Circuits to load", circuit_options,
        default=DEFAULT_CIRCUITS, key="circuits")
    load_btn = st.button("⬇️ Load Selected Circuits", type="primary", use_container_width=True)

    if page == "🧬 ML Fingerprinting":
        st.markdown("---")
        st.markdown("### 🧪 ML Pipeline")
        ml_laps = st.slider("Max laps/driver", 5, 20, 10, key="ml_laps")
        ml_btn = st.button("🚀 Run ML Pipeline", type="secondary", use_container_width=True)
    else:
        ml_btn = False
        ml_laps = 10

    st.markdown("---")
    st.markdown('<div style="text-align:center;color:#444;font-size:0.7rem;">'
        'Built with FastF1 · UMAP · HDBSCAN<br>© 2024 Kshitij Tripathi</div>',
        unsafe_allow_html=True)


# ─── Data Loading Logic ──────────────────────────────────────────────────────
if load_btn:
    progress = st.progress(0, text="Loading circuit data...")
    all_results, all_laps, all_raw, track_maps, loaded = [], [], [], {}, []
    for i, circ in enumerate(selected_circuits):
        progress.progress((i+1)/len(selected_circuits), text=f"Loading {circ}...")
        data = load_circuit_data(circ)
        if data:
            all_results.append(data["results"])
            all_laps.append(data["laps"])
            if not data["raw"].empty: all_raw.append(data["raw"])
            if data["track_map"]: track_maps[data["circuit"]] = data["track_map"]
            loaded.append(circ)
    progress.empty()

    st.session_state["session_data"] = {
        "results": pd.concat(all_results, ignore_index=True) if all_results else pd.DataFrame(),
        "laps": pd.concat(all_laps, ignore_index=True) if all_laps else pd.DataFrame(),
        "raw_telemetry": pd.concat(all_raw, ignore_index=True) if all_raw else pd.DataFrame(),
        "track_maps": track_maps,
        "loaded_circuits": loaded,
    }
    st.success(f"✅ Loaded {len(loaded)} circuits")

if ml_btn:
    with st.spinner("🔄 Running ML pipeline (UMAP + HDBSCAN)..."):
        ml_res = run_ml_pipeline(tuple(TARGET_DRIVERS), ml_laps)
        if ml_res:
            if "session_data" not in st.session_state:
                st.session_state["session_data"] = {}
            st.session_state["session_data"]["ml_results"] = ml_res
            st.success("✅ ML Pipeline complete")

# ─── Initialize empty session data if needed ─────────────────────────────────
if "session_data" not in st.session_state:
    st.session_state["session_data"] = {
        "results": pd.DataFrame(), "laps": pd.DataFrame(),
        "raw_telemetry": pd.DataFrame(), "track_maps": {}, "loaded_circuits": [],
    }

sd = st.session_state["session_data"]

# ─── Render Pages ─────────────────────────────────────────────────────────────
if page == "🏠 Home":
    render_home(sd)
elif page == "🧑‍✈️ Driver":
    render_driver(sd)
elif page == "🏎️ Car / Team":
    render_team(sd)
elif page == "🏁 Track":
    render_track(sd)
elif page == "🧬 ML Fingerprinting":
    render_ml(sd)
