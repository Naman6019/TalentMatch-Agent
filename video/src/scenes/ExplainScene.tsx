import React from "react";
import { useCurrentFrame } from "remotion";
import { SceneFrame } from "../components/SceneFrame";
import { Terminal } from "../components/Terminal";
import { C, appear, demo, mono, rise } from "../theme";

const F = demo.flow3;
const E = F.explain;
const PX = 10.5; // x 0.42 = px per point

/** Flow 3: "Why did John rank higher than Jane?" as a score waterfall + evidence table. */
export const ExplainScene: React.FC = () => {
  const frame = useCurrentFrame();
  const hi = F.scores[E.higher as keyof typeof F.scores];
  const lo = F.scores[E.lower as keyof typeof F.scores];
  let acc = lo;
  return (
    <SceneFrame kicker="FLOW 3 · EXPLAINABILITY" title="“Why did John rank higher than Jane?”" accent={C.green}>
      <Terminal user={F.user} steps={F.steps} every={35} fontSize={22} maxChars={130} />

      <div style={{ display: "flex", gap: 50, marginTop: 34 }}>
        {/* Waterfall: Jane's score + each component delta = John's score */}
        <div style={{ flex: 1, background: C.panel, borderRadius: 20, padding: "26px 30px" }}>
          <div style={{ fontSize: 28, color: C.muted, marginBottom: 16 }}>Where the {E.score_gap}-point gap comes from</div>
          <Bar label={E.lower} value={lo} start={0} color={C.amber} t={rise(frame, 150, 30)} />
          {E.component_deltas.map((d, i) => {
            const startV = acc;
            acc += d.points;
            return (
              <Bar
                key={d.component}
                label={`+ ${d.component}`}
                value={d.points}
                start={startV}
                color={C.green}
                t={rise(frame, 200 + i * 40, 30)}
                delta
              />
            );
          })}
          <Bar label={E.higher} value={hi} start={0} color={C.cyan} t={rise(frame, 200 + E.component_deltas.length * 40 + 20, 30)} />
        </div>

        {/* Requirement-level evidence */}
        <div style={{ flex: 1.1 }}>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1.2fr 1.2fr", gap: 8, fontSize: 24 }}>
            <div />
            <div style={{ fontWeight: 800, color: C.cyan, fontSize: 28, ...appear(frame, 380) }}>{E.higher}</div>
            <div style={{ fontWeight: 800, color: C.amber, fontSize: 28, ...appear(frame, 380) }}>{E.lower}</div>
            {E.requirement_differences.map((r, i) => (
              <React.Fragment key={r.requirement}>
                <div style={{ fontWeight: 700, padding: "10px 0", ...appear(frame, 400 + i * 22) }}>
                  {r.requirement} <span style={{ color: C.muted, fontSize: 19 }}>{r.kind}</span>
                </div>
                <div style={{ background: `${C.green}1A`, borderRadius: 10, padding: "10px 14px", ...appear(frame, 405 + i * 22) }}>
                  {(r as Record<string, string>)[E.higher]}
                </div>
                <div style={{ background: C.panel, color: C.muted, borderRadius: 10, padding: "10px 14px", ...appear(frame, 410 + i * 22) }}>
                  {(r as Record<string, string>)[E.lower]}
                </div>
              </React.Fragment>
            ))}
          </div>
          <div style={{ marginTop: 22, fontSize: 26, color: C.muted, ...appear(frame, 560) }}>
            Every number traces back to a requirement and a line in the resume. The LLM only phrases it.
          </div>
        </div>
      </div>
    </SceneFrame>
  );
};

const Bar: React.FC<{ label: string; value: number; start: number; color: string; t: number; delta?: boolean }> = ({
  label,
  value,
  start,
  color,
  t,
  delta,
}) => (
  <div style={{ display: "flex", alignItems: "center", marginTop: 14, opacity: Math.min(1, t * 2) }}>
    <div style={{ width: 330, fontSize: 25, color: delta ? C.muted : C.text, fontWeight: delta ? 400 : 700 }}>{label}</div>
    <div style={{ position: "relative", height: 40, flex: 1 }}>
      <div
        style={{
          position: "absolute",
          left: (delta ? start : 0) * PX * 0.42,
          width: value * PX * 0.42 * t,
          height: 40,
          borderRadius: 8,
          background: color,
          opacity: delta ? 0.85 : 1,
        }}
      />
      <div
        style={{
          position: "absolute",
          left: ((delta ? start : 0) + value) * PX * 0.42 * (delta ? 1 : t) + 12,
          top: 4,
          fontFamily: mono,
          fontSize: 26,
          opacity: t,
        }}
      >
        {delta ? `+${value}` : value}
      </div>
    </div>
  </div>
);
