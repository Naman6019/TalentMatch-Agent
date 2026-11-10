import React from "react";
import { AbsoluteFill, Easing, Interactive, interpolate, useCurrentFrame } from "remotion";
import { Chip } from "../components/Chip";
import { C, appear, demo, mono, sans } from "../theme";

export const IntroScene: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill
      style={{
        backgroundColor: C.bg,
        backgroundImage:
          "radial-gradient(circle at 70% 30%, rgba(56,189,248,0.18), transparent 50%), radial-gradient(circle at 20% 80%, rgba(167,139,250,0.16), transparent 45%)",
        fontFamily: sans,
        color: C.text,
        justifyContent: "center",
        padding: "0 140px",
      }}
    >
      <div style={{ fontFamily: mono, fontSize: 30, color: C.cyan, ...appear(frame, 5) }}>
        Milestone 3 · LangGraph agent
      </div>
      <Interactive.Div
        name="Hero title"
        style={{
          fontSize: 150,
          fontWeight: 800,
          letterSpacing: -4,
          marginTop: 10,
          opacity: interpolate(frame, [12, 40], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
          translate: interpolate(frame, [12, 40], ["0px 40px", "0px 0px"], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: Easing.bezier(0.16, 1, 0.3, 1),
          }),
        }}
      >
        TalentMatch
      </Interactive.Div>
      <Interactive.Div
        name="Hero subtitle"
        style={{
          fontSize: 48,
          color: C.muted,
          maxWidth: 1500,
          lineHeight: 1.3,
          marginTop: 20,
          opacity: interpolate(frame, [40, 70], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
        }}
      >
        An AI recruiting agent that screens resumes against a job description, explains every
        ranking, and changes its answer when you change your mind.
      </Interactive.Div>
      <div style={{ display: "flex", gap: 20, marginTop: 60, flexWrap: "wrap" }}>
        {[
          [`${demo.pool.resumes} resumes`, C.cyan],
          ["3-round screening", C.violet],
          ["Explainable scores", C.green],
          ["Human feedback loop", C.amber],
          ["Runs offline or with an LLM", C.pink],
        ].map(([t, c], i) => (
          <div key={t} style={appear(frame, 90 + i * 12)}>
            <Chip color={c} size={32}>
              {t}
            </Chip>
          </div>
        ))}
      </div>
    </AbsoluteFill>
  );
};
