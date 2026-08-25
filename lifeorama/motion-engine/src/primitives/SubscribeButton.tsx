import { useCurrentFrame, useVideoConfig, interpolate, Easing } from "remotion";
import { useBrand } from "../brand";

export const SubscribeButton: React.FC<{ delayFrames?: number }> = ({ delayFrames = 0 }) => {
  const theme = useBrand();
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const local = Math.max(0, frame - delayFrames);

  const pop = interpolate(local, [0, fps * 0.4], [0.7, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.back(1.6)),
  });
  const opacity = interpolate(local, [0, fps * 0.3], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const pulse = 1 + 0.06 * Math.sin(local / 9);
  const ringScale = 1 + ((local % (fps * 1.2)) / (fps * 1.2)) * 0.55;
  const ringOpacity = 1 - ((local % (fps * 1.2)) / (fps * 1.2));

  return (
    <div style={{ position: "relative", display: "flex", alignItems: "center", justifyContent: "center", opacity, scale: pop }}>
      <div
        style={{
          position: "absolute",
          width: 280,
          height: 90,
          borderRadius: 999,
          border: `3px solid ${theme.accent}`,
          scale: ringScale,
          opacity: ringOpacity * 0.6,
        }}
      />
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 16,
          background: theme.accent,
          borderRadius: 999,
          padding: "22px 48px",
          scale: pulse,
          boxShadow: `0 0 50px ${theme.accentDim}`,
        }}
      >
        <svg width="34" height="34" viewBox="0 0 24 24" fill="none">
          <path
            d="M12 22c1.1 0 2-.9 2-2h-4c0 1.1.9 2 2 2zm6-6v-5c0-3.07-1.64-5.64-4.5-6.32V4c0-.83-.67-1.5-1.5-1.5S10.5 3.17 10.5 4v.68C7.63 5.36 6 7.92 6 11v5l-2 2v1h16v-1l-2-2z"
            fill="#0A0E16"
          />
        </svg>
        <span style={{ fontFamily: theme.font, fontWeight: 800, fontSize: 32, color: "#0A0E16", letterSpacing: 1 }}>
          SUBSCRIBE
        </span>
      </div>
    </div>
  );
};
