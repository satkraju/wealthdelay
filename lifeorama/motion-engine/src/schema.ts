import { z } from "zod";

const figurePose = z.object({
  mirrored: z.boolean().optional(),
  raisedArm: z.enum(["left", "right", "none"]).optional(),
  rotationDeg: z.number().optional(),
  label: z.string().optional(),
});

const arrowSpec = z.object({
  direction: z.enum(["left", "right", "up", "down"]),
  state: z.enum(["active", "dim", "crossed"]).optional(),
  label: z.string().optional(),
});

export const BigStatementSchema = z.object({
  template: z.literal("big-statement"),
  text: z.string(),
  subtext: z.string().optional(),
  accent: z.boolean().optional(),
});

export const LabeledDiagramSchema = z.object({
  template: z.literal("labeled-diagram"),
  caption: z.string().optional(),
  kind: z.enum(["mirror-arrow", "figure-pose", "axis-cross"]),
  mirrorOrientation: z.enum(["vertical", "horizontal"]).optional(),
  arrows: z.array(arrowSpec).optional(),
  figures: z.array(figurePose).optional(),
});

const compareSide = z.object({
  label: z.string(),
  text: z.string().optional(),
  mirrorText: z.boolean().optional(),
  figure: figurePose.optional(),
});

export const CompareSplitSchema = z.object({
  template: z.literal("compare-split"),
  title: z.string().optional(),
  left: compareSide,
  right: compareSide,
});

export const SubscribeCtaSchema = z.object({
  template: z.literal("subscribe-cta"),
  title: z.string(),
});

// ── Finance templates (WealthDelay). Additive — do not change the schemas above. ──
const tone = z.enum(["green", "forest", "gold", "ink"]);

export const GrowthCurveSchema = z.object({
  template: z.literal("growth-curve"),
  caption: z.string().optional(),
  xAxisLabel: z.string().optional(),
  yAxisLabel: z.string().optional(),
  curves: z
    .array(
      z.object({
        label: z.string(),
        endLabel: z.string(), // e.g. "$140k"
        startFrac: z.number().optional(), // 0..1, where on the x-axis this curve begins (later start = bigger startFrac)
        tone: tone.optional(),
      }),
    )
    .min(1)
    .max(2),
});

export const ComparisonBarsSchema = z.object({
  template: z.literal("comparison-bars"),
  head: z.string().optional(),
  footnote: z.string().optional(),
  bars: z
    .array(
      z.object({
        label: z.string(),
        sub: z.string().optional(),
        valueLabel: z.string(), // e.g. "$47,000"
        frac: z.number(), // 0..1 height relative to the tallest bar
        tone: tone.optional(),
      }),
    )
    .min(2)
    .max(3),
});

export const BigNumberCalloutSchema = z.object({
  template: z.literal("big-number-callout"),
  pre: z.string().optional(), // small line above the number
  number: z.string(), // the highlighted figure, e.g. "$47,000"
  post: z.string().optional(), // line below the number
  hero: z.boolean().optional(), // forest-green hero background instead of cream
});

export const MilestoneTimelineSchema = z.object({
  template: z.literal("milestone-timeline"),
  caption: z.string().optional(),
  milestones: z
    .array(
      z.object({
        age: z.string(), // e.g. "25"
        label: z.string(), // e.g. "Start investing"
        tone: tone.optional(),
      }),
    )
    .min(2)
    .max(5),
});

// Brand hook / CTA card (stacked statement lines, optional forest hero bg + URL chip).
export const FinStatementSchema = z.object({
  template: z.literal("fin-statement"),
  lines: z
    .array(z.object({ text: z.string(), tone: tone.optional(), size: z.number().optional() }))
    .min(1)
    .max(4),
  hero: z.boolean().optional(),
  footerUrl: z.boolean().optional(), // show the "wealthdelay.com · link below" chip
});

export const VisualSchema = z.discriminatedUnion("template", [
  BigStatementSchema,
  LabeledDiagramSchema,
  CompareSplitSchema,
  SubscribeCtaSchema,
  GrowthCurveSchema,
  ComparisonBarsSchema,
  BigNumberCalloutSchema,
  MilestoneTimelineSchema,
  FinStatementSchema,
]);

export const SceneSchema = z.object({
  narration: z.string(),
  audioFile: z.string(),
  durationSec: z.number(),
  visual: VisualSchema,
});

export const SceneVideoSchema = z.object({
  scenes: z.array(SceneSchema),
  width: z.number(),
  height: z.number(),
  vertical: z.boolean().optional(),
  theme: z.enum(["lor", "wealthdelay", "wiredwrong", "forcedecoded", "careos", "executor"]).optional(), // omit -> "lor" (unchanged behaviour)
});

export type Scene = z.infer<typeof SceneSchema>;
export type VisualProps = z.infer<typeof VisualSchema>;
