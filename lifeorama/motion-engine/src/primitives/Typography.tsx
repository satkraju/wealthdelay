import { useCurrentFrame, useVideoConfig, interpolate, Easing } from "remotion";
import { useBrand } from "../brand";

type BigTextProps = {
  children: React.ReactNode;
  size?: number;
  color?: string;
  delayFrames?: number;
  accent?: boolean;
};

export const BigText: React.FC<BigTextProps> = ({
  children,
  size = 64,
  color,
  delayFrames = 0,
  accent = false,
}) => {
  const theme = useBrand();
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const local = Math.max(0, frame - delayFrames);

  const opacity = interpolate(local, [0, fps * 0.4], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const rise = interpolate(local, [0, fps * 0.45], [28, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  return (
    <div
      style={{
        fontFamily: theme.font,
        fontSize: size,
        fontWeight: 800,
        lineHeight: 1.18,
        textAlign: "center",
        color: accent ? theme.accent : (color ?? theme.text),
        opacity,
        translate: `0px ${rise}px`,
        maxWidth: "82%",
        textShadow: accent ? `0 0 40px ${theme.accentDim}` : "none",
      }}
    >
      {children}
    </div>
  );
};

type LabelProps = {
  children: React.ReactNode;
  delayFrames?: number;
  tone?: "accent" | "dim" | "danger";
};

export const Label: React.FC<LabelProps> = ({ children, delayFrames = 0, tone = "accent" }) => {
  const theme = useBrand();
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const local = Math.max(0, frame - delayFrames);

  const opacity = interpolate(local, [0, fps * 0.3], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const scale = interpolate(local, [0, fps * 0.3], [0.85, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  const color = tone === "danger" ? theme.danger : tone === "dim" ? theme.textDim : theme.accent;
  const border = tone === "danger" ? theme.danger : tone === "dim" ? theme.textDim : theme.accent;

  return (
    <div
      style={{
        fontFamily: theme.font,
        fontSize: 26,
        fontWeight: 700,
        letterSpacing: 1.2,
        textTransform: "uppercase",
        color,
        border: `2px solid ${border}`,
        borderRadius: 999,
        padding: "10px 26px",
        opacity,
        scale,
        whiteSpace: "nowrap",
      }}
    >
      {children}
    </div>
  );
};
