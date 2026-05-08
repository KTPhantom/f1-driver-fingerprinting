"""
Track Utilities — Circuit Map Rendering.

Functions for creating speed-colored track maps from X/Y telemetry data
using Plotly. Handles coordinate rotation, speed gradient mapping, and
corner annotation.

Author: Kshitij Tripathi
"""

import numpy as np
import plotly.graph_objects as go

DARK_BG = "#0E1117"
CARD_BG = "#1A1D23"
TEXT_COLOR = "#FAFAFA"


def plot_track_map(track_data: dict, title: str = "Circuit Map") -> go.Figure:
    """
    Create a speed-colored circuit map from track data.

    Args:
        track_data: Dict with X, Y, Speed arrays from load_track_map().
        title: Chart title.

    Returns:
        Plotly Figure with speed-gradient colored track outline.
    """
    if track_data is None:
        return go.Figure()

    X = track_data["X"]
    Y = track_data["Y"]
    speed = track_data["Speed"]

    fig = go.Figure()

    # Draw track as colored scatter with lines
    fig.add_trace(go.Scatter(
        x=X, y=Y, mode="markers+lines",
        marker=dict(
            size=3, color=speed,
            colorscale=[[0, "#3671C6"], [0.3, "#27F4D2"], [0.6, "#FFD700"], [1, "#E8002D"]],
            colorbar=dict(
                title="Speed (km/h)", thickness=15, len=0.6,
                tickfont=dict(color=TEXT_COLOR), titlefont=dict(color=TEXT_COLOR),
            ),
            showscale=True,
        ),
        line=dict(width=1, color="rgba(255,255,255,0.1)"),
        hovertemplate="Speed: %{marker.color:.0f} km/h<extra></extra>",
        showlegend=False,
    ))

    # Annotate corners if available
    corners = track_data.get("corners")
    if corners is not None and hasattr(corners, "iterrows"):
        try:
            ci = track_data.get("circuit_info")
            if ci is not None:
                angle = ci.rotation / 180 * np.pi
                cos_a, sin_a = np.cos(angle), np.sin(angle)
                for _, corner in corners.iterrows():
                    cx = corner.get("X", 0) * cos_a - corner.get("Y", 0) * sin_a
                    cy = corner.get("X", 0) * sin_a + corner.get("Y", 0) * cos_a
                    num = corner.get("Number", "")
                    fig.add_annotation(
                        x=cx, y=cy, text=f"T{num}",
                        font=dict(size=9, color="#8B92A5"),
                        showarrow=False, bgcolor="rgba(26,29,35,0.7)",
                    )
        except Exception:
            pass

    fig.update_layout(
        title=title,
        paper_bgcolor=DARK_BG, plot_bgcolor=CARD_BG,
        font=dict(family="Inter, sans-serif", color=TEXT_COLOR),
        xaxis=dict(visible=False, scaleanchor="y", scaleratio=1),
        yaxis=dict(visible=False),
        height=550,
        margin=dict(l=20, r=20, t=50, b=20),
    )
    return fig


def plot_track_with_driver_speed(track_data: dict, driver_tel, driver_name: str, color: str) -> go.Figure:
    """Track map colored by a specific driver's speed on their fastest lap."""
    if track_data is None or driver_tel is None or driver_tel.empty:
        return go.Figure()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=driver_tel["X"].values, y=driver_tel["Y"].values,
        mode="markers", name=driver_name,
        marker=dict(
            size=3, color=driver_tel["Speed"].values,
            colorscale=[[0, "#3671C6"], [0.3, "#27F4D2"], [0.6, "#FFD700"], [1, "#E8002D"]],
            colorbar=dict(title="km/h", thickness=12, len=0.5,
                         tickfont=dict(color=TEXT_COLOR, size=10),
                         titlefont=dict(color=TEXT_COLOR, size=10)),
            showscale=True,
        ),
        hovertemplate=f"{driver_name}<br>Speed: %{{marker.color:.0f}} km/h<extra></extra>",
    ))

    fig.update_layout(
        title=f"{driver_name} — Speed Map",
        paper_bgcolor=DARK_BG, plot_bgcolor=CARD_BG,
        font=dict(family="Inter, sans-serif", color=TEXT_COLOR),
        xaxis=dict(visible=False, scaleanchor="y", scaleratio=1),
        yaxis=dict(visible=False),
        height=450, margin=dict(l=20, r=20, t=50, b=20),
    )
    return fig
