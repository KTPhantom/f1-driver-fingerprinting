# 🏎️ F1 Driver Fingerprinting & Analytics Platform

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Next.js 16](https://img.shields.io/badge/Next.js-16-black.svg)](https://nextjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688.svg)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![ML: UMAP + HDBSCAN](https://img.shields.io/badge/ML-UMAP%20+%20HDBSCAN-blueviolet.svg)]()

> **Can you identify a Formula 1 driver purely from their telemetry patterns — no name attached?**

A full-stack analytics platform that creates **behavioral fingerprints** for F1 drivers using official telemetry data. Features a production-ready Next.js dashboard with real-time data from a FastAPI backend powered by the FastF1 library.

---

## 🧠 What Makes This Project Unique

| Aspect | Description |
|--------|-------------|
| **Unsupervised Approach** | No labeled training data needed — HDBSCAN discovers natural driver groupings |
| **Micro-Segmentation** | Laps split into 100m overlapping segments for granular behavioral analysis |
| **30-Dimensional Features** | 5 behavioral dimensions × 6 features each = rich driver style encoding |
| **Cross-Track Validation** | Train on circuits A,B,C → test on held-out D,E — proves style is transferable |
| **Production Dashboard** | Next.js 16 + FastAPI with real-time telemetry, not just a notebook |

---

## 🏗️ Architecture

```
┌──────────────┐     ┌──────────────────┐     ┌──────────────┐
│   Next.js    │────▶│    FastAPI        │────▶│   FastF1     │
│   Frontend   │     │    Backend        │     │   Telemetry  │
│  (Port 3000) │◀────│   (Port 8000)    │◀────│     API      │
└──────────────┘     └──────────────────┘     └──────────────┘
                            │
                     ┌──────┴───────┐
                     │  ML Pipeline │
                     │  UMAP +      │
                     │  HDBSCAN     │
                     └──────────────┘
```

### Dashboard Pages

| Page | Description |
|------|-------------|
| **Home** | Season overview, constructor grid with team logos & driver photos |
| **Driver** | Individual driver analysis — hero card, lap times, sectors, tire strategy, full telemetry |
| **Team** | Teammate H2H comparison, team pace ranking across the grid |
| **Track** | Speed-colored track map (canvas), lap evolution with driver filter chips |
| **Results** | Race classification table with position changes, points, DNF status |
| **Compare** | Multi-driver telemetry overlay (speed/throttle/brake) — select 2-4 drivers |
| **ML Lab** | UMAP scatter, HDBSCAN clustering, cross-track accuracy, feature importance |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- pip

### Installation

```bash
# Clone
git clone https://github.com/KTPhantom/f1-driver-fingerprinting.git
cd f1-driver-fingerprinting

# Backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### Running

```bash
# Terminal 1 — Backend (from project root)
uvicorn backend.main:app --reload --port 8000

# Terminal 2 — Frontend (from frontend/)
cd frontend
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to see the landing page.
Open [http://localhost:3000/dashboard](http://localhost:3000/dashboard) for the analytics platform.

> **Note:** First load of a circuit takes 30-60s as FastF1 downloads and caches telemetry data. Subsequent loads are instant (in-memory LRU cache).

---

## 🛠️ Tech Stack

### Backend
- **FastF1** — Official F1 telemetry data
- **FastAPI** — REST API with automatic OpenAPI docs
- **UMAP** — Dimensionality reduction (30D → 2D)
- **HDBSCAN** — Density-based clustering
- **scikit-learn** — Feature engineering & validation

### Frontend
- **Next.js 16** — React framework with App Router
- **Recharts** — Data visualization
- **Framer Motion** — Animations & transitions
- **Zustand** — Global state management
- **Tailwind CSS** — Design system ("Pitwall" dark theme)

### Data Sources
- **F1 Media CDN** — Official driver headshots & team logos
- **FastF1 API** — Real-time telemetry, lap times, results

---

## 📊 Feature Dimensions

| Dimension | Features | What It Captures |
|-----------|----------|-----------------|
| **Braking** | mean, max, std, onset, duration, decel rate | How aggressively a driver brakes |
| **Throttle** | mean, std, application rate, partial/full % | Throttle modulation style |
| **Cornering** | speed std, min, range, lateral g (mean/max/std) | Corner commitment level |
| **Gear Shifts** | mean gear, changes count, up/downshift speeds | Mechanical rhythm |
| **Speed Profile** | mean, max, entry/exit speed, delta | Overall speed management |

---

## 📁 Project Structure

```
f1-driver-fingerprinting/
├── backend/
│   ├── main.py              # FastAPI app (CORS, rate limiting, health)
│   └── routers/
│       ├── telemetry.py     # /api/telemetry/{circuit}/{driver}
│       ├── laps.py          # /api/laps/{circuit}
│       ├── results.py       # /api/results/{circuit}
│       ├── tracks.py        # /api/tracks/{circuit}
│       └── ml.py            # /api/ml/run, /api/ml/status, /api/ml/results
├── frontend/
│   ├── app/
│   │   ├── page.tsx         # Cinematic landing page
│   │   ├── not-found.tsx    # Custom 404
│   │   └── dashboard/
│   │       ├── layout.tsx   # Responsive sidebar + mobile nav
│   │       ├── page.tsx     # Season overview
│   │       ├── driver/      # Individual driver analysis
│   │       ├── team/        # Team comparison
│   │       ├── track/       # Track analysis
│   │       ├── results/     # Race results
│   │       ├── compare/     # Multi-driver overlay
│   │       └── ml/          # ML Lab
│   └── lib/
│       ├── api.ts           # Typed API client
│       ├── constants.ts     # 2025 season data
│       ├── images.ts        # F1 CDN image registry
│       └── store.ts         # Zustand global state
├── src/
│   ├── data_loader.py       # FastF1 session loading (LRU cached)
│   ├── feature_engineering.py
│   ├── clustering.py
│   └── visualization.py
├── config.py                # Season config, circuits, drivers
└── requirements.txt
```

---

## 👤 Author

**Kshitij Tripathi** — [GitHub](https://github.com/KTPhantom)

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
