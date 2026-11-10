import React from "react";
import { Audio } from "@remotion/media";
import { TransitionSeries, linearTiming } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { CalculateMetadataFunction, Freeze, Sequence } from "remotion";
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
import { BEATS, SCENE_NUMBERS, ScenePlan, TAIL, planScene, probe } from "./voiceover";

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
  plans: ScenePlan[];
  /** A single full-length voiceover instead of per-scene clips. */
  fullVoiceover: string | null;
};

export const defaultDemoProps: DemoProps = {
  plans: SCENES.map((s) => ({ duration: s.durationInFrames, holds: [], clips: [] })),
  fullVoiceover: null,
};

const total = (durations: number[]) => durations.reduce((a, b) => a + b, 0) - TRANSITION * (durations.length - 1);
export const BASE_TOTAL = total(SCENES.map((s) => s.durationInFrames));

/** Finds the recordings in public/voiceover/ and fits every scene around them. */
export const calculateDemoMetadata: CalculateMetadataFunction<DemoProps> = async () => {
  const full = await probe("full");
  if (full) {
    const plans = SCENES.map((s) => ({ duration: s.durationInFrames, holds: [], clips: [] }));
    const needed = Math.ceil(full.seconds * FPS) + TAIL;
    plans[plans.length - 1].duration += Math.max(0, needed - total(plans.map((p) => p.duration)));
    return { durationInFrames: total(plans.map((p) => p.duration)), props: { plans, fullVoiceover: full.src } };
  }
  const plans = await Promise.all(
    SCENES.map(async (s, i) => {
      const n = SCENE_NUMBERS[s.id];
      const keys = [n, ...(BEATS[s.id] ?? []).map((_, k) => `${n}-${k + 1}`)];
      const clips = await Promise.all(keys.map(probe));
      return planScene(s.id, s.durationInFrames, clips, FPS, i === 0, TRANSITION);
    }),
  );
  return { durationInFrames: total(plans.map((p) => p.duration)), props: { plans, fullVoiceover: null } };
};

/** Plays a scene with pauses inserted: original frame `at` is held for `len` frames. */
const WithHolds: React.FC<{ Scene: React.FC; holds: ScenePlan["holds"] }> = ({ Scene, holds }) => {
  if (!holds.length) return <Scene />;
  const parts: React.ReactNode[] = [];
  let out = 0;
  let orig = 0;
  holds.forEach((h, i) => {
    const play = h.at - orig;
    if (play > 0) {
      parts.push(
        <Sequence key={`p${i}`} name="Scene" from={out} durationInFrames={play} trimBefore={orig}>
          <Scene />
        </Sequence>,
      );
    }
    parts.push(
      <Sequence key={`h${i}`} name="Hold for narration" from={out + play} durationInFrames={h.len}>
        <Freeze frame={h.at}>
          <Scene />
        </Freeze>
      </Sequence>,
    );
    out += play + h.len;
    orig = h.at;
  });
  parts.push(
    <Sequence key="rest" name="Scene" from={out} trimBefore={orig}>
      <Scene />
    </Sequence>,
  );
  return <>{parts}</>;
};

export const DemoVideo: React.FC<DemoProps> = ({ plans, fullVoiceover }) => (
  <>
    <TransitionSeries>
      {SCENES.map((s, i) => (
        <React.Fragment key={s.id}>
          {i > 0 ? (
            <TransitionSeries.Transition presentation={fade()} timing={linearTiming({ durationInFrames: TRANSITION })} />
          ) : null}
          <TransitionSeries.Sequence name={s.id} durationInFrames={plans[i].duration}>
            <WithHolds Scene={s.component} holds={plans[i].holds} />
            {plans[i].clips.map((c, k) => (
              <Audio key={c.src} name={`Voiceover ${SCENE_NUMBERS[s.id]}${k ? `-${k}` : ""}`} src={c.src} from={c.from} />
            ))}
          </TransitionSeries.Sequence>
        </React.Fragment>
      ))}
    </TransitionSeries>
    {fullVoiceover ? <Audio name="Voiceover (full take)" src={fullVoiceover} /> : null}
  </>
);
