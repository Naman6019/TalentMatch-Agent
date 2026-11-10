import React from "react";
import { TransitionSeries, linearTiming } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { CompareScene } from "./scenes/CompareScene";
import { ExplainScene } from "./scenes/ExplainScene";
import { IntroScene } from "./scenes/IntroScene";
import { InterviewScene } from "./scenes/InterviewScene";
import { OutroScene } from "./scenes/OutroScene";
import { PipelineScene } from "./scenes/PipelineScene";
import { RefineScene } from "./scenes/RefineScene";
import { StackScene } from "./scenes/StackScene";
import { StateMachineScene } from "./scenes/StateMachineScene";
import { StateScene } from "./scenes/StateScene";

/** Scene list (frames @30fps). Durations leave room for a voiceover; see DEMO_SCRIPT.md. */
export const SCENES: { id: string; component: React.FC; durationInFrames: number }[] = [
  { id: "Intro", component: IntroScene, durationInFrames: 420 },
  { id: "Stack", component: StackScene, durationInFrames: 720 },
  { id: "StateMachine", component: StateMachineScene, durationInFrames: 1350 },
  { id: "AgentState", component: StateScene, durationInFrames: 660 },
  { id: "Pipeline", component: PipelineScene, durationInFrames: 1500 },
  { id: "Compare", component: CompareScene, durationInFrames: 1050 },
  { id: "Explain", component: ExplainScene, durationInFrames: 1050 },
  { id: "Refine", component: RefineScene, durationInFrames: 1350 },
  { id: "Interview", component: InterviewScene, durationInFrames: 1050 },
  { id: "Outro", component: OutroScene, durationInFrames: 660 },
];
export const TRANSITION = 15;
export const TOTAL_FRAMES = SCENES.reduce((s, x) => s + x.durationInFrames, 0) - TRANSITION * (SCENES.length - 1);

export const DemoVideo: React.FC = () => (
  <TransitionSeries>
    <TransitionSeries.Sequence name="Intro" durationInFrames={420}>
      <IntroScene />
    </TransitionSeries.Sequence>
    <TransitionSeries.Transition presentation={fade()} timing={linearTiming({ durationInFrames: 15 })} />
    <TransitionSeries.Sequence name="Stack" durationInFrames={720}>
      <StackScene />
    </TransitionSeries.Sequence>
    <TransitionSeries.Transition presentation={fade()} timing={linearTiming({ durationInFrames: 15 })} />
    <TransitionSeries.Sequence name="StateMachine" durationInFrames={1350}>
      <StateMachineScene />
    </TransitionSeries.Sequence>
    <TransitionSeries.Transition presentation={fade()} timing={linearTiming({ durationInFrames: 15 })} />
    <TransitionSeries.Sequence name="AgentState" durationInFrames={660}>
      <StateScene />
    </TransitionSeries.Sequence>
    <TransitionSeries.Transition presentation={fade()} timing={linearTiming({ durationInFrames: 15 })} />
    <TransitionSeries.Sequence name="Pipeline" durationInFrames={1500}>
      <PipelineScene />
    </TransitionSeries.Sequence>
    <TransitionSeries.Transition presentation={fade()} timing={linearTiming({ durationInFrames: 15 })} />
    <TransitionSeries.Sequence name="Compare" durationInFrames={1050}>
      <CompareScene />
    </TransitionSeries.Sequence>
    <TransitionSeries.Transition presentation={fade()} timing={linearTiming({ durationInFrames: 15 })} />
    <TransitionSeries.Sequence name="Explain" durationInFrames={1050}>
      <ExplainScene />
    </TransitionSeries.Sequence>
    <TransitionSeries.Transition presentation={fade()} timing={linearTiming({ durationInFrames: 15 })} />
    <TransitionSeries.Sequence name="Refine" durationInFrames={1350}>
      <RefineScene />
    </TransitionSeries.Sequence>
    <TransitionSeries.Transition presentation={fade()} timing={linearTiming({ durationInFrames: 15 })} />
    <TransitionSeries.Sequence name="Interview" durationInFrames={1050}>
      <InterviewScene />
    </TransitionSeries.Sequence>
    <TransitionSeries.Transition presentation={fade()} timing={linearTiming({ durationInFrames: 15 })} />
    <TransitionSeries.Sequence name="Outro" durationInFrames={660}>
      <OutroScene />
    </TransitionSeries.Sequence>
  </TransitionSeries>
);
