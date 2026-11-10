"""Build the 100-resume screening pool in ``resumes/`` (PDF / DOCX / TXT mix).

Composition (deterministic, seed 42):

* the 8 hand-written Milestone 1 candidates (``seed_resumes.RESUMES``),
* 10 hand-built "featured" candidates that make the demo conversations interesting
  (e.g. John Carter vs. Jane Brooks for the React role, an Angular expert with no React,
  a React Native developer with little web React),
* 82 generated candidates across 10 role archetypes with varied seniority, so the
  initial screen genuinely has to cut 100 down to 10.

All people, companies, e-mails (example.com) and phone numbers (555-01xx) are fictional.
Run ``python generate_resume_pool.py`` to (re)build the folder.
"""

from __future__ import annotations

import random
import shutil
from pathlib import Path
from typing import Any

from seed_resumes import RESUMES as SEED_RESUMES
from seed_resumes import render_docx, render_pdf, render_txt

OUT_DIR = Path(__file__).resolve().parent / "resumes"
POOL_SIZE = 100
REFERENCE_YEAR = 2026
RENDERERS = {"txt": render_txt, "pdf": render_pdf, "docx": render_docx}

Resume = dict[str, Any]


# --------------------------------------------------------------------------- #
# Featured candidates (hand-built so the demo flows have a story)
# --------------------------------------------------------------------------- #

def _job(role: str, company: str, dates: str, *bullets: str) -> dict[str, Any]:
    return {"role": role, "company": company, "dates": dates, "bullets": list(bullets)}


FEATURED: list[Resume] = [
    {
        "slug": "john_carter", "fmt": "pdf", "name": "John Carter", "title": "Senior Frontend Engineer",
        "contact": "john.carter@example.com | +1 (555) 010-0201 | Denver, CO | github.com/example-jcarter",
        "summary": "Frontend engineer with 7 years of experience shipping large React and TypeScript "
                   "applications. Owns performance, testing culture and GraphQL data layers.",
        "experience": [
            _job("Senior Frontend Engineer", "Summit Commerce", "2022 - Present",
                 "Led a team of 4 rebuilding checkout in React and TypeScript with Next.js; conversion up 11%.",
                 "Introduced a GraphQL (Apollo) data layer and Jest + Cypress test suites at 88% coverage.",
                 "Mentored 3 junior engineers; ran the frontend guild's accessibility reviews."),
            _job("Frontend Engineer", "Bluebird Media", "2019 - 2022",
                 "Built a React + Redux content editor in TypeScript used by 300 journalists.",
                 "Cut bundle size 40% with Webpack code-splitting; deployed to AWS CloudFront."),
            _job("Web Developer", "Pinecone Agency", "2018 - 2019",
                 "Developed JavaScript and React marketing sites with HTML, CSS and accessibility audits."),
        ],
        "education": ["B.S. Computer Science, University of Colorado Boulder, 2018"],
        "skills": {"Languages": "TypeScript, JavaScript, HTML, CSS",
                   "Frameworks": "React, Next.js, Redux, GraphQL, Apollo",
                   "Tooling": "Jest, Cypress, Webpack, Storybook, AWS, GitHub Actions"},
        "certifications": ["AWS Certified Cloud Practitioner (2021)"],
    },
    {
        "slug": "jane_brooks", "fmt": "docx", "name": "Jane Brooks", "title": "Frontend Developer",
        "contact": "jane.brooks@example.com | +1 (555) 010-0202 | Chicago, IL | janebrooks.example.dev",
        "summary": "Frontend developer with 5 years of experience building React interfaces in JavaScript. "
                   "Strong on UI craft and design systems; currently learning TypeScript.",
        "experience": [
            _job("Frontend Developer", "Lakeshore Health", "2022 - Present",
                 "Built patient-portal features in React and JavaScript with Redux and Storybook.",
                 "Drove accessibility fixes to WCAG 2.1 AA across 40 screens."),
            _job("UI Developer", "Maple Studio", "2021 - 2022",
                 "Implemented React component libraries from Figma designs with Tailwind CSS."),
            _job("Junior Web Developer", "Windy City Web", "2021 - 2021",
                 "Maintained jQuery and HTML/CSS sites for local businesses."),
        ],
        "education": ["B.A. Graphic Design, DePaul University, 2020",
                      "Frontend Web Development Bootcamp, 2021"],
        "skills": {"Languages": "JavaScript, HTML, CSS; learning TypeScript",
                   "Frameworks": "React, Redux, Tailwind CSS, jQuery",
                   "Tooling": "Storybook, Figma, Jest, Git"},
        "certifications": ["Meta Front-End Developer Professional Certificate (2021)"],
    },
    {
        "slug": "marcus_lee", "fmt": "txt", "name": "Marcus Lee", "title": "Full-Stack Engineer",
        "contact": "marcus.lee@example.com | +1 (555) 010-0203 | Atlanta, GA | github.com/example-mlee",
        "summary": "Full-stack engineer with 4 years of experience across React, TypeScript and Node.js "
                   "services on AWS.",
        "experience": [
            _job("Full-Stack Engineer", "Peachtree Fintech", "2023 - Present",
                 "Built React + TypeScript dashboards and Node.js REST APIs on AWS Lambda.",
                 "Added Playwright end-to-end tests; reduced production regressions by 30%."),
            _job("Software Engineer", "Northstar Labs", "2022 - 2023",
                 "Developed Node.js and Express services with PostgreSQL and Docker."),
        ],
        "education": ["B.S. Software Engineering, Georgia Tech, 2022"],
        "skills": {"Languages": "TypeScript, JavaScript, SQL",
                   "Frameworks": "React, Node.js, Express",
                   "Tooling": "AWS, Docker, PostgreSQL, Playwright"},
        "certifications": ["AWS Certified Developer - Associate (2024)"],
    },
    {
        "slug": "sofia_rossi", "fmt": "pdf", "name": "Sofia Rossi", "title": "Mobile Engineer",
        "contact": "sofia.rossi@example.com | +1 (555) 010-0204 | Boston, MA | github.com/example-srossi",
        "summary": "Mobile engineer with 6 years of experience, mostly React Native, recently moving "
                   "into web React work.",
        "experience": [
            _job("Mobile Engineer", "Harborline Travel", "2020 - Present",
                 "Shipped React Native apps in TypeScript to 1.2M users on iOS and Android.",
                 "Started contributing to the React web booking flow in 2025 (Next.js)."),
            _job("Junior Mobile Developer", "Copper Apps", "2020 - 2020",
                 "Built Android features in Kotlin."),
        ],
        "education": ["B.S. Computer Engineering, Northeastern University, 2020"],
        "skills": {"Languages": "TypeScript, JavaScript, Kotlin",
                   "Frameworks": "React Native, React, Next.js, Redux",
                   "Tooling": "Jest, Firebase, GitHub Actions"},
        "certifications": [],
    },
    {
        "slug": "ken_watanabe", "fmt": "docx", "name": "Ken Watanabe", "title": "Staff Frontend Engineer",
        "contact": "ken.watanabe@example.com | +1 (555) 010-0205 | San Jose, CA | github.com/example-kwatanabe",
        "summary": "Staff frontend engineer with 10 years of experience in Angular and TypeScript at scale.",
        "experience": [
            _job("Staff Frontend Engineer", "Granite Cloud", "2019 - Present",
                 "Architected an Angular and TypeScript console used by 20,000 enterprise admins.",
                 "Led RxJS state-management migration and Cypress test strategy."),
            _job("Frontend Engineer", "Redwood Systems", "2016 - 2019",
                 "Built Angular and JavaScript dashboards with GraphQL and accessibility support."),
        ],
        "education": ["M.S. Computer Science, San Jose State University, 2016"],
        "skills": {"Languages": "TypeScript, JavaScript, HTML, CSS",
                   "Frameworks": "Angular, RxJS, GraphQL",
                   "Tooling": "Cypress, Jest, Webpack, GCP"},
        "certifications": ["Google Professional Cloud Developer (2022)"],
    },
    {
        "slug": "aisha_bello", "fmt": "txt", "name": "Aisha Bello", "title": "Senior Frontend Engineer",
        "contact": "aisha.bello@example.com | +1 (555) 010-0206 | Remote | aishabello.example.dev",
        "summary": "Frontend engineer with 6 years of React and TypeScript experience in B2B SaaS, "
                   "specialising in GraphQL clients and Next.js performance.",
        "experience": [
            _job("Senior Frontend Engineer", "Cobalt Analytics", "2023 - Present",
                 "Owns the React and TypeScript analytics workspace built on Next.js and GraphQL.",
                 "Introduced Playwright visual tests and Storybook docs across 60 components."),
            _job("Frontend Engineer", "Tidewater SaaS", "2020 - 2023",
                 "Built React + TypeScript admin tools; moved REST calls to GraphQL with Apollo."),
        ],
        "education": ["B.Eng. Computer Engineering, University of Lagos, 2019"],
        "skills": {"Languages": "TypeScript, JavaScript, HTML, CSS",
                   "Frameworks": "React, Next.js, GraphQL, Apollo, Tailwind CSS",
                   "Tooling": "Playwright, Storybook, Vite, Vercel"},
        "certifications": [],
    },
    {
        "slug": "liam_oconnor", "fmt": "pdf", "name": "Liam O'Connor", "title": "Frontend Engineer",
        "contact": "liam.oconnor@example.com | +1 (555) 010-0207 | Dublin, Ireland | github.com/example-loconnor",
        "summary": "Frontend engineer with 3 years of React experience, mostly JavaScript, some TypeScript.",
        "experience": [
            _job("Frontend Engineer", "Emerald Payments", "2023 - Present",
                 "Built React features in JavaScript and TypeScript for a payments dashboard.",
                 "Wrote Jest unit tests and fixed accessibility issues flagged by axe."),
        ],
        "education": ["B.Sc. Computer Science, Trinity College Dublin, 2023"],
        "skills": {"Languages": "JavaScript, TypeScript, HTML, CSS",
                   "Frameworks": "React, Redux",
                   "Tooling": "Jest, Webpack"},
        "certifications": [],
    },
    {
        "slug": "nina_petrova", "fmt": "docx", "name": "Nina Petrova", "title": "Senior Backend Engineer",
        "contact": "nina.petrova@example.com | +1 (555) 010-0208 | Toronto, ON | github.com/example-npetrova",
        "summary": "Backend engineer with 9 years of Python experience across Django and FastAPI, "
                   "PostgreSQL and Kubernetes.",
        "experience": [
            _job("Senior Backend Engineer", "Aurora Insurance", "2021 - Present",
                 "Runs FastAPI and Python services on Kubernetes with PostgreSQL and Redis.",
                 "Led the move to Docker-based CI/CD with GitHub Actions and Terraform on AWS."),
            _job("Backend Engineer", "Lynx Data", "2017 - 2021",
                 "Built Django REST APIs and Celery workers in Python for a data platform."),
        ],
        "education": ["B.Sc. Computer Science, University of Toronto, 2017"],
        "skills": {"Languages": "Python, SQL, Go",
                   "Frameworks": "FastAPI, Django, Celery",
                   "Tooling": "Kubernetes, Docker, PostgreSQL, Redis, Terraform, AWS"},
        "certifications": ["Certified Kubernetes Application Developer (2022)"],
    },
    {
        "slug": "omar_haddad", "fmt": "txt", "name": "Omar Haddad", "title": "Machine Learning Engineer",
        "contact": "omar.haddad@example.com | +1 (555) 010-0209 | Austin, TX | github.com/example-ohaddad",
        "summary": "ML engineer with 5 years of experience training and serving PyTorch models, "
                   "with an NLP and LLM focus.",
        "experience": [
            _job("Machine Learning Engineer", "Signal Labs", "2022 - Present",
                 "Fine-tuned PyTorch NLP and LLM models; served them with FastAPI on Kubernetes.",
                 "Built MLOps pipelines with MLflow and Airflow."),
            _job("Data Scientist", "Prairie Analytics", "2021 - 2022",
                 "Built Python and scikit-learn models with pandas for churn prediction."),
        ],
        "education": ["M.S. Computer Science (Machine Learning), UT Austin, 2021"],
        "skills": {"Languages": "Python, SQL",
                   "Frameworks": "PyTorch, scikit-learn, pandas, FastAPI",
                   "Tooling": "Kubernetes, Airflow, MLflow, Docker"},
        "certifications": [],
    },
    {
        "slug": "grace_tan", "fmt": "pdf", "name": "Grace Tan", "title": "Frontend Engineer",
        "contact": "grace.tan@example.com | +1 (555) 010-0210 | Singapore | gracetan.example.dev",
        "summary": "Frontend engineer with 4 years of experience in React and TypeScript, "
                   "plus Vue.js for internal tools.",
        "experience": [
            _job("Frontend Engineer", "Lion City Logistics", "2022 - Present",
                 "Built React and TypeScript tracking dashboards with Next.js and Jest tests."),
            _job("Web Developer", "Merlion Digital", "2021 - 2022",
                 "Built Vue.js and JavaScript internal tools with REST APIs."),
        ],
        "education": ["B.Comp. Computer Science, National University of Singapore, 2021"],
        "skills": {"Languages": "TypeScript, JavaScript, HTML, CSS",
                   "Frameworks": "React, Next.js, Vue.js",
                   "Tooling": "Jest, Vite, Docker"},
        "certifications": [],
    },
]


# --------------------------------------------------------------------------- #
# Generated candidates
# --------------------------------------------------------------------------- #

FIRST_NAMES = [
    "Adrian", "Beatriz", "Caleb", "Dana", "Elena", "Farid", "Gabriel", "Hana", "Ivan", "Jasmine",
    "Kofi", "Lena", "Mateo", "Noor", "Oscar", "Paula", "Quentin", "Rosa", "Samir", "Tara",
    "Umar", "Vera", "Wesley", "Ximena", "Yusuf", "Zoe", "Arjun", "Bianca", "Chen", "Diego",
    "Esther", "Felix", "Gita", "Hugo", "Ingrid", "Jonas", "Keiko", "Luca", "Mira", "Nikhil",
    "Olivia", "Pedro", "Rania", "Stefan", "Tomas", "Uma", "Victor", "Wen", "Yara", "Zain",
]
LAST_NAMES = [
    "Alvarez", "Becker", "Costa", "Dubois", "Eriksen", "Fischer", "Gupta", "Hoffman", "Iyer", "Jensen",
    "Kowalski", "Larsen", "Moreau", "Nakamura", "Ortiz", "Patel", "Quinn", "Reyes", "Silva", "Takahashi",
    "Usman", "Vargas", "Weber", "Xu", "Yilmaz", "Zhang", "Andersson", "Bakker", "Chowdhury", "Delgado",
    "Esposito", "Fernandes", "Garcia", "Horvat", "Ibrahim", "Johansson", "Kim", "Lopez", "Mensah", "Novak",
]
COMPANIES = [
    "Acme Robotics", "Brightwave", "Cinder Labs", "Driftwood Software", "Echo Health", "Foxglove AI",
    "Gridline Energy", "Hollow Pine", "Ironclad Security", "Juniper Retail", "Keystone Bank", "Lumos Media",
    "Monarch Freight", "Nimbus Cloud", "Orchid Telecom", "Pebble Payments", "Quarry Games", "Riverbend Insurance",
    "Sable Analytics", "Thistle Education", "Umbra Systems", "Vantage Travel", "Willow Biotech", "Zephyr Mobility",
]
CITIES = ["Seattle, WA", "Austin, TX", "New York, NY", "Berlin, Germany", "London, UK", "Bangalore, India",
          "Toronto, ON", "Remote", "Amsterdam, NL", "Sydney, Australia", "Pune, India", "Lisbon, Portugal"]
UNIS = ["State University", "Institute of Technology", "University of Applied Sciences", "Polytechnic University"]

# archetype -> (titles by seniority, core skills, optional skills, bullet templates, degree)
ARCHETYPES: dict[str, dict[str, Any]] = {
    "frontend": {
        "titles": ["Junior Frontend Developer", "Frontend Engineer", "Senior Frontend Engineer"],
        "core": ["React", "JavaScript", "HTML", "CSS"],
        "optional": ["TypeScript", "Next.js", "Redux", "GraphQL", "Jest", "Cypress", "Tailwind CSS", "Storybook",
                     "Webpack", "Vue.js", "Accessibility", "AWS"],
        "templates": ["Built {a} and {b} user interfaces for a customer-facing web app.",
                      "Migrated legacy pages to {a}, improving load time by {n}%.",
                      "Set up {a} tests and {b} tooling for the frontend team."],
        "degree": "B.S. Computer Science",
    },
    "fullstack": {
        "titles": ["Junior Full-Stack Developer", "Full-Stack Engineer", "Senior Full-Stack Engineer"],
        "core": ["JavaScript", "Node.js", "SQL"],
        "optional": ["React", "TypeScript", "PostgreSQL", "MongoDB", "Docker", "AWS", "GraphQL", "Express",
                     "Vue.js", "Angular", "Redis", "Python"],
        "templates": ["Delivered features end to end with {a} on the frontend and {b} on the backend.",
                      "Designed REST APIs in {a} backed by {b}.",
                      "Containerised services with {a} and automated releases on {b}."],
        "degree": "B.S. Software Engineering",
    },
    "backend_python": {
        "titles": ["Junior Backend Developer", "Backend Engineer", "Senior Backend Engineer"],
        "core": ["Python", "SQL", "REST"],
        "optional": ["Django", "FastAPI", "Flask", "PostgreSQL", "Redis", "Docker", "Kubernetes", "AWS",
                     "Celery", "Kafka", "Terraform", "GraphQL"],
        "templates": ["Built {a} services with {b} handling {n}k requests per minute.",
                      "Refactored a monolith into {a} microservices using {b}.",
                      "Owned {a} schemas and {b} caching for core APIs."],
        "degree": "B.S. Computer Science",
    },
    "backend_java": {
        "titles": ["Junior Java Developer", "Java Engineer", "Senior Java Engineer"],
        "core": ["Java", "Spring Boot", "SQL"],
        "optional": ["Kotlin", "Kafka", "PostgreSQL", "MySQL", "Docker", "Kubernetes", "AWS", "Microservices",
                     "Redis", "Jenkins", "REST"],
        "templates": ["Developed {a} microservices with {b} for payment processing.",
                      "Tuned {a} queries and {b} consumers, cutting latency {n}%.",
                      "Migrated deployments to {a} with {b} pipelines."],
        "degree": "B.E. Computer Engineering",
    },
    "data_science": {
        "titles": ["Data Analyst", "Data Scientist", "Senior Data Scientist"],
        "core": ["Python", "SQL", "pandas"],
        "optional": ["scikit-learn", "Machine Learning", "Tableau", "Power BI", "Spark", "Airflow", "PyTorch",
                     "Statistics", "Excel", "TensorFlow"],
        "templates": ["Built {a} models with {b} that lifted retention by {n}%.",
                      "Automated reporting pipelines in {a} and {b}.",
                      "Ran A/B tests and presented {a} insights built on {b}."],
        "degree": "M.S. Statistics",
    },
    "ml": {
        "titles": ["Junior ML Engineer", "Machine Learning Engineer", "Senior Machine Learning Engineer"],
        "core": ["Python", "Machine Learning", "PyTorch"],
        "optional": ["TensorFlow", "NLP", "LLM", "MLOps", "Kubernetes", "Docker", "scikit-learn", "Spark",
                     "FastAPI", "AWS", "Computer Vision"],
        "templates": ["Trained {a} models and deployed them with {b}.",
                      "Built {a} pipelines on {b}, cutting training time {n}%.",
                      "Shipped {a} features for search ranking using {b}."],
        "degree": "M.S. Computer Science",
    },
    "devops": {
        "titles": ["Junior DevOps Engineer", "DevOps Engineer", "Senior Site Reliability Engineer"],
        "core": ["Linux", "Docker", "Kubernetes"],
        "optional": ["Terraform", "AWS", "GCP", "Azure", "Prometheus", "Grafana", "Python", "Go", "CI/CD",
                     "Jenkins", "GitHub Actions"],
        "templates": ["Ran {a} clusters provisioned with {b} across 3 regions.",
                      "Built {a} dashboards and {b} alerts, cutting MTTR {n}%.",
                      "Automated infrastructure with {a} and {b}."],
        "degree": "B.S. Information Technology",
    },
    "mobile": {
        "titles": ["Junior Mobile Developer", "Mobile Engineer", "Senior Mobile Engineer"],
        "core": ["Swift", "Kotlin"],
        "optional": ["iOS", "Android", "React Native", "Flutter", "Firebase", "TypeScript", "GraphQL", "CI/CD"],
        "templates": ["Shipped {a} and {b} releases to {n}0k monthly users.",
                      "Rebuilt onboarding in {a} with {b} analytics.",
                      "Maintained {a} apps and {b} pipelines."],
        "degree": "B.S. Computer Science",
    },
    "qa": {
        "titles": ["QA Analyst", "QA Automation Engineer", "Senior SDET"],
        "core": ["Selenium", "Test Automation"],
        "optional": ["Cypress", "Playwright", "Java", "Python", "JavaScript", "Jest", "CI/CD", "Jenkins", "REST"],
        "templates": ["Automated regression suites with {a} and {b}.",
                      "Cut release testing time {n}% with {a} on {b}.",
                      "Built API tests for {a} services using {b}."],
        "degree": "B.S. Information Systems",
    },
    "product": {
        "titles": ["Associate Product Manager", "Product Manager", "Senior Product Manager"],
        "core": ["Product Management", "Agile"],
        "optional": ["SQL", "Figma", "Jira", "A/B Testing", "Excel", "Tableau", "Stakeholder Management"],
        "templates": ["Owned the roadmap for {a} initiatives using {b}.",
                      "Launched features that grew activation {n}% using {a} and {b}.",
                      "Ran discovery interviews and {a} with {b}."],
        "degree": "MBA",
    },
}
# Weighted so the React role has a realistic but crowded field.
ARCHETYPE_WEIGHTS = {"frontend": 16, "fullstack": 12, "backend_python": 12, "backend_java": 8, "data_science": 8,
                     "ml": 7, "devops": 7, "mobile": 5, "qa": 4, "product": 3}


def _make_generated(rng: random.Random, index: int, used_names: set[str]) -> Resume:
    archetype = rng.choices(list(ARCHETYPE_WEIGHTS), weights=list(ARCHETYPE_WEIGHTS.values()))[0]
    spec = ARCHETYPES[archetype]
    while True:
        name = f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}"
        if name not in used_names:
            used_names.add(name)
            break
    total_years = rng.choice([0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 7, 8, 9, 10, 12, 14])
    level = 0 if total_years < 2 else (1 if total_years < 6 else 2)
    skills = list(spec["core"]) + rng.sample(spec["optional"], k=min(len(spec["optional"]), rng.randint(2, 6)))
    # A few candidates have a core skill only "listed" (no evidence in experience) -> a real gap to explain.
    listed_only = set(rng.sample(skills[: len(spec["core"])], k=1)) if rng.random() < 0.15 else set()

    # Split the career into 1-3 roles, most recent first.
    experience: list[dict[str, Any]] = []
    end = REFERENCE_YEAR
    remaining = max(total_years, 1)
    n_roles = 1 if remaining <= 2 else rng.randint(2, 3)
    for r in range(n_roles):
        span = remaining if r == n_roles - 1 else max(1, rng.randint(1, max(1, remaining - (n_roles - r - 1))))
        start = end - span
        remaining -= span
        role_level = max(0, level - r)
        evidence_pool = [s for s in skills if s not in listed_only]
        picks = rng.sample(evidence_pool, k=min(len(evidence_pool), rng.randint(2, 4)))
        bullets = []
        for t in rng.sample(spec["templates"], k=2):
            a, b = (picks + picks)[len(bullets)], (picks + picks)[len(bullets) + 1]
            bullets.append(t.format(a=a, b=b, n=rng.randint(10, 60)))
        if len(picks) > 2:
            bullets.append(f"Day-to-day stack: {', '.join(picks)}.")
        experience.append(_job(spec["titles"][role_level], rng.choice(COMPANIES),
                               f"{start} - {'Present' if r == 0 else end}", *bullets))
        end = start
        if remaining <= 0:
            break

    first, last = name.split(" ")
    grad_year = REFERENCE_YEAR - max(total_years, 1)
    return {
        "slug": f"{first}_{last}".lower(), "fmt": ["pdf", "docx", "txt"][index % 3],
        "name": name, "title": experience[0]["role"],
        "contact": f"{first.lower()}.{last.lower()}@example.com | +1 (555) 01{index % 100:02d}-{1000 + index} "
                   f"| {rng.choice(CITIES)}",
        "summary": f"{spec['titles'][level]} with {total_years} years of experience working with "
                   f"{', '.join(skills[:3])}.",
        "experience": experience,
        "education": [f"{spec['degree']}, {rng.choice(LAST_NAMES)} {rng.choice(UNIS)}, {grad_year}"],
        "skills": {"Core": ", ".join(skills[: len(spec["core"]) + 2]),
                   "Also": ", ".join(skills[len(spec["core"]) + 2:]) or "-"},
        "certifications": [],
    }


def build_pool(seed: int = 42) -> list[Resume]:
    rng = random.Random(seed)
    pool: list[Resume] = list(SEED_RESUMES) + list(FEATURED)
    used = {r["name"] for r in pool}
    i = 0
    while len(pool) < POOL_SIZE:
        pool.append(_make_generated(rng, i, used))
        i += 1
    return pool


def main() -> None:
    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir()
    pool = build_pool()
    for r in pool:
        RENDERERS[r["fmt"]](r, OUT_DIR / f"resume_{r['slug']}.{r['fmt']}")
    counts = {f: sum(r["fmt"] == f for r in pool) for f in RENDERERS}
    print(f"wrote {len(pool)} resumes to {OUT_DIR.name}/  {counts}")


if __name__ == "__main__":
    main()
