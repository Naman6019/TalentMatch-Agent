# Demo video: voiceover script

The silent cut is `demo/TalentMatch_demo_silent.mp4` (1920x1080, 30 fps, **5:22**), rendered with
Remotion from `video/`. Every number on screen comes from a real offline run of the agent
(`python export_video_data.py` regenerates `video/src/data/demo.json`).

## Recording your voiceover

**Recommended: one clip per scene.** Record each block below as its own file and save it in
`video/public/voiceover/` with exactly these names (`.mp3`, `.wav`, `.m4a` or `.ogg`):

| File | Scene | Base length | Beats inside the scene (seconds from scene start) |
|---|---|---|---|
| `01-intro` | Title | 14 s | |
| `02-stack` | Three tool layers | 24 s | |
| `03-state-machine` | State machine | 45 s | token runs at **15 s**, branches light up at **27 s** (one every 2.4 s) |
| `04-agent-state` | Agent state | 22 s | |
| `05-pipeline` | Flow 1: screening | 50 s | funnel 3–17 s, shortlist table at **29 s** |
| `06-compare` | Flow 2: NL query + compare | 35 s | comparison matrix at **16 s** |
| `07-explain` | Flow 3: why John > Jane | 35 s | waterfall at 5 s, evidence table at 13 s |
| `08-refine` | Flow 4: refinement | 45 s | bump chart at 11 s, reasons at 17 s |
| `09-interview` | Flow 5: questions + borderline | 35 s | borderline card at **17 s** |
| `10-outro` | Wrap-up | 22 s | |

You don't need to hit the timings: **each scene automatically stretches to fit its clip** (the
animation holds its last frame while you finish). Leave out a file and that scene stays silent.
Any recorder works (Windows Voice Recorder, Audacity, your phone). Keep a little silence at the start and end of each clip.

Then render the final video with your voice:

```bash
cd video
npm i                 # first time only
npx remotion studio   # optional: preview with audio
npm run render        # -> demo/TalentMatch_demo.mp4
```

**Alternative: one continuous take.** Save it as `video/public/voiceover/full.mp3` (or `.wav`/`.m4a`)
and follow the timecodes below; it plays from 0:00 over the unchanged scene timings (the last scene is
extended if your take runs long). Per-scene clips are ignored when `full.*` exists.

## Script

Timecodes are for the silent cut (or a single take). At a relaxed pace (~140 words/min)
the text fits its slot.

| Time · clip | On screen | Say |
|---|---|---|
| **0:00** · `01` | Title: *TalentMatch* | "This is TalentMatch, my Milestone 3 project: a LangGraph agent that screens resumes against a job description, explains every ranking, and changes its answer when the recruiter changes their mind." |
| **0:13** · `02` | Three tool layers | "The agent has three layers of tools. From Milestone 1, the sandboxed file tools: read, list, search and write, across PDF, DOCX and text. From Milestone 2, RAG search: each resume is split into meaningful chunks, one per job role or section, and indexed with BM25 plus skill tokens, so 'ReactJS' and 'React' match. And three new matching tools: extract requirements, compare candidates, and generate interview questions. The pool is a hundred resumes in three formats." |
| **0:37** · `03` | State machine builds up | "Here is the graph. It follows the brief: Start, Parse JD, Extract Requirements, Search Resumes, Rank Candidates, Generate Report, then the Human Feedback loop, and End." |
| **0:52** · `03` | Token runs along the top row | "On the first run a job description flows through all five nodes. Then the graph pauses at Human Feedback using LangGraph's interrupt, and waits for the recruiter." |
| **1:04** · `03` | Branches light up one by one | "What the recruiter says decides where it goes next. A requirement change goes to Refine, which loops back to Search, so the pool is re-screened and re-ranked. Compare, Explain, Interview Questions and Match Report each answer and come back to Feedback. Anything open-ended goes to a chat node where the LLM calls the tools itself. And 'done' ends the session." |
| **1:21** · `04` | Agent state | "The state is a TypedDict. It holds the conversation history, the job requirements and every version of them, the screening results with the reasoning behind them, and the previous shortlist, so ranking changes can be explained. It's checkpointed per conversation thread." |
| **1:43** · `05` | Flow 1: terminal trace + funnel | "Flow one: I give it the Senior Frontend job description. Watch the reasoning trace. It extracts five must-haves, React with three-plus years, TypeScript and the fundamentals, plus nice-to-haves. Round one is the RAG screen: a hundred resumes down to ten. Round two scores those ten requirement by requirement, counting years of evidence from actual job roles, not just the skills list. Round three gives hire or no-hire verdicts." |
| **2:12** · `05` | Shortlist table | "Here's the shortlist. John Carter is a Strong Hire with a perfect score. Note Jane Brooks at number eight: she has five years of React, but TypeScript only appears as 'learning TypeScript', so she's Borderline, not a hire. That distinction between *listed* and *evidenced* is what drives most of the explanations." |
| **2:32** · `06` | Flow 2: natural-language query | "Flow two shows the conversational side. 'Find me candidates with React and three-plus years experience.' It parses that into one must-have, React at three years, and runs the same pipeline." |
| **2:48** · `06` | Comparison matrix | "Back on the frontend role: 'Compare the top three side by side.' One row per requirement, with evidence in each cell. All three are Strong Hires on the must-haves; John wins on the nice-to-haves: GraphQL, testing and accessibility." |
| **3:07** · `07` | Flow 3: why John > Jane | "Flow three: 'Why did John rank higher than Jane?' The agent breaks the twenty-four-point gap into its parts: fourteen points from nice-to-haves, eight from must-have coverage, a little from depth. On the right, every difference is tied to evidence: TypeScript, seven years versus listed only. The numbers come from deterministic tools; the LLM only words the explanation, so it can't make up a reason." |
| **3:42** · `08` | Flow 4: refinement | "Flow four is iterative refinement. 'Make GraphQL a must-have and relax React to two years.' The requirement chips update, the whole pool is re-screened, and the bump chart shows who moved. Yara Johansson jumps from tenth to third, because two years of React now clears the bar and she has GraphQL. Yusuf, Alex and Grace drop because GraphQL is now required and they don't have it. The agent's own report lists each move with the reason, and two candidates fall off the shortlist entirely." |
| **4:26** · `09` | Flow 5: interview questions | "Flow five: 'Interview questions for Jane.' Depth questions quote her own resume back to her. Gap probes go after what's missing, TypeScript first. Then learning-agility and motivation questions." |
| **4:43** · `09` | Borderline card | "And for borderline candidates, an improvement suggestion. Vera Takahashi, for the ML role, meets PyTorch and machine learning but has one of three required Python years. The agent says what would get her over the line, instead of just rejecting her." |
| **5:00** · `10` | Wrap-up | "To wrap up: the agent is in matching_agent.py, the scoring in matching_tools.py, retrieval in rag_search.py, and six scripted conversation flows run with run_scenarios.py. Forty-seven tests pass with no API key. It runs fully offline, or with Claude, OpenAI, Gemini, OpenRouter or a local Ollama model. Every ranking comes with its reasons. Thanks for watching." |

## Re-rendering the silent cut

```bash
cd video
npm run render:silent   # temporarily move clips out of public/voiceover/ first
```
