// F1 Media URLs — Driver headshots, team logos, F1 branding
// Uses the official Formula 1 media CDN (publicly accessible)

// ─── F1 Logo (inline SVG data URI) ──────────────────────────────────────────
export const F1_LOGO = "/f1-logo.svg";

// ─── Driver Headshots ────────────────────────────────────────────────────────
// Pattern: official F1 media CDN headshots
const DRIVER_IMG_BASE = "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers";

export const DRIVER_IMAGES: Record<string, string> = {
  VER: `${DRIVER_IMG_BASE}/M/MAXVER01_Max_Verstappen/maxver01.png`,
  LAW: `${DRIVER_IMG_BASE}/L/LIALAW01_Liam_Lawson/lialaw01.png`,
  NOR: `${DRIVER_IMG_BASE}/L/LANNOR01_Lando_Norris/lannor01.png`,
  PIA: `${DRIVER_IMG_BASE}/O/OSCPIA01_Oscar_Piastri/oscpia01.png`,
  LEC: `${DRIVER_IMG_BASE}/C/CHALEC01_Charles_Leclerc/chalec01.png`,
  HAM: `${DRIVER_IMG_BASE}/L/LEWHAM01_Lewis_Hamilton/lewham01.png`,
  RUS: `${DRIVER_IMG_BASE}/G/GEORUS01_George_Russell/georus01.png`,
  ANT: `${DRIVER_IMG_BASE}/A/ANDANT01_Andrea_Kimi_Antonelli/andant01.png`,
  ALO: `${DRIVER_IMG_BASE}/F/FERALO01_Fernando_Alonso/feralo01.png`,
  STR: `${DRIVER_IMG_BASE}/L/LANSTR01_Lance_Stroll/lanstr01.png`,
  GAS: `${DRIVER_IMG_BASE}/P/PIEGAS01_Pierre_Gasly/piegas01.png`,
  DOO: `${DRIVER_IMG_BASE}/J/JACDOO01_Jack_Doohan/jacdoo01.png`,
  ALB: `${DRIVER_IMG_BASE}/A/ALEALB01_Alexander_Albon/alealb01.png`,
  SAI: `${DRIVER_IMG_BASE}/C/CARSAI01_Carlos_Sainz/carsai01.png`,
  TSU: `${DRIVER_IMG_BASE}/Y/YUKTSU01_Yuki_Tsunoda/yuktsu01.png`,
  HAD: `${DRIVER_IMG_BASE}/I/ISAHAD01_Isack_Hadjar/isahad01.png`,
  HUL: `${DRIVER_IMG_BASE}/N/NICHUL01_Nico_Hulkenberg/nichul01.png`,
  BOR: `${DRIVER_IMG_BASE}/G/GABBOR01_Gabriel_Bortoleto/gabbor01.png`,
  OCO: `${DRIVER_IMG_BASE}/E/ESTOCO01_Esteban_Ocon/estoco01.png`,
  BEA: `${DRIVER_IMG_BASE}/O/OLIBEA01_Oliver_Bearman/olibea01.png`,
};

// ─── Team Logos ──────────────────────────────────────────────────────────────
const TEAM_LOGO_BASE = "https://media.formula1.com/content/dam/fom-website/teams/2025";

export const TEAM_LOGOS: Record<string, string> = {
  redbull: `${TEAM_LOGO_BASE}/red-bull-racing-logo.png`,
  mclaren: `${TEAM_LOGO_BASE}/mclaren-logo.png`,
  ferrari: `${TEAM_LOGO_BASE}/ferrari-logo.png`,
  mercedes: `${TEAM_LOGO_BASE}/mercedes-logo.png`,
  aston: `${TEAM_LOGO_BASE}/aston-martin-logo.png`,
  alpine: `${TEAM_LOGO_BASE}/alpine-logo.png`,
  williams: `${TEAM_LOGO_BASE}/williams-logo.png`,
  rb: `${TEAM_LOGO_BASE}/rb-logo.png`,
  sauber: `${TEAM_LOGO_BASE}/kick-sauber-logo.png`,
  haas: `${TEAM_LOGO_BASE}/haas-logo.png`,
};

// Fallback for broken images
export const DRIVER_FALLBACK = "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/driver_fallback.png";
export const TEAM_FALLBACK = "";
