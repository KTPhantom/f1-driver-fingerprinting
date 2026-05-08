"use client";
import { useEffect, useCallback, useState } from "react";
import { motion } from "framer-motion";
import Image from "next/image";
import { useDashboardStore } from "@/lib/store";
import { CIRCUITS, DRIVERS } from "@/lib/constants";
import { DRIVER_IMAGES, DRIVER_FALLBACK } from "@/lib/images";
import { getResults, type ResultRecord } from "@/lib/api";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

const TT = { backgroundColor: "#18181B", border: "1px solid rgba(255,255,255,0.06)", borderRadius: 8 };

function Skeleton({ className = "" }: { className?: string }) {
  return <div className={`animate-pulse bg-[--color-surface-2] rounded-lg ${className}`} />;
}

export default function ResultsPage() {
  const { selectedCircuit, setCircuit } = useDashboardStore();
  const [results, setResults] = useState<ResultRecord[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadData = useCallback(async (cir: string) => {
    setLoading(true); setError(null); setResults([]);
    try {
      const res = await getResults(cir);
      setResults(res.results);
    } catch { setError("Could not load results. Ensure backend is running."); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { loadData(selectedCircuit); }, [selectedCircuit, loadData]);

  const meta = CIRCUITS.find(c => c.name === selectedCircuit);

  // Position change data
  const posData = results.filter(r => r.Position && r.GridPosition).map(r => ({
    driver: DRIVERS[r.Driver]?.name || r.Driver,
    abbr: r.Driver,
    change: r.GridPosition - r.Position,
    position: r.Position,
    grid: r.GridPosition,
    points: r.Points,
    status: r.Status,
    color: DRIVERS[r.Driver]?.color || "#888",
  }));

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap gap-3 items-center">
        <select value={selectedCircuit} onChange={e => setCircuit(e.target.value)}
          className="bg-[--color-surface-1] border border-[--color-border] rounded-lg px-4 py-2 text-sm text-[--color-text-primary] focus:outline-none">
          {CIRCUITS.map(c => <option key={c.name} value={c.name}>{c.display}</option>)}
        </select>
        {meta && <span className="label-xs">{meta.country} · {meta.distanceKm} km</span>}
      </div>

      {loading && (
        <div className="space-y-4">
          <div className="glass-card p-6 text-center">
            <div className="inline-block w-6 h-6 border-2 border-[--color-accent] border-t-transparent rounded-full animate-spin mb-3" />
            <p className="text-sm text-[--color-text-secondary]">Loading results for <strong>{meta?.display}</strong>...</p>
          </div>
          <Skeleton className="h-[600px]" />
        </div>
      )}

      {error && <div className="glass-card p-6 border-l-4 border-red-500"><p className="text-sm text-red-400">{error}</p></div>}

      {!loading && results.length > 0 && (
        <>
          {/* Results Table */}
          <motion.div className="chart-panel" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
            <div className="chart-panel-header">
              <span className="text-sm font-semibold">Race Classification</span>
              <span className="label-xs">{meta?.display}</span>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-[--color-border] text-[--color-text-tertiary] text-xs uppercase tracking-wider">
                    <th className="px-4 py-3 text-left">Pos</th>
                    <th className="px-4 py-3 text-left">Driver</th>
                    <th className="px-4 py-3 text-left hidden md:table-cell">Team</th>
                    <th className="px-4 py-3 text-center">Grid</th>
                    <th className="px-4 py-3 text-center">+/-</th>
                    <th className="px-4 py-3 text-center">Pts</th>
                    <th className="px-4 py-3 text-left hidden sm:table-cell">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {posData.map((r, i) => (
                    <tr key={r.abbr} className="border-b border-[--color-border]/50 hover:bg-[--color-surface-2]/30 transition-colors">
                      <td className="px-4 py-3 font-bold" style={{ color: i < 3 ? r.color : undefined }}>
                        {r.position}
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-2">
                          <div className="w-7 h-7 rounded-full overflow-hidden relative flex-shrink-0 border" style={{ borderColor: r.color }}>
                            <Image src={DRIVER_IMAGES[r.abbr] || DRIVER_FALLBACK} alt={r.driver} fill className="object-cover object-top"
                              onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }} />
                          </div>
                          <div>
                            <div className="font-semibold">{r.driver}</div>
                            <div className="text-[10px] text-[--color-text-tertiary] md:hidden">{DRIVERS[r.abbr]?.team}</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-4 py-3 text-[--color-text-secondary] hidden md:table-cell">{DRIVERS[r.abbr]?.team}</td>
                      <td className="px-4 py-3 text-center text-[--color-text-tertiary]">{r.grid}</td>
                      <td className="px-4 py-3 text-center font-medium">
                        <span className={r.change > 0 ? "text-green-400" : r.change < 0 ? "text-red-400" : "text-[--color-text-tertiary]"}>
                          {r.change > 0 ? `▲${r.change}` : r.change < 0 ? `▼${Math.abs(r.change)}` : "—"}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-center font-bold" style={{ color: r.points > 0 ? "#FFD700" : undefined }}>
                        {r.points || "—"}
                      </td>
                      <td className="px-4 py-3 hidden sm:table-cell">
                        <span className={`text-xs px-2 py-0.5 rounded ${r.status === "Finished" ? "text-green-400 bg-green-500/10" : "text-red-400 bg-red-500/10"}`}>
                          {r.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </motion.div>

          {/* Position Changes Chart */}
          <motion.div className="chart-panel" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <div className="chart-panel-header"><span className="text-sm font-semibold">Positions Gained / Lost</span></div>
            <div className="chart-panel-body">
              <ResponsiveContainer width="100%" height={350}>
                <BarChart data={posData.sort((a, b) => b.change - a.change)}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#27272A" />
                  <XAxis dataKey="abbr" stroke="#52525B" fontSize={10} />
                  <YAxis stroke="#52525B" fontSize={10} />
                  <Tooltip contentStyle={TT} formatter={(v) => `${Number(v) > 0 ? "+" : ""}${v} positions`} />
                  <Bar dataKey="change" radius={[4, 4, 0, 0]}>
                    {posData.sort((a, b) => b.change - a.change).map((r, i) => (
                      <rect key={i} fill={r.change >= 0 ? "#00FF88" : "#FF4B4B"} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </motion.div>
        </>
      )}

      {!loading && !error && results.length === 0 && (
        <div className="glass-card p-8 text-center"><p className="text-sm text-[--color-text-tertiary]">No results. Select a circuit.</p></div>
      )}
    </div>
  );
}
