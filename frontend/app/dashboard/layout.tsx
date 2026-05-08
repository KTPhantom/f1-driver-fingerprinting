"use client";
import { useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { Home, User, Car, Flag, FlaskConical, ChevronLeft, ChevronRight, Trophy, GitCompare } from "lucide-react";
import { useDashboardStore } from "@/lib/store";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Home", icon: Home },
  { href: "/dashboard/driver", label: "Driver", icon: User },
  { href: "/dashboard/team", label: "Team", icon: Car },
  { href: "/dashboard/track", label: "Track", icon: Flag },
  { href: "/dashboard/results", label: "Results", icon: Trophy },
  { href: "/dashboard/compare", label: "Compare", icon: GitCompare },
  { href: "/dashboard/ml", label: "ML Lab", icon: FlaskConical },
];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const accentColor = useDashboardStore(s => s.accentColor);

  // Apply accent color as CSS variable
  useEffect(() => {
    document.documentElement.style.setProperty("--accent-color", accentColor);
  }, [accentColor]);

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar — collapses to icon-only on mobile */}
      <aside className="hidden md:flex h-full w-[220px] flex-col border-r border-[--color-border] bg-[--color-surface-1]/80 backdrop-blur-xl flex-shrink-0">
        {/* Logo */}
        <div className="p-4 flex items-center gap-3 border-b border-[--color-border] h-[60px]">
          <img src="/f1-logo.svg" alt="F1" className="w-8 h-8 flex-shrink-0 object-contain" />
          <div className="overflow-hidden whitespace-nowrap">
            <div className="text-sm font-bold text-[--color-text-primary]">F1 Analytics</div>
            <div className="text-[10px] text-[--color-text-tertiary]">2025 Season</div>
          </div>
        </div>

        {/* Nav */}
        <nav className="flex-1 py-3 px-2 space-y-1 overflow-y-auto">
          {NAV_ITEMS.map(({ href, label, icon: Icon }) => {
            const active = pathname === href;
            return (
              <Link key={href} href={href}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all relative ${
                  active
                    ? "bg-[--color-accent]/10 text-[--color-accent]"
                    : "text-[--color-text-secondary] hover:text-[--color-text-primary] hover:bg-[--color-surface-2]/50"
                }`}>
                <Icon size={18} className="flex-shrink-0" />
                <span className="overflow-hidden whitespace-nowrap font-medium">{label}</span>
                {active && (
                  <motion.div layoutId="nav-active"
                    className="absolute left-0 w-[3px] h-5 rounded-r-full bg-[--color-accent]" />
                )}
              </Link>
            );
          })}
        </nav>
      </aside>

      {/* Mobile bottom nav */}
      <nav className="md:hidden fixed bottom-0 left-0 right-0 z-50 bg-[--color-surface-1]/95 backdrop-blur-xl border-t border-[--color-border] flex justify-around py-2 px-1">
        {NAV_ITEMS.slice(0, 5).map(({ href, label, icon: Icon }) => {
          const active = pathname === href;
          return (
            <Link key={href} href={href}
              className={`flex flex-col items-center gap-0.5 px-2 py-1 rounded-lg text-[10px] transition-colors ${
                active ? "text-[--color-accent]" : "text-[--color-text-tertiary]"
              }`}>
              <Icon size={18} />
              <span>{label}</span>
            </Link>
          );
        })}
      </nav>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top bar */}
        <header className="h-[60px] border-b border-[--color-border] bg-[--color-bg]/80 backdrop-blur-xl flex items-center px-4 md:px-6 flex-shrink-0">
          {/* Mobile logo */}
          <div className="md:hidden mr-3">
            <img src="/f1-logo.svg" alt="F1" className="w-7 h-7 object-contain" />
          </div>
          <div className="text-sm font-semibold text-[--color-text-primary]">
            {NAV_ITEMS.find(n => n.href === pathname)?.label || "Dashboard"}
          </div>
          <div className="ml-auto flex items-center gap-4">
            <div className="hidden sm:block text-xs text-[--color-text-tertiary] font-[family-name:var(--font-geist-mono)]">
              FastF1 2025
            </div>
            <Link href="/" className="text-xs text-[--color-text-tertiary] hover:text-[--color-text-secondary] transition-colors">
              ← Landing
            </Link>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto p-4 md:p-6 pb-20 md:pb-6">
          <AnimatePresence mode="wait">
            <motion.div key={pathname}
              initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.25 }}>
              {children}
            </motion.div>
          </AnimatePresence>
        </main>
      </div>
    </div>
  );
}
