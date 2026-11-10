import { loadFont as loadInter } from "@remotion/google-fonts/Inter";
import { loadFont as loadMono } from "@remotion/google-fonts/JetBrainsMono";
import { Easing, interpolate } from "remotion";
import data from "./data/demo.json";

export const demo = data;

export const sans = loadInter("normal", { weights: ["400", "600", "800"], subsets: ["latin"] }).fontFamily;
export const mono = loadMono("normal", { weights: ["400", "700"], subsets: ["latin"] }).fontFamily;

export const C = {
  bg: "#0A0F1E",
  panel: "#111A30",
  panel2: "#16213D",
  border: "#25345A",
  text: "#E7EDF9",
  muted: "#8C9AB8",
  cyan: "#38BDF8",
  violet: "#A78BFA",
  green: "#34D399",
  amber: "#FBBF24",
  red: "#F87171",
  pink: "#F472B6",
};

export const FPS = 30;

export const NODE_COLOR: Record<string, string> = {
  parse_jd: C.cyan,
  extract_requirements: C.cyan,
  search_resumes: C.violet,
  rank_candidates: C.violet,
  generate_report: C.green,
  human_feedback: C.amber,
  refine_requirements: C.amber,
  compare_candidates: C.pink,
  explain_ranking: C.pink,
  interview_questions: C.pink,
  candidate_report: C.pink,
  chat_agent: C.red,
};

export const VERDICT_COLOR: Record<string, string> = {
  "Strong Hire": C.green,
  Hire: C.cyan,
  Borderline: C.amber,
  "No Hire": C.red,
};

export const STATUS_COLOR: Record<string, string> = {
  met: C.green,
  partial: C.amber,
  listed: C.amber,
  missing: C.red,
};

const ease = Easing.bezier(0.16, 1, 0.3, 1);

/** 0 -> 1 over `dur` frames starting at `start` (eased, clamped). */
export const rise = (frame: number, start: number, dur = 18) =>
  interpolate(frame, [start, start + dur], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: ease,
  });

/** Fade + slide-up style for list items that appear one after another. */
export const appear = (frame: number, start: number, dy = 24) => {
  const p = rise(frame, start);
  return { opacity: p, translate: `0px ${(1 - p) * dy}px` } as const;
};
