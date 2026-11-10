import React from "react";
import { useCurrentFrame } from "remotion";
import { C, NODE_COLOR, appear, mono } from "../theme";

export type Step = { node: string; text: string };

/**
 * A chat terminal: the user's message types out, then each graph node's reasoning line
 * appears in order (one every `every` frames), like the CLI's live trace.
 */
export const Terminal: React.FC<{
  user: string;
  steps: Step[];
  start?: number;
  every?: number;
  width?: number | string;
  fontSize?: number;
  maxChars?: number;
}> = ({ user, steps, start = 10, every = 60, width = "100%", fontSize = 25, maxChars = 170 }) => {
  const frame = useCurrentFrame();
  const typed = Math.max(0, Math.min(user.length, Math.floor((frame - start) * 1.6)));
  const typingDone = start + Math.ceil(user.length / 1.6) + 12;
  return (
    <div
      style={{
        width,
        background: C.panel,
        border: `1px solid ${C.border}`,
        borderRadius: 18,
        padding: "26px 32px",
        fontFamily: mono,
        fontSize,
        lineHeight: 1.45,
        boxShadow: "0 30px 80px rgba(0,0,0,0.35)",
      }}
    >
      <div style={{ display: "flex", gap: 10, marginBottom: 18 }}>
        {[C.red, C.amber, C.green].map((c) => (
          <div key={c} style={{ width: 14, height: 14, borderRadius: 7, background: c, opacity: 0.8 }} />
        ))}
      </div>
      <div>
        <span style={{ color: C.cyan, fontWeight: 700 }}>you&gt; </span>
        <span>{user.slice(0, typed)}</span>
        {typed < user.length && frame % 30 < 18 ? <span style={{ color: C.cyan }}>|</span> : null}
      </div>
      <div style={{ marginTop: 14 }}>
        {steps.map((s, i) => {
          const at = typingDone + i * every;
          const text = s.text.length > maxChars ? s.text.slice(0, maxChars - 1) + "…" : s.text;
          return (
            <div key={i} style={{ display: "flex", gap: 16, marginTop: 10, ...appear(frame, at, 14) }}>
              <span
                style={{
                  color: NODE_COLOR[s.node] ?? C.text,
                  minWidth: 330,
                  whiteSpace: "nowrap",
                  fontWeight: 700,
                }}
              >
                ● {s.node}
              </span>
              <span style={{ color: C.muted }}>{text}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
};

/** Frame at which step `i` of a Terminal appears (to sync other visuals with it). */
export const stepFrame = (user: string, i: number, start = 10, every = 60) =>
  start + Math.ceil(user.length / 1.6) + 12 + i * every;
