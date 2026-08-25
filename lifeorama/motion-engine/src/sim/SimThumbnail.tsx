import { useEffect, useMemo, useRef } from "react";
import { AbsoluteFill } from "remotion";
import { build, focusAgentIndex, N } from "./model";
import { getBrand, type Brand, type BrandName } from "../theme";

// 1280x720, 16:9 — matches YouTube's recommended upload spec (Layer-2 convergent
// evidence: postfa.st / thumbmagic / vidIQ / snappa / techsmith all independently
// state 1280x720, ≤2MB, safe zone ~1100x620 centered, avoid bottom-right duration
// badge). No single support.google.com page states exact px — documented as such
// in CHANNEL_OVERHAUL.md per the evidence-hierarchy rule.
const W = 1280;
const H = 720;
const Y_TOP = 100;
const Y_BOT = 640;
const L_MIN = 3.9;
const L_MAX = 6.22;
const RENT_CX = 370;
const BUY_CX = 900;
const BAND_W = 420;
const THUMB_MONTH = 340; // ~year 28 — near-max visual separation, still legible

function yFor(nw: number): number {
  const l = Math.log10(Math.max(1000, nw));
  const c = Math.max(L_MIN, Math.min(L_MAX, l));
  return Y_BOT - ((c - L_MIN) / (L_MAX - L_MIN)) * (Y_BOT - Y_TOP);
}
function xFor(cohort: "rent" | "buy", jitter: number): number {
  const cx = cohort === "rent" ? RENT_CX : BUY_CX;
  return cx + (jitter - 0.5) * BAND_W;
}

export type SimThumbnailProps = { brand?: BrandName };

export const SimThumbnail: React.FC<SimThumbnailProps> = ({ brand: brandName }) => {
  const b: Brand = getBrand(brandName);
  const ref = useRef<HTMLCanvasElement>(null);
  const { agents, focus } = useMemo(() => {
    const a = build();
    return { agents: a, focus: focusAgentIndex(a) };
  }, []);

  useEffect(() => {
    const ctx = ref.current?.getContext("2d");
    if (!ctx) return;

    const g = ctx.createLinearGradient(0, 0, W, H);
    if (b.isDark) {
      g.addColorStop(0, "#0A0F1C");
      g.addColorStop(1, "#111A30");
    } else {
      g.addColorStop(0, "#FDFAF5");
      g.addColorStop(1, "#F3ECDF");
    }
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, W, H);

    for (let i = 0; i < N; i++) {
      const a = agents[i];
      const nw = a.nw[THUMB_MONTH];
      const px = xFor(a.cohort, a.x);
      const py = yFor(nw);
      const t = Math.min(1, Math.max(0, (Math.log10(Math.max(1000, nw)) - 4) / 2.2));
      let r: number, gg: number, bch: number;
      if (nw < 0) {
        r = 217; gg = 60; bch = 50;
      } else if (a.cohort === "rent") {
        r = Math.round(60 + 40 * t); gg = Math.round(120 + 90 * t); bch = Math.round(200 + 40 * t);
      } else {
        r = Math.round(200 + 40 * t); gg = Math.round(150 + 60 * t); bch = Math.round(60 + 40 * t);
      }
      const size = 3.4 + 4.2 * t; // bigger dots than the video — must read at 116x65px mobile size
      const isFocus = i === focus;
      ctx.globalAlpha = b.isDark ? 0.85 : 0.9;
      ctx.fillStyle = isFocus ? (b.isDark ? "#FFFFFF" : "#1d1d1f") : `rgb(${r},${gg},${bch})`;
      ctx.beginPath();
      ctx.arc(px, py, isFocus ? size + 3 : size, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.globalAlpha = 1;
  }, [agents, focus, b.isDark]);

  const rentColor = b.isDark ? "#7CB4FF" : "#2E6BD8";
  const buyColor = b.gold;
  const chipBg = b.isDark ? "rgba(6,10,20,0.72)" : "rgba(255,255,255,0.85)";
  const questionChipBg = b.isDark ? "rgba(0,0,0,0.55)" : "rgba(30,30,30,0.85)";

  return (
    <AbsoluteFill style={{ background: b.bg, fontFamily: b.font, overflow: "hidden" }}>
      <canvas ref={ref} width={W} height={H} style={{ width: W, height: H }} />

      {/* Safe-zone text: kept within center ~1100x620, avoids bottom-right duration badge */}
      <div style={{ position: "absolute", top: 36, left: 0, right: 0, textAlign: "center" }}>
        <div style={{ color: b.textDim, fontSize: 22, fontWeight: 800, letterSpacing: 3 }}>1,000 FAMILIES · 30 YEARS</div>
      </div>

      <div style={{ position: "absolute", top: 260, left: RENT_CX - 140, width: 280, textAlign: "center" }}>
        <div style={{ display: "inline-block", background: chipBg, borderRadius: 12, padding: "6px 26px" }}>
          <div style={{ color: rentColor, fontSize: 64, fontWeight: 900, letterSpacing: 2 }}>RENT</div>
        </div>
      </div>
      <div style={{ position: "absolute", top: 260, left: BUY_CX - 140, width: 280, textAlign: "center" }}>
        <div style={{ display: "inline-block", background: chipBg, borderRadius: 12, padding: "6px 26px" }}>
          <div style={{ color: buyColor, fontSize: 64, fontWeight: 900, letterSpacing: 2 }}>BUY</div>
        </div>
      </div>

      <div style={{ position: "absolute", top: 640, left: 0, right: 0, textAlign: "center" }}>
        <div
          style={{
            display: "inline-block",
            color: "#fff",
            fontSize: 30,
            fontWeight: 900,
            padding: "6px 22px",
            background: questionChipBg,
            borderRadius: 8,
          }}
        >
          Which wins?
        </div>
      </div>

      <div style={{ position: "absolute", top: 20, left: 24, color: b.watermark, fontSize: 18, fontWeight: 700, letterSpacing: 2 }}>
        {b.watermarkText}
      </div>
    </AbsoluteFill>
  );
};
