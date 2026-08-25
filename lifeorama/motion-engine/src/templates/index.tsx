import { BigStatement } from "./BigStatement";
import { LabeledDiagram } from "./LabeledDiagram";
import { CompareSplit } from "./CompareSplit";
import { SubscribeCta } from "./SubscribeCta";
import { GrowthCurve } from "./GrowthCurve";
import { ComparisonBars } from "./ComparisonBars";
import { BigNumberCallout } from "./BigNumberCallout";
import { MilestoneTimeline } from "./MilestoneTimeline";
import { FinStatement } from "./FinStatement";
import type { VisualProps } from "../schema";

export const SceneVisual: React.FC<{ visual: VisualProps }> = ({ visual }) => {
  switch (visual.template) {
    case "big-statement":
      return <BigStatement {...visual} />;
    case "labeled-diagram":
      return <LabeledDiagram {...visual} />;
    case "compare-split":
      return <CompareSplit {...visual} />;
    case "subscribe-cta":
      return <SubscribeCta {...visual} />;
    // ── finance (WealthDelay) ──
    case "growth-curve":
      return <GrowthCurve {...visual} />;
    case "comparison-bars":
      return <ComparisonBars {...visual} />;
    case "big-number-callout":
      return <BigNumberCallout {...visual} />;
    case "milestone-timeline":
      return <MilestoneTimeline {...visual} />;
    case "fin-statement":
      return <FinStatement {...visual} />;
    default:
      return null;
  }
};
