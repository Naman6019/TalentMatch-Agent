import React from "react";
import { Audio } from "@remotion/media";
import { TransitionSeries, linearTiming } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { CalculateMetadataFunction } from "remotion";
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
import { LEAD_IN, TAIL, findClips } from "./voiceover";

/** Base scene lengths (frames @30fps); timings in DEMO_SCRIPT.md assume these. */
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
const FPS = 30;

export type DemoProps = {
  /** Per-scene length after fitting the voiceover clips. */
  durations: number[];
  /** Per-scene voiceover clip (or null). */
  clips: (string | null)[];
  /** A single full-length voiceover instead of per-scene clips. */
  fullVoiceover: string | null;
};

export const defaultDemoProps: DemoProps = {
  durations: SCENES.map((s) => s.durationInFrames),
  clips: SCENES.map(() => null),
  fullVoiceover: null,
};

const total = (durations: number[]) => durations.reduce((a, b) => a + b, 0) - TRANSITION * (durations.length - 1);
export const BASE_TOTAL = total(defaultDemoProps.durations);

/** Finds recordings in public/voiceover/ and stretches each scene to fit its clip. */
export const calculateDemoMetadata: CalculateMetadataFunction<DemoProps> = async () => {
  const { full, perScene } = await findClips();
  if (full) {
    const durations = SCENES.map((s) => s.durationInFrames);
    const needed = Math.ceil(full.seconds * FPS) + TAIL;
    durations[durations.length - 1] += Math.max(0, needed - total(durations));
    return { durationInFrames: total(durations), props: { durations, clips: SCENES.map(() => null), fullVoiceover: full.src } };
  }
  const durations = SCENES.map((s) => {
    const clip = perScene[s.id];
    return clip ? Math.max(s.durationInFrames, LEAD_IN + Math.ceil(clip.seconds * FPS) + TAIL + TRANSITION) : s.durationInFrames;
  });
  return {
    durationInFrames: total(durations),
    props: { durations, clips: SCENES.map((s) => perScene[s.id]?.src ?? null), fullVoiceover: null },
  };
};

export const DemoVideo: React.FC<DemoProps> = ({ durations, clips, fullVoiceover }) => (
  <>
    <TransitionSeries>
      {SCENES.map((s, i) => {
        const Scene = s.component;
        return (
          <React.Fragment key={s.id}>
            {i > 0 ? (
              <TransitionSeries.Transition presentation={fade()} timing={linearTiming({ durationInFrames: TRANSITION })} />
            ) : null}
            <TransitionSeries.Sequence name={s.id} durationInFrames={durations[i]}>
              <Scene />
              {clips[i] ? <Audio name={`Voiceover ${s.id}`} src={clips[i] as string} from={i > 0 ? LEAD_IN : 6} /> : null}
            </TransitionSeries.Sequence>
          </React.Fragment>
        );
      })}
    </TransitionSeries>
    {fullVoiceover ? <Audio name="Voiceover (full take)" src={fullVoiceover} /> : null}
  </>
);
