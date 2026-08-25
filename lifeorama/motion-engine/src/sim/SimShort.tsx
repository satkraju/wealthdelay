import { useEffect, useMemo, useRef } from "react";
import { AbsoluteFill, Audio, staticFile, useCurrentFrame, interpolate, Easing } from "remotion";
import { build, aggregates, MONTHS, N } from "./model";
import { getBrand, type Brand, type BrandName } from "../theme";

// Vertical Short: 1080x1920, ~14.4s @ 30fps = 432 frames.
// Structure (viral-Shorts mechanics: hook <1.5s, cuts every ~1.5s, loop-friendly ending):
const HOOK_END = 62; // "Renters got richer than homeowners" over frozen year-17 swarm
const CRASH_END = 130; // "During the 2008 crash" + recession banner + $595k/$508k numbers
const FF_END = 271; // fast-forward swarm month 204->360 while "thirty years later..." plays
const REVEAL_END = 384; // final numbers + "same salary, same start, different endings"
const TOTAL = 432; // CTA "Which one are you?" holds, then loops

const W = 1080;
const H = 1920;
const Y_TOP = 620;
const Y_BOT = 1500;
const L_MIN = 3.9;
const L_MAX = 6.22;
const RENT_CX = 320;
const BUY_CX = 760;
const BAND_W = 360;

const fmt = (v: number) => {
  const a = Math.abs(v);
  const s = v < 0 ? "-$" : "$";
  if (a >= 1_000_000) return s + (a / 1_000_000).toFixed(2) + "M";
  if (a >= 1000) return s + Math.round(a / 1000) + "k";
  return s + Math.round(a);
};
function yFor(nw: number): number {
  const l = Math.log10(Math.max(1000, nw));
  const c = Math.max(L_MIN, Math.min(L_MAX, l));
  return Y_BOT - ((c - L_MIN) / (L_MAX - L_MIN)) * (Y_BOT - Y_TOP);
}
function xFor(cohort: "rent" | "buy", jitter: number): number {
  const cx = cohort === "rent" ? RENT_CX : BUY_CX;
  return cx + (jitter - 0.5) * BAND_W;
}

export type SimShortProps = { brand?: BrandName };

export const SimShort: React.FC<SimShortProps> = ({ brand: brandName }) => {
  const b: Brand = getBrand(brandName);
  const frame = useCurrentFrame();
  const ref = useRef<HTMLCanvasElement>(null);

  const { agents, agg } = useMemo(() => {
    const a = build();
    return { agents: a, agg: aggregates(a) };
  }, []);

  // Month: frozen at 204 (year 17) through CRASH_END, then fast-forwards to 360 by FF_END, then holds.
  const month = Math.round(
    interpolate(frame, [0, CRASH_END, FF_END, TOTAL], [204, 204, 360, 360], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
      easing: Easing.inOut(Easing.cubic),
    }),
  );
  const mm = Math.min(month, MONTHS);
  const recActive = frame < CRASH_END + 10;

  useEffect(() => {
    const ctx = ref.current?.getContext("2d");
    if (!ctx) return;
    const g = ctx.createLinearGradient(0, 0, W, H);
    if (b.isDark) { g.addColorStop(0, "#0A0F1C"); g.addColorStop(1, "#111A30"); }
    else { g.addColorStop(0, "#FDFAF5"); g.addColorStop(1, "#F3ECDF"); }
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, W, H);

    if (recActive) {
      const a2 = b.isDark ? 0.12 : 0.07;
      ctx.fillStyle = `rgba(210,70,60,${a2 + 0.05 * Math.sin(frame / 3)})`;
      ctx.fillRect(0, 0, W, H);
    }

    for (let i = 0; i < N; i++) {
      const a = agents[i];
      const nw = a.nw[mm];
      const px = xFor(a.cohort, a.x);
      const py = yFor(nw);
      const t = Math.min(1, Math.max(0, (Math.log10(Math.max(1000, nw)) - 4) / 2.2));
      let r: number, gg: number, bch: number;
      if (nw < 0) { r = 217; gg = 60; bch = 50; }
      else if (a.cohort === "rent") { r = Math.round(60 + 40 * t); gg = Math.round(120 + 90 * t); bch = Math.round(200 + 40 * t); }
      else { r = Math.round(200 + 40 * t); gg = Math.round(150 + 60 * t); bch = Math.round(60 + 40 * t); }
      const size = 3.4 + 4 * t;
      ctx.globalAlpha = b.isDark ? 0.85 : 0.9;
      ctx.fillStyle = `rgb(${r},${gg},${bch})`;
      ctx.beginPath();
      ctx.arc(px, py, size, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.globalAlpha = 1;
  }, [frame, mm, agents, recActive, b.isDark]);

  const medRent = agg.medRent[mm];
  const medBuy = agg.medBuy[mm];
  const gap = medBuy - medRent;

  const hookFade = interpolate(frame, [0, 10, HOOK_END - 10, HOOK_END], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const crashFade = interpolate(frame, [HOOK_END, HOOK_END + 8, CRASH_END - 10, CRASH_END], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const ffFade = interpolate(frame, [CRASH_END, CRASH_END + 8, FF_END - 15, FF_END], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const revealFade = interpolate(frame, [FF_END, FF_END + 10, REVEAL_END - 10, REVEAL_END], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const ctaFade = interpolate(frame, [REVEAL_END, REVEAL_END + 10], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const countersFade = interpolate(frame, [HOOK_END, HOOK_END + 10], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  const font = "'Plus Jakarta Sans', -apple-system, Inter, Helvetica, Arial, sans-serif";

  return (
    <AbsoluteFill style={{ background: b.bg, fontFamily: font, overflow: "hidden" }}>
      <Audio src={staticFile("audio/sim/short_vo.wav")} />
      <canvas ref={ref} width={W} height={H} style={{ width: W, height: H }} />

      {countersFade > 0.01 && (
        <div style={{ position: "absolute", top: 460, left: 0, right: 0, display: "flex", justifyContent: "space-around", opacity: countersFade }}>
          <div style={{ textAlign: "center" }}>
            <div style={{ color: b.textDim, fontSize: 24, fontWeight: 700 }}>RENTERS</div>
            <div style={{ color: b.isDark ? "#5B9DFF" : "#2E6BD8", fontSize: 44, fontWeight: 800 }}>{fmt(medRent)}</div>
          </div>
          <div style={{ textAlign: "center" }}>
            <div style={{ color: b.textDim, fontSize: 24, fontWeight: 700 }}>BUYERS</div>
            <div style={{ color: b.gold, fontSize: 44, fontWeight: 800 }}>{fmt(medBuy)}</div>
          </div>
        </div>
      )}

      {recActive && frame >= HOOK_END && (
        <div style={{ position: "absolute", top: 200, left: 0, right: 0, textAlign: "center" }}>
          <div style={{ display: "inline-block", color: "#fff", background: "rgba(210,70,60,0.9)", padding: "10px 28px", borderRadius: 10, fontSize: 30, fontWeight: 800 }}>
            2008 CRASH
          </div>
        </div>
      )}

      <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", opacity: hookFade, padding: 60 }}>
        <div style={{ color: b.text, fontSize: 76, fontWeight: 900, textAlign: "center", lineHeight: 1.1 }}>
          Renters got richer than homeowners
        </div>
      </AbsoluteFill>

      {crashFade > 0.01 && (
        <div style={{ position: "absolute", bottom: 340, left: 0, right: 0, textAlign: "center", opacity: crashFade }}>
          <div style={{ color: gap >= 0 ? b.green : b.danger, fontSize: 40, fontWeight: 800 }}>
            {(gap < 0 ? "+" : "-") + fmt(Math.abs(gap))} renters ahead
          </div>
        </div>
      )}

      {ffFade > 0.01 && (
        <AbsoluteFill style={{ alignItems: "center", justifyContent: "flex-start", paddingTop: 260, opacity: ffFade }}>
          <div style={{ color: b.text, fontSize: 56, fontWeight: 900, textAlign: "center", padding: "0 60px" }}>
            30 years later...
          </div>
        </AbsoluteFill>
      )}

      {revealFade > 0.01 && (
        <div style={{ position: "absolute", bottom: 320, left: 0, right: 0, textAlign: "center", opacity: revealFade, padding: "0 50px" }}>
          <div style={{ color: b.gold, fontSize: 44, fontWeight: 900 }}>
            {fmt(gap)} buyers ahead
          </div>
          <div style={{ color: b.textDim, fontSize: 28, fontWeight: 600, marginTop: 10 }}>
            Same salary. Same start. Different endings.
          </div>
        </div>
      )}

      {ctaFade > 0.01 && (
        <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", opacity: ctaFade }}>
          <div style={{ color: b.text, fontSize: 64, fontWeight: 900, textAlign: "center" }}>
            Which one are you?
          </div>
        </AbsoluteFill>
      )}

      <div style={{ position: "absolute", bottom: 40, left: 0, right: 0, textAlign: "center", color: b.textDim, fontSize: 16, fontWeight: 600 }}>
        Illustrative simulation · not financial advice
      </div>
      <div style={{ position: "absolute", top: 40, right: 30, color: b.watermark, fontSize: 18, fontWeight: 700, letterSpacing: 2 }}>
        {b.watermarkText}
      </div>
    </AbsoluteFill>
  );
};
