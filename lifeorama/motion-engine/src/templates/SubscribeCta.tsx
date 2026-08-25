import { AbsoluteFill } from "remotion";
import { BigText } from "../primitives/Typography";
import { SubscribeButton } from "../primitives/SubscribeButton";
import type { SubscribeCtaSchema } from "../schema";
import { z } from "zod";

type Props = z.infer<typeof SubscribeCtaSchema>;

export const SubscribeCta: React.FC<Props> = ({ title }) => {
  return (
    <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", flexDirection: "column", gap: 56 }}>
      <BigText size={52}>{title}</BigText>
      <SubscribeButton delayFrames={8} />
    </AbsoluteFill>
  );
};
