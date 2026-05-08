"""
Page renderers for the F1 dashboard. Each function renders one page section.
"""
import streamlit as st
import pandas as pd
import numpy as np
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import (
    TEAMS, DRIVER_FULL_NAMES, DRIVER_COLORS, DRIVER_NUMBERS,
    DRIVER_NATIONALITIES, DRIVER_TEAM_MAP, ALL_CIRCUITS, FEATURE_GROUPS,
    TRAIN_CIRCUITS, TEST_CIRCUITS, TARGET_DRIVERS,
    SegmentConfig, UMAPConfig, HDBSCANConfig,
)
from src.visualization import (
    plot_umap_2d, plot_umap_3d, plot_driver_radar, plot_confusion_matrix,
    plot_telemetry_overlay, plot_feature_importance, plot_feature_distributions,
    plot_cluster_composition, plot_per_driver_accuracy,
    plot_lap_time_progression, plot_sector_comparison,
    plot_driver_performance_heatmap, plot_speed_histogram,
    plot_teammate_comparison, plot_team_pace_ranking, plot_team_points_breakdown,
    plot_position_chart, plot_track_sector_bars, plot_lap_evolution,
)
from src.track_utils import plot_track_map


def metric_card(value, label):
    return f'''<div class="metric-card">
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div></div>'''


# ═══════════════════════════════════════════════════════════════════════════
# PAGE: HOME
# ═══════════════════════════════════════════════════════════════════════════
def render_home(session_data):
    st.markdown('<h2 style="color:#FAFAFA;">🏠 Season Overview — 2024</h2>', unsafe_allow_html=True)
    sd = session_data
    n_circuits = len(sd.get("loaded_circuits", []))
    n_drivers = len(sd.get("results", pd.DataFrame())["Driver"].unique()) if "results" in sd and not sd["results"].empty else 0
    total_laps = len(sd.get("laps", pd.DataFrame()))

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(metric_card(n_circuits, "Circuits Loaded"), unsafe_allow_html=True)
    with c2: st.markdown(metric_card(n_drivers, "Drivers"), unsafe_allow_html=True)
    with c3: st.markdown(metric_card(f"{total_laps:,}", "Laps Analyzed"), unsafe_allow_html=True)
    with c4: st.markdown(metric_card("10", "Teams"), unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🏁 Constructor Grid")
    cols = st.columns(5)
    for i, (name, data) in enumerate(TEAMS.items()):
        with cols[i % 5]:
            st.markdown(f'''<div class="metric-card" style="border-left:4px solid {data['color']};text-align:left;padding:1rem;">
                <div style="font-size:1.1rem;font-weight:700;color:{data['color']};">{data['short']}</div>
                <div style="font-size:0.8rem;color:#8B92A5;">{data['car']}</div>
                <div style="font-size:0.75rem;color:#666;margin-top:4px;">
                    {DRIVER_FULL_NAMES.get(data['drivers'][0],'')} · {DRIVER_FULL_NAMES.get(data['drivers'][1],'')}</div>
            </div>''', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# PAGE: DRIVER
# ═══════════════════════════════════════════════════════════════════════════
def render_driver(session_data):
    st.markdown('<h2 style="color:#FAFAFA;">🧑‍✈️ Driver Analysis</h2>', unsafe_allow_html=True)
    laps = session_data.get("laps", pd.DataFrame())
    results = session_data.get("results", pd.DataFrame())
    raw = session_data.get("raw_telemetry", pd.DataFrame())

    available = sorted(laps["Driver"].unique()) if not laps.empty else list(DRIVER_FULL_NAMES.keys())
    driver = st.selectbox("Select Driver", available, format_func=lambda x: f"{x} — {DRIVER_FULL_NAMES.get(x,x)}", key="drv_sel")
    if not driver: return

    team = DRIVER_TEAM_MAP.get(driver, "")
    num = DRIVER_NUMBERS.get(driver, "")
    nat = DRIVER_NATIONALITIES.get(driver, "")
    color = DRIVER_COLORS.get(driver, "#888")

    # Hero card
    st.markdown(f'''<div class="metric-card" style="border-left:5px solid {color};text-align:left;padding:1.5rem;display:flex;justify-content:space-between;align-items:center;">
        <div>
            <div style="font-size:2rem;font-weight:800;color:#FAFAFA;">{DRIVER_FULL_NAMES.get(driver,driver)}</div>
            <div style="font-size:1rem;color:#8B92A5;">{team} · {nat}</div>
        </div>
        <div style="font-size:3.5rem;font-weight:900;color:{color};opacity:0.6;">#{num}</div>
    </div>''', unsafe_allow_html=True)
    st.markdown("")

    if laps.empty:
        st.info("Load circuit data first using the sidebar.")
        return

    # Row 1: Lap progression + Sectors
    c1, c2 = st.columns(2)
    with c1:
        circuits_avail = laps[laps["Driver"]==driver]["Circuit"].unique()
        circ = st.selectbox("Circuit", circuits_avail, key="drv_circ") if len(circuits_avail) > 0 else None
        if circ:
            fig = plot_lap_time_progression(laps[laps["Circuit"]==circ], driver)
            st.plotly_chart(fig, use_container_width=True)
    with c2:
        if circ:
            fig = plot_sector_comparison(laps[laps["Circuit"]==circ], driver, available)
            st.plotly_chart(fig, use_container_width=True)

    # Row 2: Results heatmap + Speed distribution
    c1, c2 = st.columns(2)
    with c1:
        if not results.empty:
            fig = plot_driver_performance_heatmap(results, driver)
            st.plotly_chart(fig, use_container_width=True)
    with c2:
        if not raw.empty:
            fig = plot_speed_histogram(raw, driver, circ)
            st.plotly_chart(fig, use_container_width=True)

    # Row 3: Telemetry deep-dive
    if not raw.empty and circ:
        st.markdown("### 📡 Telemetry Deep-Dive")
        compare_with = st.multiselect("Compare with", [d for d in available if d != driver],
            default=[], max_selections=2, key="drv_compare",
            format_func=lambda x: DRIVER_FULL_NAMES.get(x,x))
        all_d = [driver] + compare_with
        co1, co2 = st.columns(2)
        with co1:
            st.plotly_chart(plot_telemetry_overlay(raw, all_d, circ, "Speed"), use_container_width=True)
        with co2:
            st.plotly_chart(plot_telemetry_overlay(raw, all_d, circ, "Throttle"), use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════
# PAGE: TEAM / CAR
# ═══════════════════════════════════════════════════════════════════════════
def render_team(session_data):
    st.markdown('<h2 style="color:#FAFAFA;">🏎️ Car / Team Analysis</h2>', unsafe_allow_html=True)
    laps = session_data.get("laps", pd.DataFrame())
    results = session_data.get("results", pd.DataFrame())
    raw = session_data.get("raw_telemetry", pd.DataFrame())

    team_names = list(TEAMS.keys())
    team_key = st.selectbox("Select Team", team_names, format_func=lambda x: TEAMS[x]["short"], key="team_sel")
    team = TEAMS[team_key]
    d1, d2 = team["drivers"]

    # Hero
    st.markdown(f'''<div class="metric-card" style="border-top:4px solid {team['color']};text-align:left;padding:1.5rem;">
        <div style="display:flex;justify-content:space-between;align-items:center;">
            <div>
                <div style="font-size:2rem;font-weight:800;color:{team['color']};">{team['short']}</div>
                <div style="font-size:1rem;color:#8B92A5;">{team['car']}</div>
            </div>
            <div style="text-align:right;">
                <div style="color:#FAFAFA;font-weight:600;">{DRIVER_FULL_NAMES.get(d1,d1)}</div>
                <div style="color:#8B92A5;">{DRIVER_FULL_NAMES.get(d2,d2)}</div>
            </div>
        </div>
    </div>''', unsafe_allow_html=True)
    st.markdown("")

    if laps.empty:
        st.info("Load circuit data first using the sidebar.")
        return

    # Teammate H2H
    fig = plot_teammate_comparison(laps, results, d1, d2, team["color"])
    st.plotly_chart(fig, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        fig = plot_team_pace_ranking(laps, highlight_team=team["short"])
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        if not results.empty:
            fig = plot_team_points_breakdown(results, [d1, d2], team["color"])
            st.plotly_chart(fig, use_container_width=True)

    # Car telemetry
    if not raw.empty:
        st.markdown("### 📡 Car Telemetry — Teammate Overlay")
        circuits_avail = raw["Circuit"].unique()
        circ = st.selectbox("Circuit", circuits_avail, key="team_circ")
        if circ:
            co1, co2 = st.columns(2)
            with co1:
                st.plotly_chart(plot_telemetry_overlay(raw, [d1,d2], circ, "Speed"), use_container_width=True)
            with co2:
                st.plotly_chart(plot_telemetry_overlay(raw, [d1,d2], circ, "Throttle"), use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════
# PAGE: TRACK
# ═══════════════════════════════════════════════════════════════════════════
def render_track(session_data):
    st.markdown('<h2 style="color:#FAFAFA;">🏁 Track Analysis</h2>', unsafe_allow_html=True)
    laps = session_data.get("laps", pd.DataFrame())
    raw = session_data.get("raw_telemetry", pd.DataFrame())
    track_maps = session_data.get("track_maps", {})

    if laps.empty:
        st.info("Load circuit data first using the sidebar.")
        return

    circuits = sorted(laps["Circuit"].unique())
    circ = st.selectbox("Select Circuit", circuits, key="track_sel")
    if not circ: return

    # Find circuit metadata
    meta = next((c for c in ALL_CIRCUITS if c[1] in circ or circ in c[0]), None)
    if meta:
        st.markdown(f'''<div class="metric-card" style="text-align:left;padding:1.2rem;">
            <div style="font-size:1.5rem;font-weight:700;color:#FAFAFA;">{meta[0]}</div>
            <div style="color:#8B92A5;">{meta[2]} · {meta[3].title()} Circuit · {meta[4]} km</div>
        </div>''', unsafe_allow_html=True)
        st.markdown("")

    # Track map
    c1, c2 = st.columns([1, 1])
    with c1:
        tm = track_maps.get(circ)
        if tm:
            fig = plot_track_map(tm, title=f"Speed Map — {circ}")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Track map not available for this circuit.")
    with c2:
        circ_laps = laps[laps["Circuit"]==circ]
        fig = plot_track_sector_bars(circ_laps)
        st.plotly_chart(fig, use_container_width=True)

    # Lap evolution + Position chart
    circ_laps = laps[laps["Circuit"]==circ]
    c1, c2 = st.columns(2)
    with c1:
        fig = plot_lap_evolution(circ_laps)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = plot_position_chart(circ_laps)
        st.plotly_chart(fig, use_container_width=True)

    # Telemetry comparison
    st.markdown("### 📡 Driver Comparison on this Track")
    available_d = sorted(circ_laps["Driver"].unique()) if not circ_laps.empty else []
    sel = st.multiselect("Compare Drivers", available_d, default=available_d[:3],
        format_func=lambda x: DRIVER_FULL_NAMES.get(x,x), key="track_drivers")
    if sel and not raw.empty:
        co1, co2 = st.columns(2)
        with co1:
            st.plotly_chart(plot_telemetry_overlay(raw, sel, circ, "Speed"), use_container_width=True)
        with co2:
            st.plotly_chart(plot_telemetry_overlay(raw, sel, circ, "Brake"), use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════
# PAGE: ML FINGERPRINTING (existing, wrapped)
# ═══════════════════════════════════════════════════════════════════════════
def render_ml(session_data):
    st.markdown('<h2 style="color:#FAFAFA;">🧬 ML Driver Fingerprinting</h2>', unsafe_allow_html=True)
    st.markdown('*Identifying drivers purely from telemetry using UMAP + HDBSCAN clustering*')

    ml = session_data.get("ml_results")
    if ml is None:
        st.warning("⚠️ ML pipeline has not been run yet. Click **Run ML Pipeline** in the sidebar.")
        return

    train_df = ml["train_clustered"]
    test_df = ml["test_clustered"]
    metrics = ml["cluster_metrics"]
    cross = ml["cross_track"]
    profiles = ml["profiles"]
    raw_df = session_data.get("raw_telemetry", pd.DataFrame())

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 Overview", "📊 Telemetry", "🧬 Fingerprints", "🔬 Cross-Track", "📈 Features"])

    with tab1:
        c1,c2,c3,c4 = st.columns(4)
        with c1: st.markdown(metric_card(f"{len(train_df):,}", "Train Segments"), unsafe_allow_html=True)
        with c2: st.markdown(metric_card(metrics["n_clusters"], "Clusters"), unsafe_allow_html=True)
        with c3: st.markdown(metric_card(f"{metrics['ari']:.3f}", "ARI"), unsafe_allow_html=True)
        with c4: st.markdown(metric_card(f"{cross.get('overall_accuracy',0):.1%}", "Cross-Track Acc"), unsafe_allow_html=True)

        met_df = pd.DataFrame({"Metric":["Silhouette","ARI","NMI","Noise"],
            "Value":[f"{metrics['silhouette']:.4f}",f"{metrics['ari']:.4f}",
                     f"{metrics['nmi']:.4f}",f"{metrics['noise_pct']:.1f}%"]})
        st.dataframe(met_df, use_container_width=True, hide_index=True)

    with tab2:
        if not raw_df.empty:
            ca = raw_df["Circuit"].unique().tolist()
            sc = st.selectbox("Circuit", ca, key="ml_circ")
            ch = st.selectbox("Channel", ["Speed","Throttle","Brake","RPM"], key="ml_ch")
            sd2 = st.multiselect("Drivers", TARGET_DRIVERS, default=TARGET_DRIVERS[:3],
                format_func=lambda x: DRIVER_FULL_NAMES.get(x,x), key="ml_drv")
            if sd2:
                st.plotly_chart(plot_telemetry_overlay(raw_df, sd2, sc, ch), use_container_width=True)

    with tab3:
        vm = st.radio("Viz", ["2D","3D"], horizontal=True, key="ml_viz")
        cb = st.radio("Color", ["Driver","Circuit","Cluster"], horizontal=True, key="ml_col")
        fig = plot_umap_2d(train_df, cb) if vm=="2D" else plot_umap_3d(train_df, cb)
        st.plotly_chart(fig, use_container_width=True)
        c1,c2 = st.columns(2)
        with c1: st.plotly_chart(plot_cluster_composition(train_df), use_container_width=True)
        with c2:
            if not profiles.empty:
                rd = st.multiselect("Radar", TARGET_DRIVERS[:4], default=TARGET_DRIVERS[:3],
                    format_func=lambda x: DRIVER_FULL_NAMES.get(x,x), key="ml_radar")
                valid = [d for d in rd if d in profiles.index]
                if valid: st.plotly_chart(plot_driver_radar(profiles, valid), use_container_width=True)

    with tab4:
        if cross:
            c1,c2 = st.columns(2)
            with c1: st.plotly_chart(plot_confusion_matrix(cross["confusion_matrix"], cross["driver_labels"]), use_container_width=True)
            with c2: st.plotly_chart(plot_per_driver_accuracy(cross["per_driver_accuracy"], cross["random_baseline"]), use_container_width=True)

    with tab5:
        st.plotly_chart(plot_feature_importance(train_df), use_container_width=True)
        fc = [c for c in train_df.columns if c not in ("Driver","Circuit","LapNumber","SegmentId",
            "UMAP_1","UMAP_2","UMAP_3D_1","UMAP_3D_2","UMAP_3D_3","Cluster","Cluster_Prob")]
        sf = st.selectbox("Feature", fc, key="ml_feat")
        st.plotly_chart(plot_feature_distributions(train_df, sf, TARGET_DRIVERS), use_container_width=True)
