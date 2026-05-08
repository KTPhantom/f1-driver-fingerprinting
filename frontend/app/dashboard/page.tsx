"use client";
import { motion } from "framer-motion";
import Image from "next/image";
import Link from "next/link";
import { TEAMS, DRIVERS } from "@/lib/constants";
import { TEAM_LOGOS, DRIVER_IMAGES, DRIVER_FALLBACK } from "@/lib/images";
import { useDashboardStore } from "@/lib/store";

const stagger = { visible: { transition: { staggerChildren: 0.06 } } };
const fadeUp = { hidden: { opacity: 0, y: 12 }, visible: { opacity: 1, y: 0 } };

export default function DashboardHome() {
  const { setDriver, setTeam } = useDashboardStore();

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold mb-1">Season Overview</h1>
        <p className="text-sm text-[--color-text-secondary]">2025 Formula 1 World Championship — Analytics Platform</p>
      </div>

      {/* Stats */}
      <motion.div className="grid grid-cols-2 md:grid-cols-4 gap-4" initial="hidden" animate="visible" variants={stagger}>
        {[
          { value: "24", label: "Races" },
          { value: "10", label: "Teams" },
          { value: "20", label: "Drivers" },
          { value: "30", label: "Features" },
        ].map(({ value, label }) => (
          <motion.div key={label} className="stat-card" variants={fadeUp}>
            <div className="text-3xl font-bold bg-gradient-to-r from-[#00D4FF] to-[#7B61FF] bg-clip-text text-transparent font-[family-name:var(--font-geist-mono)]">
              {value}
            </div>
            <div className="label-xs mt-1">{label}</div>
          </motion.div>
        ))}
      </motion.div>

      {/* Constructor Grid */}
      <div>
        <h2 className="text-lg font-semibold mb-4">Constructor Grid</h2>
        <motion.div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3"
          initial="hidden" animate="visible" variants={stagger}>
          {Object.entries(TEAMS).map(([key, team]) => (
            <motion.div key={team.short} variants={fadeUp}>
              <Link href="/dashboard/team" onClick={() => setTeam(key)}
                className="glass-card p-4 md:p-5 block cursor-pointer group hover:scale-[1.02] transition-transform"
                style={{ borderLeft: `3px solid ${team.color}` }}>
                <div className="flex items-center gap-3 mb-3">
                  {TEAM_LOGOS[key] && (
                    <div className="w-8 h-8 relative flex-shrink-0">
                      <Image src={TEAM_LOGOS[key]} alt={team.short} fill className="object-contain"
                        onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }} />
                    </div>
                  )}
                  <div className="min-w-0">
                    <div className="text-sm md:text-base font-bold truncate" style={{ color: team.color }}>{team.short}</div>
                    <div className="text-xs text-[--color-text-tertiary] truncate">{team.car}</div>
                  </div>
                </div>
                <div className="space-y-1.5">
                  {team.drivers.map(d => (
                    <div key={d} className="flex items-center gap-2">
                      <div className="w-6 h-6 rounded-full overflow-hidden relative flex-shrink-0 border" style={{ borderColor: DRIVERS[d]?.color }}>
                        <Image src={DRIVER_IMAGES[d] || DRIVER_FALLBACK} alt={DRIVERS[d]?.name || d} fill className="object-cover object-top"
                          onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }} />
                      </div>
                      <span className="text-xs text-[--color-text-secondary] truncate">{DRIVERS[d]?.name}</span>
                    </div>
                  ))}
                </div>
              </Link>
            </motion.div>
          ))}
        </motion.div>
      </div>

      {/* Methodology */}
      <div className="glass-card p-6">
        <h2 className="text-lg font-semibold mb-3">Platform Methodology</h2>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          {[
            { step: "01", title: "Acquire", desc: "Official telemetry via FastF1" },
            { step: "02", title: "Segment", desc: "100m overlapping windows" },
            { step: "03", title: "Extract", desc: "30-dim behavioral features" },
            { step: "04", title: "Embed", desc: "UMAP dimensionality reduction" },
            { step: "05", title: "Cluster", desc: "HDBSCAN density grouping" },
          ].map(({ step, title, desc }) => (
            <div key={step} className="text-center">
              <div className="text-[--color-accent] font-[family-name:var(--font-geist-mono)] text-xs mb-1">{step}</div>
              <div className="text-sm font-semibold">{title}</div>
              <div className="text-xs text-[--color-text-tertiary] mt-0.5">{desc}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
