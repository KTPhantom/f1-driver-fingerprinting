// Zustand store — global dashboard state (shared across all pages)
import { create } from "zustand";

interface DashboardStore {
  // ─── Selection state ───
  selectedDriver: string;
  selectedTeam: string;
  selectedCircuit: string;
  // ─── Theme ───
  accentColor: string;
  // ─── ML pipeline ───
  mlStatus: "idle" | "running" | "complete" | "error";
  mlProgress: string;
  // ─── Compare mode ───
  compareDrivers: string[];
  compareMode: boolean;
  // ─── Actions ───
  setDriver: (d: string) => void;
  setTeam: (t: string) => void;
  setCircuit: (c: string) => void;
  setAccent: (c: string) => void;
  setMlStatus: (s: "idle" | "running" | "complete" | "error") => void;
  setMlProgress: (p: string) => void;
  toggleCompareMode: () => void;
  addCompareDriver: (d: string) => void;
  removeCompareDriver: (d: string) => void;
  clearCompareDrivers: () => void;
}

export const useDashboardStore = create<DashboardStore>((set) => ({
  selectedDriver: "VER",
  selectedTeam: "redbull",
  selectedCircuit: "Australia",
  accentColor: "#00D4FF",
  mlStatus: "idle",
  mlProgress: "",
  compareDrivers: [],
  compareMode: false,
  setDriver: (d) => set({ selectedDriver: d }),
  setTeam: (t) => set({ selectedTeam: t }),
  setCircuit: (c) => set({ selectedCircuit: c }),
  setAccent: (c) => set({ accentColor: c }),
  setMlStatus: (s) => set({ mlStatus: s }),
  setMlProgress: (p) => set({ mlProgress: p }),
  toggleCompareMode: () => set((s) => ({ compareMode: !s.compareMode, compareDrivers: [] })),
  addCompareDriver: (d) => set((s) => ({
    compareDrivers: s.compareDrivers.includes(d) ? s.compareDrivers : [...s.compareDrivers, d].slice(0, 4),
  })),
  removeCompareDriver: (d) => set((s) => ({
    compareDrivers: s.compareDrivers.filter(x => x !== d),
  })),
  clearCompareDrivers: () => set({ compareDrivers: [] }),
}));
