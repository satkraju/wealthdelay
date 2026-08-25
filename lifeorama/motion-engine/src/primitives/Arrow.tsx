import { useCurrentFrame, useVideoConfig, interpolate, Easing } from "remotion";
import { useBrand } from "../brand";

export type ArrowDirection = "left" | "right" | "up" | "down";
export type ArrowState = "active" | "dim" | "crossed";

type Props = {
  direction: ArrowDirection;
  state?: ArrowState;
  length?: number;
  thickness?: number;
  delayFrames?: number;
  color?: string;
};

const rotationFor: Record<ArrowDirection, number> = {
  right: 0,
  down: 90,
  left: 180,
  up: 270,
};

export const Arrow: React.FC<Props> = ({
  direction,
  state = "active",
  length = 180,
  thickness = 6,
  delayFrames = 0,
  color,
}) => {
  const theme = useBrand();
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const local = Math.max(0, frame - delayFrames);

  const draw = interpolate(local, [0, fps * 0.5], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  const crossIn = interpolate(local, [fps * 0.5, fps * 0.85], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  const strokeColor = color ?? (state === "dim" ? theme.textDim : theme.accent);
  const opacity = state === "dim" ? 0.45 : 1;
  const headSize = thickness * 3.2;
  const lineLen = Math.max(0, length - headSize) * draw;

  return (
    <div
      style={{
        width: length,
        height: headSize * 2,
        position: "relative",
        rotate: `${rotationFor[direction]}deg`,
        opacity,
      }}
    >
      <svg width={length} height={headSize * 2} style={{ position: "absolute", top: 0, left: 0 }}>
        <line
          x1={0}
          y1={headSize}
          x2={lineLen}
          y2={headSize}
          stroke={strokeColor}
          strokeWidth={thickness}
          strokeLinecap="round"
        />
        <polygon
          points={`${lineLen},${headSize - headSize} ${lineLen + headSize * draw},${headSize} ${lineLen},${headSize + headSize}`}
          fill={strokeColor}
        />
        {state === "crossed" && (
          <g style={{ opacity: crossIn }}>
            <line
              x1={length * 0.5 - 26}
              y1={headSize - 26}
              x2={length * 0.5 + 26}
              y2={headSize + 26}
              stroke={theme.danger}
              strokeWidth={8}
              strokeLinecap="round"
            />
            <line
              x1={length * 0.5 - 26}
              y1={headSize + 26}
              x2={length * 0.5 + 26}
              y2={headSize - 26}
              stroke={theme.danger}
              strokeWidth={8}
              strokeLinecap="round"
            />
          </g>
        )}
      </svg>
    </div>
  );
};
