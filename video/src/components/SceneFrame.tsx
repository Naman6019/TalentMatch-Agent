import React from "react";
import { AbsoluteFill, Easing, Interactive, interpolate, useCurrentFrame } from "remotion";
import { C, sans } from "../theme";

/** Shared scene chrome: background grid, kicker + title, and a content area. */
export const SceneFrame: React.FC<{
  kicker: string;
  title: string;
  accent?: string;
  children: React.ReactNode;
}> = ({ kicker, title, accent = C.cyan, children }) => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill
      style={{
        backgroundColor: C.bg,
        backgroundImage:
          "radial-gradient(circle at 85% 0%, rgba(56,189,248,0.10), transparent 45%), radial-gradient(circle at 0% 100%, rgba(167,139,250,0.10), transparent 40%)",
        fontFamily: sans,
        color: C.text,
      }}
    >
      <AbsoluteFill
        style={{
          backgroundImage:
            "linear-gradient(rgba(255,255,255,0.025) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.025) 1px, transparent 1px)",
          backgroundSize: "64px 64px",
        }}
      />
      <div style={{ position: "absolute", left: 100, top: 70, right: 100 }}>
        <div
          style={{
            fontSize: 26,
            letterSpacing: 6,
            fontWeight: 600,
            color: accent,
            opacity: interpolate(frame, [0, 15], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
          }}
        >
          {kicker}
        </div>
        <Interactive.Div
          name="Scene title"
          style={{
            fontSize: 64,
            fontWeight: 800,
            marginTop: 8,
            lineHeight: 1.1,
            opacity: interpolate(frame, [4, 22], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
              easing: Easing.bezier(0.16, 1, 0.3, 1),
            }),
            translate: interpolate(frame, [4, 22], ["0px 30px", "0px 0px"], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
              easing: Easing.bezier(0.16, 1, 0.3, 1),
            }),
          }}
        >
          {title}
        </Interactive.Div>
      </div>
      <div style={{ position: "absolute", left: 100, right: 100, top: 230, bottom: 70 }}>{children}</div>
    </AbsoluteFill>
  );
};
