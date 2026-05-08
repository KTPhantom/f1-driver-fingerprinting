"""
Central configuration for the F1 Driver Fingerprinting & Analytics Dashboard.

All hyperparameters, constants, session definitions, team/driver metadata,
and the full 2025 calendar are managed here.
"""

from pathlib import Path
from dataclasses import dataclass
from typing import List, Tuple, Dict

# ─── Paths ────────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent
CACHE_DIR = PROJECT_ROOT / "cache"
CACHE_DIR.mkdir(exist_ok=True)

# ─── Season ───────────────────────────────────────────────────────────────────
YEAR = 2025

# ─── Full 2025 Calendar ──────────────────────────────────────────────────────
# (display_name, fastf1_name, country, track_type, lap_distance_km)
ALL_CIRCUITS = [
    ("Australian GP", "Australia", "Australia", "street", 5.278),
    ("Chinese GP", "China", "China", "permanent", 5.451),
    ("Japanese GP", "Japan", "Japan", "permanent", 5.807),
    ("Bahrain GP", "Bahrain", "Bahrain", "permanent", 5.412),
    ("Saudi Arabian GP", "Saudi Arabia", "Saudi Arabia", "street", 6.174),
    ("Miami GP", "Miami", "USA", "street", 5.412),
    ("Emilia Romagna GP", "Emilia Romagna", "Italy", "permanent", 4.909),
    ("Monaco GP", "Monaco", "Monaco", "street", 3.337),
    ("Spanish GP", "Spain", "Spain", "permanent", 4.657),
    ("Canadian GP", "Canada", "Canada", "semi-permanent", 4.361),
    ("Austrian GP", "Austria", "Austria", "permanent", 4.318),
    ("British GP", "Great Britain", "UK", "permanent", 5.891),
    ("Belgian GP", "Belgium", "Belgium", "permanent", 7.004),
    ("Hungarian GP", "Hungary", "Hungary", "permanent", 4.381),
    ("Dutch GP", "Netherlands", "Netherlands", "permanent", 4.259),
    ("Italian GP", "Italy", "Italy", "permanent", 5.793),
    ("Azerbaijan GP", "Azerbaijan", "Azerbaijan", "street", 6.003),
    ("Singapore GP", "Singapore", "Singapore", "street", 4.940),
    ("US GP", "United States", "USA", "permanent", 5.513),
    ("Mexico City GP", "Mexico", "Mexico", "permanent", 4.304),
    ("São Paulo GP", "São Paulo", "Brazil", "permanent", 4.309),
    ("Las Vegas GP", "Las Vegas", "USA", "street", 6.201),
    ("Qatar GP", "Qatar", "Qatar", "permanent", 5.380),
    ("Abu Dhabi GP", "Abu Dhabi", "UAE", "semi-permanent", 5.281),
]

# Default curated set for quick loading
DEFAULT_CIRCUITS = ["Australia", "Japan", "Great Britain", "Italy", "Spain", "Belgium"]

# ML train/test split circuits
TRAIN_CIRCUITS: List[Tuple[str, str]] = [
    ("Australia", "R"), ("Japan", "R"), ("Great Britain", "R"), ("Italy", "R"),
]
TEST_CIRCUITS: List[Tuple[str, str]] = [
    ("Spain", "R"), ("Belgium", "R"),
]

# ─── Teams (Constructors) — 2025 ─────────────────────────────────────────────
TEAMS = {
    "Red Bull Racing": {
        "short": "Red Bull", "color": "#3671C6", "accent": "#1B3A67",
        "car": "RB21", "drivers": ["VER", "LAW"],
    },
    "McLaren": {
        "short": "McLaren", "color": "#FF8000", "accent": "#47290E",
        "car": "MCL39", "drivers": ["NOR", "PIA"],
    },
    "Scuderia Ferrari": {
        "short": "Ferrari", "color": "#E8002D", "accent": "#470010",
        "car": "SF-25", "drivers": ["LEC", "HAM"],
    },
    "Mercedes-AMG Petronas": {
        "short": "Mercedes", "color": "#27F4D2", "accent": "#0D4D42",
        "car": "W16", "drivers": ["RUS", "ANT"],
    },
    "Aston Martin": {
        "short": "Aston Martin", "color": "#229971", "accent": "#0D3D2D",
        "car": "AMR25", "drivers": ["ALO", "STR"],
    },
    "Alpine": {
        "short": "Alpine", "color": "#00A1E8", "accent": "#0D3A54",
        "car": "A525", "drivers": ["GAS", "DOO"],
    },
    "Williams": {
        "short": "Williams", "color": "#1868DB", "accent": "#0F2D5A",
        "car": "FW47", "drivers": ["ALB", "SAI"],
    },
    "Racing Bulls": {
        "short": "Racing Bulls", "color": "#6C98FF", "accent": "#1E2D4D",
        "car": "VCARB 02", "drivers": ["TSU", "HAD"],
    },
    "Kick Sauber": {
        "short": "Sauber", "color": "#01C00E", "accent": "#0A3D0D",
        "car": "C45", "drivers": ["HUL", "BOR"],
    },
    "Haas F1 Team": {
        "short": "Haas", "color": "#B6BABD", "accent": "#3A3C3E",
        "car": "VF-25", "drivers": ["OCO", "BEA"],
    },
}

# ─── All Drivers — 2025 ──────────────────────────────────────────────────────
DRIVER_FULL_NAMES = {
    "VER": "Max Verstappen", "LAW": "Liam Lawson",
    "NOR": "Lando Norris", "PIA": "Oscar Piastri",
    "LEC": "Charles Leclerc", "HAM": "Lewis Hamilton",
    "RUS": "George Russell", "ANT": "Andrea Kimi Antonelli",
    "ALO": "Fernando Alonso", "STR": "Lance Stroll",
    "GAS": "Pierre Gasly", "DOO": "Jack Doohan",
    "ALB": "Alexander Albon", "SAI": "Carlos Sainz",
    "TSU": "Yuki Tsunoda", "HAD": "Isack Hadjar",
    "HUL": "Nico Hulkenberg", "BOR": "Gabriel Bortoleto",
    "OCO": "Esteban Ocon", "BEA": "Oliver Bearman",
}

DRIVER_NUMBERS = {
    "VER": 1, "LAW": 30, "NOR": 4, "PIA": 81,
    "LEC": 16, "HAM": 44, "RUS": 63, "ANT": 12,
    "ALO": 14, "STR": 18, "GAS": 10, "DOO": 7,
    "ALB": 23, "SAI": 55, "TSU": 22, "HAD": 6,
    "HUL": 27, "BOR": 5, "OCO": 31, "BEA": 87,
}

DRIVER_NATIONALITIES = {
    "VER": "🇳🇱 Dutch", "LAW": "🇳🇿 New Zealander",
    "NOR": "🇬🇧 British", "PIA": "🇦🇺 Australian",
    "LEC": "🇲🇨 Monégasque", "HAM": "🇬🇧 British",
    "RUS": "🇬🇧 British", "ANT": "🇮🇹 Italian",
    "ALO": "🇪🇸 Spanish", "STR": "🇨🇦 Canadian",
    "GAS": "🇫🇷 French", "DOO": "🇦🇺 Australian",
    "ALB": "🇹🇭 Thai", "SAI": "🇪🇸 Spanish",
    "TSU": "🇯🇵 Japanese", "HAD": "🇫🇷 French",
    "HUL": "🇩🇪 German", "BOR": "🇧🇷 Brazilian",
    "OCO": "🇫🇷 French", "BEA": "🇬🇧 British",
}

# Per-driver unique colors (differentiated within teams)
DRIVER_COLORS = {
    "VER": "#3671C6", "LAW": "#1B3A67",
    "NOR": "#FF8000", "PIA": "#E06A00",
    "LEC": "#E8002D", "HAM": "#FF5C5C",
    "RUS": "#27F4D2", "ANT": "#18A38A",
    "ALO": "#229971", "STR": "#165E46",
    "GAS": "#00A1E8", "DOO": "#007AB8",
    "ALB": "#1868DB", "SAI": "#1050A0",
    "TSU": "#6C98FF", "HAD": "#4A6FCC",
    "HUL": "#01C00E", "BOR": "#00900A",
    "OCO": "#B6BABD", "BEA": "#8A8D90",
}

# Reverse lookups
DRIVER_TEAM_MAP = {}
TEAM_COLORS = {}
for team_name, team_data in TEAMS.items():
    TEAM_COLORS[team_name] = team_data["color"]
    TEAM_COLORS[team_data["short"]] = team_data["color"]
    for d in team_data["drivers"]:
        DRIVER_TEAM_MAP[d] = team_data["short"]

# Target drivers for ML pipeline (subset)
TARGET_DRIVERS: List[str] = [
    "VER", "HAM", "NOR", "LEC", "PIA", "SAI", "RUS", "ALO", "GAS", "TSU",
]

# ─── Micro-Segment Configuration ─────────────────────────────────────────────
@dataclass
class SegmentConfig:
    segment_distance_m: float = 100.0
    min_segment_points: int = 5
    min_speed_threshold: float = 30.0
    overlap_ratio: float = 0.5

@dataclass
class UMAPConfig:
    n_components_cluster: int = 10
    n_neighbors_cluster: int = 30
    min_dist_cluster: float = 0.0
    metric_cluster: str = "euclidean"
    n_components_viz: int = 2
    n_neighbors_viz: int = 15
    min_dist_viz: float = 0.1
    metric_viz: str = "euclidean"
    n_components_3d: int = 3
    n_neighbors_3d: int = 15
    min_dist_3d: float = 0.1
    random_state: int = 42

@dataclass
class HDBSCANConfig:
    min_cluster_size: int = 15
    min_samples: int = 5
    cluster_selection_epsilon: float = 0.0
    cluster_selection_method: str = "eom"
    prediction_data: bool = True

# ─── Feature Engineering ─────────────────────────────────────────────────────
FEATURE_GROUPS = {
    "braking": [
        "brake_mean", "brake_max", "brake_std",
        "brake_onset_pct", "brake_duration_pct",
        "deceleration_rate_mean", "deceleration_rate_max",
    ],
    "throttle": [
        "throttle_mean", "throttle_std", "throttle_max",
        "throttle_application_rate", "partial_throttle_pct",
        "full_throttle_pct", "throttle_smoothness",
    ],
    "cornering": [
        "speed_std", "speed_min", "speed_range",
        "lateral_g_mean", "lateral_g_max", "lateral_g_std",
    ],
    "gear_shift": [
        "gear_mean", "gear_std", "gear_changes_count",
        "upshift_speed_mean", "downshift_speed_mean",
    ],
    "speed_profile": [
        "speed_mean", "speed_max", "entry_speed",
        "exit_speed", "speed_delta",
    ],
}
ALL_FEATURES = [f for group in FEATURE_GROUPS.values() for f in group]
