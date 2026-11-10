import React from "react";
import { useCurrentFrame } from "remotion";
import { Chip } from "../components/Chip";
import { SceneFrame } from "../components/SceneFrame";
import { C, VERDICT_COLOR, appear, demo, mono, rise } from "../theme";

const F = demo.flow4;
const ROW = 58;
const TOP = 150;
const LX = 0;
const RX = 740;
const COL_W = 380;
const LINES_AT = 330;
const REASONS_AT = 520;

/** Flow 4: change requirements mid-conversation; the agent re-screens and explains every move. */
export const RefineScene: React.FC = () => {
  const frame = useCurrentFrame();
  const typed = Math.max(0, Math.min(F.user.length, Math.floor((frame - 20) * 1.4)));
  const afterBy = Object.fromEntries(F.after.map((a) => [a.name, a]));
  const beforeBy = Object.fromEntries(F.before.map((a) => [a.name, a]));
  const lineP = rise(frame, LINES_AT, 60);
  const movers = F.changes.filter((c) => c.from !== null && c.to !== null && c.from !== c.to).slice(0, 4);
  const y = (rank: number) => TOP + (rank - 1) * ROW + ROW / 2;

  return (
    <SceneFrame kicker="FLOW 4 · ITERATIVE REFINEMENT" title="Change the requirements, watch it re-rank" accent={C.amber}>
      <div style={{ fontFamily: mono, fontSize: 30 }}>
        <span style={{ color: C.cyan, fontWeight: 700 }}>you&gt; </span>
        {F.user.slice(0, typed)}
      </div>
      <div style={{ display: "flex", gap: 14, marginTop: 16, flexWrap: "wrap", ...appear(frame, 150) }}>
        {F.mustAfter.map((m) => {
          const changed = m.startsWith("GraphQL") || m.startsWith("React");
          return (
            <Chip key={m} color={changed ? C.amber : C.cyan} size={24}>
              {`must · ${m}${m.startsWith("React") ? "  (was 3+)" : m.startsWith("GraphQL") ? "  (was nice)" : ""}`}
            </Chip>
          );
        })}
      </div>

      {/* bump chart */}
      <div style={{ position: "absolute", left: LX, top: TOP - 46, fontSize: 24, color: C.muted, ...appear(frame, 200) }}>Before</div>
      <div style={{ position: "absolute", left: RX, top: TOP - 46, fontSize: 24, color: C.muted, ...appear(frame, 260) }}>After</div>
      <svg width={1720} height={800} style={{ position: "absolute", left: 0, top: 0 }}>
        {F.before.map((b) => {
          const a = afterBy[b.name];
          const y1 = y(b.rank);
          const y2 = a ? y(a.rank) : y(11) + 20;
          const color = !a ? C.red : a.rank < b.rank ? C.green : a.rank > b.rank ? C.amber : C.muted;
          const x1 = LX + COL_W;
          const x2 = a ? RX : RX - 120;
          return (
            <path
              key={b.name}
              d={`M ${x1} ${y1} C ${x1 + 160} ${y1}, ${x2 - 160} ${y2}, ${x2} ${y2}`}
              fill="none"
              stroke={color}
              strokeWidth={3.5}
              opacity={0.85}
              pathLength={1}
              style={{ strokeDasharray: 1, strokeDashoffset: 1 - lineP }}
            />
          );
        })}
      </svg>
      {F.before.map((b, i) => (
        <Row key={`b${b.name}`} x={LX} y={y(b.rank)} name={b.name} score={b.score} verdict={b.verdict} rank={b.rank} style={appear(frame, 200 + i * 5)} />
      ))}
      {F.after.map((a, i) => (
        <Row
          key={`a${a.name}`}
          x={RX}
          y={y(a.rank)}
          name={a.name}
          score={a.score}
          verdict={a.verdict}
          rank={a.rank}
          isNew={!beforeBy[a.name]}
          style={appear(frame, 270 + i * 5)}
        />
      ))}
      <div style={{ position: "absolute", left: RX - 100, top: y(11) + 6, fontSize: 22, color: C.red, ...appear(frame, LINES_AT + 60) }}>
        dropped: {F.changes.filter((c) => c.to === null).map((c) => c.name).join(", ")}
      </div>

      {/* reasons */}
      <div style={{ position: "absolute", left: 1170, top: TOP - 10, width: 550 }}>
        <div style={{ fontSize: 28, fontWeight: 800, marginBottom: 12, ...appear(frame, REASONS_AT) }}>What changed (agent's report)</div>
        {movers.map((c, i) => (
          <div
            key={c.name}
            style={{
              background: C.panel,
              borderLeft: `5px solid ${(c.to as number) < (c.from as number) ? C.green : C.amber}`,
              borderRadius: 12,
              padding: "12px 18px",
              marginTop: 12,
              ...appear(frame, REASONS_AT + 30 + i * 45),
            }}
          >
            <div style={{ fontSize: 26, fontWeight: 700 }}>
              {c.name}{" "}
              <span style={{ fontFamily: mono, color: (c.to as number) < (c.from as number) ? C.green : C.amber }}>
                #{c.from} → #{c.to}
              </span>{" "}
              <span style={{ fontFamily: mono, fontSize: 22, color: C.muted }}>
                {c.score_from} → {c.score_to}
              </span>
            </div>
            <div style={{ fontSize: 21, color: C.muted, marginTop: 4 }}>{c.reason}</div>
          </div>
        ))}
      </div>
    </SceneFrame>
  );
};

const Row: React.FC<{
  x: number;
  y: number;
  name: string;
  score: number;
  verdict: string;
  rank: number;
  isNew?: boolean;
  style: React.CSSProperties;
}> = ({ x, y, name, score, verdict, rank, isNew, style }) => (
  <div
    style={{
      position: "absolute",
      left: x,
      top: y - 24,
      width: COL_W,
      height: 48,
      display: "flex",
      alignItems: "center",
      gap: 12,
      padding: "0 16px",
      borderRadius: 10,
      background: C.panel,
      border: `1.5px solid ${isNew ? C.violet : C.border}`,
      fontSize: 23,
      ...style,
    }}
  >
    <span style={{ fontFamily: mono, color: C.muted, width: 40 }}>#{rank}</span>
    <span style={{ flex: 1, fontWeight: 700, whiteSpace: "nowrap" }}>{name}</span>
    <span style={{ fontFamily: mono }}>{score}</span>
    <span style={{ width: 12, height: 12, borderRadius: 6, background: VERDICT_COLOR[verdict] }} />
  </div>
);
