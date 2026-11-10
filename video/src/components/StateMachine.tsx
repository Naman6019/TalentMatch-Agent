import React from "react";
import { interpolate } from "remotion";
import { C, NODE_COLOR, mono, rise, sans } from "../theme";

type Node = { id: string; label: string; x: number; y: number; w?: number; kind?: "terminal" };

// Layout in full-frame (1920x1080) coordinates. Mirrors MatchingAgent.build_graph().
export const NODES: Node[] = [
  { id: "start", label: "START", x: 150, y: 400, kind: "terminal" },
  { id: "parse_jd", label: "Parse JD", x: 420, y: 400 },
  { id: "extract_requirements", label: "Extract Requirements", x: 720, y: 400 },
  { id: "search_resumes", label: "Search Resumes", x: 1020, y: 400 },
  { id: "rank_candidates", label: "Rank Candidates", x: 1320, y: 400 },
  { id: "generate_report", label: "Generate Report", x: 1620, y: 400 },
  { id: "human_feedback", label: "Human Feedback", x: 1460, y: 620 },
  { id: "end", label: "END", x: 1780, y: 620, kind: "terminal" },
  { id: "refine_requirements", label: "Refine Reqs", x: 235, y: 850 },
  { id: "compare_candidates", label: "Compare", x: 525, y: 850 },
  { id: "explain_ranking", label: "Explain Rank", x: 815, y: 850 },
  { id: "interview_questions", label: "Interview Qs", x: 1105, y: 850 },
  { id: "candidate_report", label: "Match Report", x: 1395, y: 850 },
  { id: "chat_agent", label: "Chat (LLM+tools)", x: 1685, y: 850 },
];
const BOX_W = 262;
const BOX_H = 92;
const byId = Object.fromEntries(NODES.map((n) => [n.id, n]));
const top = (id: string) => [byId[id].x, byId[id].y - (byId[id].kind ? 50 : BOX_H / 2)] as const;
const bottom = (id: string) => [byId[id].x, byId[id].y + (byId[id].kind ? 50 : BOX_H / 2)] as const;
const left = (id: string) => [byId[id].x - (byId[id].kind ? 50 : BOX_W / 2), byId[id].y] as const;
const right = (id: string) => [byId[id].x + (byId[id].kind ? 50 : BOX_W / 2), byId[id].y] as const;

export const MAIN_PATH = ["start", "parse_jd", "extract_requirements", "search_resumes", "rank_candidates", "generate_report"];
export const BRANCHES = [
  "refine_requirements",
  "compare_candidates",
  "explain_ranking",
  "interview_questions",
  "candidate_report",
  "chat_agent",
];

type Edge = { id: string; d: string; dashed?: boolean; both?: boolean; label?: string; lx?: number; ly?: number };

const seg = (a: readonly [number, number], b: readonly [number, number]) => `M ${a[0]} ${a[1]} L ${b[0]} ${b[1]}`;

export const EDGES: Edge[] = [
  ...MAIN_PATH.slice(0, -1).map((id, i) => ({ id: `${id}>${MAIN_PATH[i + 1]}`, d: seg(right(id), left(MAIN_PATH[i + 1])) })),
  { id: "generate_report>human_feedback", d: seg(bottom("generate_report"), [byId.human_feedback.x + 80, top("human_feedback")[1]]) },
  { id: "human_feedback>end", d: seg(right("human_feedback"), left("end")), label: "done", lx: 1660, ly: 600 },
  ...BRANCHES.map((b) => ({
    id: `human_feedback>${b}`,
    d: seg([byId.human_feedback.x + (byId[b].x - byId.human_feedback.x) * 0.12, bottom("human_feedback")[1]], top(b)),
    both: b !== "refine_requirements",
  })),
  {
    id: "refine_requirements>search_resumes",
    d: `M ${left("refine_requirements")[0] + 30} ${top("refine_requirements")[1]} L ${left("refine_requirements")[0] + 30} 520 L ${byId.search_resumes.x - 60} 520 L ${byId.search_resumes.x - 60} ${bottom("search_resumes")[1]}`,
    label: "re-screen + re-rank",
    lx: 560,
    ly: 506,
  },
  {
    id: "human_feedback>parse_jd",
    d: `M ${left("human_feedback")[0]} ${byId.human_feedback.y} L ${byId.parse_jd.x} ${byId.human_feedback.y} L ${byId.parse_jd.x} ${bottom("parse_jd")[1]}`,
    dashed: true,
    label: "new search",
    lx: 980,
    ly: 606,
  },
];

/**
 * The agent's LangGraph as an animated diagram.
 * `t` = frame within the scene; pass a large `t` and `still` to render the complete diagram.
 */
export const StateMachine: React.FC<{ t: number; still?: boolean; highlight?: string | null; token?: [number, number] | null }> = ({
  t,
  still = false,
  highlight = null,
  token = null,
}) => {
  const nodeAt = (id: string): number => {
    const mi = MAIN_PATH.indexOf(id);
    if (mi >= 0) return 20 + mi * 25;
    if (id === "human_feedback") return 190;
    if (id === "end") return 215;
    return 250 + BRANCHES.indexOf(id) * 22;
  };
  const edgeAt = (e: Edge) => Math.max(nodeAt(e.id.split(">")[0]), nodeAt(e.id.split(">")[1])) + 6;
  const p = (start: number) => (still ? 1 : rise(t, start, 22));

  return (
    <svg width={1920} height={1080} viewBox="0 0 1920 1080" style={{ position: "absolute", inset: 0 }}>
      <defs>
        <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="9" markerHeight="9" orient="auto-start-reverse">
          <path d="M 0 0 L 10 5 L 0 10 z" fill={C.muted} />
        </marker>
        <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur stdDeviation="10" result="b" />
          <feMerge>
            <feMergeNode in="b" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>

      {EDGES.map((e) => {
        const prog = p(edgeAt(e));
        const hot = highlight && e.id.includes(highlight);
        return (
          <g key={e.id} opacity={highlight && !hot ? 0.35 : 1}>
            <path
              d={e.d}
              fill="none"
              stroke={hot ? C.amber : C.muted}
              strokeWidth={hot ? 4 : 2.5}
              strokeDasharray={e.dashed ? "10 10" : undefined}
              pathLength={e.dashed ? undefined : 1}
              style={e.dashed ? { opacity: prog } : { strokeDasharray: 1, strokeDashoffset: 1 - prog }}
              markerEnd={prog > 0.95 ? "url(#arrow)" : undefined}
              markerStart={e.both && prog > 0.95 ? "url(#arrow)" : undefined}
            />
            {e.label ? (
              <text x={e.lx} y={e.ly} fill={C.muted} fontSize={22} fontFamily={mono} opacity={prog}>
                {e.label}
              </text>
            ) : null}
          </g>
        );
      })}

      {NODES.map((n) => {
        const prog = p(nodeAt(n.id));
        const color = NODE_COLOR[n.id] ?? C.text;
        const hot = highlight === n.id || (highlight === "end" && n.id === "end");
        const dim = highlight && !hot && n.id !== "human_feedback";
        if (n.kind === "terminal") {
          return (
            <g key={n.id} opacity={prog * (dim ? 0.45 : 1)}>
              <circle cx={n.x} cy={n.y} r={50} fill={C.panel2} stroke={hot ? C.amber : C.text} strokeWidth={hot ? 4 : 2} />
              <text x={n.x} y={n.y + 9} textAnchor="middle" fill={C.text} fontSize={24} fontWeight={800} fontFamily={sans}>
                {n.label}
              </text>
            </g>
          );
        }
        return (
          <g
            key={n.id}
            opacity={prog * (dim ? 0.45 : 1)}
            transform={`translate(0 ${(1 - prog) * 20})`}
            filter={hot ? "url(#glow)" : undefined}
          >
            <rect
              x={n.x - BOX_W / 2}
              y={n.y - BOX_H / 2}
              width={BOX_W}
              height={BOX_H}
              rx={18}
              fill={C.panel}
              stroke={hot ? C.amber : color}
              strokeWidth={hot ? 4 : 2.5}
            />
            <text x={n.x} y={n.y - 4} textAnchor="middle" fill={C.text} fontSize={n.label.length > 16 ? 22 : 28} fontWeight={800} fontFamily={sans}>
              {n.label}
            </text>
            <text x={n.x} y={n.y + 28} textAnchor="middle" fill={color} fontSize={19} fontFamily={mono}>
              {n.id === "human_feedback" ? "interrupt()" : n.id}
            </text>
          </g>
        );
      })}

      {token ? (
        <circle
          cx={token[0]}
          cy={token[1]}
          r={14}
          fill={C.amber}
          filter="url(#glow)"
          opacity={interpolate(t % 1000, [0, 1], [1, 1])}
        />
      ) : null}

      <g opacity={p(330)}>
        <text x={100} y={1000} fill={C.muted} fontSize={22} fontFamily={sans}>
          Round 1 = Search Resumes (100 → 10) · Rounds 2-3 = Rank Candidates (deep analysis, hire / no-hire) · ↔ = returns to Human Feedback
        </text>
      </g>
    </svg>
  );
};

/** Position of a token travelling along the main path, for progress 0..1. */
export const tokenAlongMain = (progress: number): [number, number] => {
  const pts: [number, number][] = [
    ...MAIN_PATH.map((id) => [byId[id].x, byId[id].y] as [number, number]),
    [byId.human_feedback.x, byId.human_feedback.y],
  ];
  const segs = pts.length - 1;
  const x = Math.min(progress, 0.9999) * segs;
  const i = Math.floor(x);
  const f = x - i;
  return [pts[i][0] + (pts[i + 1][0] - pts[i][0]) * f, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * f];
};
