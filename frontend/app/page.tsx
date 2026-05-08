"use client";
import { motion, useScroll, useTransform, useSpring, useInView } from "framer-motion";
import { useRef, useEffect, useState } from "react";
import Link from "next/link";
import Image from "next/image";
import { Activity, Brain, Layers, Target, Zap, GitBranch, ArrowRight, ExternalLink } from "lucide-react";
import { TEAMS, DRIVERS } from "@/lib/constants";
import { TEAM_LOGOS } from "@/lib/images";

// ─── Animated Counter ────────────────────────────────────────────────────────
function Counter({ value, suffix = "", label }: { value: number; suffix?: string; label: string }) {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, amount: 0.5 });
  const [display, setDisplay] = useState(0);
  useEffect(() => {
    if (!isInView) return;
    let start = 0;
    const step = value / 40;
    const timer = setInterval(() => {
      start += step;
      if (start >= value) { setDisplay(value); clearInterval(timer); }
      else setDisplay(Math.floor(start));
    }, 25);
    return () => clearInterval(timer);
  }, [isInView, value]);
  return (
    <motion.div ref={ref} className="stat-card text-center"
      initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }} transition={{ duration: 0.5 }}>
      <div className="text-4xl font-bold bg-gradient-to-r from-[#00D4FF] to-[#7B61FF] bg-clip-text text-transparent font-[family-name:var(--font-geist-mono)]">
        {display}{suffix}
      </div>
      <div className="label-xs mt-2">{label}</div>
    </motion.div>
  );
}

// ─── Pipeline Step ───────────────────────────────────────────────────────────
function PipelineStep({ icon: Icon, title, desc, color, index }: {
  icon: React.ElementType; title: string; desc: string; color: string; index: number;
}) {
  return (
    <motion.div className="flex flex-col items-center text-center min-w-[180px]"
      initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }} transition={{ duration: 0.5, delay: index * 0.12 }}>
      <div className="w-14 h-14 rounded-xl flex items-center justify-center mb-3"
        style={{ background: `${color}20`, border: `1px solid ${color}40` }}>
        <Icon size={24} style={{ color }} />
      </div>
      <h3 className="text-sm font-semibold text-[--color-text-primary] mb-1">{title}</h3>
      <p className="text-xs text-[--color-text-secondary] max-w-[160px]">{desc}</p>
      {index < 4 && (
        <div className="hidden md:block absolute mt-7 ml-[180px]">
          <ArrowRight size={16} className="text-[--color-text-tertiary]" />
        </div>
      )}
    </motion.div>
  );
}

// ─── Landing Page ────────────────────────────────────────────────────────────
export default function LandingPage() {
  const heroRef = useRef(null);
  const { scrollYProgress } = useScroll({ target: heroRef, offset: ["start start", "end start"] });
  const heroOpacity = useTransform(scrollYProgress, [0, 0.5], [1, 0]);
  const heroY = useTransform(scrollYProgress, [0, 0.5], [0, -80]);

  const teamEntries = Object.entries(TEAMS);

  return (
    <main className="min-h-screen">
      {/* ═══ HERO ═══ */}
      <section ref={heroRef} className="relative min-h-screen flex items-center justify-center overflow-hidden">
        {/* Animated grid background */}
        <div className="absolute inset-0 opacity-[0.03]"
          style={{ backgroundImage: "linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)", backgroundSize: "60px 60px" }} />
        {/* Glow orbs */}
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-[#3671C6] rounded-full blur-[180px] opacity-10" />
        <div className="absolute bottom-1/3 right-1/4 w-80 h-80 bg-[#E8002D] rounded-full blur-[180px] opacity-8" />

        <motion.div className="relative z-10 text-center px-6 max-w-4xl" style={{ opacity: heroOpacity, y: heroY }}>
          <motion.div className="label-xs mb-6 tracking-[0.2em]"
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2 }}>
            UNSUPERVISED MACHINE LEARNING × FORMULA 1
          </motion.div>
          <motion.h1 className="text-5xl md:text-7xl font-bold leading-[1.1] mb-6"
            initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3, duration: 0.7 }}>
            Can You Identify a Driver{" "}
            <span className="bg-gradient-to-r from-[#00D4FF] via-[#7B61FF] to-[#FF4BCD] bg-clip-text text-transparent">
              by Feel Alone?
            </span>
          </motion.h1>
          <motion.p className="text-lg text-[--color-text-secondary] max-w-2xl mx-auto mb-10"
            initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
            Behavioral fingerprinting for F1 drivers using 30-dimensional telemetry features,
            UMAP dimensionality reduction, and HDBSCAN density clustering.
          </motion.p>
          <motion.div className="flex gap-4 justify-center"
            initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.7 }}>
            <Link href="/dashboard"
              className="px-8 py-3.5 rounded-xl font-semibold text-sm bg-gradient-to-r from-[#00D4FF] to-[#7B61FF] text-white hover:opacity-90 transition-opacity flex items-center gap-2">
              Explore Dashboard <ArrowRight size={16} />
            </Link>
            <a href="#pipeline"
              className="px-8 py-3.5 rounded-xl font-semibold text-sm border border-[--color-border] text-[--color-text-secondary] hover:text-[--color-text-primary] hover:border-[--color-text-tertiary] transition-colors">
              View Methodology
            </a>
          </motion.div>
        </motion.div>

        {/* Scroll indicator */}
        <motion.div className="absolute bottom-8 left-1/2 -translate-x-1/2"
          animate={{ y: [0, 8, 0] }} transition={{ repeat: Infinity, duration: 2 }}>
          <div className="w-5 h-8 rounded-full border border-[--color-text-tertiary] flex justify-center pt-1.5">
            <div className="w-1 h-2 rounded-full bg-[--color-text-tertiary]" />
          </div>
        </motion.div>
      </section>

      {/* ═══ PIPELINE ═══ */}
      <section id="pipeline" className="py-24 px-6 max-w-6xl mx-auto">
        <motion.div className="text-center mb-16"
          initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }}>
          <div className="label-xs mb-3">THE PIPELINE</div>
          <h2 className="text-3xl md:text-4xl font-bold">From Raw Telemetry to Driver Identity</h2>
        </motion.div>
        <div className="flex flex-wrap justify-center gap-8 relative">
          <PipelineStep icon={Activity} title="Acquire" desc="High-frequency telemetry via FastF1 API" color="#3671C6" index={0} />
          <PipelineStep icon={Layers} title="Segment" desc="100m overlapping micro-windows" color="#FF8000" index={1} />
          <PipelineStep icon={Brain} title="Extract" desc="30 features across 5 dimensions" color="#27F4D2" index={2} />
          <PipelineStep icon={GitBranch} title="Embed" desc="UMAP: 30D → 2D manifold" color="#E8002D" index={3} />
          <PipelineStep icon={Target} title="Cluster" desc="HDBSCAN density-based grouping" color="#FFD700" index={4} />
        </div>
      </section>

      {/* ═══ METRICS ═══ */}
      <section className="py-24 px-6 bg-[--color-surface-1]/50">
        <div className="max-w-4xl mx-auto">
          <motion.div className="text-center mb-16"
            initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }}>
            <div className="label-xs mb-3">KEY RESULTS</div>
            <h2 className="text-3xl font-bold">Proving Behavioral Transferability</h2>
          </motion.div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Counter value={30} label="Behavioral Features" />
            <Counter value={10} label="Drivers Analyzed" />
            <Counter value={5} label="Behavioral Dimensions" />
            <Counter value={6} label="Circuits Validated" />
          </div>
        </div>
      </section>

      {/* ═══ TEAMS GRID ═══ */}
      <section className="py-24 px-6 max-w-6xl mx-auto">
        <motion.div className="text-center mb-16"
          initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }}>
          <div className="label-xs mb-3">2025 SEASON</div>
          <h2 className="text-3xl font-bold">The Grid</h2>
        </motion.div>
        <motion.div className="grid grid-cols-2 md:grid-cols-5 gap-3"
          initial="hidden" whileInView="visible" viewport={{ once: true }}
          variants={{ visible: { transition: { staggerChildren: 0.06 } } }}>
          {teamEntries.map(([key, team]) => (
            <motion.div key={team.short} className="glass-card p-4 cursor-pointer hover:scale-[1.02] transition-transform"
              style={{ borderLeft: `3px solid ${team.color}` }}
              variants={{ hidden: { opacity: 0, y: 12 }, visible: { opacity: 1, y: 0 } }}>
              <div className="flex items-center gap-2 mb-2">
                {TEAM_LOGOS[key] && (
                  <div className="w-6 h-6 relative flex-shrink-0">
                    <Image src={TEAM_LOGOS[key]} alt={team.short} fill className="object-contain"
                      onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }} />
                  </div>
                )}
                <div className="text-sm font-bold" style={{ color: team.color }}>{team.short}</div>
              </div>
              <div className="text-xs text-[--color-text-tertiary]">{team.car}</div>
              <div className="text-[11px] text-[--color-text-secondary] mt-2">
                {DRIVERS[team.drivers[0]]?.name} · {DRIVERS[team.drivers[1]]?.name}
              </div>
            </motion.div>
          ))}
        </motion.div>
      </section>

      {/* ═══ TECH STACK ═══ */}
      <section className="py-24 px-6 bg-[--color-surface-1]/50">
        <div className="max-w-4xl mx-auto text-center">
          <div className="label-xs mb-3">BUILT WITH</div>
          <h2 className="text-3xl font-bold mb-8">Technology Stack</h2>
          <div className="flex flex-wrap justify-center gap-3">
            {["FastF1", "UMAP", "HDBSCAN", "scikit-learn", "NumPy", "Pandas", "Next.js", "React", "Recharts", "Framer Motion", "FastAPI", "Tailwind CSS"].map((t) => (
              <span key={t} className="px-4 py-2 rounded-lg text-sm border border-[--color-border] text-[--color-text-secondary] bg-[--color-surface-1]">{t}</span>
            ))}
          </div>
        </div>
      </section>

      {/* ═══ CTA FOOTER ═══ */}
      <section className="py-32 px-6 text-center">
        <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }} transition={{ duration: 0.6 }}>
          <h2 className="text-4xl md:text-5xl font-bold mb-6">
            Ready to Explore the{" "}
            <span className="bg-gradient-to-r from-[#00D4FF] to-[#FF8000] bg-clip-text text-transparent">Data?</span>
          </h2>
          <p className="text-[--color-text-secondary] mb-10 max-w-lg mx-auto">
            Dive into the interactive dashboard. Analyze drivers, teams, circuits, and ML clustering results.
          </p>
          <Link href="/dashboard"
            className="inline-flex items-center gap-3 px-10 py-4 rounded-xl font-bold text-lg bg-gradient-to-r from-[#00D4FF] to-[#7B61FF] text-white hover:opacity-90 transition-all glow-accent">
            Enter Dashboard <ArrowRight size={20} />
          </Link>
          <div className="mt-8 flex gap-4 justify-center">
            <a href="https://github.com/KTPhantom" target="_blank" rel="noopener"
              className="flex items-center gap-2 text-sm text-[--color-text-tertiary] hover:text-[--color-text-secondary] transition-colors">
              <ExternalLink size={16} /> GitHub
            </a>
          </div>
        </motion.div>
      </section>
    </main>
  );
}
