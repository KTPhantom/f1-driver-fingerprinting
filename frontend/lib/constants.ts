// F1 Teams, Drivers, Circuits — 2025 Season Constants

export interface Team {
  name: string; short: string; color: string; accent: string;
  car: string; drivers: [string, string];
}

export interface Driver {
  abbr: string; name: string; number: number; nationality: string;
  team: string; color: string;
}

export interface Circuit {
  display: string; name: string; country: string; type: string; distanceKm: number;
}

export const TEAMS: Record<string, Team> = {
  redbull: { name: "Red Bull Racing", short: "Red Bull", color: "#3671C6", accent: "#1B3A67", car: "RB21", drivers: ["VER", "LAW"] },
  mclaren: { name: "McLaren", short: "McLaren", color: "#FF8000", accent: "#47290E", car: "MCL39", drivers: ["NOR", "PIA"] },
  ferrari: { name: "Scuderia Ferrari", short: "Ferrari", color: "#E8002D", accent: "#470010", car: "SF-25", drivers: ["LEC", "HAM"] },
  mercedes: { name: "Mercedes-AMG Petronas", short: "Mercedes", color: "#27F4D2", accent: "#0D4D42", car: "W16", drivers: ["RUS", "ANT"] },
  aston: { name: "Aston Martin", short: "Aston Martin", color: "#229971", accent: "#0D3D2D", car: "AMR25", drivers: ["ALO", "STR"] },
  alpine: { name: "Alpine", short: "Alpine", color: "#00A1E8", accent: "#0D3A54", car: "A525", drivers: ["GAS", "DOO"] },
  williams: { name: "Williams", short: "Williams", color: "#1868DB", accent: "#0F2D5A", car: "FW47", drivers: ["ALB", "SAI"] },
  rb: { name: "Racing Bulls", short: "Racing Bulls", color: "#6C98FF", accent: "#1E2D4D", car: "VCARB 02", drivers: ["TSU", "HAD"] },
  sauber: { name: "Kick Sauber", short: "Sauber", color: "#01C00E", accent: "#0A3D0D", car: "C45", drivers: ["HUL", "BOR"] },
  haas: { name: "Haas F1 Team", short: "Haas", color: "#B6BABD", accent: "#3A3C3E", car: "VF-25", drivers: ["OCO", "BEA"] },
};

export const DRIVERS: Record<string, Driver> = {
  // Red Bull
  VER: { abbr: "VER", name: "Max Verstappen", number: 1, nationality: "Dutch", team: "Red Bull", color: "#3671C6" },
  LAW: { abbr: "LAW", name: "Liam Lawson", number: 30, nationality: "New Zealander", team: "Red Bull", color: "#1B3A67" },
  // McLaren
  NOR: { abbr: "NOR", name: "Lando Norris", number: 4, nationality: "British", team: "McLaren", color: "#FF8000" },
  PIA: { abbr: "PIA", name: "Oscar Piastri", number: 81, nationality: "Australian", team: "McLaren", color: "#E06A00" },
  // Ferrari
  LEC: { abbr: "LEC", name: "Charles Leclerc", number: 16, nationality: "Monégasque", team: "Ferrari", color: "#E8002D" },
  HAM: { abbr: "HAM", name: "Lewis Hamilton", number: 44, nationality: "British", team: "Ferrari", color: "#FF5C5C" },
  // Mercedes
  RUS: { abbr: "RUS", name: "George Russell", number: 63, nationality: "British", team: "Mercedes", color: "#27F4D2" },
  ANT: { abbr: "ANT", name: "Andrea Kimi Antonelli", number: 12, nationality: "Italian", team: "Mercedes", color: "#18A38A" },
  // Aston Martin
  ALO: { abbr: "ALO", name: "Fernando Alonso", number: 14, nationality: "Spanish", team: "Aston Martin", color: "#229971" },
  STR: { abbr: "STR", name: "Lance Stroll", number: 18, nationality: "Canadian", team: "Aston Martin", color: "#165E46" },
  // Alpine
  GAS: { abbr: "GAS", name: "Pierre Gasly", number: 10, nationality: "French", team: "Alpine", color: "#00A1E8" },
  DOO: { abbr: "DOO", name: "Jack Doohan", number: 7, nationality: "Australian", team: "Alpine", color: "#007AB8" },
  // Williams
  ALB: { abbr: "ALB", name: "Alexander Albon", number: 23, nationality: "Thai", team: "Williams", color: "#1868DB" },
  SAI: { abbr: "SAI", name: "Carlos Sainz", number: 55, nationality: "Spanish", team: "Williams", color: "#1050A0" },
  // Racing Bulls
  TSU: { abbr: "TSU", name: "Yuki Tsunoda", number: 22, nationality: "Japanese", team: "Racing Bulls", color: "#6C98FF" },
  HAD: { abbr: "HAD", name: "Isack Hadjar", number: 6, nationality: "French", team: "Racing Bulls", color: "#4A6FCC" },
  // Sauber
  HUL: { abbr: "HUL", name: "Nico Hulkenberg", number: 27, nationality: "German", team: "Sauber", color: "#01C00E" },
  BOR: { abbr: "BOR", name: "Gabriel Bortoleto", number: 5, nationality: "Brazilian", team: "Sauber", color: "#00900A" },
  // Haas
  OCO: { abbr: "OCO", name: "Esteban Ocon", number: 31, nationality: "French", team: "Haas", color: "#B6BABD" },
  BEA: { abbr: "BEA", name: "Oliver Bearman", number: 87, nationality: "British", team: "Haas", color: "#8A8D90" },
};

export const CIRCUITS: Circuit[] = [
  { display: "Australian GP", name: "Australia", country: "Australia", type: "street", distanceKm: 5.278 },
  { display: "Chinese GP", name: "China", country: "China", type: "permanent", distanceKm: 5.451 },
  { display: "Japanese GP", name: "Japan", country: "Japan", type: "permanent", distanceKm: 5.807 },
  { display: "Bahrain GP", name: "Bahrain", country: "Bahrain", type: "permanent", distanceKm: 5.412 },
  { display: "Saudi Arabian GP", name: "Saudi Arabia", country: "Saudi Arabia", type: "street", distanceKm: 6.174 },
  { display: "Miami GP", name: "Miami", country: "USA", type: "street", distanceKm: 5.412 },
  { display: "Emilia Romagna GP", name: "Emilia Romagna", country: "Italy", type: "permanent", distanceKm: 4.909 },
  { display: "Monaco GP", name: "Monaco", country: "Monaco", type: "street", distanceKm: 3.337 },
  { display: "Spanish GP", name: "Spain", country: "Spain", type: "permanent", distanceKm: 4.657 },
  { display: "Canadian GP", name: "Canada", country: "Canada", type: "semi-permanent", distanceKm: 4.361 },
  { display: "Austrian GP", name: "Austria", country: "Austria", type: "permanent", distanceKm: 4.318 },
  { display: "British GP", name: "Great Britain", country: "UK", type: "permanent", distanceKm: 5.891 },
  { display: "Belgian GP", name: "Belgium", country: "Belgium", type: "permanent", distanceKm: 7.004 },
  { display: "Hungarian GP", name: "Hungary", country: "Hungary", type: "permanent", distanceKm: 4.381 },
  { display: "Dutch GP", name: "Netherlands", country: "Netherlands", type: "permanent", distanceKm: 4.259 },
  { display: "Italian GP", name: "Italy", country: "Italy", type: "permanent", distanceKm: 5.793 },
  { display: "Azerbaijan GP", name: "Azerbaijan", country: "Azerbaijan", type: "street", distanceKm: 6.003 },
  { display: "Singapore GP", name: "Singapore", country: "Singapore", type: "street", distanceKm: 4.940 },
  { display: "US GP", name: "United States", country: "USA", type: "permanent", distanceKm: 5.513 },
  { display: "Mexico City GP", name: "Mexico", country: "Mexico", type: "permanent", distanceKm: 4.304 },
  { display: "São Paulo GP", name: "São Paulo", country: "Brazil", type: "permanent", distanceKm: 4.309 },
  { display: "Las Vegas GP", name: "Las Vegas", country: "USA", type: "street", distanceKm: 6.201 },
  { display: "Qatar GP", name: "Qatar", country: "Qatar", type: "permanent", distanceKm: 5.380 },
  { display: "Abu Dhabi GP", name: "Abu Dhabi", country: "UAE", type: "semi-permanent", distanceKm: 5.281 },
];

export const DEFAULT_CIRCUITS = ["Australia", "Japan", "Great Britain", "Italy", "Spain", "Belgium"];

export const FEATURE_GROUPS: Record<string, string[]> = {
  braking: ["brake_mean", "brake_max", "brake_std", "brake_onset_pct", "brake_duration_pct", "deceleration_rate_mean", "deceleration_rate_max"],
  throttle: ["throttle_mean", "throttle_std", "throttle_max", "throttle_application_rate", "partial_throttle_pct", "full_throttle_pct", "throttle_smoothness"],
  cornering: ["speed_std", "speed_min", "speed_range", "lateral_g_mean", "lateral_g_max", "lateral_g_std"],
  gear_shift: ["gear_mean", "gear_std", "gear_changes_count", "upshift_speed_mean", "downshift_speed_mean"],
  speed_profile: ["speed_mean", "speed_max", "entry_speed", "exit_speed", "speed_delta"],
};

export const FEATURE_GROUP_COLORS: Record<string, string> = {
  braking: "#FF4B4B", throttle: "#00D4FF", cornering: "#FFD700",
  gear_shift: "#00FF88", speed_profile: "#FF69B4",
};

export function getDriverTeamKey(abbr: string): string | undefined {
  return Object.keys(TEAMS).find(k => TEAMS[k].drivers.includes(abbr));
}

export function getTeamForDriver(abbr: string): Team | undefined {
  const key = getDriverTeamKey(abbr);
  return key ? TEAMS[key] : undefined;
}
