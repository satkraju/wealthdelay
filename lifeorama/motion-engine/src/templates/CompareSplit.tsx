import { AbsoluteFill } from "remotion";
import { MirrorLine } from "../primitives/MirrorLine";
import { Figure } from "../primitives/Figure";
import { BigText, Label } from "../primitives/Typography";
import { useBrand } from "../brand";
import type { CompareSplitSchema } from "../schema";
import { z } from "zod";

type Props = z.infer<typeof CompareSplitSchema>;

const Side: React.FC<Props["left"] & { delayFrames: number }> = ({ label, text, mirrorText, figure, delayFrames }) => {
  const theme = useBrand();
  return (
    <div style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", gap: 24 }}>
      <Label delayFrames={delayFrames}>{label}</Label>
      {figure && <Figure {...figure} delayFrames={delayFrames + 6} />}
      {text && (
        <div
          style={{
            fontFamily: theme.font,
            fontSize: 56,
            fontWeight: 800,
            color: theme.text,
            scale: mirrorText ? "-1 1" : "1 1",
          }}
        >
          {text}
        </div>
      )}
    </div>
  );
};

export const CompareSplit: React.FC<Props> = ({ title, left, right }) => {
  return (
    <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", flexDirection: "column", gap: 50 }}>
      {title && <BigText size={40}>{title}</BigText>}
      <div style={{ position: "relative", display: "flex", width: "82%", alignItems: "center", justifyContent: "space-around" }}>
        <Side {...left} delayFrames={0} />
        <div style={{ position: "relative", width: 6, height: 280, marginInline: 40 }}>
          <MirrorLine />
        </div>
        <Side {...right} delayFrames={10} />
      </div>
    </AbsoluteFill>
  );
};
