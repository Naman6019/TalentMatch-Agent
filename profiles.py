"""Turn raw resume text into a structured :class:`CandidateProfile`.

Everything here is deterministic and offline: a skill taxonomy with aliases, a parser for
``Role - Company (YYYY - YYYY|Present)`` experience lines, and per-skill *evidence*:

* ``skill_years[skill]`` - years of roles whose bullets mention the skill (overlaps merged),
* ``listed_only``         - skills that appear only in the SKILLS section, with no work evidence.

That evidence is what makes rankings explainable ("React: 3 yrs evidenced in 2 roles" vs.
"TypeScript: listed only").
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from functools import lru_cache
from typing import Any

REFERENCE_YEAR = 2026  # "Present" resolves to this year; fixed so results are reproducible.

# canonical skill -> aliases (regex fragments, matched case-insensitively with word guards)
SKILL_ALIASES: dict[str, list[str]] = {
    "React": [r"react(?:\.js|js)?(?!\s*native)"],
    "React Native": [r"react\s*native"],
    "TypeScript": [r"typescript"],
    "JavaScript": [r"javascript", r"es6"],
    "Node.js": [r"node(?:\.js|js)?"],
    "Next.js": [r"next\.?js"],
    "Vue.js": [r"vue(?:\.js)?"],
    "Angular": [r"angular(?:js)?"],
    "Redux": [r"redux"],
    "GraphQL": [r"graphql", r"apollo"],
    "HTML": [r"html5?"],
    "CSS": [r"css3?", r"scss"],
    "Tailwind CSS": [r"tailwind(?:\s*css)?"],
    "Jest": [r"jest"],
    "Cypress": [r"cypress"],
    "Playwright": [r"playwright"],
    "Selenium": [r"selenium"],
    "Storybook": [r"storybook"],
    "Webpack": [r"webpack"],
    "Accessibility": [r"accessib\w*", r"wcag", r"a11y"],
    "Python": [r"python"],
    "Django": [r"django"],
    "FastAPI": [r"fastapi"],
    "Flask": [r"flask"],
    "Celery": [r"celery"],
    "Java": [r"java(?!\s*script)"],
    "Kotlin": [r"kotlin"],
    "Spring Boot": [r"spring(?:\s*boot)?"],
    "Go": [r"golang"],
    "Swift": [r"swift"],
    "iOS": [r"ios"],
    "Android": [r"android"],
    "Flutter": [r"flutter"],
    "Express": [r"express(?:\.js)?"],
    "SQL": [r"sql(?!alchemy)"],
    "PostgreSQL": [r"postgres(?:ql)?"],
    "MySQL": [r"mysql"],
    "MongoDB": [r"mongo(?:db)?"],
    "Redis": [r"redis"],
    "Kafka": [r"kafka"],
    "REST": [r"rest(?:ful)?(?:\s*apis?)?(?=\W)"],
    "Microservices": [r"micro-?services?"],
    "Docker": [r"docker"],
    "Kubernetes": [r"kubernetes", r"k8s"],
    "Terraform": [r"terraform"],
    "AWS": [r"aws", r"amazon web services"],
    "GCP": [r"gcp", r"google cloud"],
    "Azure": [r"azure"],
    "CI/CD": [r"ci/cd", r"continuous (?:integration|delivery)"],
    "GitHub Actions": [r"github actions"],
    "Jenkins": [r"jenkins"],
    "Linux": [r"linux"],
    "Prometheus": [r"prometheus"],
    "Grafana": [r"grafana"],
    "Machine Learning": [r"machine learning", r"\bml\b(?!flow)"],
    "PyTorch": [r"pytorch"],
    "TensorFlow": [r"tensorflow"],
    "scikit-learn": [r"scikit-learn", r"sklearn"],
    "pandas": [r"pandas"],
    "NLP": [r"nlp", r"natural language processing"],
    "LLM": [r"llms?", r"large language models?"],
    "MLOps": [r"mlops", r"mlflow"],
    "Computer Vision": [r"computer vision"],
    "Spark": [r"spark"],
    "Airflow": [r"airflow"],
    "Statistics": [r"statistic\w*"],
    "Tableau": [r"tableau"],
    "Power BI": [r"power\s*bi"],
    "Excel": [r"excel"],
    "Figma": [r"figma"],
    "Agile": [r"agile", r"scrum"],
    "Product Management": [r"product manage\w*", r"roadmap"],
    "Test Automation": [r"test automation", r"automated (?:regression|tests?)"],
}
# Evidence of the key implies evidence of the values (a TypeScript role is JavaScript experience).
IMPLIES: dict[str, list[str]] = {
    "TypeScript": ["JavaScript"], "React": ["JavaScript", "HTML", "CSS"], "Next.js": ["React", "JavaScript"],
    "Vue.js": ["JavaScript", "HTML", "CSS"], "Angular": ["JavaScript", "HTML", "CSS"], "React Native": ["JavaScript"], "Node.js": ["JavaScript"],
    "Express": ["Node.js", "JavaScript", "REST"], "Django": ["Python", "REST"], "FastAPI": ["Python", "REST"],
    "Flask": ["Python", "REST"],
    "pandas": ["Python"], "PyTorch": ["Python"], "scikit-learn": ["Python"], "Spring Boot": ["Java", "REST"],
    "PostgreSQL": ["SQL"], "MySQL": ["SQL"], "Kubernetes": ["Docker"],
}


def expand_implied(skills: list[str]) -> list[str]:
    out = list(skills)
    for s in skills:
        for implied in IMPLIES.get(s, []):
            if implied not in out:
                out.append(implied)
    return out


# 'Go' needs case-sensitive matching ("go" is a common English word).
_CASE_SENSITIVE: dict[str, list[str]] = {"Go": [r"\bGo\b(?![-'])"]}


@lru_cache(maxsize=None)
def _compiled() -> list[tuple[str, re.Pattern[str]]]:
    out = []
    for skill, aliases in SKILL_ALIASES.items():
        out.append((skill, re.compile(r"(?<![\w.+#/-])(?:" + "|".join(aliases) + r")(?![\w+#])", re.I)))
    for skill, aliases in _CASE_SENSITIVE.items():
        out.append((skill, re.compile("|".join(aliases))))
    return out


def find_skills(text: str) -> list[str]:
    """Canonical skills mentioned in ``text`` (taxonomy order, de-duplicated)."""
    return [skill for skill, pattern in _compiled() if pattern.search(text)]


def canonical_skill(name: str) -> str:
    """Map a free-text skill name onto the taxonomy ('reactjs' -> 'React'); unknown names pass through."""
    hits = find_skills(name)
    if hits:
        # prefer the most specific hit ("React Native" over "React")
        return max(hits, key=len)
    return name.strip()


# --------------------------------------------------------------------------- #
# Profile
# --------------------------------------------------------------------------- #

@dataclass
class Role:
    title: str
    company: str
    start: int
    end: int
    skills: list[str]
    text: str

    @property
    def years(self) -> int:
        return max(self.end - self.start, 1 if self.end == self.start else 0)


@dataclass
class CandidateProfile:
    candidate_id: str          # file stem, e.g. "resume_john_carter"
    name: str
    headline: str
    filepath: str
    total_years: float
    skills: list[str]                          # everything mentioned anywhere
    skill_years: dict[str, float]              # skill -> evidenced years
    listed_only: list[str]                     # in SKILLS section but never evidenced in a role
    roles: list[dict[str, Any]] = field(default_factory=list)
    education: list[str] = field(default_factory=list)
    certifications: list[str] = field(default_factory=list)
    leadership: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @property
    def first_name(self) -> str:
        return self.name.split()[0] if self.name else ""


_ROLE_RE = re.compile(
    r"^\s*(?P<title>[^\n]+?)\s+-\s+(?P<company>[^\n(]+?)\s*\(\s*(?P<start>(?:19|20)\d{2})\s*[-–]\s*"
    r"(?P<end>(?:19|20)\d{2}|Present)\s*\)",
    re.M | re.I,
)
_SECTION_RE = re.compile(
    r"^\s*(PROFESSIONAL SUMMARY|SUMMARY|EXPERIENCE|PROJECTS|EDUCATION|SKILLS|CERTIFICATIONS)\s*$",
    re.M | re.I,
)
_SINCE_RE = re.compile(r"\b(?:since|in|from)\s+((?:19|20)\d{2})\b", re.I)
_LEADERSHIP_RE =re.compile(r"\b(led|mentor\w*|managed|team lead|architected|owns|owned)\b", re.I)


def _sections(text: str) -> dict[str, str]:
    marks = [(m.start(), m.end(), m.group(1).upper()) for m in _SECTION_RE.finditer(text)]
    out: dict[str, str] = {"HEADER": text[: marks[0][0]] if marks else text}
    for i, (_, end, name) in enumerate(marks):
        stop = marks[i + 1][0] if i + 1 < len(marks) else len(text)
        out[name] = out.get(name, "") + text[end:stop]
    return out


def _merge_years(spans: list[tuple[int, int]]) -> float:
    """Total years covered by possibly overlapping [start, end) spans; a same-year span counts 0.5."""
    if not spans:
        return 0.0
    total = 0.0
    merged: list[list[int]] = []
    for s, e in sorted(spans):
        if merged and s <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], e)
        else:
            merged.append([s, e])
    for s, e in merged:
        total += (e - s) if e > s else 0.5
    return float(total)


def _clean_lines(block: str) -> list[str]:
    lines = []
    for line in block.splitlines():
        line = line.strip().lstrip("*•-").strip()
        if line and not set(line) <= {"-"}:
            lines.append(line)
    return lines


def parse_resume(text: str, candidate_id: str, filepath: str) -> CandidateProfile:
    sections = _sections(text)
    header = _clean_lines(sections.get("HEADER", ""))
    name = header[0].title() if header else candidate_id
    name = re.sub(r"\bO'(\w)", lambda m: "O'" + m.group(1).upper(), name)
    headline = header[1] if len(header) > 1 else ""

    exp_text = sections.get("EXPERIENCE", "")
    matches = list(_ROLE_RE.finditer(exp_text))
    roles: list[Role] = []
    for i, m in enumerate(matches):
        body = exp_text[m.end(): matches[i + 1].start() if i + 1 < len(matches) else len(exp_text)]
        end = REFERENCE_YEAR if m.group("end").lower() == "present" else int(m.group("end"))
        roles.append(Role(m.group("title").strip(), m.group("company").strip(), int(m.group("start")), end,
                          expand_implied(find_skills(m.group("title") + "\n" + body)), body.strip()))

    skill_spans: dict[str, list[tuple[int, int]]] = {}
    for role in roles:
        # A bullet like "Started contributing to React in 2025" only evidences the skill from 2025 on.
        late: dict[str, int] = {}
        plain: set[str] = set(find_skills(role.title))
        for bullet in _clean_lines(role.text):
            since = _SINCE_RE.search(bullet)
            for skill in expand_implied(find_skills(bullet)):
                if since and role.start <= int(since.group(1)) <= role.end:
                    late[skill] = max(late.get(skill, 0), int(since.group(1)))
                else:
                    plain.add(skill)
        for skill in role.skills:
            start = role.start if skill in plain else late.get(skill, role.start)
            skill_spans.setdefault(skill, []).append((start, role.end))
    skill_years = {s: _merge_years(spans) for s, spans in skill_spans.items()}

    all_skills = find_skills(text)
    listed_section = sections.get("SKILLS", "") + sections.get("PROFESSIONAL SUMMARY", "") + sections.get("SUMMARY", "")
    listed_only = [s for s in find_skills(listed_section) if s not in skill_years]
    # "learning TypeScript" / "basic Python" are weak claims: treat as listed-only, never as evidence.
    for weak in re.finditer(r"\b(?:learning|basic|some|introductory|familiar with)\s+([\w.+#/ -]{2,30})", text, re.I):
        for s in find_skills(weak.group(1))[:1]:
            if s not in skill_years and s not in listed_only:
                listed_only.append(s)

    return CandidateProfile(
        candidate_id=candidate_id,
        name=name,
        headline=headline,
        filepath=filepath,
        total_years=_merge_years([(r.start, r.end) for r in roles]),
        skills=all_skills,
        skill_years=skill_years,
        listed_only=listed_only,
        roles=[{"title": r.title, "company": r.company, "start": r.start, "end": r.end, "skills": r.skills}
               for r in roles],
        education=_clean_lines(sections.get("EDUCATION", "")),
        certifications=_clean_lines(sections.get("CERTIFICATIONS", "")),
        leadership=bool(_LEADERSHIP_RE.search(exp_text)),
    )
