import { useCurrentFrame, useVideoConfig, interpolate, Easing } from "remotion";
import { useBrand } from "../brand";

type Props = {
  mirrored?: boolean;
  raisedArm?: "left" | "right" | "none";
  rotationDeg?: number;
  height?: number;
  color?: string;
  delayFrames?: number;
  label?: string;
};

export const Figure: React.FC<Props> = ({
  mirrored = false,
  raisedArm = "none",
  rotationDeg = 0,
  height = 320,
  color,
  delayFrames = 0,
  label,
}) => {
  const theme = useBrand();
  color = color ?? theme.text;
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const local = Math.max(0, frame - delayFrames);

  const riseIn = interpolate(local, [0, fps * 0.5], [24, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  const fadeIn = interpolate(local, [0, fps * 0.4], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const w = height * 0.42;
  const armUp = raisedArm !== "none";
  const armSide = raisedArm === "right" ? 1 : -1;

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: 14,
        translate: `0px ${riseIn}px`,
        opacity: fadeIn,
      }}
    >
      <div style={{ scale: mirrored ? "-1 1" : "1 1", rotate: `${rotationDeg}deg` }}>
        <svg width={w} height={height} viewBox="0 0 100 230">
          <circle cx="50" cy="28" r="22" fill={color} />
          <rect x="32" y="54" width="36" height="92" rx="16" fill={color} />
          <rect x="14" y="60" width="14" height="70" rx="7" fill={color} opacity={armUp && armSide < 0 ? 0 : 1} />
          <rect x="72" y="60" width="14" height="70" rx="7" fill={color} opacity={armUp && armSide > 0 ? 0 : 1} />
          {armUp && (
            <rect
              x={armSide > 0 ? 72 : 14}
              y="60"
              width="14"
              height="70"
              rx="7"
              fill={color}
              transform={`rotate(${armSide > 0 ? -165 : 165} ${armSide > 0 ? 79 : 21} 60)`}
            />
          )}
          <rect x="36" y="146" width="13" height="78" rx="6" fill={color} />
          <rect x="51" y="146" width="13" height="78" rx="6" fill={color} />
        </svg>
      </div>
      {label && (
        <div
          style={{
            fontFamily: theme.font,
            fontSize: 22,
            fontWeight: 700,
            letterSpacing: 1.5,
            color: theme.textDim,
            textTransform: "uppercase",
          }}
        >
          {label}
        </div>
      )}
    </div>
  );
};
