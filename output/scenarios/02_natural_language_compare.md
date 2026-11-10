# Natural-language search + side-by-side comparison

_Start from a one-line ask, then compare the top 3 head to head._

## Turn 1

**User:** Find me candidates with React and 3+ years experience

**Agent reasoning (graph nodes):**
```
[parse_jd] Read the job brief from chat (9 words).
[extract_requirements] rule-based parser: must-have = React 3+y; nice-to-have = none; 3+ yrs total
[search_resumes] Round 1: RAG query 'React React' over 100 resumes -> kept top 10 (cut-off quick score 93.8). Most common misses: no React (80).
[rank_candidates] Round 2: scored 10 candidates requirement by requirement (evidenced years, resume quotes). Leader: Aisha Bello (99.8).
[rank_candidates] Round 3: hire/no-hire -> Strong Hire 8, Borderline 1, No Hire 1.
[generate_report] Wrote the explainable match report to output/reports/candidates_with_react_3_yrs_v1.md.
```

**Agent:**

## Shortlist: Candidates with React 3+ yrs
**Candidates with React 3+ yrs**
Must-have: React (3+ yrs)
Nice-to-have: none
Experience: 3+ years total

Screened **100** resumes -> deep-analysed **10** -> recommendations below.

| # | Candidate | Score | Verdict | Top strength | Main gap |
|---|---|---|---|---|---|
| 1 | Aisha Bello | 99.8 | Strong Hire | React: 6 yrs evidenced, 3 above the bar | - |
| 2 | John Carter | 99.8 | Strong Hire | React: 8 yrs evidenced, 5 above the bar | - |
| 3 | Yusuf Yilmaz | 99.8 | Strong Hire | React: 14 yrs evidenced, 11 above the bar | - |
| 4 | Ivan Garcia | 99.7 | Strong Hire | React: 10 yrs evidenced, 7 above the bar | - |
| 5 | Wen Costa | 99.7 | Strong Hire | React: 7 yrs evidenced, 4 above the bar | - |
| 6 | Jane Brooks | 98.1 | Strong Hire | React: 5 yrs evidenced, 2 above the bar | - |
| 7 | Jonas Garcia | 95 | Strong Hire | React: 3 yrs evidenced | - |
| 8 | Tara Mensah | 94.8 | Strong Hire | React: 3 yrs evidenced | - |
| 9 | Yara Johansson | 76.4 | Borderline | - | React (must-have): 2 of 3 required years evidenced |
| 10 | Sofia Rossi | 58.1 | No Hire | 6 years total experience | React (must-have): 1 of 3 required years evidenced |

### Agent assessment
Aisha Bello leads with 99.8/100: React: 6 yrs evidenced, 3 above the bar, 6 years total experience, Leadership/mentoring evidence.

### Borderline - what would make them a hire
- **Yara Johansson**: React: 2 of 3 required years evidenced. Probe adjacent experience in the screen; consider a mid-level offer or revisit in 6-12 months.

Full match report (all 10 candidates, evidence per requirement): `output/reports/candidates_with_react_3_yrs_v1.md`

_Try: "Compare the top 3", "Why did X rank higher than Y?", "Make GraphQL a must-have", "Interview questions for X", "Tell me about X"._

## Turn 2

**User:** Compare the top 3 matches side by side

**Agent reasoning (graph nodes):**
```
[human_feedback] Routed to 'compare' via rules; top 3
[compare_candidates] Compared Aisha Bello, John Carter, Yusuf Yilmaz; winner Aisha Bello.
```

**Agent:**

## Head-to-head: Aisha Bello vs John Carter vs Yusuf Yilmaz

| Requirement | Aisha Bello | John Carter | Yusuf Yilmaz | Edge |
|---|---|---|---|---|
| React (must) | [+] 6 yrs evidenced (needs 3) | [+] 8 yrs evidenced (needs 3) | [+] 14 yrs evidenced (needs 3) | tie |
| **Score / verdict** | **99.8** Strong Hire | **99.8** Strong Hire | **99.8** Strong Hire | Aisha Bello |

Aisha Bello comes out ahead overall, leading or sharing the lead on 0 of 1 requirement rows. Aisha Bello: Strong Hire (99.8). John Carter: Strong Hire (99.8). Yusuf Yilmaz: Strong Hire (99.8).
