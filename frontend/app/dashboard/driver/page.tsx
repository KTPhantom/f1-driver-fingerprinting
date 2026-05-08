"use client";
import { useEffect, useCallback, useState } from "react";
import { motion } from "framer-motion";
import Image from "next/image";
import { useDashboardStore } from "@/lib/store";
import { DRIVERS, CIRCUITS, getTeamForDriver, getDriverTeamKey } from "@/lib/constants";
import { DRIVER_IMAGES, DRIVER_FALLBACK, TEAM_LOGOS } from "@/lib/images";
import { getLaps, getTelemetry, type LapRecord, type TelemetryData } from "@/lib/api";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, Legend } from "recharts";

const TT = { backgroundColor: "#18181B", border: "1px solid rgba(255,255,255,0.06)", borderRadius: 8 };

function Skeleton({ className = "" }: { className?: string }) {
  return <div className={`animate-pulse bg-[--color-surface-2] rounded-lg ${className}`} />;
}

export default function DriverPage() {
  const driverList = Object.values(DRIVERS);
  const { selectedDriver, selectedCircuit, setDriver, setCircuit, setAccent } = useDashboardStore();
  const [laps, setLaps] = useState<LapRecord[]>([]);
  const [telemetry, setTelemetry] = useState<TelemetryData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [imgError, setImgError] = useState(false);

  const driver = DRIVERS[selectedDriver];
  const team = getTeamForDriver(selectedDriver);
  const teamKey = getDriverTeamKey(selectedDriver);

  // Update accent color when driver changes
  useEffect(() => { if (driver) setAccent(driver.color); }, [selectedDriver, driver, setAccent]);
  useEffect(() => { setImgError(false); }, [selectedDriver]);

  const loadData = useCallback(async (drv: string, cir: string) => {
    setLoading(true); setError(null); setLaps([]); setTelemetry(null);
    try {
      const [lapRes, telRes] = await Promise.allSettled([
        getLaps(cir).then(r => r.laps.filter(l => l.Driver === drv)),
        getTelemetry(cir, drv),
      ]);
      if (lapRes.status === "fulfilled") setLaps(lapRes.value);
      if (telRes.status === "fulfilled") setTelemetry(telRes.value);
      if (lapRes.status === "rejected" && telRes.status === "rejected")
        setError("Could not load data. Ensure backend is running on :8000.");
    } catch (e) { setError(String(e)); } finally { setLoading(false); }
  }, []);

  useEffect(() => { loadData(selectedDriver, selectedCircuit); }, [selectedDriver, selectedCircuit, loadData]);

  // Telemetry chart with gear
  const telChart = telemetry ? telemetry.distance
    .filter((_, i) => i % 5 === 0)
    .map((d, i) => ({
      dist: Math.round(d),
      speed: telemetry.speed[i * 5],
      throttle: telemetry.throttle[i * 5],
      brake: telemetry.brake[i * 5] * 100,
      gear: telemetry.gear[i * 5],
    })) : [];

  const sectorData = laps.length > 0 ? [
    { sector: "S1", best: Math.min(...laps.filter(l => l.Sector1Time).map(l => l.Sector1Time!)) },
    { sector: "S2", best: Math.min(...laps.filter(l => l.Sector2Time).map(l => l.Sector2Time!)) },
    { sector: "S3", best: Math.min(...laps.filter(l => l.Sector3Time).map(l => l.Sector3Time!)) },
  ] : [];

  // Tire strategy
  const stints = laps.reduce<{ compound: string; start: number; end: number; life: number }[]>((acc, l) => {
    const last = acc[acc.length - 1];
    if (last && last.compound === l.Compound) { last.end = l.LapNumber; last.life = l.TyreLife || 0; }
    else if (l.Compound) acc.push({ compound: l.Compound, start: l.LapNumber, end: l.LapNumber, life: l.TyreLife || 0 });
    return acc;
  }, []);

  const compoundColor: Record<string, string> = { SOFT: "#FF3333", MEDIUM: "#FFD700", HARD: "#FFFFFF", INTERMEDIATE: "#00CC00", WET: "#0088FF" };

  const driverImg = DRIVER_IMAGES[selectedDriver] || DRIVER_FALLBACK;
  const teamLogo = teamKey ? TEAM_LOGOS[teamKey] : undefined;

  return (
    <div className="space-y-6">
      {/* Controls */}
      <div className="flex flex-wrap gap-3">
        <select value={selectedDriver} onChange={e => setDriver(e.target.value)}
          className="bg-[--color-surface-1] border border-[--color-border] rounded-lg px-4 py-2 text-sm text-[--color-text-primary] focus:outline-none focus:border-[--color-accent]">
          {driverList.map(d => <option key={d.abbr} value={d.abbr}>{d.abbr} — {d.name}</option>)}
        </select>
        <select value={selectedCircuit} onChange={e => setCircuit(e.target.value)}
          className="bg-[--color-surface-1] border border-[--color-border] rounded-lg px-4 py-2 text-sm text-[--color-text-primary] focus:outline-none focus:border-[--color-accent]">
          {CIRCUITS.map(c => <option key={c.name} value={c.name}>{c.display}</option>)}
        </select>
      </div>

      {/* Hero Card */}
      {driver && (
        <motion.div key={selectedDriver} className="relative overflow-hidden rounded-2xl"
          style={{ background: `linear-gradient(135deg, ${driver.color}18, ${driver.color}08, transparent)` }}
          initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}>
          <div className="h-1 w-full" style={{ background: `linear-gradient(90deg, ${driver.color}, transparent)` }} />
          <div className="flex items-stretch">
            <div className="relative w-36 md:w-48 min-h-[180px] flex-shrink-0 overflow-hidden">
              <div className="absolute inset-0" style={{ background: `linear-gradient(135deg, ${driver.color}30, transparent 60%)` }} />
              {!imgError ? (
                <Image src={driverImg} alt={driver.name} fill className="object-cover object-top" sizes="192px"
                  onError={() => setImgError(true)} priority />
              ) : (
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="text-5xl font-black opacity-20" style={{ color: driver.color }}>{driver.number}</span>
                </div>
              )}
            </div>
            <div className="flex-1 p-4 md:p-6 flex flex-col justify-center min-w-0">
              <div className="flex items-center gap-3 mb-1">
                <span className="text-xs font-bold tracking-widest uppercase" style={{ color: driver.color }}>#{driver.number}</span>
                <span className="text-xs text-[--color-text-tertiary]">·</span>
                <span className="text-xs text-[--color-text-secondary]">{driver.nationality}</span>
              </div>
              <h1 className="text-2xl md:text-4xl font-bold tracking-tight mb-2 truncate">{driver.name}</h1>
              <div className="flex items-center gap-3">
                {teamLogo && <Image src={teamLogo} alt={team?.short || ""} width={80} height={24} className="object-contain opacity-80"
                  onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }} />}
                <span className="text-sm text-[--color-text-secondary] truncate">{team?.name}</span>
              </div>
              <div className="flex items-center gap-3 mt-3 flex-wrap">
                <span className="px-3 py-1 rounded-md text-xs font-medium" style={{ background: `${driver.color}20`, color: driver.color }}>{team?.car}</span>
                <span className="text-xs text-[--color-text-tertiary] font-[family-name:var(--font-geist-mono)]">{selectedCircuit} · 2025</span>
              </div>
            </div>
            <div className="hidden lg:flex items-center pr-8">
              <span className="text-[100px] font-black leading-none opacity-[0.04]" style={{ color: driver.color }}>{driver.number}</span>
            </div>
          </div>
        </motion.div>
      )}

      {/* Loading Skeletons */}
      {loading && (
        <div className="space-y-4">
          <div className="glass-card p-6 text-center">
            <div className="inline-block w-6 h-6 border-2 border-[--color-accent] border-t-transparent rounded-full animate-spin mb-3" />
            <p className="text-sm text-[--color-text-secondary]">Loading <strong>{driver?.name}</strong> at <strong>{selectedCircuit}</strong>...</p>
            <p className="text-xs text-[--color-text-tertiary] mt-1">First load may take 30-60s</p>
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <Skeleton className="h-[340px]" /><Skeleton className="h-[340px]" />
          </div>
          <Skeleton className="h-[400px]" />
        </div>
      )}

      {error && <div className="glass-card p-6 border-l-4 border-red-500"><p className="text-sm text-red-400">{error}</p></div>}

      {/* Lap Times + Sectors */}
      {!loading && laps.length > 0 && (
        <motion.div className="grid grid-cols-1 lg:grid-cols-2 gap-4" key={`l-${selectedDriver}-${selectedCircuit}`}
          initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
          <div className="chart-panel">
            <div className="chart-panel-header"><span className="text-sm font-semibold">Lap Time Progression</span><span className="label-xs">{laps.length} laps</span></div>
            <div className="chart-panel-body">
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={laps.map(l => ({ lap: l.LapNumber, time: l.LapTime }))}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#27272A" /><XAxis dataKey="lap" stroke="#52525B" fontSize={11} />
                  <YAxis stroke="#52525B" fontSize={11} domain={["auto", "auto"]} reversed />
                  <Tooltip contentStyle={TT} /><Line type="monotone" dataKey="time" stroke={driver?.color} strokeWidth={2} dot={{ r: 2 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
          <div className="chart-panel">
            <div className="chart-panel-header"><span className="text-sm font-semibold">Best Sector Times</span></div>
            <div className="chart-panel-body">
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={sectorData}><CartesianGrid strokeDasharray="3 3" stroke="#27272A" />
                  <XAxis dataKey="sector" stroke="#52525B" fontSize={11} /><YAxis stroke="#52525B" fontSize={11} />
                  <Tooltip contentStyle={TT} /><Bar dataKey="best" fill={driver?.color} radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </motion.div>
      )}

      {/* Tire Strategy */}
      {!loading && stints.length > 0 && (
        <motion.div className="chart-panel" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
          <div className="chart-panel-header"><span className="text-sm font-semibold">Tire Strategy</span><span className="label-xs">{stints.length} stints</span></div>
          <div className="chart-panel-body">
            <div className="flex items-center gap-2 flex-wrap">
              {stints.map((s, i) => (
                <div key={i} className="flex items-center gap-2 px-3 py-2 rounded-lg border border-[--color-border]" style={{ borderLeftColor: compoundColor[s.compound] || "#888", borderLeftWidth: 3 }}>
                  <div className="w-3 h-3 rounded-full" style={{ background: compoundColor[s.compound] || "#888" }} />
                  <div>
                    <div className="text-xs font-semibold">{s.compound}</div>
                    <div className="text-[10px] text-[--color-text-tertiary]">Laps {s.start}–{s.end} ({s.end - s.start + 1} laps)</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </motion.div>
      )}

      {/* Telemetry with Gear */}
      {!loading && telChart.length > 0 && (
        <motion.div className="chart-panel" key={`t-${selectedDriver}-${selectedCircuit}`} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
          <div className="chart-panel-header"><span className="text-sm font-semibold">Fastest Lap Telemetry</span><span className="label-xs">{telemetry?.points} pts</span></div>
          <div className="chart-panel-body">
            <ResponsiveContainer width="100%" height={350}>
              <LineChart data={telChart}><CartesianGrid strokeDasharray="3 3" stroke="#27272A" />
                <XAxis dataKey="dist" stroke="#52525B" fontSize={10} /><YAxis stroke="#52525B" fontSize={10} />
                <Tooltip contentStyle={TT} /><Legend />
                <Line type="monotone" dataKey="speed" name="Speed" stroke="#00D4FF" strokeWidth={1.5} dot={false} />
                <Line type="monotone" dataKey="throttle" name="Throttle" stroke="#00FF88" strokeWidth={1.5} dot={false} />
                <Line type="monotone" dataKey="brake" name="Brake %" stroke="#FF4B4B" strokeWidth={1.5} dot={false} />
                <Line type="monotone" dataKey="gear" name="Gear" stroke="#FFD700" strokeWidth={1} dot={false} yAxisId="right" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </motion.div>
      )}

      {!loading && !error && laps.length === 0 && telChart.length === 0 && (
        <div className="glass-card p-8 text-center"><p className="text-sm text-[--color-text-tertiary]">No data loaded. Select a driver and circuit.</p></div>
      )}
    </div>
  );
}
