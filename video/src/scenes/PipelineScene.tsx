import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { Chip } from "../components/Chip";
import { SceneFrame } from "../components/SceneFrame";
import { Terminal, stepFrame } from "../components/Terminal";
import { C, VERDICT_COLOR, appear, demo, mono, rise } from "../theme";

const F = demo.flow1;
const EVERY = 95;
const TABLE_AT = 870;

/** Flow 1: JD file -> three screening rounds -> shortlist with verdicts. */
export const PipelineScene: React.FC = () => {
  const frame = useCurrentFrame();
  const at = (i: number) => stepFrame(F.user, i, 10, EVERY);
  const terminalOut = rise(frame, TABLE_AT - 20, 25);
  const verdictOrder = ["Strong Hire", "Hire", "Borderline", "No Hire"] as const;
  const verdicts = F.verdicts as Record<string, number>;

  return (
    <SceneFrame kicker="FLOW 1 · MULTI-ROUND SCREENING" title="From a job description to a hire / no-hire shortlist" accent={C.violet}>
      {/* Left: live reasoning trace, right: the funnel */}
      <div style={{ display: "flex", gap: 40, opacity: 1 - terminalOut, position: "absolute", inset: 0 }}>
        <div style={{ flex: 1.45 }}>
          <Terminal user={F.user} steps={F.steps} every={EVERY} fontSize={23} maxChars={150} />
        </div>
        <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: 22 }}>
          <Stage
            label="Round 1 · RAG screen"
            value={`${Math.round(interpolate(frame, [at(2), at(2) + 40], [F.screen.screened, F.screen.kept], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }))}`}
            sub={`of ${F.screen.screened} resumes kept · cut-off ${F.screen.cutoff}`}
            color={C.violet}
            show={rise(frame, at(2))}
          />
          <Stage
            label="Round 2 · deep analysis"
            value={`${F.screen.kept}`}
            sub="scored per requirement with resume evidence"
            color={C.cyan}
            show={rise(frame, at(3))}
          />
          <div style={{ background: C.panel, borderRadius: 18, padding: "22px 28px", opacity: rise(frame, at(4)) }}>
            <div style={{ fontSize: 26, color: C.muted, marginBottom: 14 }}>Round 3 · recommendation</div>
            {verdictOrder.map((v, i) => (
              <div key={v} style={{ display: "flex", alignItems: "center", gap: 16, marginTop: 10 }}>
                <span style={{ width: 200, fontSize: 28, fontWeight: 600, color: VERDICT_COLOR[v] }}>{v}</span>
                <div
                  style={{
                    height: 30,
                    borderRadius: 8,
                    background: VERDICT_COLOR[v],
                    width: (verdicts[v] ?? 0) * 60 * rise(frame, at(4) + 10 + i * 8, 25),
                  }}
                />
                <span style={{ fontFamily: mono, fontSize: 28 }}>{verdicts[v] ?? 0}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Then: the shortlist table */}
      <div style={{ position: "absolute", inset: 0, opacity: rise(frame, TABLE_AT, 25) }}>
        <div style={{ display: "flex", gap: 18, marginBottom: 18, flexWrap: "wrap" }}>
          {demo.requirements.must.map((m) => (
            <Chip key={m} color={C.cyan} size={24}>{`must · ${m}`}</Chip>
          ))}
          {demo.requirements.nice.slice(0, 4).map((m) => (
            <Chip key={m} color={C.muted} size={24}>{`nice · ${m}`}</Chip>
          ))}
        </div>
        {F.shortlist.map((a, i) => (
          <div
            key={a.name}
            style={{
              display: "flex",
              alignItems: "center",
              gap: 24,
              padding: "9px 22px",
              marginTop: 8,
              borderRadius: 12,
              background: i % 2 ? "transparent" : C.panel,
              fontSize: 27,
              ...appear(frame, TABLE_AT + 15 + i * 9, 16),
            }}
          >
            <span style={{ fontFamily: mono, color: C.muted, width: 40 }}>#{a.rank}</span>
            <span style={{ width: 250, fontWeight: 700 }}>{a.name}</span>
            <div style={{ width: 280, height: 18, background: C.panel2, borderRadius: 9 }}>
              <div
                style={{
                  height: 18,
                  borderRadius: 9,
                  background: VERDICT_COLOR[a.verdict],
                  width: `${a.score * rise(frame, TABLE_AT + 30 + i * 9, 30)}%`,
                }}
              />
            </div>
            <span style={{ fontFamily: mono, width: 80 }}>{a.score}</span>
            <span style={{ width: 190, color: VERDICT_COLOR[a.verdict], fontWeight: 700 }}>{a.verdict}</span>
            <span style={{ color: C.muted, fontSize: 23, flex: 1, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
              {a.gap === "-" ? a.strength : a.gap}
            </span>
          </div>
        ))}
      </div>
    </SceneFrame>
  );
};

const Stage: React.FC<{ label: string; value: string; sub: string; color: string; show: number }> = ({
  label,
  value,
  sub,
  color,
  show,
}) => (
  <div
    style={{
      background: C.panel,
      borderRadius: 18,
      padding: "20px 28px",
      borderLeft: `6px solid ${color}`,
      opacity: show,
      translate: `${(1 - show) * 30}px 0px`,
    }}
  >
    <div style={{ fontSize: 26, color: C.muted }}>{label}</div>
    <div style={{ display: "flex", alignItems: "baseline", gap: 18 }}>
      <span style={{ fontSize: 76, fontWeight: 800, color }}>{value}</span>
      <span style={{ fontSize: 26, color: C.muted }}>{sub}</span>
    </div>
  </div>
);
