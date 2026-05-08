"use client";
import { useEffect, useCallback, useState } from "react";
import { motion } from "framer-motion";
import Image from "next/image";
import { useDashboardStore } from "@/lib/store";
import { TEAMS, DRIVERS, CIRCUITS } from "@/lib/constants";
import { TEAM_LOGOS, DRIVER_IMAGES, DRIVER_FALLBACK } from "@/lib/images";
import { getLaps, type LapRecord } from "@/lib/api";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts";

const TT = { backgroundColor: "#18181B", border: "1px solid rgba(255,255,255,0.06)", borderRadius: 8 };
const teamKeys = Object.keys(TEAMS);

function Skeleton({ className = "" }: { className?: string }) {
  return <div className={`animate-pulse bg-[--color-surface-2] rounded-lg ${className}`} />;
}

export default function TeamPage() {
  const { selectedTeam, selectedCircuit, setTeam, setCircuit, setAccent } = useDashboardStore();
  const [laps, setLaps] = useState<LapRecord[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const team = TEAMS[selectedTeam] || TEAMS[teamKeys[0]];
  const [d1, d2] = team.drivers;

  useEffect(() => { setAccent(team.color); }, [selectedTeam, team, setAccent]);

  const loadData = useCallback(async (cir: string) => {
    setLoading(true); setError(null); setLaps([]);
    try { const res = await getLaps(cir); setLaps(res.laps); }
    catch { setError("Could not load lap data. Ensure backend is running."); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { loadData(selectedCircuit); }, [selectedCircuit, loadData]);

  const d1Laps = laps.filter(l => l.Driver === d1);
  const d2Laps = laps.filter(l => l.Driver === d2);
  const avg = (arr: number[]) => arr.length ? arr.reduce((a, b) => a + b, 0) / arr.length : 0;

  const compData = d1Laps.length > 0 || d2Laps.length > 0 ? [
    { metric: "Avg Lap (s)", [d1]: +(avg(d1Laps.filter(l => l.LapTime).map(l => l.LapTime!)).toFixed(2)), [d2]: +(avg(d2Laps.filter(l => l.LapTime).map(l => l.LapTime!)).toFixed(2)) },
    { metric: "Best Lap (s)", [d1]: d1Laps.filter(l => l.LapTime).length ? +Math.min(...d1Laps.filter(l => l.LapTime).map(l => l.LapTime!)).toFixed(2) : 0, [d2]: d2Laps.filter(l => l.LapTime).length ? +Math.min(...d2Laps.filter(l => l.LapTime).map(l => l.LapTime!)).toFixed(2) : 0 },
    { metric: "Laps", [d1]: d1Laps.length, [d2]: d2Laps.length },
  ] : [];

  const teamPace = Object.values(TEAMS).map(t => {
    const tLaps = laps.filter(l => t.drivers.includes(l.Driver)).map(l => l.LapTime || 0).filter(v => v > 0);
    tLaps.sort((a, b) => a - b);
    const median = tLaps.length ? tLaps[Math.floor(tLaps.length / 2)] : 0;
    return { team: t.short, median, color: t.color };
  }).filter(t => t.median > 0).sort((a, b) => a.median - b.median);

  const best = teamPace[0]?.median || 0;
  const paceData = teamPace.map(t => ({ ...t, delta: +(t.median - best).toFixed(3) }));

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap gap-3">
        <select value={selectedTeam} onChange={e => setTeam(e.target.value)}
          className="bg-[--color-surface-1] border border-[--color-border] rounded-lg px-4 py-2 text-sm text-[--color-text-primary] focus:outline-none">
          {teamKeys.map(k => <option key={k} value={k}>{TEAMS[k].short}</option>)}
        </select>
        <select value={selectedCircuit} onChange={e => setCircuit(e.target.value)}
          className="bg-[--color-surface-1] border border-[--color-border] rounded-lg px-4 py-2 text-sm text-[--color-text-primary] focus:outline-none">
          {CIRCUITS.map(c => <option key={c.name} value={c.name}>{c.display}</option>)}
        </select>
      </div>

      {/* Team Hero */}
      <motion.div key={selectedTeam} className="relative overflow-hidden rounded-2xl"
        style={{ background: `linear-gradient(135deg, ${team.color}15, transparent)` }}
        initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <div className="h-1 w-full" style={{ background: `linear-gradient(90deg, ${team.color}, transparent)` }} />
        <div className="p-4 md:p-6 flex items-center gap-4 md:gap-6 flex-wrap">
          {TEAM_LOGOS[selectedTeam] && (
            <div className="w-16 h-16 md:w-20 md:h-20 flex-shrink-0 relative">
              <Image src={TEAM_LOGOS[selectedTeam]} alt={team.short} fill className="object-contain"
                onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }} />
            </div>
          )}
          <div className="flex-1 min-w-0">
            <h1 className="text-2xl md:text-3xl font-bold truncate" style={{ color: team.color }}>{team.name}</h1>
            <p className="text-sm text-[--color-text-tertiary] mt-1">{team.car}</p>
          </div>
          <div className="flex items-center gap-3">
            {[d1, d2].map(d => (
              <div key={d} className="flex items-center gap-2">
                <div className="w-10 h-10 rounded-full overflow-hidden relative border-2" style={{ borderColor: DRIVERS[d]?.color }}>
                  <Image src={DRIVER_IMAGES[d] || DRIVER_FALLBACK} alt={DRIVERS[d]?.name || d} fill className="object-cover object-top"
                    onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }} />
                </div>
                <div className="hidden md:block">
                  <div className="text-sm font-semibold">{DRIVERS[d]?.name}</div>
                  <div className="text-[10px] text-[--color-text-tertiary]">#{DRIVERS[d]?.number}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </motion.div>

      {loading && (
        <div className="space-y-4">
          <div className="glass-card p-6 text-center">
            <div className="inline-block w-6 h-6 border-2 border-[--color-accent] border-t-transparent rounded-full animate-spin mb-3" />
            <p className="text-sm text-[--color-text-secondary]">Loading <strong>{selectedCircuit}</strong> data...</p>
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4"><Skeleton className="h-[340px]" /><Skeleton className="h-[340px]" /></div>
        </div>
      )}

      {error && <div className="glass-card p-6 border-l-4 border-red-500"><p className="text-sm text-red-400">{error}</p></div>}

      {!loading && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {compData.length > 0 && (
            <motion.div className="chart-panel" key={`h-${selectedTeam}-${selectedCircuit}`} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
              <div className="chart-panel-header"><span className="text-sm font-semibold">Teammate H2H</span></div>
              <div className="chart-panel-body">
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={compData} layout="vertical"><CartesianGrid strokeDasharray="3 3" stroke="#27272A" />
                    <XAxis type="number" stroke="#52525B" fontSize={10} /><YAxis dataKey="metric" type="category" stroke="#52525B" fontSize={11} width={100} />
                    <Tooltip contentStyle={TT} /><Legend />
                    <Bar dataKey={d1} name={DRIVERS[d1]?.name} fill={DRIVERS[d1]?.color} radius={[0, 4, 4, 0]} />
                    <Bar dataKey={d2} name={DRIVERS[d2]?.name} fill={DRIVERS[d2]?.color} radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </motion.div>
          )}
          {paceData.length > 0 && (
            <motion.div className="chart-panel" key={`p-${selectedCircuit}`} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
              <div className="chart-panel-header"><span className="text-sm font-semibold">Team Pace Ranking</span></div>
              <div className="chart-panel-body">
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={paceData} layout="vertical"><CartesianGrid strokeDasharray="3 3" stroke="#27272A" />
                    <XAxis type="number" stroke="#52525B" fontSize={10} /><YAxis dataKey="team" type="category" stroke="#52525B" fontSize={11} width={100} />
                    <Tooltip contentStyle={TT} formatter={(v) => `+${v}s`} /><Bar dataKey="delta" fill="#00D4FF" radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </motion.div>
          )}
        </div>
      )}

      {!loading && !error && compData.length === 0 && paceData.length === 0 && (
        <div className="glass-card p-8 text-center"><p className="text-sm text-[--color-text-tertiary]">No data loaded.</p></div>
      )}
    </div>
  );
}
