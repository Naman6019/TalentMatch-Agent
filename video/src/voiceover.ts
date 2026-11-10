import { ALL_FORMATS, Input, UrlSource } from "mediabunny";
import { getStaticFiles, staticFile } from "remotion";

/**
 * Your own voiceover recordings, one clip per scene, in video/public/voiceover/:
 *
 *   01-intro.mp3  02-stack.mp3  03-state-machine.mp3  04-agent-state.mp3  05-pipeline.mp3
 *   06-compare.mp3  07-explain.mp3  08-refine.mp3  09-interview.mp3  10-outro.mp3
 *
 * .mp3, .wav, .m4a and .ogg all work. Missing clips are fine (that scene stays silent).
 * A scene is stretched to fit its clip, so you never have to match the timings exactly; the
 * scene's animation just holds its last frame while you finish talking.
 *
 * Alternatively record ONE take for the whole video as voiceover/full.mp3 (or .wav/.m4a);
 * it plays from 0:00 over the unchanged scene timings in DEMO_SCRIPT.md.
 */
export const CLIP_NAMES: Record<string, string> = {
  Intro: "01-intro",
  Stack: "02-stack",
  StateMachine: "03-state-machine",
  AgentState: "04-agent-state",
  Pipeline: "05-pipeline",
  Compare: "06-compare",
  Explain: "07-explain",
  Refine: "08-refine",
  Interview: "09-interview",
  Outro: "10-outro",
};

const EXTENSIONS = ["mp3", "wav", "m4a", "ogg"];

/** Frames of silence before a clip starts (lets the fade-in finish) and after it ends. */
export const LEAD_IN = 18;
export const TAIL = 24;

export type ClipInfo = { src: string; seconds: number };

const probe = async (path: string): Promise<ClipInfo | null> => {
  const present = new Set(getStaticFiles().map((f) => f.name));
  for (const ext of EXTENSIONS) {
    const name = `voiceover/${path}.${ext}`;
    if (!present.has(name)) continue;
    const src = staticFile(name);
    try {
      const input = new Input({ formats: ALL_FORMATS, source: new UrlSource(src) });
      return { src, seconds: await input.computeDuration() };
    } catch {
      // unreadable file: try the next extension
    }
  }
  return null;
};

export const findClips = async (): Promise<{ full: ClipInfo | null; perScene: Record<string, ClipInfo | null> }> => {
  const full = await probe("full");
  const entries = await Promise.all(
    Object.entries(CLIP_NAMES).map(async ([id, name]) => [id, full ? null : await probe(name)] as const),
  );
  return { full, perScene: Object.fromEntries(entries) };
};
