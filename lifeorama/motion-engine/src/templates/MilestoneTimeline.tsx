import { AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate, Easing } from "remotion";
import { z } from "zod";
import type { MilestoneTimelineSchema } from "../schema";
import { useBrand } from "../brand";
import { FinText, useReveal, toneColor } from "../finance/anim";

type Props = z.infer<typeof MilestoneTimelineSchema>;

const LINE_X = 150; // px from left edge of the rail column

const Row: React.FC<{ age: string; label: string; tone?: "green" | "forest" | "gold" | "ink"; delaySec: number }> = ({
  age,
  label,
  tone,
  delaySec,
}) => {
  const b = useBrand();
  const { opacity, translate } = useReveal(delaySec, 18);
  const col = toneColor(b, tone);
  return (
    <div style={{ display: "flex", alignItems: "center", height: 200, opacity, translate }}>
      {/* dot on the rail */}
      <div style={{ width: LINE_X * 2, display: "flex", justifyContent: "center", flexShrink: 0 }}>
        <div
          style={{
            width: 46,
            height: 46,
            borderRadius: 999,
            background: col,
            border: `8px solid ${b.card}`,
            boxShadow: "0 6px 18px rgba(5,46,22,0.22)",
          }}
        />
      </div>
      {/* age pill + label */}
      <div style={{ display: "flex", alignItems: "center", gap: 26 }}>
        <div
          style={{
            fontFamily: b.font,
            fontSize: 44,
            fontWeight: 800,
            color: b.card,
            background: col,
            borderRadius: 18,
            padding: "8px 24px",
            letterSpacing: "-0.02em",
            whiteSpace: "nowrap",
          }}
        >
          {age}
        </div>
        <div
          style={{
            fontFamily: b.font,
            fontSize: 46,
            fontWeight: 700,
            color: b.ink,
            letterSpacing: "-0.02em",
            maxWidth: 620,
            lineHeight: 1.15,
          }}
        >
          {label}
        </div>
      </div>
    </div>
  );
};

export const MilestoneTimeline: React.FC<Props> = ({ caption, milestones }) => {
  const b = useBrand();
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  // rail grows downward as milestones appear
  const railGrow = interpolate(frame, [fps * 0.2, fps * (0.3 + milestones.length * 0.3)], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.inOut(Easing.cubic),
  });

  return (
    <AbsoluteFill style={{ background: b.bg, flexDirection: "column", alignItems: "center", padding: "150px 70px 90px" }}>
      {caption && (
        <div style={{ marginBottom: 30 }}>
          <FinText size={58} weight={800}>
            {caption}
          </FinText>
        </div>
      )}
      <div style={{ position: "relative", width: "100%", flex: 1 }}>
        {/* the rail */}
        <div
          style={{
            position: "absolute",
            left: LINE_X * 2 - 5,
            top: 70,
            width: 10,
            height: `calc((100% - 140px) * ${railGrow})`,
            background: "rgba(5,46,22,0.16)",
            borderRadius: 999,
          }}
        />
        <div style={{ display: "flex", flexDirection: "column", justifyContent: "center", height: "100%" }}>
          {milestones.map((m, i) => (
            <Row key={i} age={m.age} label={m.label} tone={m.tone} delaySec={0.3 + i * 0.3} />
          ))}
        </div>
      </div>
    </AbsoluteFill>
  );
};
