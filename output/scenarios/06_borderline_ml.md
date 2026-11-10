# Borderline candidates and improvement suggestions

_ML role: inspect a borderline candidate, compare them with the leader, end the session._

## Turn 1

**User:** job_descriptions/ml_engineer.txt

**Agent reasoning (graph nodes):**
```
[parse_jd] Read the job brief from job_descriptions/ml_engineer.txt (33 words).
[extract_requirements] rule-based parser: must-have = Python 3+y, PyTorch, Machine Learning; nice-to-have = NLP or LLM, MLOps, Airflow, Kubernetes, FastAPI
[search_resumes] Round 1: RAG query 'Python PyTorch Machine Learning Python PyTorch Machine Learning NLP LLM MLOps Airflow Kubernetes FastAPI Machine Learning Engineer' over 100 resumes -> kept top 10 (cut-off quick score 87.7). Most common misses: no PyTorch (87), no Machine Learning (86), no Python (46).
[rank_candidates] Round 2: scored 10 candidates requirement by requirement (evidenced years, resume quotes). Leader: Omar Haddad (99.4).
[rank_candidates] Round 3: hire/no-hire -> Strong Hire 6, Hire 2, Borderline 1, No Hire 1.
[generate_report] Wrote the explainable match report to output/reports/machine_learning_engineer_v1.md.
```

**Agent:**

## Shortlist: Machine Learning Engineer
**Machine Learning Engineer**
Must-have: Python (3+ yrs), PyTorch, Machine Learning
Nice-to-have: NLP or LLM, MLOps, Airflow, Kubernetes, FastAPI

Screened **100** resumes -> deep-analysed **10** -> recommendations below.

| # | Candidate | Score | Verdict | Top strength | Main gap |
|---|---|---|---|---|---|
| 1 | Omar Haddad | 99.4 | Strong Hire | Python: 5 yrs evidenced, 2 above the bar | - |
| 2 | Ivan Fischer | 87.9 | Strong Hire | Python: 12 yrs evidenced, 9 above the bar | Airflow (nice-to-have): not found on resume |
| 3 | Uma Nakamura | 87.8 | Strong Hire | Python: 7 yrs evidenced, 4 above the bar | NLP or LLM (nice-to-have): none of NLP or LLM found |
| 4 | Tara Garcia | 86.9 | Strong Hire | Python: 4 yrs evidenced, 1 above the bar | MLOps (nice-to-have): not found on resume |
| 5 | Dana Dubois | 86.2 | Strong Hire | Python: 3 yrs evidenced | MLOps (nice-to-have): not found on resume |
| 6 | Sara Lindqvist | 85.5 | Strong Hire | Python: 6 yrs evidenced, 3 above the bar | NLP or LLM (nice-to-have): NLP: listed on resume but no work experience shows it |
| 7 | Tomas Fernandes | 84.6 | Hire | Python: 5 yrs evidenced, 2 above the bar | NLP or LLM (nice-to-have): none of NLP or LLM found |
| 8 | Ingrid Esposito | 81.4 | Hire | Python: 9 yrs evidenced, 6 above the bar | NLP or LLM (nice-to-have): none of NLP or LLM found |
| 9 | Vera Takahashi | 65.4 | Borderline | PyTorch: 1 yr evidenced | Python (must-have): 1 of 3 required years evidenced |
| 10 | Samir Bakker | 57.2 | No Hire | Machine Learning: 1 yr evidenced | Python (must-have): 1 of 3 required years evidenced |

### Agent assessment
Omar Haddad leads with 99.4/100: Python: 5 yrs evidenced, 2 above the bar, PyTorch: 4 yrs evidenced, Machine Learning: 4 yrs evidenced.

### Borderline - what would make them a hire
- **Vera Takahashi**: Python: 1 of 3 required years evidenced. Probe adjacent experience in the screen; consider a mid-level offer or revisit in 6-12 months.

Full match report (all 10 candidates, evidence per requirement): `output/reports/machine_learning_engineer_v1.md`

_Try: "Compare the top 3", "Why did X rank higher than Y?", "Make GraphQL a must-have", "Interview questions for X", "Tell me about X"._

## Turn 2

**User:** Tell me about Vera Takahashi

**Agent reasoning (graph nodes):**
```
[human_feedback] Routed to 'detail' via rules; candidates: Vera Takahashi
[candidate_report] Match report for Vera Takahashi.
```

**Agent:**

### 9. Vera Takahashi - Junior ML Engineer  (65.4/100, Borderline)
*resumes/resume_vera_takahashi.docx | 1 yrs total*

**Recommendation:** Borderline: close: Python is 1 of 3 required years evidenced (score 65.4/100, 2/3 must-haves met)

| Requirement | Type | Status | Evidence |
|---|---|---|---|
| Python 3+ yrs | must | partial | 1 of 3 required years evidenced |
| PyTorch | must | met | Shipped PyTorch features for search ranking using Machine Learning. |
| Machine Learning | must | met | Junior ML Engineer - Umbra Systems  (2025 - Present) |
| NLP or LLM | nice | missing | none of NLP or LLM found |
| MLOps | nice | listed | listed on resume but no work experience shows it |
| Airflow | nice | missing | not found on resume |
| Kubernetes | nice | missing | not found on resume |
| FastAPI | nice | missing | not found on resume |

**Strengths:** PyTorch: 1 yr evidenced; Machine Learning: 1 yr evidenced
**Gaps:** Python (must-have): 1 of 3 required years evidenced; NLP or LLM (nice-to-have): none of NLP or LLM found; MLOps (nice-to-have): listed on resume but no work experience shows it; Airflow (nice-to-have): not found on resume; Kubernetes (nice-to-have): not found on resume; FastAPI (nice-to-have): not found on resume

**Improvement suggestions:**
- Python: 1 of 3 required years evidenced. Probe adjacent experience in the screen; consider a mid-level offer or revisit in 6-12 months.

## Turn 3

**User:** Compare Omar Haddad and Vera Takahashi

**Agent reasoning (graph nodes):**
```
[human_feedback] Routed to 'compare' via rules; candidates: Omar Haddad, Vera Takahashi
[compare_candidates] Compared Omar Haddad, Vera Takahashi; winner Omar Haddad.
```

**Agent:**

## Head-to-head: Omar Haddad vs Vera Takahashi

| Requirement | Omar Haddad | Vera Takahashi | Edge |
|---|---|---|---|
| Python (must) | [+] 5 yrs evidenced (needs 3) | [~] 1 of 3 required years evidenced | Omar Haddad |
| PyTorch (must) | [+] 4 yrs evidenced | [+] 1 yr evidenced | tie |
| Machine Learning (must) | [+] 4 yrs evidenced | [+] 1 yr evidenced | tie |
| NLP or LLM (nice) | [+] NLP: 4 yrs evidenced | [-] none of NLP or LLM found | Omar Haddad |
| MLOps (nice) | [+] 4 yrs evidenced | [?] listed on resume but no work experience shows it | Omar Haddad |
| Airflow (nice) | [+] 4 yrs evidenced | [-] not found on resume | Omar Haddad |
| Kubernetes (nice) | [+] 4 yrs evidenced | [-] not found on resume | Omar Haddad |
| FastAPI (nice) | [+] 4 yrs evidenced | [-] not found on resume | Omar Haddad |
| **Score / verdict** | **99.4** Strong Hire | **65.4** Borderline | Omar Haddad |

Omar Haddad comes out ahead overall, leading or sharing the lead on 6 of 8 requirement rows. Omar Haddad: Strong Hire (99.4). Vera Takahashi: Borderline (65.4).

## Turn 4

**User:** done

**Agent reasoning (graph nodes):**
```
[human_feedback] Routed to 'end' via rules
```

**Agent:**

Session ended. Reports are in output/reports/.
