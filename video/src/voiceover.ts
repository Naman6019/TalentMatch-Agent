import { ALL_FORMATS, Input, UrlSource } from "mediabunny";
import { getStaticFiles, staticFile } from "remotion";

/**
 * Your voiceover recordings live in video/public/voiceover/ (any sub-folder), named by scene number:
 *
 *   01  02  03  03-1  04  05  05-1  06  06-1  07  08  09  09-1  10
 *
 * "NN" is the scene's main clip; "NN-1", "NN-2" are the next beats of that scene in DEMO_SCRIPT.md
 * (e.g. 05 = terminal trace + funnel, 05-1 = shortlist table). "01-intro"-style names also work.
 * Audio-only files (.mp3 .wav .m4a .aac .ogg) are preferred over video files (.mp4 .mov .webm)
 * with the same name, so you can keep your raw screen recordings next to extracted audio.
 *
 * Placement: the main clip starts as the scene fades in; each beat clip starts when its visual
 * appears. If the previous clip is still playing then, the scene's animation pauses (holds the
 * frame) until you finish, so narration and visuals stay in sync. Scenes grow to fit their clips.
 *
 * A single take for the whole video can instead be saved as voiceover/full.*.
 */
export const SCENE_NUMBERS: Record<string, string> = {
  Intro: "01",
  Stack: "02",
  StateMachine: "03",
  AgentState: "04",
  Pipeline: "05",
  Compare: "06",
  Explain: "07",
  Refine: "08",
  Interview: "09",
  Outro: "10",
};

/** Scene-local frames where each beat's visual appears (beat 1, beat 2, ...). Keep in sync with the scenes. */
export const BEATS: Record<string, number[]> = {
  StateMachine: [450, 820], // token run, branches light up
  Pipeline: [870], // shortlist table
  Compare: [470], // comparison matrix
  Interview: [520], // borderline card
};

const AUDIO_EXT = ["mp3", "wav", "m4a", "aac", "ogg"];
const VIDEO_EXT = ["mp4", "mov", "webm", "mkv"];

/** Frames before the first clip (lets the fade-in finish), between clips, and after the last one. */
export const LEAD_IN = 18;
export const GAP = 8;
export const TAIL = 24;

export type ClipInfo = { src: string; seconds: number };

const duration = async (src: string) =>
  new Input({ formats: ALL_FORMATS, source: new UrlSource(src) }).computeDuration();

/** Find the best file for a clip key like "05" or "05-1". */
const findFile = (key: string): string | null => {
  const files = getStaticFiles()
    .map((f) => f.name)
    .filter((n) => n.startsWith("voiceover/"));
  const rank = (name: string) => {
    const base = name.split("/").pop() as string;
    const dot = base.lastIndexOf(".");
    const stem = base.slice(0, dot).toLowerCase();
    const ext = base.slice(dot + 1).toLowerCase();
    // exact "05-1", or "05-intro"-style for main clips (but never "05-1" when looking for "05")
    const matches = stem === key || (!key.includes("-") && stem.startsWith(`${key}-`) && !/^\d+-\d+$/.test(stem));
    if (!matches) return -1;
    if (AUDIO_EXT.includes(ext)) return 2;
    if (VIDEO_EXT.includes(ext)) return 1;
    return -1;
  };
  const best = files.map((n) => [rank(n), n] as const).filter(([r]) => r > 0).sort((a, b) => b[0] - a[0])[0];
  return best ? best[1] : null;
};

export const probe = async (key: string): Promise<ClipInfo | null> => {
  const name = findFile(key);
  if (!name) return null;
  try {
    const src = staticFile(name);
    return { src, seconds: await duration(src) };
  } catch {
    return null;
  }
};

export type ScenePlan = {
  /** Scene length in frames after fitting the clips. */
  duration: number;
  /** Pauses in the scene animation: hold original frame `at` for `len` frames. */
  holds: { at: number; len: number }[];
  /** Clips with their start frame in the (stretched) scene. */
  clips: { src: string; from: number }[];
};

/** Lay out one scene's clips against its beats. */
export const planScene = (
  id: string,
  base: number,
  clips: (ClipInfo | null)[], // [main, beat1, beat2, ...]
  fps: number,
  isFirst: boolean,
  transition: number,
): ScenePlan => {
  const beats = BEATS[id] ?? [];
  const holds: ScenePlan["holds"] = [];
  const placed: ScenePlan["clips"] = [];
  let delay = 0;
  let end = 0;
  clips.forEach((clip, i) => {
    if (!clip) return;
    const len = Math.ceil(clip.seconds * fps);
    let start: number;
    if (i === 0) {
      start = isFirst ? 6 : LEAD_IN;
    } else {
      const beat = beats[i - 1];
      if (beat === undefined) {
        start = end + GAP; // extra clip with no visual beat: right after the previous one
      } else {
        const visual = beat + delay;
        start = Math.max(visual, end + GAP);
        if (start > visual) {
          holds.push({ at: beat, len: start - visual });
          delay += start - visual;
        }
      }
    }
    placed.push({ src: clip.src, from: start });
    end = start + len;
  });
  const duration = Math.max(base + delay, placed.length ? end + TAIL + transition : 0);
  return { duration, holds, clips: placed };
};
