# Change requirements mid-conversation, re-rank, explain the moves

_Make GraphQL a must-have, relax React years, then undo GraphQL; the agent re-screens each time._

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

**User:** Make GraphQL a must-have and relax React to 2 years

**Agent reasoning (graph nodes):**
```
[human_feedback] Routed to 'refine' via rules
[refine_requirements] (rule-based) GraphQL is now a must-have (was nice-to-have); React requirement changed from 3+ to 2+ years. Re-screening the pool.
[search_resumes] Round 1: RAG query 'React TypeScript JavaScript HTML CSS GraphQL React TypeScript JavaScript HTML CSS GraphQL Next.js Jest Cypress Accessibility AWS Senior Frontend Engineer' over 100 resumes -> kept top 10 (cut-off quick score 80.9). Most common misses: no HTML (85), no CSS (85), no GraphQL (80).
[rank_candidates] Round 2: scored 10 candidates requirement by requirement (evidenced years, resume quotes). Leader: John Carter (100).
[rank_candidates] Round 3: hire/no-hire -> Strong Hire 1, Hire 1, Borderline 1, No Hire 7.
[rank_candidates] Re-ranked after the requirement change: 11 candidates moved.
[generate_report] Wrote the explainable match report to output/reports/senior_frontend_engineer_v2.md.
```

**Agent:**

## Shortlist: Senior Frontend Engineer
**Senior Frontend Engineer**
Must-have: React (2+ yrs), TypeScript, JavaScript, HTML, CSS, GraphQL
Nice-to-have: Next.js, Jest or Cypress, Accessibility, AWS
Experience: 5+ years total

Screened **100** resumes -> deep-analysed **10** -> recommendations below.

| # | Candidate | Score | Verdict | Top strength | Main gap |
|---|---|---|---|---|---|
| 1 | John Carter | 100 | Strong Hire | React: 8 yrs evidenced, 6 above the bar | - |
| 2 | Aisha Bello | 84.7 | Hire | React: 6 yrs evidenced, 4 above the bar | Jest or Cypress (nice-to-have): none of Jest or Cypress found |
| 3 | Yara Johansson | 71.6 | Borderline | React: 2 yrs evidenced | TypeScript (must-have): listed on resume but no work experience shows it |
| 4 | Yusuf Yilmaz | 66.3 | No Hire | React: 14 yrs evidenced, 12 above the bar | GraphQL (must-have): not found on resume |
| 5 | Alex Chen | 64.1 | No Hire | React: 5 yrs evidenced, 3 above the bar | GraphQL (must-have): not found on resume |
| 6 | Ken Watanabe | 64.1 | No Hire | TypeScript: 7 yrs evidenced | React (must-have): not found on resume |
| 7 | Grace Tan | 63.8 | No Hire | React: 4 yrs evidenced, 2 above the bar | GraphQL (must-have): not found on resume |
| 8 | Chen Usman | 59.2 | No Hire | React: 6 yrs evidenced, 4 above the bar | TypeScript (must-have): not found on resume |
| 9 | Samir Gupta | 56 | No Hire | React: 3 yrs evidenced, 1 above the bar | TypeScript (must-have): listed on resume but no work experience shows it |
| 10 | Jane Brooks | 53.8 | No Hire | React: 5 yrs evidenced, 3 above the bar | TypeScript (must-have): listed on resume but no work experience shows it |

### What changed
- **Aisha Bello** #3 -> #2 (up; 87.7 -> 84.7): React (must-have) met, GraphQL (must-have) met; nice-to-haves -3.0
- **Yara Johansson** #10 -> #3 (up; 69.2 -> 71.6): React (must-have) met, GraphQL (must-have) met; must-have coverage +5.1; nice-to-haves -2.5
- **Yusuf Yilmaz** #2 -> #4 (down; 89.2 -> 66.3): GraphQL (must-have) missing, React (must-have) met; must-have coverage -9.2; nice-to-haves +2.5
- **Alex Chen** #4 -> #5 (down; 87.3 -> 64.1): GraphQL (must-have) missing, React (must-have) met; must-have coverage -9.2; nice-to-haves +2.0
- **Ken Watanabe** entered at #6 (64.1): newly entered the shortlist
- **Grace Tan** #5 -> #7 (down; 87 -> 63.8): GraphQL (must-have) missing, React (must-have) met; must-have coverage -9.2; nice-to-haves +2.0
- **Chen Usman** entered at #8 (59.2): newly entered the shortlist
- **Samir Gupta** #7 -> #9 (down; 77.6 -> 56): GraphQL (must-have) missing, React (must-have) met; must-have coverage -7.8; nice-to-haves +2.0
- **Jane Brooks** #8 -> #10 (down; 76 -> 53.8): GraphQL (must-have) missing, React (must-have) met; must-have coverage -7.8; nice-to-haves +1.5
- **Jonas Garcia** dropped out (was #6, 79.8)
- **Sofia Rossi** dropped out (was #9, 75.7)

### Agent assessment
John Carter leads with 100/100: React: 8 yrs evidenced, 6 above the bar, TypeScript: 7 yrs evidenced, GraphQL: 4 yrs evidenced.

### Borderline - what would make them a hire
- **Yara Johansson**: TypeScript: listed but never shown in a role. Ask for a TypeScript code sample or a short take-home; if it holds up they clear this bar.

Full match report (all 10 candidates, evidence per requirement): `output/reports/senior_frontend_engineer_v2.md`

_Try: "Compare the top 3", "Why did X rank higher than Y?", "Make GraphQL a must-have", "Interview questions for X", "Tell me about X"._

## Turn 3

**User:** Actually GraphQL is nice to have again

**Agent reasoning (graph nodes):**
```
[human_feedback] Routed to 'refine' via rules
[refine_requirements] (rule-based) GraphQL is now nice-to-have. Re-screening the pool.
[search_resumes] Round 1: RAG query 'React TypeScript JavaScript HTML CSS React TypeScript JavaScript HTML CSS Next.js Jest Cypress Accessibility AWS GraphQL Senior Frontend Engineer' over 100 resumes -> kept top 10 (cut-off quick score 87.6). Most common misses: no HTML (85), no CSS (85), no React (80).
[rank_candidates] Round 2: scored 10 candidates requirement by requirement (evidenced years, resume quotes). Leader: John Carter (100).
[rank_candidates] Round 3: hire/no-hire -> Strong Hire 5, Hire 1, Borderline 4.
[rank_candidates] Re-ranked after the requirement change: 11 candidates moved.
[generate_report] Wrote the explainable match report to output/reports/senior_frontend_engineer_v3.md.
```

**Agent:**

## Shortlist: Senior Frontend Engineer
**Senior Frontend Engineer**
Must-have: React (2+ yrs), TypeScript, JavaScript, HTML, CSS
Nice-to-have: Next.js, Jest or Cypress, Accessibility, AWS, GraphQL
Experience: 5+ years total

Screened **100** resumes -> deep-analysed **10** -> recommendations below.

| # | Candidate | Score | Verdict | Top strength | Main gap |
|---|---|---|---|---|---|
| 1 | John Carter | 100 | Strong Hire | React: 8 yrs evidenced, 6 above the bar | - |
| 2 | Yusuf Yilmaz | 89.2 | Strong Hire | React: 14 yrs evidenced, 12 above the bar | Jest or Cypress (nice-to-have): none of Jest or Cypress found |
| 3 | Aisha Bello | 87.7 | Strong Hire | React: 6 yrs evidenced, 4 above the bar | Jest or Cypress (nice-to-have): none of Jest or Cypress found |
| 4 | Alex Chen | 87.6 | Strong Hire | React: 5 yrs evidenced, 3 above the bar | Next.js (nice-to-have): listed on resume but no work experience shows it |
| 5 | Grace Tan | 87.3 | Strong Hire | React: 4 yrs evidenced, 2 above the bar | Accessibility (nice-to-have): not found on resume |
| 6 | Jonas Garcia | 80.1 | Hire | React: 3 yrs evidenced, 1 above the bar | Next.js (nice-to-have): not found on resume |
| 7 | Samir Gupta | 77.9 | Borderline | React: 3 yrs evidenced, 1 above the bar | TypeScript (must-have): listed on resume but no work experience shows it |
| 8 | Sofia Rossi | 77.5 | Borderline | TypeScript: 6 yrs evidenced | React (must-have): 1 of 2 required years evidenced |
| 9 | Jane Brooks | 76.3 | Borderline | React: 5 yrs evidenced, 3 above the bar | TypeScript (must-have): listed on resume but no work experience shows it |
| 10 | Yara Johansson | 72.9 | Borderline | React: 2 yrs evidenced | TypeScript (must-have): listed on resume but no work experience shows it |

### What changed
- **Yusuf Yilmaz** #4 -> #2 (up; 66.3 -> 89.2): GraphQL (nice-to-have) missing; must-have coverage +9.2; nice-to-haves -2.5
- **Aisha Bello** #2 -> #3 (down; 84.7 -> 87.7): GraphQL (nice-to-have) met; nice-to-haves +3.0
- **Alex Chen** #5 -> #4 (up; 64.1 -> 87.6): GraphQL (nice-to-have) missing; must-have coverage +9.2; nice-to-haves -2.0
- **Grace Tan** #7 -> #5 (up; 63.8 -> 87.3): GraphQL (nice-to-have) missing; must-have coverage +9.2; nice-to-haves -2.0
- **Jonas Garcia** entered at #6 (80.1): newly entered the shortlist
- **Samir Gupta** #9 -> #7 (up; 56 -> 77.9): GraphQL (nice-to-have) missing; must-have coverage +7.8; nice-to-haves -2.0
- **Sofia Rossi** entered at #8 (77.5): newly entered the shortlist
- **Jane Brooks** #10 -> #9 (up; 53.8 -> 76.3): GraphQL (nice-to-have) missing; must-have coverage +7.8; nice-to-haves -1.5
- **Yara Johansson** #3 -> #10 (down; 71.6 -> 72.9): GraphQL (nice-to-have) met; must-have coverage -1.4; nice-to-haves +2.5
- **Ken Watanabe** dropped out (was #6, 64.1)
- **Chen Usman** dropped out (was #8, 59.2)

### Agent assessment
John Carter leads with 100/100: React: 8 yrs evidenced, 6 above the bar, TypeScript: 7 yrs evidenced, Bonus: Next.js.

### Borderline - what would make them a hire
- **Samir Gupta**: TypeScript: listed but never shown in a role. Ask for a TypeScript code sample or a short take-home; if it holds up they clear this bar.
- **Sofia Rossi**: React: 1 of 2 required years evidenced. Probe adjacent experience in the screen; consider a mid-level offer or revisit in 6-12 months.
- **Jane Brooks**: TypeScript: listed but never shown in a role. Ask for a TypeScript code sample or a short take-home; if it holds up they clear this bar.

Full match report (all 10 candidates, evidence per requirement): `output/reports/senior_frontend_engineer_v3.md`

_Try: "Compare the top 3", "Why did X rank higher than Y?", "Make GraphQL a must-have", "Interview questions for X", "Tell me about X"._
