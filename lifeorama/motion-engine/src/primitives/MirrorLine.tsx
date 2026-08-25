import { useCurrentFrame, useVideoConfig, interpolate, Easing } from "remotion";
import { useBrand } from "../brand";

type Props = {
  orientation?: "vertical" | "horizontal";
  delayFrames?: number;
};

export const MirrorLine: React.FC<Props> = ({ orientation = "vertical", delayFrames = 0 }) => {
  const theme = useBrand();
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const local = Math.max(0, frame - delayFrames);

  const grow = interpolate(local, [0, fps * 0.6], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  const glow = 0.5 + 0.5 * Math.sin(frame / 14);

  const vertical = orientation === "vertical";

  return (
    <div
      style={{
        position: "absolute",
        top: vertical ? "50%" : "50%",
        left: "50%",
        translate: "-50% -50%",
        width: vertical ? 6 : `${grow * 78}%`,
        height: vertical ? `${grow * 78}%` : 6,
        background: `linear-gradient(${vertical ? "180deg" : "90deg"}, transparent, ${theme.accent}, transparent)`,
        boxShadow: `0 0 ${20 + glow * 14}px ${theme.accent}`,
        borderRadius: 4,
      }}
    />
  );
};
