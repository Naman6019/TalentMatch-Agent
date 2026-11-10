import React from "react";
import { useCurrentFrame } from "remotion";
import { SceneFrame } from "../components/SceneFrame";
import { C, appear, mono } from "../theme";

const GROUPS: { title: string; color: string; fields: [string, string][] }[] = [
  {
    title: "Conversation history",
    color: C.cyan,
    fields: [
      ["messages", "every user + agent turn (add_messages)"],
      ["pending", "routed intent of the current turn"],
      ["turn", "how many feedback rounds so far"],
    ],
  },
  {
    title: "Job understanding",
    color: C.violet,
    fields: [
      ["jd_text / jd_source", "the brief, from a file or chat"],
      ["requirements", "must-have, nice-to-have, years"],
      ["requirements_history", "every version after refinements"],
    ],
  },
  {
    title: "Shortlist + reasoning",
    color: C.green,
    fields: [
      ["screen", "round 1: 100 → 10, cut reasons"],
      ["shortlist", "rounds 2-3: scores, evidence, verdicts"],
      ["previous_shortlist / ranking_changes", "who moved and why"],
      ["reasoning", "step-by-step trace (append-only)"],
    ],
  },
];

export const StateScene: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <SceneFrame kicker="AGENT STATE" title="What the agent remembers between turns" accent={C.violet}>
      <div style={{ display: "flex", gap: 36 }}>
        {GROUPS.map((g, gi) => (
          <div
            key={g.title}
            style={{
              flex: g.fields.length > 3 ? 1.25 : 1,
              background: C.panel,
              borderRadius: 22,
              borderTop: `5px solid ${g.color}`,
              padding: "28px 32px",
              ...appear(frame, 25 + gi * 45, 40),
            }}
          >
            <div style={{ fontSize: 38, fontWeight: 800, marginBottom: 12 }}>{g.title}</div>
            {g.fields.map(([name, desc], fi) => (
              <div key={name} style={{ marginTop: 20, ...appear(frame, 55 + gi * 45 + fi * 12) }}>
                <div style={{ fontFamily: mono, fontSize: 27, color: g.color, fontWeight: 700 }}>{name}</div>
                <div style={{ fontSize: 26, color: C.muted, marginTop: 4 }}>{desc}</div>
              </div>
            ))}
          </div>
        ))}
      </div>
      <div
        style={{
          marginTop: 44,
          fontSize: 32,
          color: C.muted,
          display: "flex",
          gap: 14,
          alignItems: "center",
          ...appear(frame, 300),
        }}
      >
        <span style={{ fontFamily: mono, color: C.amber }}>MatchState(TypedDict)</span>
        <span>· checkpointed per conversation thread with</span>
        <span style={{ fontFamily: mono, color: C.amber }}>InMemorySaver</span>
        <span>· paused with</span>
        <span style={{ fontFamily: mono, color: C.amber }}>interrupt()</span>
      </div>
    </SceneFrame>
  );
};
