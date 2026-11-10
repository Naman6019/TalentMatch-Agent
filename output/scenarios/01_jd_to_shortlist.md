# JD file -> 3-round screen -> report

_Parse a JD, extract must/nice requirements, screen 100 resumes to 10, recommend hire/no-hire._

## Turn 1

**User:** job_descriptions/senior_frontend_react.txt

**Agent reasoning (graph nodes):**
```
[parse_jd] Read the job brief from job_descriptions/senior_frontend_react.txt (79 words).
[extract_requirements] rule-based parser: must-have = React 3+y, TypeScript, JavaScript, HTML, CSS; nice-to-have = Next.js, GraphQL, Jest or Cypress, Accessibility, AWS; 5+ yrs total
[search_resumes] Round 1: RAG query 'React TypeScript JavaScript HTML CSS React TypeScript JavaScript HTML CSS Next.js GraphQL Jest Cypress Accessibility AWS Senior Frontend Engineer' over 100 resumes -> kept top 10 (cut-off quick score 87.6). Most common misses: no HTML (85), no CSS (85), no React (80).
[rank_candidates] Round 2: scored 10 candidates requirement by requirement (evidenced years, resume quotes). Leader: John Carter (100).
[rank_candidates] Round 3: hire/no-hire -> Strong Hire 5, Hire 1, Borderline 3, No Hire 1.
[generate_report] Wrote the explainable match report to output/reports/senior_frontend_engineer_v1.md.
```

**Agent:**

## Shortlist: Senior Frontend Engineer
**Senior Frontend Engineer**
Must-have: React (3+ yrs), TypeScript, JavaScript, HTML, CSS
Nice-to-have: Next.js, GraphQL, Jest or Cypress, Accessibility, AWS
Experience: 5+ years total

Screened **100** resumes -> deep-analysed **10** -> recommendations below.

| # | Candidate | Score | Verdict | Top strength | Main gap |
|---|---|---|---|---|---|
| 1 | John Carter | 100 | Strong Hire | React: 8 yrs evidenced, 5 above the bar | - |
| 2 | Yusuf Yilmaz | 89.2 | Strong Hire | React: 14 yrs evidenced, 11 above the bar | GraphQL (nice-to-have): not found on resume |
| 3 | Aisha Bello | 87.7 | Strong Hire | React: 6 yrs evidenced, 3 above the bar | Jest or Cypress (nice-to-have): none of Jest or Cypress found |
| 4 | Alex Chen | 87.3 | Strong Hire | React: 5 yrs evidenced, 2 above the bar | Next.js (nice-to-have): listed on resume but no work experience shows it |
| 5 | Grace Tan | 87 | Strong Hire | React: 4 yrs evidenced, 1 above the bar | GraphQL (nice-to-have): not found on resume |
| 6 | Jonas Garcia | 79.8 | Hire | React: 3 yrs evidenced | Next.js (nice-to-have): not found on resume |
| 7 | Samir Gupta | 77.6 | Borderline | React: 3 yrs evidenced | TypeScript (must-have): listed on resume but no work experience shows it |
| 8 | Jane Brooks | 76 | Borderline | React: 5 yrs evidenced, 2 above the bar | TypeScript (must-have): listed on resume but no work experience shows it |
| 9 | Sofia Rossi | 75.7 | Borderline | TypeScript: 6 yrs evidenced | React (must-have): 1 of 3 required years evidenced |
| 10 | Yara Johansson | 69.2 | No Hire | Bonus: GraphQL | React (must-have): 2 of 3 required years evidenced |

### Agent assessment
John Carter leads with 100/100: React: 8 yrs evidenced, 5 above the bar, TypeScript: 7 yrs evidenced, Bonus: Next.js.

### Borderline - what would make them a hire
- **Samir Gupta**: TypeScript: listed but never shown in a role. Ask for a TypeScript code sample or a short take-home; if it holds up they clear this bar.
- **Jane Brooks**: TypeScript: listed but never shown in a role. Ask for a TypeScript code sample or a short take-home; if it holds up they clear this bar.
- **Sofia Rossi**: React: 1 of 3 required years evidenced. Probe adjacent experience in the screen; consider a mid-level offer or revisit in 6-12 months.

Full match report (all 10 candidates, evidence per requirement): `output/reports/senior_frontend_engineer_v1.md`

_Try: "Compare the top 3", "Why did X rank higher than Y?", "Make GraphQL a must-have", "Interview questions for X", "Tell me about X"._

## Turn 2

**User:** Show me the shortlist again

**Agent reasoning (graph nodes):**
```
[human_feedback] Routed to 'report' via rules
[generate_report] Wrote the explainable match report to output/reports/senior_frontend_engineer_v1.md.
```

**Agent:**

## Shortlist: Senior Frontend Engineer
**Senior Frontend Engineer**
Must-have: React (3+ yrs), TypeScript, JavaScript, HTML, CSS
Nice-to-have: Next.js, GraphQL, Jest or Cypress, Accessibility, AWS
Experience: 5+ years total

Screened **100** resumes -> deep-analysed **10** -> recommendations below.

| # | Candidate | Score | Verdict | Top strength | Main gap |
|---|---|---|---|---|---|
| 1 | John Carter | 100 | Strong Hire | React: 8 yrs evidenced, 5 above the bar | - |
| 2 | Yusuf Yilmaz | 89.2 | Strong Hire | React: 14 yrs evidenced, 11 above the bar | GraphQL (nice-to-have): not found on resume |
| 3 | Aisha Bello | 87.7 | Strong Hire | React: 6 yrs evidenced, 3 above the bar | Jest or Cypress (nice-to-have): none of Jest or Cypress found |
| 4 | Alex Chen | 87.3 | Strong Hire | React: 5 yrs evidenced, 2 above the bar | Next.js (nice-to-have): listed on resume but no work experience shows it |
| 5 | Grace Tan | 87 | Strong Hire | React: 4 yrs evidenced, 1 above the bar | GraphQL (nice-to-have): not found on resume |
| 6 | Jonas Garcia | 79.8 | Hire | React: 3 yrs evidenced | Next.js (nice-to-have): not found on resume |
| 7 | Samir Gupta | 77.6 | Borderline | React: 3 yrs evidenced | TypeScript (must-have): listed on resume but no work experience shows it |
| 8 | Jane Brooks | 76 | Borderline | React: 5 yrs evidenced, 2 above the bar | TypeScript (must-have): listed on resume but no work experience shows it |
| 9 | Sofia Rossi | 75.7 | Borderline | TypeScript: 6 yrs evidenced | React (must-have): 1 of 3 required years evidenced |
| 10 | Yara Johansson | 69.2 | No Hire | Bonus: GraphQL | React (must-have): 2 of 3 required years evidenced |

### Agent assessment
John Carter leads with 100/100: React: 8 yrs evidenced, 5 above the bar, TypeScript: 7 yrs evidenced, Bonus: Next.js.

### Borderline - what would make them a hire
- **Samir Gupta**: TypeScript: listed but never shown in a role. Ask for a TypeScript code sample or a short take-home; if it holds up they clear this bar.
- **Jane Brooks**: TypeScript: listed but never shown in a role. Ask for a TypeScript code sample or a short take-home; if it holds up they clear this bar.
- **Sofia Rossi**: React: 1 of 3 required years evidenced. Probe adjacent experience in the screen; consider a mid-level offer or revisit in 6-12 months.

Full match report (all 10 candidates, evidence per requirement): `output/reports/senior_frontend_engineer_v1.md`

_Try: "Compare the top 3", "Why did X rank higher than Y?", "Make GraphQL a must-have", "Interview questions for X", "Tell me about X"._
