import React from "react";
import { useCurrentFrame } from "remotion";
import { Chip } from "../components/Chip";
import { SceneFrame } from "../components/SceneFrame";
import { C, STATUS_COLOR, VERDICT_COLOR, appear, demo, mono, rise } from "../theme";

const F = demo.flow5;
const B = F.borderline;
const PART2 = 520;
const TYPE_COLOR: Record<string, string> = {
  depth: C.cyan,
  "gap probe": C.amber,
  "learning agility": C.violet,
  behavioural: C.pink,
};

/** Flow 5: tailored interview questions, then a borderline candidate's improvement suggestions. */
export const InterviewScene: React.FC = () => {
  const frame = useCurrentFrame();
  const out = rise(frame, PART2 - 20, 20);
  return (
    <SceneFrame kicker="FLOW 5 · INTERVIEW PREP + BORDERLINE CANDIDATES" title="Interview prep and near-miss advice" accent={C.pink}>
      <div style={{ position: "absolute", inset: 0, opacity: 1 - out }}>
        <div style={{ fontFamily: mono, fontSize: 30, marginBottom: 18 }}>
          <span style={{ color: C.cyan, fontWeight: 700 }}>you&gt; </span>
          {F.user}
        </div>
        {F.questions.slice(0, 6).map((q, i) => (
          <div
            key={i}
            style={{
              display: "flex",
              gap: 20,
              alignItems: "flex-start",
              background: C.panel,
              borderRadius: 14,
              padding: "14px 22px",
              marginTop: 12,
              ...appear(frame, 40 + i * 45),
            }}
          >
            <Chip color={TYPE_COLOR[q.type] ?? C.text} size={22} style={{ minWidth: 190, textAlign: "center" }}>
              {q.type}
            </Chip>
            <div style={{ fontSize: 25, lineHeight: 1.35 }}>
              <b>{q.area}: </b>
              <span style={{ color: C.muted }}>{q.question.length > 210 ? q.question.slice(0, 209) + "…" : q.question}</span>
            </div>
          </div>
        ))}
      </div>

      <div style={{ position: "absolute", inset: 0, display: "flex", gap: 40, opacity: rise(frame, PART2, 25) }}>
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: 28, color: C.muted }}>ML Engineer role · round 3 verdict</div>
          <div style={{ fontSize: 60, fontWeight: 800, marginTop: 6 }}>{B.name}</div>
          <div style={{ display: "flex", gap: 16, marginTop: 10 }}>
            <Chip color={VERDICT_COLOR[B.verdict]} size={30}>{B.verdict}</Chip>
            <Chip color={C.text} size={30}>{`${B.score} / 100`}</Chip>
          </div>
          <div style={{ marginTop: 26 }}>
            {B.breakdown.map((b, i) => (
              <div
                key={b.req}
                style={{ display: "flex", gap: 16, fontSize: 28, marginTop: 12, ...appear(frame, PART2 + 40 + i * 10, 10) }}
              >
                <span style={{ width: 16, height: 16, borderRadius: 8, marginTop: 9, background: STATUS_COLOR[b.status] }} />
                <span style={{ width: 230, fontWeight: 700, color: b.kind === "must" ? C.text : C.muted }}>{b.req}</span>
                <span style={{ color: C.muted }}>{b.detail}</span>
              </div>
            ))}
          </div>
        </div>
        <div style={{ flex: 1, ...appear(frame, PART2 + 160, 30) }}>
          <div
            style={{
              background: C.panel,
              border: `2px solid ${C.amber}88`,
              borderRadius: 22,
              padding: "28px 32px",
            }}
          >
            <div style={{ fontSize: 30, fontWeight: 800, color: C.amber }}>Improvement suggestion</div>
            {B.suggestions.map((s) => (
              <div key={s} style={{ fontSize: 30, lineHeight: 1.4, marginTop: 16 }}>
                {s}
              </div>
            ))}
            <div style={{ fontSize: 24, color: C.muted, marginTop: 22, fontFamily: mono }}>{B.rationale}</div>
          </div>
        </div>
      </div>
    </SceneFrame>
  );
};
