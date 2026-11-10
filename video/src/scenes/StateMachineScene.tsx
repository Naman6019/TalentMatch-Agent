import React from "react";
import { AbsoluteFill, Interactive, interpolate, useCurrentFrame } from "remotion";
import { BRANCHES, StateMachine, tokenAlongMain } from "../components/StateMachine";
import { C, mono, rise, sans } from "../theme";

const CAPTIONS: Record<string, string> = {
  refine_requirements: "“Make GraphQL a must-have”  →  re-screen and re-rank",
  compare_candidates: "“Compare the top 3 matches side by side”",
  explain_ranking: "“Why did John rank higher than Jane?”",
  interview_questions: "“Interview questions for Jane”",
  candidate_report: "“Tell me about Sofia”  →  strengths, gaps, suggestions",
  chat_agent: "“Which candidates have AWS experience?”  →  LLM calls tools",
  end: "“done”  →  END",
};

const TOKEN_START = 450;
const TOKEN_LEN = 330;
const BRANCH_START = 820;
const BRANCH_EACH = 72;

/** Full-scene diagram; also exported as a still for docs/state_machine.png. */
export const StateMachineScene: React.FC<{ still?: boolean }> = ({ still = false }) => {
  const frame = useCurrentFrame();
  const t = still ? 10_000 : frame;
  const tokenP = interpolate(t, [TOKEN_START, TOKEN_START + TOKEN_LEN], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const showToken = !still && t >= TOKEN_START && t < BRANCH_START;
  const order = [...BRANCHES, "end"];
  const bi = Math.floor((t - BRANCH_START) / BRANCH_EACH);
  const highlight = !still && t >= BRANCH_START && bi < order.length ? order[bi] : null;

  return (
    <AbsoluteFill style={{ backgroundColor: C.bg, fontFamily: sans, color: C.text }}>
      <AbsoluteFill
        style={{
          backgroundImage:
            "linear-gradient(rgba(255,255,255,0.025) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.025) 1px, transparent 1px)",
          backgroundSize: "64px 64px",
        }}
      />
      <div style={{ position: "absolute", left: 100, top: 70 }}>
        <div style={{ fontSize: 26, letterSpacing: 6, fontWeight: 600, color: C.amber }}>PART A · LANGGRAPH STATE MACHINE</div>
        <Interactive.Div
          name="Diagram title"
          style={{
            fontSize: 64,
            fontWeight: 800,
            marginTop: 8,
            opacity: interpolate(frame, [0, 20], [still ? 1 : 0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
          }}
        >
          START → … → Human Feedback Loop → END
        </Interactive.Div>
      </div>

      <StateMachine t={t} still={still} highlight={highlight} token={showToken ? tokenAlongMain(tokenP) : null} />

      {highlight ? (
        <div
          style={{
            position: "absolute",
            right: 100,
            top: 210,
            fontFamily: mono,
            fontSize: 32,
            color: C.amber,
            background: C.panel,
            border: `1.5px solid ${C.amber}88`,
            borderRadius: 14,
            padding: "14px 24px",
            opacity: rise(t - BRANCH_START - bi * BRANCH_EACH, 0, 10),
          }}
        >
          {CAPTIONS[highlight]}
        </div>
      ) : null}
      {showToken ? (
        <div
          style={{
            position: "absolute",
            right: 100,
            top: 210,
            fontFamily: mono,
            fontSize: 30,
            color: C.text,
            background: C.panel,
            border: `1.5px solid ${C.border}`,
            borderRadius: 14,
            padding: "14px 24px",
          }}
        >
          first run: a JD flows through all five nodes, then the graph pauses
        </div>
      ) : null}
    </AbsoluteFill>
  );
};

export const StateMachineStill: React.FC = () => <StateMachineScene still />;
