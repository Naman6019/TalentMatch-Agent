# Why did John rank higher than Jane?

_Explain a ranking with point deltas and requirement-level evidence._

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

**User:** Why did John rank higher than Jane?

**Agent reasoning (graph nodes):**
```
[human_feedback] Routed to 'explain' via rules; candidates: John Carter, Jane Brooks
[explain_ranking] John Carter vs Jane Brooks: gap 24 pts, biggest driver nice-to-haves.
```

**Agent:**

## Why John Carter (#1, 100) ranks above Jane Brooks (#8, 76)

Gap: **24 points**. Where it comes from:
- nice-to-haves: +14 pts for John Carter
- must-have coverage: +8.3 pts for John Carter
- depth beyond the bar: +1.3 pts for John Carter

| Requirement | John Carter | Jane Brooks |
|---|---|---|
| TypeScript (must) | 7 yrs evidenced | listed on resume but no work experience shows it |
| Next.js (nice) | 4 yrs evidenced | not found on resume |
| GraphQL (nice) | 4 yrs evidenced | not found on resume |
| Jest or Cypress (nice) | Jest: 4 yrs evidenced | Jest: listed on resume but no work experience shows it |
| AWS (nice) | 3 yrs evidenced | not found on resume |

John Carter is ahead by 24 points, mostly from nice-to-haves (+14). Key differences - TypeScript: 7 yrs evidenced vs listed on resume but no work experience shows it; Next.js: 4 yrs evidenced vs not found on resume.

## Turn 3

**User:** Tell me about Jane

**Agent reasoning (graph nodes):**
```
[human_feedback] Routed to 'detail' via rules; candidates: Jane Brooks
[candidate_report] Match report for Jane Brooks.
```

**Agent:**

### 8. Jane Brooks - Frontend Developer  (76/100, Borderline)
*resumes/resume_jane_brooks.docx | 5 yrs total*

**Recommendation:** Borderline: close: TypeScript is listed on resume but no work experience shows it (score 76/100, 4/5 must-haves met)

| Requirement | Type | Status | Evidence |
|---|---|---|---|
| React 3+ yrs | must | met | Implemented React component libraries from Figma designs with Tailwind CSS. |
| TypeScript | must | listed | listed on resume but no work experience shows it |
| JavaScript | must | met | Built patient-portal features in React and JavaScript with Redux and Storybook. |
| HTML | must | met | Maintained jQuery and HTML/CSS sites for local businesses. |
| CSS | must | met | Implemented React component libraries from Figma designs with Tailwind CSS. |
| Next.js | nice | missing | not found on resume |
| GraphQL | nice | missing | not found on resume |
| Jest or Cypress | nice | listed | Jest: listed on resume but no work experience shows it |
| Accessibility | nice | met | Drove accessibility fixes to WCAG 2.1 AA across 40 screens. |
| AWS | nice | missing | not found on resume |

**Strengths:** React: 5 yrs evidenced, 2 above the bar; Bonus: Accessibility; Certified: Meta Front-End Developer Professional Certificate (2021)
**Gaps:** TypeScript (must-have): listed on resume but no work experience shows it; Next.js (nice-to-have): not found on resume; GraphQL (nice-to-have): not found on resume; Jest or Cypress (nice-to-have): Jest: listed on resume but no work experience shows it; AWS (nice-to-have): not found on resume

**Improvement suggestions:**
- TypeScript: listed but never shown in a role. Ask for a TypeScript code sample or a short take-home; if it holds up they clear this bar.
