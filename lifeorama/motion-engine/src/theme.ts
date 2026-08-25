// ─────────────────────────────────────────────────────────────────────────────
// LOR theme (UNCHANGED). All existing LOR templates/components import these two
// exports directly — they must keep their exact values so LOR renders identically.
// ─────────────────────────────────────────────────────────────────────────────
export const theme = {
  bg: "#0A0E16",
  bgGradientTo: "#121A2B",
  text: "#F5F7FA",
  textDim: "#8B97AC",
  accent: "#4FD8FF",
  accentDim: "#2C5066",
  danger: "#FF5D5D",
  font: "-apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif",
};

export const bgStyle: React.CSSProperties = {
  background: `linear-gradient(135deg, ${theme.bg} 0%, ${theme.bgGradientTo} 100%)`,
};

// ─────────────────────────────────────────────────────────────────────────────
// Brand registry (additive). Default brand = "lor" reproduces the values above,
// so anything that doesn't opt into a brand behaves exactly as before.
// WealthDelay = cream / forest-green / gold, Plus Jakarta Sans (loaded in fonts.ts).
// ─────────────────────────────────────────────────────────────────────────────
export type BrandName = "lor" | "wealthdelay" | "wiredwrong" | "forcedecoded" | "careos" | "executor";

export type Brand = {
  font: string;
  isDark: boolean; // true = light text on a dark bg (lor/forcedecoded/wiredwrong); false = light/cream bg
  text: string;
  textDim: string;
  accent: string;
  accentDim: string;
  danger: string;
  // page backgrounds
  bg: string; // standard scene background (CSS background value)
  heroBg: string; // dark/hero background for hooks + CTAs
  onHero: string; // primary text color on the hero background
  onHeroDim: string; // secondary text color on the hero background
  // finance palette
  green: string;
  greenDark: string;
  forest: string;
  gold: string;
  mint: string;
  ink: string;
  card: string; // card / surface fill on a light background
  watermark: string; // small brand mark color (top corner)
  watermarkText: string; // small brand mark label
  captionBg: string; // caption strip gradient
  captionText: string;
};

const WJ = "'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif";

export const brands: Record<BrandName, Brand> = {
  lor: {
    font: theme.font,
    isDark: true,
    text: theme.text,
    textDim: theme.textDim,
    accent: theme.accent,
    accentDim: theme.accentDim,
    danger: theme.danger,
    bg: `linear-gradient(135deg, ${theme.bg} 0%, ${theme.bgGradientTo} 100%)`,
    heroBg: `linear-gradient(135deg, ${theme.bg} 0%, ${theme.bgGradientTo} 100%)`,
    onHero: theme.text,
    onHeroDim: theme.textDim,
    green: theme.accent,
    greenDark: theme.accentDim,
    forest: theme.bg,
    gold: "#FFD36E",
    mint: theme.accent,
    ink: theme.text,
    card: "#1A2233",
    watermark: "rgba(255,255,255,0.55)",
    watermarkText: "LIFE · O · RAMA",
    captionBg: "linear-gradient(to top, rgba(0,0,0,0.72), rgba(0,0,0,0))",
    captionText: "#fff",
  },
  wealthdelay: {
    font: WJ,
    isDark: false,
    text: "#1d1d1f",
    textDim: "#6e6e73",
    accent: "#16A34A",
    accentDim: "#15803d",
    danger: "#DC2626",
    bg: "linear-gradient(160deg, #FDFAF5 0%, #F7F2E8 100%)",
    heroBg: "linear-gradient(150deg, #052E16 0%, #16A34A 140%)",
    onHero: "#FFFFFF",
    onHeroDim: "#BBF7D0",
    green: "#16A34A",
    greenDark: "#15803d",
    forest: "#052E16",
    gold: "#F0B237",
    mint: "#86EFAC",
    ink: "#1d1d1f",
    card: "#FFFFFF",
    watermark: "rgba(5,46,22,0.45)",
    watermarkText: "WEALTHDELAY",
    captionBg: "linear-gradient(to top, rgba(5,46,22,0.10), rgba(5,46,22,0))",
    captionText: "#1d1d1f",
  },
  careos: {
    font: WJ,
    isDark: false,
    text: "#2D3436",
    textDim: "#6B7A77",
    accent: "#0F766E",
    accentDim: "#7FBDB5",
    danger: "#C0392B",
    bg: "linear-gradient(160deg, #FBF7F0 0%, #F3ECDF 100%)",
    heroBg: "linear-gradient(150deg, #0B3B36 0%, #157A6E 140%)",
    onHero: "#FFF7EC",
    onHeroDim: "#A7D8CE",
    green: "#59A96A",
    greenDark: "#3D7A4C",
    forest: "#134E4A",
    gold: "#E0A83C",
    mint: "#99E2D0",
    ink: "#2D3436",
    card: "#FFFFFF",
    watermark: "rgba(19,78,74,0.45)",
    watermarkText: "CARE OS",
    captionBg: "linear-gradient(to top, rgba(19,78,74,0.10), rgba(19,78,74,0))",
    captionText: "#2D3436",
  },
  executor: {
    font: WJ,
    isDark: false,
    text: "#26303E",
    textDim: "#6E7787",
    accent: "#46689B",
    accentDim: "#A9BCD8",
    danger: "#B4433A",
    bg: "linear-gradient(160deg, #FAF8F3 0%, #F1EDE4 100%)",
    heroBg: "linear-gradient(150deg, #1B2740 0%, #46689B 140%)",
    onHero: "#F7F5EF",
    onHeroDim: "#B9C7DE",
    green: "#59876B",
    greenDark: "#3D6350",
    forest: "#1B2740",
    gold: "#C9A227",
    mint: "#A9BCD8",
    ink: "#26303E",
    card: "#FFFFFF",
    watermark: "rgba(27,39,64,0.45)",
    watermarkText: "EXECUTOR'S CHECKLIST",
    captionBg: "linear-gradient(to top, rgba(27,39,64,0.10), rgba(27,39,64,0))",
    captionText: "#26303E",
  },
  forcedecoded: {
    font: theme.font,
    isDark: true,
    text: "#F2F5FA",
    textDim: "#93A3BC",
    accent: "#5B9DFF",
    accentDim: "#24406B",
    danger: "#FF5D5D",
    bg: "linear-gradient(135deg, #0B1220 0%, #101B33 100%)",
    heroBg: "linear-gradient(135deg, #0B1220 0%, #12264D 100%)",
    onHero: "#F2F5FA",
    onHeroDim: "#93A3BC",
    green: "#3DDC97",
    greenDark: "#1B6B4A",
    forest: "#2E5BBA",
    gold: "#FFC94D",
    mint: "#5B9DFF",
    ink: "#F2F5FA",
    card: "#17233B",
    watermark: "rgba(255,255,255,0.55)",
    watermarkText: "FORCE DECODED",
    captionBg: "linear-gradient(to top, rgba(0,0,0,0.72), rgba(0,0,0,0))",
    captionText: "#fff",
  },
  wiredwrong: {
    font: theme.font,
    isDark: true,
    text: theme.text,
    textDim: theme.textDim,
    accent: "#FF4D4D",
    accentDim: "#7A1C1C",
    danger: "#FF5D5D",
    bg: `linear-gradient(135deg, ${theme.bg} 0%, ${theme.bgGradientTo} 100%)`,
    heroBg: `linear-gradient(135deg, #0A0E16 0%, #1A0505 100%)`,
    onHero: theme.text,
    onHeroDim: theme.textDim,
    green: "#FF4D4D",
    greenDark: "#7A1C1C",
    forest: "#0A0E16",
    gold: "#FFD36E",
    mint: "#FF4D4D",
    ink: theme.text,
    card: "#1A2233",
    watermark: "rgba(255,255,255,0.55)",
    watermarkText: "WIRED WRONG",
    captionBg: "linear-gradient(to top, rgba(0,0,0,0.72), rgba(0,0,0,0))",
    captionText: "#fff",
  },
};

export const getBrand = (name?: BrandName): Brand => brands[name ?? "lor"];
