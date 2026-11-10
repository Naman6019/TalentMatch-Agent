import React from "react";
import { useCurrentFrame } from "remotion";
import { Chip } from "../components/Chip";
import { SceneFrame } from "../components/SceneFrame";
import { C, appear, demo, mono } from "../theme";

const COLUMNS: { title: string; sub: string; color: string; tools: [string, string][] }[] = [
  {
    title: "File system tools",
    sub: "Milestone 1 · sandboxed",
    color: C.cyan,
    tools: [
      ["read_file", "PDF / DOCX / TXT text"],
      ["list_files", "folder listing + filter"],
      ["search_in_file", "keyword with context"],
      ["write_file", "reports to output/"],
    ],
  },
  {
    title: "RAG search",
    sub: "Milestone 2 · retrieval",
    color: C.violet,
    tools: [
      ["chunk by meaning", "1 chunk per role / section"],
      ["BM25 + skill tokens", "'ReactJS' = 'React'"],
      ["rag_search", "grounded snippets"],
      ["search_candidates", "rank people, not chunks"],
    ],
  },
  {
    title: "Matching tools",
    sub: "Milestone 3 · new",
    color: C.green,
    tools: [
      ["extract_requirements", "must-have vs nice-to-have"],
      ["compare_candidates", "head-to-head matrix"],
      ["generate_interview_questions", "depth + gap probes"],
      ["explain / re-rank", "score deltas, moves"],
    ],
  },
];

export const StackScene: React.FC = () => {
  const frame = useCurrentFrame();
  const f = demo.pool.formats;
  return (
    <SceneFrame kicker="WHAT THE AGENT CAN USE" title="Three tool layers, one agent">
      <div style={{ display: "flex", gap: 36, marginTop: 10 }}>
        {COLUMNS.map((col, ci) => (
          <div
            key={col.title}
            style={{
              flex: 1,
              background: C.panel,
              border: `1.5px solid ${col.color}55`,
              borderRadius: 22,
              padding: "30px 34px",
              ...appear(frame, 30 + ci * 40, 40),
            }}
          >
            <div style={{ fontSize: 24, color: col.color, fontWeight: 600, letterSpacing: 2 }}>{col.sub.toUpperCase()}</div>
            <div style={{ fontSize: 44, fontWeight: 800, marginTop: 6, marginBottom: 18 }}>{col.title}</div>
            {col.tools.map(([name, desc], ti) => (
              <div key={name} style={{ marginTop: 18, ...appear(frame, 60 + ci * 40 + ti * 14) }}>
                <div style={{ fontFamily: mono, fontSize: 28, color: C.text, fontWeight: 700 }}>{name}</div>
                <div style={{ fontSize: 26, color: C.muted, marginTop: 2 }}>{desc}</div>
              </div>
            ))}
          </div>
        ))}
      </div>
      <div style={{ display: "flex", gap: 20, marginTop: 40, alignItems: "center", ...appear(frame, 260) }}>
        <span style={{ fontSize: 32, color: C.muted }}>Screening pool:</span>
        <Chip color={C.cyan} size={30}>{`${demo.pool.resumes} resumes`}</Chip>
        <Chip color={C.text} size={30}>{`${f.pdf} PDF`}</Chip>
        <Chip color={C.text} size={30}>{`${f.docx} DOCX`}</Chip>
        <Chip color={C.text} size={30}>{`${f.txt} TXT`}</Chip>
        <Chip color={C.violet} size={30}>{`${demo.pool.chunks} RAG chunks`}</Chip>
      </div>
    </SceneFrame>
  );
};
