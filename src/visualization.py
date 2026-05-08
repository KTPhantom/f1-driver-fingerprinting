"""
Visualization Module — Full F1 Dashboard Charts.

All Plotly figure generators for the dashboard. Includes:
- Original ML charts (UMAP, radar, confusion matrix, etc.)
- NEW Driver charts (lap progression, sectors, heatmap)
- NEW Team charts (teammate H2H, pace ranking, points)
- NEW Track charts (position chart, lap evolution, sector bars)

Author: Kshitij Tripathi
"""

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import DRIVER_COLORS, DRIVER_FULL_NAMES, FEATURE_GROUPS, DRIVER_TEAM_MAP

DARK_BG = "#0E1117"
CARD_BG = "#1A1D23"
GRID_COLOR = "#2A2D35"
TEXT_COLOR = "#FAFAFA"
ACCENT = "#00D4FF"

LAYOUT_DEFAULTS = dict(
    paper_bgcolor=DARK_BG, plot_bgcolor=CARD_BG,
    font=dict(family="Inter, sans-serif", color=TEXT_COLOR, size=12),
    margin=dict(l=60, r=30, t=50, b=50),
    xaxis=dict(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR),
    yaxis=dict(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR),
)

def _c(d): return DRIVER_COLORS.get(d, "#888")
def _n(d): return DRIVER_FULL_NAMES.get(d, d)


# ═══════════════════════════════════════════════════════════════════════════════
# ORIGINAL ML CHARTS (preserved)
# ═══════════════════════════════════════════════════════════════════════════════

def plot_umap_2d(df, color_by="Driver", title="UMAP 2D — Driver Embeddings"):
    fig = px.scatter(df, x="UMAP_1", y="UMAP_2", color=color_by,
        color_discrete_map=DRIVER_COLORS if color_by == "Driver" else None,
        hover_data=["Driver", "Circuit", "Cluster"], title=title, opacity=0.7)
    fig.update_traces(marker=dict(size=5, line=dict(width=0.3, color="#000")))
    fig.update_layout(**LAYOUT_DEFAULTS, legend_title=color_by, height=600)
    return fig

def plot_umap_3d(df, color_by="Driver", title="UMAP 3D — Driver Embeddings"):
    fig = px.scatter_3d(df, x="UMAP_3D_1", y="UMAP_3D_2", z="UMAP_3D_3",
        color=color_by, color_discrete_map=DRIVER_COLORS if color_by == "Driver" else None,
        hover_data=["Driver", "Circuit"], title=title, opacity=0.7)
    fig.update_traces(marker=dict(size=3))
    fig.update_layout(paper_bgcolor=DARK_BG, font=dict(family="Inter, sans-serif", color=TEXT_COLOR),
        height=700, scene=dict(
            xaxis=dict(backgroundcolor=CARD_BG, gridcolor=GRID_COLOR),
            yaxis=dict(backgroundcolor=CARD_BG, gridcolor=GRID_COLOR),
            zaxis=dict(backgroundcolor=CARD_BG, gridcolor=GRID_COLOR)))
    return fig

def plot_driver_radar(profiles_df, drivers, feature_group="all"):
    if feature_group != "all" and feature_group in FEATURE_GROUPS:
        cols = [c for c in FEATURE_GROUPS[feature_group] if c in profiles_df.columns]
    else:
        cols = [c for c in profiles_df.columns if c in [f for g in FEATURE_GROUPS.values() for f in g]]
    if not cols: return go.Figure()
    data = profiles_df.loc[drivers, cols].copy()
    for c in cols:
        rng = profiles_df[c].max() - profiles_df[c].min()
        data[c] = (data[c] - profiles_df[c].min()) / rng if rng > 0 else 0.5
    fig = go.Figure()
    for driver in drivers:
        vals = data.loc[driver].values.tolist(); vals.append(vals[0])
        labels = cols + [cols[0]]
        fig.add_trace(go.Scatterpolar(r=vals, theta=labels, name=_n(driver),
            fill="toself", opacity=0.3, line=dict(color=_c(driver), width=2)))
    fig.update_layout(polar=dict(bgcolor=CARD_BG,
        radialaxis=dict(visible=True, range=[0, 1], gridcolor=GRID_COLOR),
        angularaxis=dict(gridcolor=GRID_COLOR)),
        paper_bgcolor=DARK_BG, font=dict(family="Inter, sans-serif", color=TEXT_COLOR, size=11),
        title="Driver Behavioral Fingerprint", height=550, showlegend=True)
    return fig

def plot_confusion_matrix(cm, labels, title="Cross-Track — Confusion Matrix"):
    dl = [_n(l) for l in labels]
    cm_n = cm.astype(float); rs = cm_n.sum(axis=1, keepdims=True); rs[rs==0]=1; cm_n = cm_n/rs
    fig = go.Figure(data=go.Heatmap(z=cm_n, x=dl, y=dl,
        colorscale=[[0,CARD_BG],[0.5,"#1E3A5F"],[1,ACCENT]],
        text=cm, texttemplate="%{text}", textfont=dict(size=12, color=TEXT_COLOR)))
    fig.update_layout(**LAYOUT_DEFAULTS, title=title, height=550,
        xaxis_title="Predicted", yaxis_title="True",
        yaxis=dict(autorange="reversed", gridcolor=GRID_COLOR))
    return fig

def plot_telemetry_overlay(raw_df, drivers, circuit, channel="Speed"):
    mask = raw_df["Circuit"].str.contains(circuit, case=False, na=False)
    data = raw_df[mask].copy()
    fig = go.Figure()
    for driver in drivers:
        d = data[data["Driver"]==driver]
        if d.empty: continue
        laps = sorted(d["LapNumber"].unique())
        if not laps: continue
        ld = d[d["LapNumber"]==laps[0]]
        fig.add_trace(go.Scatter(x=ld["Distance"], y=ld[channel], mode="lines",
            name=_n(driver), line=dict(color=_c(driver), width=1.5), opacity=0.85))
    fig.update_layout(**LAYOUT_DEFAULTS, title=f"{channel} vs Distance — {circuit}",
        xaxis_title="Distance (m)", yaxis_title=channel, height=400, hovermode="x unified")
    return fig

def plot_feature_importance(feature_df, top_n=15):
    nc = [c for c in feature_df.columns if c not in ("Driver","Circuit","LapNumber","SegmentId",
        "UMAP_1","UMAP_2","UMAP_3D_1","UMAP_3D_2","UMAP_3D_3","Cluster","Cluster_Prob")]
    imp = {}
    for col in nc:
        groups = [g[col].values for _, g in feature_df.groupby("Driver")]
        groups = [g for g in groups if len(g)>1]
        if len(groups)<2: continue
        gm = feature_df[col].mean()
        b = sum(len(g)*(g.mean()-gm)**2 for g in groups)/(len(groups)-1)
        w = sum(g.var()*(len(g)-1) for g in groups)/(sum(len(g) for g in groups)-len(groups))
        imp[col] = b/(w+1e-10)
    idf = pd.DataFrame({"Feature":list(imp.keys()),"F":list(imp.values())})
    idf = idf.sort_values("F", ascending=True).tail(top_n)
    gc = {"braking":"#FF4B4B","throttle":"#00D4FF","cornering":"#FFD700",
          "gear_shift":"#00FF88","speed_profile":"#FF69B4","other":"#888"}
    def gg(f):
        for gn,fs in FEATURE_GROUPS.items():
            if f in fs: return gn
        return "other"
    idf["Color"] = idf["Feature"].map(lambda f: gc[gg(f)])
    fig = go.Figure(go.Bar(x=idf["F"], y=idf["Feature"], orientation="h",
        marker_color=idf["Color"], text=idf["F"].round(1), textposition="outside"))
    fig.update_layout(**LAYOUT_DEFAULTS, title="Most Discriminative Features (F-Statistic)",
        xaxis_title="F-Statistic", height=500)
    return fig

def plot_feature_distributions(feature_df, feature_name, drivers=None):
    data = feature_df.copy()
    if drivers: data = data[data["Driver"].isin(drivers)]
    fig = px.box(data, x="Driver", y=feature_name, color="Driver",
        color_discrete_map=DRIVER_COLORS, title=f"Distribution: {feature_name}")
    fig.update_layout(**LAYOUT_DEFAULTS, height=400, showlegend=False)
    return fig

def plot_cluster_composition(df):
    ct = pd.crosstab(df["Cluster"], df["Driver"]); ct = ct[ct.index != -1]
    fig = go.Figure()
    for d in ct.columns:
        fig.add_trace(go.Bar(name=_n(d), x=[f"C{c}" for c in ct.index],
            y=ct[d], marker_color=_c(d)))
    fig.update_layout(**LAYOUT_DEFAULTS, barmode="stack",
        title="Driver Composition per Cluster", height=450)
    return fig

def plot_per_driver_accuracy(pda, rb):
    d = list(pda.keys()); a = list(pda.values())
    fig = go.Figure()
    fig.add_trace(go.Bar(y=[_n(x) for x in d], x=a, orientation="h",
        marker_color=[_c(x) for x in d], text=[f"{x:.0%}" for x in a], textposition="outside"))
    fig.add_vline(x=rb, line_dash="dash", line_color="#FF4B4B", annotation_text="Random")
    fig.update_layout(**LAYOUT_DEFAULTS, title="Per-Driver Cross-Track Accuracy",
        xaxis_title="Accuracy", xaxis=dict(range=[0,1.1], gridcolor=GRID_COLOR), height=450)
    return fig


# ═══════════════════════════════════════════════════════════════════════════════
# NEW: DRIVER ANALYSIS CHARTS
# ═══════════════════════════════════════════════════════════════════════════════

def plot_lap_time_progression(lap_df, driver, title=None):
    """Line chart of lap times across a race, colored by tire compound."""
    d = lap_df[lap_df["Driver"]==driver].copy()
    if d.empty: return go.Figure()
    compound_colors = {"SOFT":"#FF3333","MEDIUM":"#FFD700","HARD":"#CCCCCC",
                       "INTERMEDIATE":"#44BB44","WET":"#3366FF"}
    fig = go.Figure()
    if "Compound" in d.columns:
        for compound in d["Compound"].unique():
            cd = d[d["Compound"]==compound]
            fig.add_trace(go.Scatter(x=cd["LapNumber"], y=cd["LapTime"], mode="lines+markers",
                name=compound, line=dict(color=compound_colors.get(compound, "#888"), width=2),
                marker=dict(size=4)))
    else:
        fig.add_trace(go.Scatter(x=d["LapNumber"], y=d["LapTime"], mode="lines+markers",
            name=_n(driver), line=dict(color=_c(driver), width=2), marker=dict(size=4)))
    fig.update_layout(**LAYOUT_DEFAULTS, height=400,
        title=title or f"Lap Time Progression — {_n(driver)}",
        xaxis_title="Lap Number", yaxis_title="Lap Time (s)",
        yaxis=dict(autorange="reversed", gridcolor=GRID_COLOR))
    return fig


def plot_sector_comparison(lap_df, driver, all_drivers=None):
    """Grouped bar: driver's best sectors vs field average."""
    d = lap_df[lap_df["Driver"]==driver]
    sectors = ["Sector1Time","Sector2Time","Sector3Time"]
    available = [s for s in sectors if s in lap_df.columns]
    if not available or d.empty: return go.Figure()

    driver_best = [d[s].min() for s in available]
    if all_drivers:
        field_avg = [lap_df[lap_df["Driver"].isin(all_drivers)][s].median() for s in available]
    else:
        field_avg = [lap_df[s].median() for s in available]

    labels = ["Sector 1","Sector 2","Sector 3"][:len(available)]
    fig = go.Figure()
    fig.add_trace(go.Bar(name=_n(driver), x=labels, y=driver_best,
        marker_color=_c(driver), text=[f"{v:.3f}s" for v in driver_best], textposition="outside"))
    fig.add_trace(go.Bar(name="Field Median", x=labels, y=field_avg,
        marker_color="#555", text=[f"{v:.3f}s" for v in field_avg], textposition="outside"))
    fig.update_layout(**LAYOUT_DEFAULTS, barmode="group", height=400,
        title=f"Best Sector Times — {_n(driver)} vs Field",
        yaxis_title="Time (s)", yaxis=dict(gridcolor=GRID_COLOR))
    return fig


def plot_driver_performance_heatmap(results_df, driver):
    """Heatmap of finishing positions across circuits."""
    d = results_df[results_df["Driver"]==driver]
    if d.empty: return go.Figure()
    fig = go.Figure(go.Bar(
        x=d["Circuit"], y=d["Position"],
        marker=dict(color=d["Position"],
            colorscale=[[0,"#00FF88"],[0.3,"#27F4D2"],[0.5,"#FFD700"],[1,"#FF4B4B"]],
            cmin=1, cmax=20),
        text=d["Position"].astype(int).astype(str), textposition="outside",
        hovertemplate="%{x}<br>P%{y}<extra></extra>"))
    fig.update_layout(**LAYOUT_DEFAULTS, height=350,
        title=f"Race Results — {_n(driver)}",
        xaxis_title="Circuit", yaxis_title="Position",
        yaxis=dict(autorange="reversed", range=[0.5, 21], gridcolor=GRID_COLOR))
    return fig


def plot_speed_histogram(raw_df, driver, circuit=None):
    """Speed distribution histogram."""
    d = raw_df[raw_df["Driver"]==driver]
    if circuit: d = d[d["Circuit"].str.contains(circuit, case=False, na=False)]
    if d.empty: return go.Figure()
    fig = go.Figure(go.Histogram(x=d["Speed"], nbinsx=60, marker_color=_c(driver),
        opacity=0.8, name=_n(driver)))
    fig.update_layout(**LAYOUT_DEFAULTS, height=350,
        title=f"Speed Distribution — {_n(driver)}",
        xaxis_title="Speed (km/h)", yaxis_title="Frequency")
    return fig


# ═══════════════════════════════════════════════════════════════════════════════
# NEW: TEAM / CAR ANALYSIS CHARTS
# ═══════════════════════════════════════════════════════════════════════════════

def plot_teammate_comparison(lap_df, results_df, driver1, driver2, team_color):
    """Back-to-back bar comparing two teammates."""
    metrics = {}
    # Average lap time
    for d in [driver1, driver2]:
        dl = lap_df[lap_df["Driver"]==d]
        metrics[d] = {"Avg Lap (s)": dl["LapTime"].mean() if not dl.empty else 0}
        dr = results_df[results_df["Driver"]==d]
        metrics[d]["Avg Finish"] = dr["Position"].mean() if not dr.empty else 0
        metrics[d]["Total Points"] = dr["Points"].sum() if not dr.empty else 0

    cats = list(metrics[driver1].keys())
    v1 = [metrics[driver1][c] for c in cats]
    v2 = [metrics[driver2][c] for c in cats]

    fig = make_subplots(rows=1, cols=3, subplot_titles=cats)
    for i, cat in enumerate(cats):
        fig.add_trace(go.Bar(x=[_n(driver1)], y=[v1[i]], marker_color=_c(driver1),
            name=_n(driver1), showlegend=(i==0), text=[f"{v1[i]:.1f}"], textposition="outside"), row=1, col=i+1)
        fig.add_trace(go.Bar(x=[_n(driver2)], y=[v2[i]], marker_color=_c(driver2),
            name=_n(driver2), showlegend=(i==0), text=[f"{v2[i]:.1f}"], textposition="outside"), row=1, col=i+1)

    fig.update_layout(paper_bgcolor=DARK_BG, plot_bgcolor=CARD_BG,
        font=dict(family="Inter, sans-serif", color=TEXT_COLOR),
        height=400, title="Teammate Head-to-Head", showlegend=True,
        margin=dict(l=40,r=20,t=60,b=40))
    fig.update_xaxes(gridcolor=GRID_COLOR)
    fig.update_yaxes(gridcolor=GRID_COLOR)
    return fig


def plot_team_pace_ranking(lap_df, highlight_team=None):
    """Horizontal bar: average race pace for all teams."""
    if "Team" not in lap_df.columns or lap_df.empty: return go.Figure()
    pace = lap_df.groupby("Team")["LapTime"].median().sort_values()
    if pace.empty: return go.Figure()
    best = pace.iloc[0]
    delta = pace - best

    from config import TEAM_COLORS
    colors = [TEAM_COLORS.get(t, "#888") for t in delta.index]
    borders = ["3px solid #FFD700" if t == highlight_team else "none" for t in delta.index]

    fig = go.Figure(go.Bar(
        y=delta.index, x=delta.values, orientation="h",
        marker_color=colors,
        text=[f"+{v:.3f}s" if v > 0 else "REF" for v in delta.values],
        textposition="outside"))
    fig.update_layout(**LAYOUT_DEFAULTS, height=450,
        title="Team Pace Ranking (Median Lap Delta to Leader)",
        xaxis_title="Delta to Leader (s)")
    return fig


def plot_team_points_breakdown(results_df, team_drivers, team_color):
    """Stacked bar: points per driver per circuit."""
    d = results_df[results_df["Driver"].isin(team_drivers)]
    if d.empty: return go.Figure()
    fig = go.Figure()
    for i, driver in enumerate(team_drivers):
        dd = d[d["Driver"]==driver]
        fig.add_trace(go.Bar(name=_n(driver), x=dd["Circuit"], y=dd["Points"],
            marker_color=_c(driver)))
    fig.update_layout(**LAYOUT_DEFAULTS, barmode="stack", height=400,
        title="Points Breakdown by Driver", yaxis_title="Points")
    return fig


# ═══════════════════════════════════════════════════════════════════════════════
# NEW: TRACK ANALYSIS CHARTS
# ═══════════════════════════════════════════════════════════════════════════════

def plot_position_chart(lap_df):
    """Classic F1 position chart — all drivers' positions lap by lap."""
    if "LapNumber" not in lap_df.columns: return go.Figure()
    fig = go.Figure()
    # We need to compute approximate position from lap times
    # Group by lap, rank by cumulative time
    drivers = lap_df["Driver"].unique()
    for driver in drivers:
        d = lap_df[lap_df["Driver"]==driver].sort_values("LapNumber")
        if d.empty: continue
        # Approximate position from lap time ranking per lap
        fig.add_trace(go.Scatter(
            x=d["LapNumber"], y=d["LapTime"].rank(method="min").values,
            mode="lines", name=_n(driver),
            line=dict(color=_c(driver), width=1.5), opacity=0.85))

    # Better approach: rank drivers by lap time each lap
    fig.data = []  # Clear and redo properly
    pivot = lap_df.pivot_table(index="LapNumber", columns="Driver", values="LapTime")
    ranks = pivot.rank(axis=1, method="min")
    for driver in ranks.columns:
        r = ranks[driver].dropna()
        fig.add_trace(go.Scatter(x=r.index, y=r.values, mode="lines",
            name=_n(driver), line=dict(color=_c(driver), width=1.8), opacity=0.9))

    fig.update_layout(**LAYOUT_DEFAULTS, height=500,
        title="Lap Time Position Chart",
        xaxis_title="Lap Number", yaxis_title="Position (by lap time)",
        yaxis=dict(autorange="reversed", dtick=1, gridcolor=GRID_COLOR),
        hovermode="x unified")
    return fig


def plot_track_sector_bars(lap_df, top_n=10):
    """Best sector times for all drivers at a circuit."""
    sectors = ["Sector1Time","Sector2Time","Sector3Time"]
    available = [s for s in sectors if s in lap_df.columns]
    if not available: return go.Figure()

    fig = make_subplots(rows=1, cols=len(available),
        subplot_titles=[f"Sector {i+1}" for i in range(len(available))])

    for i, sec in enumerate(available):
        best = lap_df.groupby("Driver")[sec].min().nsmallest(top_n).sort_values()
        fig.add_trace(go.Bar(
            y=[_n(d) for d in best.index], x=best.values, orientation="h",
            marker_color=[_c(d) for d in best.index],
            text=[f"{v:.3f}" for v in best.values], textposition="outside",
            showlegend=False), row=1, col=i+1)

    fig.update_layout(paper_bgcolor=DARK_BG, plot_bgcolor=CARD_BG,
        font=dict(family="Inter, sans-serif", color=TEXT_COLOR),
        height=450, title="Best Sector Times", margin=dict(l=100,r=20,t=60,b=40))
    fig.update_xaxes(gridcolor=GRID_COLOR)
    fig.update_yaxes(gridcolor=GRID_COLOR)
    return fig


def plot_lap_evolution(lap_df, drivers=None, top_n=6):
    """Multi-line: lap times across the race for multiple drivers."""
    if drivers is None:
        avg = lap_df.groupby("Driver")["LapTime"].median().nsmallest(top_n)
        drivers = avg.index.tolist()

    fig = go.Figure()
    for driver in drivers:
        d = lap_df[lap_df["Driver"]==driver].sort_values("LapNumber")
        if d.empty: continue
        fig.add_trace(go.Scatter(x=d["LapNumber"], y=d["LapTime"], mode="lines",
            name=_n(driver), line=dict(color=_c(driver), width=1.5), opacity=0.85))

    fig.update_layout(**LAYOUT_DEFAULTS, height=450,
        title="Lap Time Evolution", xaxis_title="Lap", yaxis_title="Lap Time (s)",
        yaxis=dict(gridcolor=GRID_COLOR), hovermode="x unified")
    return fig
