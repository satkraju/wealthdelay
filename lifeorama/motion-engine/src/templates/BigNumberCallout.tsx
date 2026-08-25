import { AbsoluteFill, interpolate, Easing } from "remotion";
import { z } from "zod";
import type { BigNumberCalloutSchema } from "../schema";
import { useBrand } from "../brand";
import { FinText, useProgress, countUpString } from "../finance/anim";

type Props = z.infer<typeof BigNumberCalloutSchema>;

export const BigNumberCallout: React.FC<Props> = ({ pre, number, post, hero }) => {
  const b = useBrand();
  const p = useProgress(0.15, 0.9);
  const shown = countUpString(number, p);
  const pop = interpolate(p, [0, 1], [0.78, 1], { easing: Easing.out(Easing.cubic) });

  return (
    <AbsoluteFill
      style={{
        background: hero ? b.heroBg : b.bg,
        alignItems: "center",
        justifyContent: "center",
        flexDirection: "column",
        gap: 28,
        padding: "0 90px",
      }}
    >
      {pre && (
        <FinText size={56} weight={700} delaySec={0} onHero={hero} color={hero ? b.onHeroDim : b.textDim}>
          {pre}
        </FinText>
      )}
      <div
        style={{
          fontFamily: b.font,
          fontSize: 220,
          fontWeight: 800,
          letterSpacing: "-0.04em",
          lineHeight: 1,
          color: b.gold,
          scale: String(pop),
          textShadow: hero ? "0 8px 50px rgba(0,0,0,0.35)" : "0 8px 40px rgba(5,46,22,0.18)",
          fontVariantNumeric: "tabular-nums",
        }}
      >
        {shown}
      </div>
      {post && (
        <FinText size={62} weight={800} delaySec={0.5} onHero={hero}>
          {post}
        </FinText>
      )}
    </AbsoluteFill>
  );
};
