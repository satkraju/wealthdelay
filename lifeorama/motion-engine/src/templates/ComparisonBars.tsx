import { AbsoluteFill } from "remotion";
import { z } from "zod";
import type { ComparisonBarsSchema } from "../schema";
import { useBrand } from "../brand";
import { FinText, useProgress, countUpString, toneColor } from "../finance/anim";

type Props = z.infer<typeof ComparisonBarsSchema>;

export const ComparisonBars: React.FC<Props> = ({ head, bars, footnote }) => {
  const b = useBrand();
  const grow = useProgress(0.35, 1.0); // bars rise together
  const MAXH = 760; // px, tallest bar

  return (
    <AbsoluteFill style={{ background: b.bg, flexDirection: "column", alignItems: "center", padding: "150px 70px 90px" }}>
      {head && (
        <div style={{ marginBottom: footnote ? 10 : 40 }}>
          <FinText size={64} weight={800}>
            {head}
          </FinText>
        </div>
      )}
      {footnote && (
        <div style={{ marginBottom: 30 }}>
          <FinText size={40} weight={700} delaySec={1.2} color={b.gold}>
            {footnote}
          </FinText>
        </div>
      )}

      <div
        style={{
          flex: 1,
          width: "100%",
          display: "flex",
          alignItems: "flex-end",
          justifyContent: "center",
          gap: 70,
          paddingBottom: 20,
        }}
      >
        {bars.map((bar, i) => {
          const h = MAXH * Math.max(0.06, bar.frac) * grow;
          const col = toneColor(b, bar.tone);
          return (
            <div key={i} style={{ display: "flex", flexDirection: "column", alignItems: "center", width: 300 }}>
              {/* value label (counts up) sits just above the bar */}
              <div
                style={{
                  fontFamily: b.font,
                  fontSize: 60,
                  fontWeight: 800,
                  letterSpacing: "-0.03em",
                  color: b.ink,
                  marginBottom: 16,
                  fontVariantNumeric: "tabular-nums",
                }}
              >
                {countUpString(bar.valueLabel, grow)}
              </div>
              {/* the bar */}
              <div
                style={{
                  width: 230,
                  height: h,
                  background: col,
                  borderRadius: 26,
                  boxShadow: "0 14px 36px rgba(5,46,22,0.18)",
                }}
              />
              {/* label + sub under the bar */}
              <div style={{ marginTop: 22, textAlign: "center" }}>
                <div style={{ fontFamily: b.font, fontSize: 42, fontWeight: 800, color: b.ink, letterSpacing: "-0.02em" }}>
                  {bar.label}
                </div>
                {bar.sub && (
                  <div style={{ fontFamily: b.font, fontSize: 30, fontWeight: 600, color: b.textDim, marginTop: 6 }}>
                    {bar.sub}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
