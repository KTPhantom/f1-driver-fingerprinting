"use client";
import { useEffect, useCallback, useState } from "react";
import { motion } from "framer-motion";
import { useDashboardStore } from "@/lib/store";
import { DRIVERS, CIRCUITS } from "@/lib/constants";
import { getMultiTelemetry, type MultiTelemetry } from "@/lib/api";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts";

const TT = { backgroundColor: "#18181B", border: "1px solid rgba(255,255,255,0.06)", borderRadius: 8 };

const driverList = Object.values(DRIVERS);

export default function ComparePage() {
  const { selectedCircuit, setCircuit, compareDrivers, addCompareDriver, removeCompareDriver, clearCompareDrivers } = useDashboardStore();
  const [telemetry, setTelemetry] = useState<MultiTelemetry | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadData = useCallback(async (cir: string, drivers: string[]) => {
    if (drivers.length < 2) { setTelemetry(null); return; }
    setLoading(true); setError(null); setTelemetry(null);
    try {
      const res = await getMultiTelemetry(cir, drivers);
      setTelemetry(res);
    } catch { setError("Could not load comparison data."); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => {
    if (compareDrivers.length >= 2) loadData(selectedCircuit, compareDrivers);
  }, [selectedCircuit, compareDrivers, loadData]);

  // Build overlay chart data
  const chartData = telemetry ? (() => {
    const allDrivers = Object.keys(telemetry.drivers);
    const refDriver = allDrivers[0];
    const refDist = telemetry.drivers[refDriver]?.distance || [];
    return refDist.filter((_, i) => i % 5 === 0).map((d, idx) => {
      const row: Record<string, number> = { dist: Math.round(d) };
      allDrivers.forEach(drv => {
        const dd = telemetry.drivers[drv];
        if (dd) {
          row[`${drv}_speed`] = dd.speed[idx * 5] ?? 0;
          row[`${drv}_throttle`] = dd.throttle[idx * 5] ?? 0;
          row[`${drv}_brake`] = (dd.brake[idx * 5] ?? 0) * 100;
        }
      });
      return row;
    });
  })() : [];

  const loadedDrivers = telemetry ? Object.keys(telemetry.drivers) : [];

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap gap-3 items-center">
        <select value={selectedCircuit} onChange={e => setCircuit(e.target.value)}
          className="bg-[--color-surface-1] border border-[--color-border] rounded-lg px-4 py-2 text-sm text-[--color-text-primary] focus:outline-none">
          {CIRCUITS.map(c => <option key={c.name} value={c.name}>{c.display}</option>)}
        </select>
      </div>

      {/* Driver selector */}
      <div className="glass-card p-4">
        <div className="flex items-center gap-3 mb-3">
          <h2 className="text-sm font-semibold">Select 2-4 drivers to compare</h2>
          {compareDrivers.length > 0 && (
            <button onClick={clearCompareDrivers} className="text-xs text-[--color-text-tertiary] hover:text-[--color-text-primary]">Clear all</button>
          )}
        </div>
        <div className="flex flex-wrap gap-1.5">
          {driverList.map(d => {
            const active = compareDrivers.includes(d.abbr);
            return (
              <button key={d.abbr} onClick={() => active ? removeCompareDriver(d.abbr) : addCompareDriver(d.abbr)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${active ? "text-white" : "text-[--color-text-secondary] border border-[--color-border] hover:border-[--color-text-tertiary]"}`}
                style={active ? { background: d.color } : {}}>
                {d.abbr} — {d.name}
              </button>
            );
          })}
        </div>
        <div className="mt-3 flex gap-2 flex-wrap">
          {compareDrivers.map(d => (
            <span key={d} className="inline-flex items-center gap-1 px-2 py-1 rounded text-xs text-white" style={{ background: DRIVERS[d]?.color }}>
              {DRIVERS[d]?.name} <button onClick={() => removeCompareDriver(d)} className="ml-1 opacity-60 hover:opacity-100">×</button>
            </span>
          ))}
        </div>
      </div>

      {compareDrivers.length < 2 && (
        <div className="glass-card p-8 text-center">
          <div className="text-4xl mb-3">⚡</div>
          <h2 className="text-lg font-semibold mb-1">Telemetry Comparison</h2>
          <p className="text-sm text-[--color-text-secondary]">Select at least 2 drivers above to overlay their fastest lap telemetry.</p>
        </div>
      )}

      {loading && (
        <div className="glass-card p-8 text-center">
          <div className="inline-block w-6 h-6 border-2 border-[--color-accent] border-t-transparent rounded-full animate-spin mb-3" />
          <p className="text-sm text-[--color-text-secondary]">Loading telemetry comparison...</p>
        </div>
      )}

      {error && <div className="glass-card p-6 border-l-4 border-red-500"><p className="text-sm text-red-400">{error}</p></div>}

      {!loading && chartData.length > 0 && (
        <>
          {/* Speed Overlay */}
          <motion.div className="chart-panel" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
            <div className="chart-panel-header"><span className="text-sm font-semibold">Speed Comparison</span></div>
            <div className="chart-panel-body">
              <ResponsiveContainer width="100%" height={350}>
                <LineChart data={chartData}><CartesianGrid strokeDasharray="3 3" stroke="#27272A" />
                  <XAxis dataKey="dist" stroke="#52525B" fontSize={10} /><YAxis stroke="#52525B" fontSize={10} />
                  <Tooltip contentStyle={TT} /><Legend />
                  {loadedDrivers.map(d => <Line key={d} type="monotone" dataKey={`${d}_speed`} name={`${DRIVERS[d]?.name || d} Speed`}
                    stroke={DRIVERS[d]?.color || "#888"} strokeWidth={1.5} dot={false} />)}
                </LineChart>
              </ResponsiveContainer>
            </div>
          </motion.div>

          {/* Throttle Overlay */}
          <motion.div className="chart-panel" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 }}>
            <div className="chart-panel-header"><span className="text-sm font-semibold">Throttle Comparison</span></div>
            <div className="chart-panel-body">
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={chartData}><CartesianGrid strokeDasharray="3 3" stroke="#27272A" />
                  <XAxis dataKey="dist" stroke="#52525B" fontSize={10} /><YAxis stroke="#52525B" fontSize={10} domain={[0, 100]} />
                  <Tooltip contentStyle={TT} /><Legend />
                  {loadedDrivers.map(d => <Line key={d} type="monotone" dataKey={`${d}_throttle`} name={`${DRIVERS[d]?.name || d}`}
                    stroke={DRIVERS[d]?.color || "#888"} strokeWidth={1.5} dot={false} />)}
                </LineChart>
              </ResponsiveContainer>
            </div>
          </motion.div>

          {/* Brake Overlay */}
          <motion.div className="chart-panel" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <div className="chart-panel-header"><span className="text-sm font-semibold">Brake Comparison</span></div>
            <div className="chart-panel-body">
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={chartData}><CartesianGrid strokeDasharray="3 3" stroke="#27272A" />
                  <XAxis dataKey="dist" stroke="#52525B" fontSize={10} /><YAxis stroke="#52525B" fontSize={10} domain={[0, 100]} />
                  <Tooltip contentStyle={TT} /><Legend />
                  {loadedDrivers.map(d => <Line key={d} type="monotone" dataKey={`${d}_brake`} name={`${DRIVERS[d]?.name || d}`}
                    stroke={DRIVERS[d]?.color || "#888"} strokeWidth={1.5} dot={false} />)}
                </LineChart>
              </ResponsiveContainer>
            </div>
          </motion.div>
        </>
      )}
    </div>
  );
}
