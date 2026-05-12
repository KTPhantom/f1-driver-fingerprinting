// API client — typed fetch helpers for the FastAPI backend
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "https://maverickt-f1-race-analysis.hf.space";

async function fetcher<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${url}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...options?.headers },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `API Error ${res.status}`);
  }
  return res.json();
}

// Telemetry
export interface TelemetryData {
  driver: string; circuit: string; points: number;
  distance: number[]; speed: number[]; throttle: number[]; brake: number[]; gear: number[];
}
export const getTelemetry = (circuit: string, driver: string) =>
  fetcher<TelemetryData>(`/api/telemetry/${circuit}/${driver}`);

export interface MultiTelemetry {
  circuit: string;
  drivers: Record<string, { distance: number[]; speed: number[]; throttle: number[]; brake: number[] }>;
}
export const getMultiTelemetry = (circuit: string, drivers: string[]) =>
  fetcher<MultiTelemetry>(`/api/telemetry/${circuit}?drivers=${drivers.join(",")}`);

// Laps
export interface LapRecord {
  Driver: string; LapNumber: number; LapTime: number | null;
  Sector1Time: number | null; Sector2Time: number | null; Sector3Time: number | null;
  Compound: string | null; TyreLife: number | null; Team: string | null; Circuit: string;
}
export const getLaps = (circuit: string) =>
  fetcher<{ circuit: string; laps: LapRecord[]; count: number }>(`/api/laps/${circuit}`);

// Results
export interface ResultRecord {
  Driver: string; Team: string; Position: number; GridPosition: number;
  Status: string; Points: number; Circuit: string;
}
export const getResults = (circuit: string) =>
  fetcher<{ circuit: string; results: ResultRecord[] }>(`/api/results/${circuit}`);
export const getMultiResults = (circuits: string[]) =>
  fetcher<{ results: ResultRecord[] }>(`/api/results/multi`, {
    method: "POST", body: JSON.stringify({ circuits }),
  });

// Tracks
export interface TrackMapData {
  circuit: string; x: number[]; y: number[]; speed: number[]; points: number;
}
export const getTrackMap = (circuit: string) =>
  fetcher<TrackMapData>(`/api/tracks/${circuit}`);

export interface CircuitInfo {
  display: string; name: string; country: string; type: string; distance_km: number;
}
export const getCircuitList = () =>
  fetcher<{ circuits: CircuitInfo[] }>(`/api/tracks/list`);

// ML
export interface UmapPoint { x: number; y: number; driver: string; circuit: string; cluster: number; }
export interface MLResults {
  umap_points: UmapPoint[];
  cluster_metrics: { n_clusters: number; silhouette: number; ari: number; nmi: number; noise_pct: number };
  cross_track: {
    overall_accuracy: number; random_baseline: number;
    per_driver_accuracy: Record<string, number>;
    confusion_matrix: number[][]; driver_labels: string[];
  };
  profiles: Record<string, Record<string, number>>;
  feature_importance: Record<string, number>;
  train_segments: number; drivers_analyzed: string[];
}
export const runML = () =>
  fetcher<{ status: string }>(`/api/ml/run`, { method: "POST", body: JSON.stringify({}) });
export const getMLStatus = () =>
  fetcher<{ status: string; error: string | null }>(`/api/ml/status`);
export const getMLResults = () =>
  fetcher<MLResults>(`/api/ml/results`);
