import { AbsoluteFill } from "remotion";
import { MirrorLine } from "../primitives/MirrorLine";
import { Arrow } from "../primitives/Arrow";
import { Figure } from "../primitives/Figure";
import { Label } from "../primitives/Typography";
import type { LabeledDiagramSchema } from "../schema";
import { z } from "zod";

type Props = z.infer<typeof LabeledDiagramSchema>;

export const LabeledDiagram: React.FC<Props> = ({ caption, kind, mirrorOrientation, arrows, figures }) => {
  return (
    <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", flexDirection: "column", gap: 56 }}>
      {caption && (
        <div style={{ position: "absolute", top: "14%" }}>
          <Label>{caption}</Label>
        </div>
      )}

      {kind === "mirror-arrow" && (
        <div style={{ position: "relative", width: 760, height: 360, display: "flex", alignItems: "center", justifyContent: "center" }}>
          <MirrorLine orientation={mirrorOrientation ?? "vertical"} />
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", width: "100%" }}>
            {(arrows ?? []).map((a, i) => (
              <div key={i} style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 18 }}>
                <Arrow direction={a.direction} state={a.state} delayFrames={i * 8} />
                {a.label && <Label tone={a.state === "crossed" ? "danger" : a.state === "dim" ? "dim" : "accent"} delayFrames={i * 8 + 12}>{a.label}</Label>}
              </div>
            ))}
          </div>
        </div>
      )}

      {kind === "axis-cross" && (
        <div style={{ position: "relative", width: 460, height: 460 }}>
          {(arrows ?? []).map((a, i) => (
            <div
              key={i}
              style={{
                position: "absolute",
                top: "50%",
                left: "50%",
                translate: "-50% -50%",
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                rotate:
                  a.direction === "up" ? "0deg" : a.direction === "down" ? "180deg" : a.direction === "left" ? "270deg" : "90deg",
              }}
            >
              <div style={{ translate: "0px -90px" }}>
                <Arrow direction="up" state={a.state} delayFrames={i * 6} length={150} />
              </div>
            </div>
          ))}
          <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column", gap: 8 }}>
            {(arrows ?? []).map(
              (a, i) =>
                a.label && (
                  <div
                    key={i}
                    style={{
                      position: "absolute",
                      ...(a.direction === "up" && { top: -36, left: "50%", translate: "-50% 0" }),
                      ...(a.direction === "down" && { bottom: -36, left: "50%", translate: "-50% 0" }),
                      ...(a.direction === "left" && { left: -10, top: "50%", translate: "-100% -50%" }),
                      ...(a.direction === "right" && { right: -10, top: "50%", translate: "100% -50%" }),
                    }}
                  >
                    <Label tone={a.state === "crossed" ? "danger" : a.state === "dim" ? "dim" : "accent"} delayFrames={i * 6 + 14}>
                      {a.label}
                    </Label>
                  </div>
                ),
            )}
          </div>
        </div>
      )}

      {kind === "figure-pose" && (
        <div style={{ display: "flex", alignItems: "flex-end", justifyContent: "center", gap: 90 }}>
          {(figures ?? []).map((f, i) => (
            <Figure key={i} {...f} delayFrames={i * 10} />
          ))}
        </div>
      )}
    </AbsoluteFill>
  );
};
