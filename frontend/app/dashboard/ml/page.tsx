"use client";
import { useState, useEffect, useCallback } from "react";
import { motion } from "framer-motion";
import { DRIVERS } from "@/lib/constants";
import { useDashboardStore } from "@/lib/store";
import { runML, getMLStatus, getMLResults, type MLResults, type UmapPoint } from "@/lib/api";
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  BarChart, Bar, RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Legend } from "recharts";

const TT = { backgroundColor: "#18181B", border: "1px solid rgba(255,255,255,0.06)", borderRadius: 8 };

const PIPELINE_STEPS = [
  { key: "acquire", label: "Acquiring Telemetry", icon: "📡" },
  { key: "segment", label: "Micro-Segmenting", icon: "🔬" },
  { key: "features", label: "Extracting Features", icon: "🧮" },
  { key: "umap", label: "UMAP Embedding", icon: "🌐" },
  { key: "cluster", label: "HDBSCAN Clustering", icon: "🎯" },
  { key: "validate", label: "Cross-Track Validation", icon: "✅" },
];

export default function MLPage() {
  const [status, setStatus] = useState<string>("idle");
  const [results, setResults] = useState<MLResults | null>(null);
  const [tab, setTab] = useState<"overview" | "umap" | "crosstrack" | "features">("overview");
  const { mlProgress, setMlProgress } = useDashboardStore();

  const startPipeline = async () => {
    try {
      await runML();
      setStatus("running");
      setMlProgress("acquire");
      pollStatus();
    } catch { setStatus("error"); }
  };

  const pollStatus = useCallback(async () => {
    let step = 0;
    const interval = setInterval(async () => {
      try {
        const s = await getMLStatus();
        setStatus(s.status);
        // Simulate progress steps based on elapsed time
        if (s.status === "running" && step < PIPELINE_STEPS.length - 1) {
          step++;
          setMlProgress(PIPELINE_STEPS[step].key);
        }
        if (s.status === "complete") {
          clearInterval(interval);
          setMlProgress("");
          const r = await getMLResults();
          setResults(r);
        } else if (s.status === "error") {
          clearInterval(interval);
          setMlProgress("");
        }
      } catch { clearInterval(interval); }
    }, 5000);
  }, [setMlProgress]);

  useEffect(() => {
    getMLStatus().then(s => {
      setStatus(s.status);
      if (s.status === "complete") getMLResults().then(setResults);
    }).catch(() => {});
  }, []);

  const umapByDriver = results?.umap_points ? Object.entries(
    results.umap_points.reduce<Record<string, UmapPoint[]>>((acc, p) => {
      if (!acc[p.driver]) acc[p.driver] = [];
      acc[p.driver].push(p);
      return acc;
    }, {})
  ) : [];

  const featureData = results?.feature_importance ? Object.entries(results.feature_importance)
    .slice(0, 15).map(([name, value]) => ({ name: name.replace(/_/g, " "), value: +value.toFixed(1) })) : [];

  const profileDrivers = results?.drivers_analyzed?.slice(0, 4) || [];
  const profileKeys = results?.profiles ? Object.keys(Object.values(results.profiles)[0] || {}).slice(0, 8) : [];
  const radarData = profileKeys.map(key => {
    const row: Record<string, string | number> = { feature: key.replace(/_/g, " ").slice(0, 14) };
    profileDrivers.forEach(d => {
      const prof = results?.profiles?.[d];
      if (prof) {
        const vals = Object.values(results!.profiles).map(p => p[key] || 0);
        const min = Math.min(...vals), max = Math.max(...vals);
        row[d] = max > min ? +((prof[key] - min) / (max - min)).toFixed(2) : 0.5;
      }
    });
    return row;
  });

  const tabs = [
    { key: "overview" as const, label: "Overview" },
    { key: "umap" as const, label: "UMAP" },
    { key: "crosstrack" as const, label: "Cross-Track" },
    { key: "features" as const, label: "Features" },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center gap-4">
        <h1 className="text-2xl font-bold">ML Lab</h1>
        <div className={`px-3 py-1 rounded-full text-xs font-medium ${
          status === "idle" ? "bg-[--color-surface-2] text-[--color-text-tertiary]" :
          status === "running" ? "bg-yellow-500/20 text-yellow-400" :
          status === "complete" ? "bg-green-500/20 text-green-400" :
          "bg-red-500/20 text-red-400"
        }`}>{status}</div>
        {status !== "running" && (
          <button onClick={startPipeline}
            className="px-5 py-2 rounded-lg text-sm font-semibold bg-gradient-to-r from-[#00D4FF] to-[#7B61FF] text-white hover:opacity-90 transition-opacity">
            {status === "complete" ? "Re-run Pipeline" : "Run Pipeline"}
          </button>
        )}
      </div>

      {/* Pipeline Progress */}
      {status === "running" && (
        <motion.div className="glass-card p-6" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
          <div className="flex items-center gap-4 mb-4">
            <div className="w-6 h-6 border-2 border-yellow-400 border-t-transparent rounded-full animate-spin" />
            <p className="text-sm text-[--color-text-secondary]">Pipeline running...</p>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-6 gap-2">
            {PIPELINE_STEPS.map((step, i) => {
              const currentIdx = PIPELINE_STEPS.findIndex(s => s.key === mlProgress);
              const done = i < currentIdx;
              const active = i === currentIdx;
              return (
                <div key={step.key} className={`p-3 rounded-lg text-center transition-all ${
                  done ? "bg-green-500/10 border border-green-500/30" :
                  active ? "bg-yellow-500/10 border border-yellow-500/30 animate-pulse" :
                  "bg-[--color-surface-2]/50 border border-[--color-border]"
                }`}>
                  <div className="text-lg mb-1">{done ? "✅" : step.icon}</div>
                  <div className={`text-[10px] font-medium ${done ? "text-green-400" : active ? "text-yellow-400" : "text-[--color-text-tertiary]"}`}>
                    {step.label}
                  </div>
                </div>
              );
            })}
          </div>
        </motion.div>
      )}

      {/* Empty state */}
      {!results && status !== "running" && (
        <div className="glass-card p-12 text-center">
          <div className="text-6xl mb-4">🧬</div>
          <h2 className="text-xl font-semibold mb-2">Driver Fingerprinting Pipeline</h2>
          <p className="text-sm text-[--color-text-secondary] max-w-md mx-auto">
            UMAP + HDBSCAN unsupervised clustering on 30-dimensional behavioral features.
            Trains on 4 circuits, validates on 2 held-out circuits.
          </p>
        </div>
      )}

      {results && (
        <>
          <div className="flex gap-1 p-1 bg-[--color-surface-1] rounded-lg w-fit flex-wrap">
            {tabs.map(t => (
              <button key={t.key} onClick={() => setTab(t.key)}
                className={`px-4 py-2 rounded-md text-sm transition-colors ${
                  tab === t.key ? "bg-[--color-accent]/20 text-[--color-accent] font-medium" : "text-[--color-text-secondary] hover:text-[--color-text-primary]"
                }`}>{t.label}</button>
            ))}
          </div>

          {tab === "overview" && (
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              {[
                { v: results.train_segments.toLocaleString(), l: "Segments" },
                { v: results.cluster_metrics.n_clusters, l: "Clusters" },
                { v: results.cluster_metrics.silhouette.toFixed(3), l: "Silhouette" },
                { v: results.cluster_metrics.ari.toFixed(3), l: "ARI" },
                { v: `${(results.cross_track.overall_accuracy * 100).toFixed(1)}%`, l: "Cross-Track Acc" },
              ].map(({ v, l }) => (
                <motion.div key={l} className="stat-card" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
                  <div className="text-2xl font-bold font-[family-name:var(--font-geist-mono)] text-[--color-accent]">{v}</div>
                  <div className="label-xs mt-1">{l}</div>
                </motion.div>
              ))}
            </div>
          )}

          {tab === "umap" && (
            <div className="chart-panel">
              <div className="chart-panel-header"><span className="text-sm font-semibold">UMAP 2D Embedding</span></div>
              <div className="chart-panel-body">
                <ResponsiveContainer width="100%" height={500}>
                  <ScatterChart><CartesianGrid strokeDasharray="3 3" stroke="#27272A" />
                    <XAxis dataKey="x" name="UMAP 1" stroke="#52525B" fontSize={10} />
                    <YAxis dataKey="y" name="UMAP 2" stroke="#52525B" fontSize={10} />
                    <Tooltip contentStyle={TT} />
                    {umapByDriver.map(([driver, points]) => (
                      <Scatter key={driver} name={DRIVERS[driver]?.name || driver} data={points} fill={DRIVERS[driver]?.color || "#888"} opacity={0.7} />
                    ))}
                  </ScatterChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}

          {tab === "crosstrack" && results.cross_track && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <div className="chart-panel">
                <div className="chart-panel-header"><span className="text-sm font-semibold">Per-Driver Accuracy</span></div>
                <div className="chart-panel-body">
                  <ResponsiveContainer width="100%" height={400}>
                    <BarChart data={Object.entries(results.cross_track.per_driver_accuracy)
                      .map(([d, a]) => ({ driver: DRIVERS[d]?.name || d, acc: +(a * 100).toFixed(1), fill: DRIVERS[d]?.color || "#888" }))
                      .sort((a, b) => b.acc - a.acc)} layout="vertical">
                      <CartesianGrid strokeDasharray="3 3" stroke="#27272A" />
                      <XAxis type="number" stroke="#52525B" fontSize={10} domain={[0, 100]} />
                      <YAxis dataKey="driver" type="category" stroke="#52525B" fontSize={11} width={120} />
                      <Tooltip contentStyle={TT} formatter={(v) => `${v}%`} />
                      <Bar dataKey="acc" fill="#00D4FF" radius={[0, 4, 4, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
              <div className="chart-panel">
                <div className="chart-panel-header"><span className="text-sm font-semibold">Behavioral Radar</span></div>
                <div className="chart-panel-body">
                  <ResponsiveContainer width="100%" height={400}>
                    <RadarChart data={radarData}><PolarGrid stroke="#27272A" />
                      <PolarAngleAxis dataKey="feature" tick={{ fill: "#A1A1AA", fontSize: 10 }} />
                      <PolarRadiusAxis domain={[0, 1]} tick={false} axisLine={false} />
                      <Legend />
                      {profileDrivers.map(d => (
                        <Radar key={d} name={DRIVERS[d]?.name || d} dataKey={d}
                          stroke={DRIVERS[d]?.color || "#888"} fill={DRIVERS[d]?.color || "#888"} fillOpacity={0.15} />
                      ))}
                    </RadarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          )}

          {tab === "features" && (
            <div className="chart-panel">
              <div className="chart-panel-header"><span className="text-sm font-semibold">Feature Importance (F-Statistic)</span></div>
              <div className="chart-panel-body">
                <ResponsiveContainer width="100%" height={450}>
                  <BarChart data={featureData} layout="vertical"><CartesianGrid strokeDasharray="3 3" stroke="#27272A" />
                    <XAxis type="number" stroke="#52525B" fontSize={10} /><YAxis dataKey="name" type="category" stroke="#52525B" fontSize={10} width={150} />
                    <Tooltip contentStyle={TT} /><Bar dataKey="value" fill="#00D4FF" radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
