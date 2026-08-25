import "./index.css";
import { Composition, CalculateMetadataFunction } from "remotion";
import { SceneVideo, XFADE_FRAMES } from "./SceneVideo";
import { SceneVideoSchema } from "./schema";
import { SimComposition } from "./sim/SimComposition";
import { SimThumbnail } from "./sim/SimThumbnail";
import { SimShort } from "./sim/SimShort";
import { z } from "zod";

const FPS = 30;

const calculateMetadata: CalculateMetadataFunction<z.infer<typeof SceneVideoSchema>> = async ({ props }) => {
  const totalSceneFrames = props.scenes.reduce(
    (sum, s) => sum + Math.max(1, Math.round(s.durationSec * FPS)),
    0,
  );
  const transitionFrames = Math.max(0, props.scenes.length - 1) * XFADE_FRAMES;

  return {
    durationInFrames: Math.max(1, totalSceneFrames - transitionFrames),
    width: props.width,
    height: props.height,
    fps: FPS,
  };
};

export const RemotionRoot: React.FC = () => {
  return (
    <>
    <Composition
      id="SimVideo"
      component={SimComposition}
      fps={FPS}
      width={1920}
      height={1080}
      durationInFrames={2178}
      defaultProps={{ brand: "lor" as const }}
    />
    <Composition
      id="SimThumbnail"
      component={SimThumbnail}
      fps={FPS}
      width={1280}
      height={720}
      durationInFrames={1}
      defaultProps={{ brand: "lor" as const }}
    />
    <Composition
      id="SimShort"
      component={SimShort}
      fps={FPS}
      width={1080}
      height={1920}
      durationInFrames={432}
      defaultProps={{ brand: "lor" as const }}
    />
    <Composition
      id="SceneVideo"
      component={SceneVideo}
      schema={SceneVideoSchema}
      fps={FPS}
      width={1920}
      height={1080}
      durationInFrames={150}
      defaultProps={{
        width: 1920,
        height: 1080,
        vertical: false,
        scenes: [
          {
            narration: "Why do mirrors flip left and right but not up and down?",
            audioFile: "audio/sample/scene0.wav",
            durationSec: 5,
            visual: { template: "big-statement", text: "Why do mirrors flip left and right but not up and down?" },
          },
        ],
      }}
      calculateMetadata={calculateMetadata}
    />
    </>
  );
};
