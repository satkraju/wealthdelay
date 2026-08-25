import { AbsoluteFill } from "remotion";
import { BigText } from "../primitives/Typography";
import type { BigStatementSchema } from "../schema";
import { z } from "zod";

type Props = z.infer<typeof BigStatementSchema>;

export const BigStatement: React.FC<Props> = ({ text, subtext, accent }) => {
  return (
    <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", flexDirection: "column", gap: 28 }}>
      <BigText size={68} accent={accent}>
        {text}
      </BigText>
      {subtext && <BigText size={30} delayFrames={10}>{subtext}</BigText>}
    </AbsoluteFill>
  );
};
