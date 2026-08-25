import { AbsoluteFill } from "remotion";
import { z } from "zod";
import type { FinStatementSchema } from "../schema";
import { useBrand } from "../brand";
import { FinText, useReveal, toneColor } from "../finance/anim";

type Props = z.infer<typeof FinStatementSchema>;

const UrlChip: React.FC<{ hero?: boolean }> = ({ hero }) => {
  const b = useBrand();
  const { opacity, translate } = useReveal(0.7, 16);
  return (
    <div style={{ opacity, translate, marginTop: 44, display: "flex", flexDirection: "column", alignItems: "center", gap: 14 }}>
      <div
        style={{
          fontFamily: b.font,
          fontWeight: 800,
          fontSize: 46,
          color: hero ? b.forest : "#fff",
          background: hero ? "#fff" : b.green,
          borderRadius: 999,
          padding: "20px 46px",
          boxShadow: "0 12px 30px rgba(5,46,22,0.28)",
          letterSpacing: "-0.01em",
        }}
      >
        wealthdelay.com
      </div>
      <div style={{ fontFamily: b.font, fontWeight: 600, fontSize: 32, color: hero ? b.onHeroDim : b.textDim }}>
        Free calculator — link below
      </div>
    </div>
  );
};

export const FinStatement: React.FC<Props> = ({ lines, hero, footerUrl }) => {
  const b = useBrand();
  return (
    <AbsoluteFill
      style={{
        background: hero ? b.heroBg : b.bg,
        alignItems: "center",
        justifyContent: "center",
        flexDirection: "column",
        gap: 22,
        padding: "0 80px",
      }}
    >
      {lines.map((ln, i) => {
        const color = ln.tone ? toneColor(b, ln.tone) : hero ? b.onHero : b.ink;
        return (
          <FinText key={i} size={ln.size ?? 78} weight={800} delaySec={i * 0.28} color={color}>
            {ln.text}
          </FinText>
        );
      })}
      {footerUrl && <UrlChip hero={hero} />}
    </AbsoluteFill>
  );
};
