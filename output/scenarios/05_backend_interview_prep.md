# Backend role: candidate deep dive + interview questions

_Different JD; drill into a candidate and generate tailored screening questions._

## Turn 1

**User:** job_descriptions/backend_python.txt

**Agent reasoning (graph nodes):**
```
[parse_jd] Read the job brief from job_descriptions/backend_python.txt (51 words).
[extract_requirements] rule-based parser: must-have = Python 4+y, Django or FastAPI, PostgreSQL, REST; nice-to-have = Docker, Kubernetes, AWS, Celery or Redis, Terraform; 4+ yrs total
[search_resumes] Round 1: RAG query 'Python Django FastAPI PostgreSQL REST Python Django FastAPI PostgreSQL REST Docker Kubernetes AWS Celery Redis Terraform Backend Engineer (Python)' over 100 resumes -> kept top 10 (cut-off quick score 74.9). Most common misses: no PostgreSQL (81), no Django or FastAPI (79), no REST (57).
[rank_candidates] Round 2: scored 10 candidates requirement by requirement (evidenced years, resume quotes). Leader: Nina Petrova (100).
[rank_candidates] Round 3: hire/no-hire -> Strong Hire 3, Borderline 2, No Hire 5.
[generate_report] Wrote the explainable match report to output/reports/backend_engineer_python_v1.md.
```

**Agent:**

## Shortlist: Backend Engineer (Python)
**Backend Engineer (Python)**
Must-have: Python (4+ yrs), Django or FastAPI, PostgreSQL, REST
Nice-to-have: Docker, Kubernetes, AWS, Celery or Redis, Terraform
Experience: 4+ years total

Screened **100** resumes -> deep-analysed **10** -> recommendations below.

| # | Candidate | Score | Verdict | Top strength | Main gap |
|---|---|---|---|---|---|
| 1 | Nina Petrova | 100 | Strong Hire | Python: 9 yrs evidenced, 5 above the bar | - |
| 2 | John Doe | 89.7 | Strong Hire | Python: 10 yrs evidenced, 6 above the bar | Docker (nice-to-have): listed on resume but no work experience shows it |
| 3 | Samir Yilmaz | 86.8 | Strong Hire | Python: 12 yrs evidenced, 8 above the bar | Docker (nice-to-have): not found on resume |
| 4 | Nikhil Johansson | 80.8 | Borderline | Python: 4 yrs evidenced | PostgreSQL (must-have): listed on resume but no work experience shows it |
| 5 | Rania Xu | 70.9 | Borderline | Python: 5 yrs evidenced, 1 above the bar | Django or FastAPI (must-have): FastAPI: listed on resume but no work experience shows it |
| 6 | Bianca Fernandes | 64.6 | No Hire | PostgreSQL: 7 yrs evidenced | Python (must-have): listed on resume but no work experience shows it |
| 7 | Oscar Andersson | 56.1 | No Hire | Python: 5 yrs evidenced, 1 above the bar | PostgreSQL (must-have): not found on resume |
| 8 | Lena Ibrahim | 55 | No Hire | Python: 5 yrs evidenced, 1 above the bar | PostgreSQL (must-have): not found on resume |
| 9 | Pedro Ibrahim | 45.2 | No Hire | PostgreSQL: 7 yrs evidenced | Python (must-have): listed on resume but no work experience shows it |
| 10 | Ximena Garcia | 32.8 | No Hire | Bonus: Celery or Redis | Python (must-have): 2 of 4 required years evidenced |

### Agent assessment
Nina Petrova leads with 100/100: Python: 9 yrs evidenced, 5 above the bar, Django or FastAPI: 5 yrs evidenced, PostgreSQL: 5 yrs evidenced.

### Borderline - what would make them a hire
- **Nikhil Johansson**: PostgreSQL: listed but never shown in a role. Ask for a PostgreSQL code sample or a short take-home; if it holds up they clear this bar.
- **Rania Xu**: Django or FastAPI: listed but never shown in a role. Ask for a Django or FastAPI code sample or a short take-home; if it holds up they clear this bar.

Full match report (all 10 candidates, evidence per requirement): `output/reports/backend_engineer_python_v1.md`

_Try: "Compare the top 3", "Why did X rank higher than Y?", "Make GraphQL a must-have", "Interview questions for X", "Tell me about X"._

## Turn 2

**User:** Tell me about Nina Petrova

**Agent reasoning (graph nodes):**
```
[human_feedback] Routed to 'detail' via rules; candidates: Nina Petrova
[candidate_report] Match report for Nina Petrova.
```

**Agent:**

### 1. Nina Petrova - Senior Backend Engineer  (100/100, Strong Hire)
*resumes/resume_nina_petrova.docx | 9 yrs total*

**Recommendation:** Strong Hire: meets every must-have with room to spare (score 100/100, 4/4 must-haves met)

| Requirement | Type | Status | Evidence |
|---|---|---|---|
| Python 4+ yrs | must | met | Built Django REST APIs and Celery workers in Python for a data platform. |
| Django or FastAPI | must | met | Runs FastAPI and Python services on Kubernetes with PostgreSQL and Redis. |
| PostgreSQL | must | met | Runs FastAPI and Python services on Kubernetes with PostgreSQL and Redis. |
| REST | must | met | Built Django REST APIs and Celery workers in Python for a data platform. |
| Docker | nice | met | Led the move to Docker-based CI/CD with GitHub Actions and Terraform on AWS. |
| Kubernetes | nice | met | Runs FastAPI and Python services on Kubernetes with PostgreSQL and Redis. |
| AWS | nice | met | Led the move to Docker-based CI/CD with GitHub Actions and Terraform on AWS. |
| Celery or Redis | nice | met | Runs FastAPI and Python services on Kubernetes with PostgreSQL and Redis. |
| Terraform | nice | met | Led the move to Docker-based CI/CD with GitHub Actions and Terraform on AWS. |

**Strengths:** Python: 9 yrs evidenced, 5 above the bar; Django or FastAPI: 5 yrs evidenced; PostgreSQL: 5 yrs evidenced; Bonus: Docker; Bonus: Kubernetes; Bonus: AWS; Bonus: Celery or Redis; Bonus: Terraform; 9 years total experience; Leadership/mentoring evidence; Certified: Certified Kubernetes Application Developer (2022)
**Gaps:** none

## Turn 3

**User:** Interview questions for John Doe

**Agent reasoning (graph nodes):**
```
[human_feedback] Routed to 'questions' via rules; candidates: John Doe
[interview_questions] 6 questions for John Doe (depth on evidenced skills, probes on gaps).
```

**Agent:**

## Screening questions for John Doe

1. **[depth - Python]** You wrote: "Maintained internal Python tooling and Flask services; automated deployments with Fabric.". Walk me through the hardest Python problem in that work: what broke, how you diagnosed it, and what you would do differently now.
2. **[depth - Django or FastAPI]** You wrote: "Designed Python (FastAPI, SQLAlchemy) microservices handling 4,000 requests/second.". Walk me through the hardest Django or FastAPI problem in that work: what broke, how you diagnosed it, and what you would do differently now.
3. **[depth - PostgreSQL]** You wrote: "Wrote Python data-migration scripts that moved 80M rows between PostgreSQL clusters with zero". Walk me through the hardest PostgreSQL problem in that work: what broke, how you diagnosed it, and what you would do differently now.
4. **[learning agility - Docker, Kubernetes, AWS]** We also use Docker, Kubernetes, AWS. Which of these have you touched, and how do you usually pick up a new tool on a deadline?
5. **[behavioural - leadership]** Describe a time you mentored someone or led a technical decision the team disagreed with. How did you get to alignment?
6. **[behavioural - motivation]** Why are you looking to move on from Northwind Logistics, and what would make this Backend Engineer (Python) a step up for you?
