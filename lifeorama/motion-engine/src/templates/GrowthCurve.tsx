import { AbsoluteFill } from "remotion";
import { z } from "zod";
import type { GrowthCurveSchema } from "../schema";
import { useBrand } from "../brand";
import { FinText, useProgress, countUpString, toneColor } from "../finance/anim";

type Props = z.infer<typeof GrowthCurveSchema>;

// plot geometry (SVG user units; the SVG scales to fit the canvas)
const PW = 900; // plot width
const PH = 980; // plot height
const PAD_L = 40;
const PAD_B = 70;
const PAD_R = 30; // keep curve ends off the right edge so end-labels fit
const baselineY = PH - PAD_B;
const plotW = PW - PAD_L - PAD_R;

const numFrom = (s: string): number => {
  const m = s.match(/[\d,]*\d/);
  return m ? parseInt(m[0].replace(/,/g, ""), 10) || 0 : 0;
};

const buildCurve = (startFrac: number, topFrac: number) => {
  const K = 2.3;
  const denom = Math.exp(K) - 1;
  const x0 = PAD_L + startFrac * plotW;
  const xEnd = PAD_L + plotW;
  const pts: [number, number][] = [];
  const N = 48;
  for (let i = 0; i <= N; i++) {
    const t = i / N;
    const v = (Math.exp(K * t) - 1) / denom;
    const x = x0 + (xEnd - x0) * t;
    const y = baselineY - topFrac * (baselineY - PH * 0.06) * v;
    pts.push([x, y]);
  }
  let d = `M ${pts[0][0].toFixed(1)} ${pts[0][1].toFixed(1)}`;
  let len = 0;
  for (let i = 1; i < pts.length; i++) {
    d += ` L ${pts[i][0].toFixed(1)} ${pts[i][1].toFixed(1)}`;
    len += Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]);
  }
  return { d, len, end: pts[pts.length - 1] };
};

export const GrowthCurve: React.FC<Props> = ({ caption, curves, xAxisLabel }) => {
  const b = useBrand();
  const draw = useProgress(0.3, 1.4);
  const labelP = Math.max(0, (draw - 0.82) / 0.18); // end-value reveal
  const maxVal = Math.max(...curves.map((c) => numFrom(c.endLabel)), 1);

  return (
    <AbsoluteFill style={{ background: b.bg, flexDirection: "column", alignItems: "center", padding: "140px 60px 70px" }}>
      {caption && (
        <div style={{ marginBottom: 18 }}>
          <FinText size={56} weight={800}>
            {caption}
          </FinText>
        </div>
      )}

      {/* legend (top, safe from the caption strip) */}
      <div style={{ display: "flex", gap: 44, marginBottom: 10, flexWrap: "wrap", justifyContent: "center" }}>
        {curves.map((c, i) => {
          const col = toneColor(b, c.tone ?? (i === 0 ? "green" : "gold"));
          return (
            <div key={i} style={{ display: "flex", alignItems: "center", gap: 12 }}>
              <div style={{ width: 26, height: 26, borderRadius: 999, background: col }} />
              <span style={{ fontFamily: b.font, fontSize: 32, fontWeight: 700, color: b.textDim }}>{c.label}</span>
            </div>
          );
        })}
      </div>

      <div style={{ flex: 1, width: "100%", display: "flex", alignItems: "center", justifyContent: "center" }}>
        <svg viewBox={`0 0 ${PW} ${PH}`} style={{ width: "100%", maxHeight: "100%" }}>
          <line x1={PAD_L} y1={6} x2={PAD_L} y2={baselineY} stroke="rgba(5,46,22,0.16)" strokeWidth={3} />
          <line x1={PAD_L} y1={baselineY} x2={PW - PAD_R + 14} y2={baselineY} stroke="rgba(5,46,22,0.16)" strokeWidth={3} />

          {curves.map((c, i) => {
            const topFrac = numFrom(c.endLabel) / maxVal;
            const { d, len, end } = buildCurve(c.startFrac ?? 0, topFrac);
            const col = toneColor(b, c.tone ?? (i === 0 ? "green" : "gold"));
            return (
              <g key={i}>
                <path
                  d={d}
                  fill="none"
                  stroke={col}
                  strokeWidth={14}
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeDasharray={len}
                  strokeDashoffset={len * (1 - draw)}
                />
                <circle cx={end[0]} cy={end[1]} r={16 * labelP} fill={col} />
                {/* end-value label, anchored at the curve end (well clear of the caption) */}
                <text
                  x={end[0] - 26}
                  y={end[1] - 26}
                  textAnchor="end"
                  style={{
                    fontFamily: "Arial, sans-serif",
                    fontWeight: 700,
                    fontSize: 58,
                    fill: col,
                    opacity: labelP,
                  }}
                >
                  {countUpString(c.endLabel, labelP)}
                </text>
              </g>
            );
          })}

          {xAxisLabel && (
            <text
              x={PAD_L + plotW / 2}
              y={baselineY + 48}
              textAnchor="middle"
              style={{ fontFamily: b.font, fontWeight: 600, fontSize: 30, fill: "rgba(82,82,91,0.85)" }}
            >
              {xAxisLabel}
            </text>
          )}
        </svg>
      </div>
    </AbsoluteFill>
  );
};
