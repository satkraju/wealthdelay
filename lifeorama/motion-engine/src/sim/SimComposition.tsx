import { useEffect, useMemo, useRef } from "react";
import { AbsoluteFill, Audio, staticFile, useCurrentFrame, interpolate, Easing } from "remotion";
import { build, aggregates, focusAgentIndex, MONTHS, N, RECESSION_START, RECESSION_END } from "./model";
import { getBrand, type Brand, type BrandName } from "../theme";

// ── Timeline (2115 frames @ 30fps ≈ 70.5s) ──
// Keyframes are matched to George's ACTUAL spoken timestamps (Whisper transcript),
// not a proportional guess — verified via /watch transcript-vs-visual QA pass.
// "Then year 17. The crash." lands at 0:23 → visual crash starts at 0:23.
// "30 years in... $1.5 million" lands at 0:36-39 → visual reaches year 30 by 0:39.
//
// HOOK-LOCK (algorithm moat, doctrine surface #2): the intro card is compressed to
// ~3s of full-impact hook per official YT guidance (hook within 3-5s; the swarm is
// already visibly moving behind the title so the premise is proven immediately,
// never a static screen with nothing happening).
const F = [0, 494, 711, 865, 1020, 1205, 2024, 2178];
const M = [0, 15, 204, 216, 228, 360, 360, 360];
const HOOK_OUT = 93; // 3.1s — hard hook lock, title starts dissolving into the live swarm
const INTRO_OUT = 494; // ~16.5s — full explanatory setup fades, matches "at first they move together"
const ZOOM_START = 1236; // ~41.2s — just after reaching year 30, narration shifts to final numbers
const ZOOM_END = 1792; // ~59.7s — matches "more wealth you can't touch, or less wealth you can spend"
const OUTRO_START = 2024; // ~67.5s — VO ends (corrected-numbers version); end-screen-safe outro begins
const TOTAL = 2178; // ~72.6s — 5s outro buffer for YT's end-screen overlay + watermark (last 15s window)
// NOTE: rescaled proportionally from the prior VO duration as a first pass — re-verify
// against the REAL transcript timestamps per SOP 4b before treating this as final.

const W = 1920;
const H = 1080;
const Y_TOP = 150;
const Y_BOT = 980;
const L_MIN = 3.9;
const L_MAX = 6.22;
const RENT_CX = 560;
const BUY_CX = 1360;
const BAND_W = 640;

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

export type SimCompositionProps = { brand?: BrandName };

export const SimComposition: React.FC<SimCompositionProps> = ({ brand: brandName }) => {
  const b: Brand = getBrand(brandName);
  const frame = useCurrentFrame();
  const ref = useRef<HTMLCanvasElement>(null);

  const { agents, agg, focus } = useMemo(() => {
    const a = build();
    return { agents: a, agg: aggregates(a), focus: focusAgentIndex(a) };
  }, []);

  const month = Math.round(interpolate(frame, F, M, { extrapolateLeft: "clamp", extrapolateRight: "clamp" }));
  const mm = Math.min(month, MONTHS);
  const year = Math.floor(month / 12);
  const recActive = month >= RECESSION_START && month <= RECESSION_END;

  const zoom = interpolate(frame, [ZOOM_START, ZOOM_END], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.inOut(Easing.cubic),
  });
  const fx = xFor("buy", agents[focus].x);
  const fy = yFor(agents[focus].nw[mm]);
  const scale = 1 + zoom * 2.2;
  const shake = recActive ? Math.sin(frame / 1.7) * 3 : 0;
  const tx = zoom * (W / 2 - fx) * (scale / 3.2) + shake;
  const ty = zoom * (H / 2 - fy) * (scale / 3.2);

  useEffect(() => {
    const ctx = ref.current?.getContext("2d");
    if (!ctx) return;

    // Canvas background + ink follow the brand's own bg/text (not hardcoded dark).
    if (b.isDark) {
      const g = ctx.createLinearGradient(0, 0, W, H);
      g.addColorStop(0, "#0A0F1C");
      g.addColorStop(1, "#111A30");
      ctx.fillStyle = g;
    } else {
      const g = ctx.createLinearGradient(0, 0, W, H);
      g.addColorStop(0, "#FDFAF5");
      g.addColorStop(1, "#F3ECDF");
      ctx.fillStyle = g;
    }
    ctx.fillRect(0, 0, W, H);

    const gridColor = b.isDark ? "rgba(255,255,255,0.06)" : "rgba(20,20,20,0.10)";
    const gridLabel = b.isDark ? "rgba(255,255,255,0.28)" : "rgba(30,30,30,0.4)";
    ctx.strokeStyle = gridColor;
    ctx.lineWidth = 1;
    ctx.font = "18px sans-serif";
    ctx.fillStyle = gridLabel;
    for (const gv of [50000, 250000, 1000000]) {
      const y = yFor(gv);
      ctx.beginPath();
      ctx.moveTo(120, y);
      ctx.lineTo(W - 120, y);
      ctx.stroke();
      ctx.fillText(fmt(gv), 60, y + 5);
    }

    if (recActive) {
      const recAlpha = b.isDark ? 0.1 + 0.06 * Math.sin(frame / 3) : 0.06 + 0.04 * Math.sin(frame / 3);
      ctx.fillStyle = `rgba(210,70,60,${recAlpha})`;
      ctx.fillRect(0, 0, W, H);
    }

    for (let i = 0; i < N; i++) {
      const a = agents[i];
      const nw = a.nw[mm];
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
      const size = 2.6 + 3.2 * t;
      const isFocus = i === focus && zoom > 0.02;
      ctx.globalAlpha = b.isDark ? 0.8 : 0.88;
      ctx.fillStyle = isFocus ? (b.isDark ? "#FFFFFF" : "#1d1d1f") : `rgb(${r},${gg},${bch})`;
      ctx.beginPath();
      ctx.arc(px, py, isFocus ? size + 2 : size, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.globalAlpha = 1;

    if (zoom > 0.02) {
      const px = xFor("buy", agents[focus].x);
      const py = yFor(agents[focus].nw[mm]);
      ctx.strokeStyle = b.isDark ? "rgba(255,255,255,0.9)" : "rgba(20,20,20,0.75)";
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(px, py, 16 + 4 * Math.sin(frame / 5), 0, Math.PI * 2);
      ctx.stroke();
    }
  }, [frame, mm, agents, focus, recActive, zoom, b.isDark]);

  const medRent = agg.medRent[mm];
  const medBuy = agg.medBuy[mm];
  const gap = medBuy - medRent;

  // Hook (0-3s): the big promise, full opacity, immediately over live motion.
  const hookFade = interpolate(frame, [0, 10, HOOK_OUT], [0, 1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  // Setup (3-16s): smaller explanatory subtext, fades once counters take over.
  const setupFade = interpolate(frame, [HOOK_OUT, HOOK_OUT + 15, INTRO_OUT - 40, INTRO_OUT], [0, 1, 1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const uiFade = interpolate(frame, [INTRO_OUT, INTRO_OUT + 30], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const verdictFade = interpolate(frame, [ZOOM_START + 60, ZOOM_START + 140, OUTRO_START, OUTRO_START + 30], [0, 1, 1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  // Outro (last ~5s): swarm settles, UI clears — leaves clean space for YT's
  // end-screen overlay + watermark, which both claim the final ~15s window.
  const outroSettle = interpolate(frame, [OUTRO_START, TOTAL], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  const chromeFade = 1 - outroSettle; // fades counters/labels/gridlines out for the outro

  const rentColor = b.isDark ? "#5B9DFF" : "#2E6BD8";
  const buyColor = b.gold;
  const gapPositive = b.green;
  const gapNegative = b.danger;
  const verdictCardBg = b.isDark ? "rgba(10,15,28,0.92)" : "rgba(255,255,255,0.95)";
  const verdictBorder = b.isDark ? "rgba(255,255,255,0.45)" : "rgba(20,20,20,0.18)";
  const verdictSubText = b.isDark ? "#C9D3E6" : b.textDim;

  return (
    <AbsoluteFill style={{ background: b.bg, fontFamily: b.font, overflow: "hidden" }}>
      <Audio src={staticFile("audio/sim/vo.wav")} />

      <div style={{ position: "absolute", inset: 0, transform: `translate(${tx}px, ${ty}px) scale(${scale})`, transformOrigin: "0 0" }}>
        <canvas ref={ref} width={W} height={H} style={{ width: W, height: H }} />
      </div>

      <div style={{ position: "absolute", top: 96, left: RENT_CX - 160, width: 320, textAlign: "center", opacity: uiFade * chromeFade }}>
        <div style={{ color: rentColor, fontSize: 34, fontWeight: 800, letterSpacing: 2 }}>500 RENTERS</div>
      </div>
      <div style={{ position: "absolute", top: 96, left: BUY_CX - 160, width: 320, textAlign: "center", opacity: uiFade * chromeFade }}>
        <div style={{ color: buyColor, fontSize: 34, fontWeight: 800, letterSpacing: 2 }}>500 BUYERS</div>
      </div>

      <div style={{ position: "absolute", top: 30, left: 210, opacity: uiFade * chromeFade }}>
        <div style={{ color: b.textDim, fontSize: 22, fontWeight: 700, letterSpacing: 3 }}>YEAR</div>
        <div style={{ color: b.text, fontSize: 84, fontWeight: 800, lineHeight: 0.9 }}>{year}</div>
      </div>

      <Counter x={1486} y={36} label="RENTERS · median net worth" value={fmt(medRent)} color={rentColor} textDim={b.textDim} card={b.card} fade={uiFade * chromeFade} />
      <Counter x={1486} y={150} label="BUYERS · median net worth" value={fmt(medBuy)} color={buyColor} textDim={b.textDim} card={b.card} fade={uiFade * chromeFade} />
      <Counter x={1486} y={264} label="GAP · buyer − renter" value={(gap < 0 ? "-" : "+") + fmt(Math.abs(gap))} color={gap >= 0 ? gapPositive : gapNegative} textDim={b.textDim} card={b.card} fade={uiFade * chromeFade} />

      {recActive && (
        <div style={{ position: "absolute", top: 150, left: "50%", transform: "translateX(-50%)" }}>
          <div style={{ color: "#fff", background: "rgba(210,70,60,0.88)", padding: "8px 26px", borderRadius: 8, fontSize: 26, fontWeight: 800, letterSpacing: 2 }}>
            RECESSION · markets crash ~57%
          </div>
        </div>
      )}

      {/* HOOK (0-3s): the promise, immediate and full-impact, over live motion already running underneath */}
      <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", opacity: hookFade }}>
        <div style={{ color: b.text, fontSize: 108, fontWeight: 800, lineHeight: 1.05, textAlign: "center" }}>Rent or Buy?</div>
      </AbsoluteFill>

      {/* SETUP (3-16s): the context the hook promised, now that attention is locked */}
      <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", opacity: setupFade }}>
        <div style={{ textAlign: "center", padding: 40 }}>
          <div style={{ color: b.textDim, fontSize: 30, fontWeight: 700, letterSpacing: 3, marginBottom: 18 }}>1,000 FAMILIES · SAME $60,000 SALARY</div>
          <div style={{ color: b.text, fontSize: 92, fontWeight: 800, lineHeight: 1.05 }}>Rent or Buy?</div>
          <div style={{ color: rentColor, fontSize: 40, fontWeight: 700, marginTop: 24 }}>30 years. Watch every one of them.</div>
        </div>
      </AbsoluteFill>

      {/* Closing verdict */}
      {verdictFade > 0.01 && (
        <div
          style={{
            position: "absolute",
            left: "50%",
            bottom: 80,
            transform: "translateX(-50%)",
            width: 1180,
            background: verdictCardBg,
            border: `2px solid ${verdictBorder}`,
            borderRadius: 16,
            padding: "26px 40px",
            textAlign: "center",
            opacity: verdictFade,
          }}
        >
          <div style={{ color: b.text, fontSize: 36, fontWeight: 800 }}>
            More wealth you can't touch, or less wealth you can spend?
          </div>
          <div style={{ color: verdictSubText, fontSize: 25, marginTop: 12, lineHeight: 1.4 }}>
            Buyer: {fmt(medBuy)} — mostly locked in the house.
            <br />
            Renter: {fmt(medRent)} — every dollar liquid, spendable tomorrow.
          </div>
        </div>
      )}

      {/* OUTRO (last ~5s): swarm settles + chrome clears, leaving simple space for
          YT's end-screen overlay + subscribe watermark (both claim the final ~15s). */}
      {outroSettle > 0.02 && (
        <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", opacity: outroSettle }}>
          <div style={{ textAlign: "center" }}>
            <div style={{ color: b.text, fontSize: 44, fontWeight: 800 }}>More simulations every week.</div>
            <div style={{ color: rentColor, fontSize: 28, fontWeight: 700, marginTop: 14 }}>{b.watermarkText}</div>
          </div>
        </AbsoluteFill>
      )}

      {/* Compliance disclaimer: ALWAYS on full opacity, entire runtime (hook → outro),
          never tied to chromeFade/uiFade. High-contrast chip, not thin text-on-bg. */}
      <div
        style={{
          position: "absolute",
          bottom: 22,
          left: "50%",
          transform: "translateX(-50%)",
          background: b.isDark ? "rgba(0,0,0,0.55)" : "rgba(255,255,255,0.85)",
          color: b.isDark ? "rgba(255,255,255,0.92)" : "#1d1d1f",
          fontSize: 20,
          fontWeight: 700,
          padding: "6px 20px",
          borderRadius: 8,
          whiteSpace: "nowrap",
        }}
      >
        Illustrative simulation · historical averages, not a guarantee · not financial advice
      </div>
      {/* Watermark moved to bottom-RIGHT (2026-07-04 fix): top-right collided with the
          three counter boxes once uiFade kicks in (confirmed on the live upload).
          Bottom-right stays clear of the centered disclaimer chip and verdict card. */}
      <div style={{ position: "absolute", bottom: 26, right: 44, color: b.watermark, fontSize: 20, fontWeight: 700, letterSpacing: 3 }}>
        {b.watermarkText}
      </div>
    </AbsoluteFill>
  );
};

const Counter: React.FC<{ x: number; y: number; label: string; value: string; color: string; textDim: string; card: string; fade: number }> = ({
  x, y, label, value, color, textDim, card, fade,
}) => (
  <div style={{ position: "absolute", left: x, top: y, width: 400, background: card + "CC", border: `1px solid ${color}55`, borderRadius: 12, padding: "12px 20px", opacity: fade }}>
    <div style={{ color: textDim, fontSize: 19, fontWeight: 700, letterSpacing: 1 }}>{label}</div>
    <div style={{ color, fontSize: 50, fontWeight: 800, lineHeight: 1 }}>{value}</div>
  </div>
);

export const SIM_TOTAL_FRAMES = TOTAL;
