import React from "react";
import { Interactive, useCurrentFrame } from "remotion";
import { SceneFrame } from "../components/SceneFrame";
import { C, appear, demo, mono } from "../theme";

const ITEMS: [string, string, string][] = [
  ["matching_agent.py", "LangGraph state, 12 nodes, interrupt-based feedback loop", C.cyan],
  ["matching_tools.py", "requirements, 3 screening rounds, compare, explain, questions", C.violet],
  ["rag_search.py", "section chunking + BM25 with skill-token expansion", C.violet],
  ["chat_cli.py", "live reasoning trace in the terminal", C.green],
  ["run_scenarios.py", "6 scripted conversation flows → transcripts", C.amber],
  ["docs/state_machine.png", "the graph, rendered from this video's diagram", C.pink],
];

export const OutroScene: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <SceneFrame kicker="WRAP-UP" title="Deterministic scores, LLM where language matters" accent={C.green}>
      <div style={{ display: "flex", gap: 60 }}>
        <div style={{ flex: 1.3 }}>
          {ITEMS.map(([f, d, c], i) => (
            <div key={f} style={{ marginTop: i ? 22 : 0, ...appear(frame, 20 + i * 18) }}>
              <div style={{ fontFamily: mono, fontSize: 30, color: c, fontWeight: 700 }}>{f}</div>
              <div style={{ fontSize: 27, color: C.muted }}>{d}</div>
            </div>
          ))}
        </div>
        <div style={{ flex: 1 }}>
          <div style={{ background: C.panel, borderRadius: 22, padding: "30px 34px", ...appear(frame, 150) }}>
            <div style={{ fontFamily: mono, fontSize: 44, color: C.green, fontWeight: 700 }}>{demo.tests.summary.split(" in ")[0]}</div>
            <div style={{ fontSize: 27, color: C.muted, marginTop: 6 }}>pytest · offline, no API key · scripted fake LLM for the tool loop</div>
          </div>
          <div style={{ background: C.panel, borderRadius: 22, padding: "30px 34px", marginTop: 24, ...appear(frame, 190) }}>
            <div style={{ fontSize: 34, fontWeight: 800 }}>Runs offline or with</div>
            <div style={{ fontSize: 28, color: C.muted, marginTop: 8 }}>Claude · OpenAI · Gemini · OpenRouter · Ollama</div>
          </div>
          <Interactive.Div
            name="Closing line"
            style={{ fontSize: 34, fontWeight: 600, marginTop: 40, color: C.text, ...appear(frame, 260) }}
          >
            Every ranking comes with its reasons.
          </Interactive.Div>
        </div>
      </div>
    </SceneFrame>
  );
};
