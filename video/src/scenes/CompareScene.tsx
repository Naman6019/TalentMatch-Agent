import React from "react";
import { useCurrentFrame } from "remotion";
import { Chip } from "../components/Chip";
import { SceneFrame } from "../components/SceneFrame";
import { Terminal } from "../components/Terminal";
import { C, STATUS_COLOR, VERDICT_COLOR, appear, demo, mono, rise } from "../theme";

const F = demo.flow2;
const PART2 = 470;
const ICON: Record<string, string> = { met: "✓", partial: "~", listed: "?", missing: "✗" };

/** Flow 2: a one-line natural-language search, then a head-to-head comparison. */
export const CompareScene: React.FC = () => {
  const frame = useCurrentFrame();
  const part1Out = rise(frame, PART2 - 25, 25);
  const cmp = F.compare;
  return (
    <SceneFrame kicker="FLOW 2 · CONVERSATIONAL INTERFACE" title="Ask in plain English, then compare side by side" accent={C.pink}>
      <div style={{ position: "absolute", inset: 0, display: "flex", gap: 40, opacity: 1 - part1Out }}>
        <div style={{ flex: 1.3 }}>
          <Terminal user={F.user} steps={F.steps.slice(0, 5)} every={55} fontSize={22} maxChars={120} />
        </div>
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: 28, color: C.muted, marginBottom: 14, ...appear(frame, 300) }}>
            Parsed as: <Chip color={C.cyan} size={26}>{`must · ${F.nlMust.join(", ")}`}</Chip>
          </div>
          {F.nlTop.map((a, i) => (
            <div
              key={a.name}
              style={{
                background: C.panel,
                borderRadius: 14,
                padding: "14px 22px",
                marginTop: 12,
                display: "flex",
                justifyContent: "space-between",
                fontSize: 28,
                ...appear(frame, 320 + i * 10),
              }}
            >
              <span>
                <b>{a.name}</b> <span style={{ color: C.muted, fontSize: 24 }}>{a.strength.split(",")[0]}</span>
              </span>
              <span style={{ fontFamily: mono, color: C.green }}>{a.score}</span>
            </div>
          ))}
        </div>
      </div>

      <div style={{ position: "absolute", inset: 0, opacity: rise(frame, PART2, 25) }}>
        <div style={{ fontFamily: mono, fontSize: 28, marginBottom: 20 }}>
          <span style={{ color: C.muted }}>Senior Frontend shortlist · </span>
          <span style={{ color: C.cyan, fontWeight: 700 }}>you&gt; </span>
          {F.followUp}
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "300px repeat(3, 1fr)", gap: 8, fontSize: 25 }}>
          <div />
          {cmp.summary.map((s, i) => (
            <div
              key={s.name}
              style={{
                background: C.panel2,
                borderRadius: 12,
                padding: "12px 18px",
                borderTop: `5px solid ${VERDICT_COLOR[s.verdict as string]}`,
                ...appear(frame, PART2 + 20 + i * 8),
              }}
            >
              <div style={{ fontSize: 30, fontWeight: 800 }}>{s.name}</div>
              <div style={{ color: C.muted }}>
                #{s.rank} · {s.score} · <span style={{ color: VERDICT_COLOR[s.verdict as string] }}>{s.verdict}</span>
              </div>
            </div>
          ))}
          {cmp.rows.map((r, ri) => (
            <React.Fragment key={r.req}>
              <div
                style={{
                  padding: "8px 14px",
                  fontWeight: 700,
                  color: r.kind === "must" ? C.text : C.muted,
                  ...appear(frame, PART2 + 60 + ri * 14, 10),
                }}
              >
                {r.req} <span style={{ fontSize: 20, color: C.muted }}>{r.kind}</span>
              </div>
              {r.cells.map((c, ci) => {
                const winner = r.winner !== "tie" && r.winner.split(" & ").includes(cmp.names[ci]);
                return (
                  <div
                    key={ci}
                    style={{
                      padding: "8px 14px",
                      borderRadius: 10,
                      background: winner ? `${C.green}22` : C.panel,
                      border: winner ? `1.5px solid ${C.green}88` : `1.5px solid transparent`,
                      color: C.text,
                      whiteSpace: "nowrap",
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                      ...appear(frame, PART2 + 66 + ri * 14 + ci * 3, 10),
                    }}
                  >
                    <span style={{ color: STATUS_COLOR[c.status], fontWeight: 800, marginRight: 10 }}>{ICON[c.status]}</span>
                    {c.detail}
                  </div>
                );
              })}
            </React.Fragment>
          ))}
        </div>
        <div style={{ marginTop: 22, fontSize: 30, ...appear(frame, PART2 + 260) }}>
          Overall: <b style={{ color: C.green }}>{cmp.names[0]}</b>
          <span style={{ color: C.muted }}> wins the nice-to-have rows; same verdict, different depth.</span>
        </div>
      </div>
    </SceneFrame>
  );
};
