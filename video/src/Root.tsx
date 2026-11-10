import React from "react";
import { Composition, Folder, Still } from "remotion";
import { DemoVideo, SCENES, TOTAL_FRAMES } from "./DemoVideo";
import { StateMachineStill } from "./scenes/StateMachineScene";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition id="TalentMatchDemo" component={DemoVideo} durationInFrames={TOTAL_FRAMES} fps={30} width={1920} height={1080} />
      <Folder name="Scenes">
        {SCENES.map((s) => (
          <Composition
            key={s.id}
            id={s.id}
            component={s.component}
            durationInFrames={s.durationInFrames}
            fps={30}
            width={1920}
            height={1080}
          />
        ))}
      </Folder>
      <Still id="StateMachineDiagram" component={StateMachineStill} width={1920} height={1080} />
    </>
  );
};
