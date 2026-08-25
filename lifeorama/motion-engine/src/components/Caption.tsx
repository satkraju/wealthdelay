import { useCurrentFrame, useVideoConfig, interpolate } from "remotion";
import { getBrand, type Brand } from "../theme";

export const Caption: React.FC<{
  text: string;
  durationInFrames: number;
  vertical?: boolean;
  brand?: Brand;
}> = ({ text, durationInFrames, vertical, brand }) => {
  const b = brand ?? getBrand("lor");
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const fadeIn = interpolate(frame, [0, fps * 0.15], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const fadeOut = interpolate(
    frame,
    [durationInFrames - fps * 0.2, durationInFrames],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );
  const opacity = Math.min(fadeIn, fadeOut);

  // LOR (white text) -> dark gradient strip. WealthDelay (dark text) -> readable
  // translucent panel that works over both cream and forest backgrounds.
  const lightOnDark = b.captionText.toLowerCase() === "#fff";

  if (lightOnDark) {
    return (
      <div
        style={{
          position: "absolute",
          bottom: 0,
          left: 0,
          right: 0,
          height: vertical ? "18%" : "22%",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          background: b.captionBg,
          opacity,
        }}
      >
        <div
          style={{
            fontFamily: b.font,
            fontWeight: 600,
            fontSize: vertical ? 40 : 44,
            color: b.captionText,
            textAlign: "center",
            maxWidth: vertical ? "88%" : "84%",
            textShadow: "0 2px 6px rgba(0,0,0,0.7)",
            lineHeight: 1.3,
          }}
        >
          {text}
        </div>
      </div>
    );
  }

  return (
    <div
      style={{
        position: "absolute",
        bottom: vertical ? "5%" : "4%",
        left: 0,
        right: 0,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        opacity,
      }}
    >
      <div
        style={{
          fontFamily: b.font,
          fontWeight: 600,
          fontSize: vertical ? 38 : 42,
          color: b.captionText,
          textAlign: "center",
          maxWidth: vertical ? "84%" : "80%",
          lineHeight: 1.3,
          background: "rgba(255,255,255,0.92)",
          borderRadius: 22,
          padding: vertical ? "18px 30px" : "16px 28px",
          boxShadow: "0 8px 26px rgba(5,46,22,0.16)",
        }}
      >
        {text}
      </div>
    </div>
  );
};
