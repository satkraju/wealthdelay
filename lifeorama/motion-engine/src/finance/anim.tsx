import { useCurrentFrame, useVideoConfig, interpolate, Easing } from "remotion";
import { useBrand } from "../brand";
import type { Brand } from "../theme";

// ── shared easing windows ────────────────────────────────────────────────────
export const useReveal = (delaySec = 0, riseFromPx = 24) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const local = Math.max(0, frame - delaySec * fps);
  const opacity = interpolate(local, [0, fps * 0.4], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const rise = interpolate(local, [0, fps * 0.45], [riseFromPx, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  return { opacity, rise, translate: `0px ${rise}px` };
};

// progress 0..1 over [delaySec, delaySec+durSec], eased out-cubic
export const useProgress = (delaySec = 0, durSec = 0.9) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const local = Math.max(0, frame - delaySec * fps);
  return interpolate(local, [0, durSec * fps], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
};

// ── count-up: animate the numeric run inside a label string ───────────────────
// "$140k" -> "$0k".."$140k" ; "$47,000" -> "$0".."$47,000" (commas preserved)
export const countUpString = (finalStr: string, progress: number): string => {
  const m = finalStr.match(/[\d,]*\d/);
  if (!m) return finalStr;
  const raw = m[0];
  const hadComma = raw.includes(",");
  const target = parseInt(raw.replace(/,/g, ""), 10);
  if (!isFinite(target)) return finalStr;
  const cur = Math.round(target * Math.min(1, Math.max(0, progress)));
  const shown = hadComma || target >= 1000 ? cur.toLocaleString("en-US") : String(cur);
  return finalStr.slice(0, m.index) + shown + finalStr.slice((m.index ?? 0) + raw.length);
};

// ── tone -> brand color ───────────────────────────────────────────────────────
export const toneColor = (b: Brand, tone?: "green" | "forest" | "gold" | "ink"): string => {
  switch (tone) {
    case "forest":
      return b.forest;
    case "gold":
      return b.gold;
    case "ink":
      return b.ink;
    case "green":
    default:
      return b.green;
  }
};

// ── brand-aware finance text (rises + fades in) ───────────────────────────────
export const FinText: React.FC<{
  children: React.ReactNode;
  size?: number;
  weight?: number;
  color?: string;
  delaySec?: number;
  onHero?: boolean;
  maxWidth?: string | number;
  align?: "center" | "left";
}> = ({ children, size = 64, weight = 800, color, delaySec = 0, onHero = false, maxWidth = "84%", align = "center" }) => {
  const b = useBrand();
  const { opacity, translate } = useReveal(delaySec);
  return (
    <div
      style={{
        fontFamily: b.font,
        fontSize: size,
        fontWeight: weight,
        lineHeight: 1.16,
        letterSpacing: "-0.02em",
        textAlign: align,
        color: color ?? (onHero ? b.onHero : b.ink),
        opacity,
        translate,
        maxWidth,
      }}
    >
      {children}
    </div>
  );
};
