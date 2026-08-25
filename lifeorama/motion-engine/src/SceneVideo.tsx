import { AbsoluteFill, Audio, staticFile, useVideoConfig } from "remotion";
import { TransitionSeries, linearTiming } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { SceneVisual } from "./templates";
import { Caption } from "./components/Caption";
import { Watermark } from "./components/Watermark";
import { getBrand } from "./theme";
import { BrandProvider } from "./brand";
import { ensureBrandFonts } from "./fonts";
import type { SceneVideoSchema } from "./schema";
import { z } from "zod";

type Props = z.infer<typeof SceneVideoSchema>;

const XFADE_FRAMES = 8;

export const SceneVideo: React.FC<Props> = ({ scenes, vertical, theme }) => {
  const { fps } = useVideoConfig();
  ensureBrandFonts(); // idempotent; only matters when a brand uses Plus Jakarta Sans
  const brand = getBrand(theme);

  return (
    <BrandProvider name={theme}>
      <AbsoluteFill style={{ background: brand.bg }}>
        <TransitionSeries>
          {scenes.map((scene, i) => {
            const durationInFrames = Math.max(1, Math.round(scene.durationSec * fps));
            const sequence = (
              <TransitionSeries.Sequence key={`scene-${i}`} durationInFrames={durationInFrames}>
                <AbsoluteFill>
                  <SceneVisual visual={scene.visual} />
                  <Audio src={staticFile(scene.audioFile)} />
                  <Caption text={scene.narration} durationInFrames={durationInFrames} vertical={vertical} brand={brand} />
                  <Watermark brand={brand} />
                </AbsoluteFill>
              </TransitionSeries.Sequence>
            );

            if (i === scenes.length - 1) {
              return sequence;
            }

            return [
              sequence,
              <TransitionSeries.Transition
                key={`xfade-${i}`}
                presentation={fade()}
                timing={linearTiming({ durationInFrames: XFADE_FRAMES })}
              />,
            ];
          })}
        </TransitionSeries>
      </AbsoluteFill>
    </BrandProvider>
  );
};

export { XFADE_FRAMES };
