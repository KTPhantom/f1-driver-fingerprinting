"use client";
import { useEffect, useCallback, useState, useRef } from "react";
import { motion } from "framer-motion";
import { useDashboardStore } from "@/lib/store";
import { CIRCUITS, DRIVERS } from "@/lib/constants";
import { getTrackMap, getLaps, type TrackMapData, type LapRecord } from "@/lib/api";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts";

const TT = { backgroundColor: "#18181B", border: "1px solid rgba(255,255,255,0.06)", borderRadius: 8 };

function Skeleton({ className = "" }: { className?: string }) {
  return <div className={`animate-pulse bg-[--color-surface-2] rounded-lg ${className}`} />;
}

function TrackMapCanvas({ data }: { data: TrackMapData }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !data.x.length) return;
    const ctx = canvas.getContext("2d"); if (!ctx) return;
    canvas.width = canvas.offsetWidth * 2; canvas.height = canvas.offsetHeight * 2;
    ctx.scale(2, 2);
    const cw = canvas.offsetWidth, ch = canvas.offsetHeight;
    ctx.fillStyle = "#18181B"; ctx.fillRect(0, 0, cw, ch);
    const pad = 30;
    const xMin = Math.min(...data.x), xMax = Math.max(...data.x);
    const yMin = Math.min(...data.y), yMax = Math.max(...data.y);
    const xR = xMax - xMin || 1, yR = yMax - yMin || 1;
    const scale = Math.min((cw - pad * 2) / xR, (ch - pad * 2) / yR);
    const ox = (cw - xR * scale) / 2, oy = (ch - yR * scale) / 2;
    const tx = (x: number) => (x - xMin) * scale + ox;
    const ty = (y: number) => ch - ((y - yMin) * scale + oy);
    const sMin = Math.min(...data.speed), sMax = Math.max(...data.speed), sR = sMax - sMin || 1;
    const col = (s: number) => {
      const t = (s - sMin) / sR;
      if (t < 0.33) return `rgb(${54 + t * 3 * -15}, ${113 + t * 3 * 131}, ${198 + t * 3 * 12})`;
      if (t < 0.66) return `rgb(${39 + (t - .33) * 3 * 216}, ${244 + (t - .33) * 3 * -29}, ${210 + (t - .33) * 3 * -210})`;
      return `rgb(${255 - (t - .66) * 3 * 23}, ${215 - (t - .66) * 3 * 215}, ${(t - .66) * 3 * 45})`;
    };
    for (let i = 1; i < data.x.length; i++) {
      ctx.beginPath(); ctx.moveTo(tx(data.x[i - 1]), ty(data.y[i - 1]));
      ctx.lineTo(tx(data.x[i]), ty(data.y[i])); ctx.strokeStyle = col(data.speed[i]); ctx.lineWidth = 2.5; ctx.stroke();
    }
    const grd = ctx.createLinearGradient(cw - 140, 0, cw - 20, 0);
    grd.addColorStop(0, "#3671C6"); grd.addColorStop(0.5, "#FFD700"); grd.addColorStop(1, "#E8002D");
    ctx.fillStyle = grd; ctx.fillRect(cw - 140, ch - 30, 120, 8);
    ctx.fillStyle = "#52525B"; ctx.font = "10px sans-serif";
    ctx.fillText(`${Math.round(sMin)}`, cw - 140, ch - 12); ctx.fillText(`${Math.round(sMax)} km/h`, cw - 60, ch - 12);
  }, [data]);
  return <canvas ref={canvasRef} className="w-full rounded-lg" style={{ height: 400, background: "#18181B" }} />;
}

export default function TrackPage() {
  const { selectedCircuit, setCircuit } = useDashboardStore();
  const [trackMap, setTrackMap] = useState<TrackMapData | null>(null);
  const [laps, setLaps] = useState<LapRecord[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedDrivers, setSelectedDrivers] = useState<string[]>([]);

  const loadData = useCallback(async (cir: string) => {
    setLoading(true); setError(null); setTrackMap(null); setLaps([]);
    try {
      const [tmRes, lapRes] = await Promise.allSettled([getTrackMap(cir), getLaps(cir)]);
      if (tmRes.status === "fulfilled") setTrackMap(tmRes.value);
      if (lapRes.status === "fulfilled") setLaps(lapRes.value.laps);
      if (tmRes.status === "rejected" && lapRes.status === "rejected") setError("Could not load data. Ensure backend is running.");
    } catch (e) { setError(String(e)); } finally { setLoading(false); }
  }, []);

  useEffect(() => { loadData(selectedCircuit); }, [selectedCircuit, loadData]);

  const meta = CIRCUITS.find(c => c.name === selectedCircuit);

  // Get all drivers in this race
  const allDrivers = [...new Set(laps.map(l => l.Driver))].sort();

  // Auto-select top 6 if none selected
  const activeDrivers = selectedDrivers.length > 0 ? selectedDrivers : (() => {
    const driverAvg = Object.entries(
      laps.reduce<Record<string, number[]>>((acc, l) => { if (!acc[l.Driver]) acc[l.Driver] = []; if (l.LapTime) acc[l.Driver].push(l.LapTime); return acc; }, {})
    ).map(([d, t]) => ({ d, avg: t.reduce((a, b) => a + b, 0) / t.length })).sort((a, b) => a.avg - b.avg).slice(0, 6).map(x => x.d);
    return driverAvg;
  })();

  const lapNumbers = [...new Set(laps.filter(l => activeDrivers.includes(l.Driver)).map(l => l.LapNumber))].sort((a, b) => a - b);
  const evolutionData = lapNumbers.map(ln => {
    const row: Record<string, number> = { lap: ln };
    activeDrivers.forEach(d => { const l = laps.find(l => l.Driver === d && l.LapNumber === ln); if (l?.LapTime) row[d] = +l.LapTime.toFixed(2); });
    return row;
  });

  const toggleDriver = (d: string) => {
    setSelectedDrivers(prev => {
      if (prev.includes(d)) return prev.filter(x => x !== d);
      if (prev.length >= 8) return prev;
      return [...prev, d];
    });
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap gap-3 items-center">
        <select value={selectedCircuit} onChange={e => setCircuit(e.target.value)}
          className="bg-[--color-surface-1] border border-[--color-border] rounded-lg px-4 py-2 text-sm text-[--color-text-primary] focus:outline-none">
          {CIRCUITS.map(c => <option key={c.name} value={c.name}>{c.display}</option>)}
        </select>
        {meta && <span className="label-xs">{meta.country} · {meta.type} · {meta.distanceKm} km</span>}
      </div>

      {meta && (
        <motion.div className="glass-card p-6" key={selectedCircuit} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
          <h1 className="text-2xl font-bold">{meta.display}</h1>
          <p className="text-sm text-[--color-text-secondary] mt-1">{meta.country} · {meta.type} · {meta.distanceKm} km</p>
        </motion.div>
      )}

      {/* Driver filter chips */}
      {!loading && allDrivers.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          <span className="text-xs text-[--color-text-tertiary] self-center mr-2">Filter drivers:</span>
          {allDrivers.map(d => {
            const active = activeDrivers.includes(d);
            return (
              <button key={d} onClick={() => toggleDriver(d)}
                className={`px-2.5 py-1 rounded-full text-xs font-medium transition-all ${active ? "text-white" : "text-[--color-text-tertiary] border border-[--color-border]"}`}
                style={active ? { background: DRIVERS[d]?.color || "#888" } : {}}>
                {d}
              </button>
            );
          })}
          {selectedDrivers.length > 0 && (
            <button onClick={() => setSelectedDrivers([])} className="px-2.5 py-1 rounded-full text-xs text-[--color-text-tertiary] border border-[--color-border] hover:text-[--color-text-primary]">
              Reset
            </button>
          )}
        </div>
      )}

      {loading && (
        <div className="space-y-4">
          <div className="glass-card p-6 text-center">
            <div className="inline-block w-6 h-6 border-2 border-[--color-accent] border-t-transparent rounded-full animate-spin mb-3" />
            <p className="text-sm text-[--color-text-secondary]">Loading <strong>{meta?.display}</strong>...</p>
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4"><Skeleton className="h-[440px]" /><Skeleton className="h-[440px]" /></div>
        </div>
      )}

      {error && <div className="glass-card p-6 border-l-4 border-red-500"><p className="text-sm text-red-400">{error}</p></div>}

      {!loading && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {trackMap && (
            <motion.div className="chart-panel" key={`m-${selectedCircuit}`} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
              <div className="chart-panel-header"><span className="text-sm font-semibold">Speed Map</span><span className="label-xs">{trackMap.points} pts</span></div>
              <div className="chart-panel-body p-0"><TrackMapCanvas data={trackMap} /></div>
            </motion.div>
          )}
          {evolutionData.length > 0 && (
            <motion.div className="chart-panel" key={`e-${selectedCircuit}`} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
              <div className="chart-panel-header"><span className="text-sm font-semibold">Lap Time Evolution</span><span className="label-xs">{laps.length} total laps</span></div>
              <div className="chart-panel-body">
                <ResponsiveContainer width="100%" height={400}>
                  <LineChart data={evolutionData}><CartesianGrid strokeDasharray="3 3" stroke="#27272A" />
                    <XAxis dataKey="lap" stroke="#52525B" fontSize={10} /><YAxis stroke="#52525B" fontSize={10} domain={["auto", "auto"]} />
                    <Tooltip contentStyle={TT} /><Legend />
                    {activeDrivers.map(d => <Line key={d} type="monotone" dataKey={d} name={DRIVERS[d]?.name || d} stroke={DRIVERS[d]?.color || "#888"} strokeWidth={1.5} dot={false} />)}
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </motion.div>
          )}
        </div>
      )}

      {!loading && !error && !trackMap && evolutionData.length === 0 && (
        <div className="glass-card p-8 text-center"><p className="text-sm text-[--color-text-tertiary]">No track data. Select a circuit.</p></div>
      )}
    </div>
  );
}
