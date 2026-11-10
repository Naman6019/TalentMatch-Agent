"""RAG search over the resume pool (the retrieval half of retrieval-augmented generation).

Pipeline
--------
1. **Load** every resume through the Milestone 1 tools (``list_files`` + ``read_file``), so the
   sandbox and PDF/DOCX/TXT extraction are reused, not re-implemented.
2. **Chunk** each resume by meaning, not by character count: one chunk for the summary, one
   per experience role, one each for skills / education / certifications. A retrieved chunk is
   therefore a self-contained piece of evidence ("Frontend Engineer - Bluebird Media 2019-2022 ...").
3. **Index** chunks with BM25. Tokens are words *plus* canonical skill tokens from the taxonomy
   (``skill:react``), so "ReactJS", "React.js" and "react" all hit the same postings - a cheap,
   deterministic form of query expansion that needs no embedding model.
4. **Retrieve** chunks (``search``) or candidates (``search_candidates``: chunk scores
   aggregated per person). The agent feeds retrieved chunks to the LLM as grounded evidence.

The parsed :class:`profiles.CandidateProfile` objects are built in the same pass and cached on
disk (``.cache/index.json``), keyed by file size + mtime, so restarts are instant.
"""

from __future__ import annotations

import json
import math
import re
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

from fs_tools import get_root, list_files, read_file
from profiles import CandidateProfile, find_skills, parse_resume

import hashlib

# The cache is invalidated whenever the parsing code changes, not just when resumes change.
CACHE_VERSION = hashlib.sha1(b"".join(
    (Path(__file__).resolve().parent / f).read_bytes() for f in ("profiles.py", "rag_search.py")
)).hexdigest()[:12]
_WORD_RE = re.compile(r"[a-z0-9][a-z0-9+#.]*[a-z0-9+#]|[a-z0-9]")
_STOP = frozenset("a an and the of to in for with on at by from as is are was were be or our we i my "
                  "years year experience using used built".split())


@dataclass
class Chunk:
    chunk_id: str
    candidate_id: str
    name: str
    section: str
    text: str


def tokenize(text: str) -> list[str]:
    words = [w for w in _WORD_RE.findall(text.lower()) if w not in _STOP]
    skills = ["skill:" + s.lower() for s in find_skills(text)]
    return words + skills


def chunk_resume(text: str, profile: CandidateProfile) -> list[Chunk]:
    """Section/role-level chunks. Falls back to paragraph chunks if no sections are found."""
    from profiles import _ROLE_RE, _sections  # internal helpers, shared on purpose

    cid, name = profile.candidate_id, profile.name
    chunks: list[Chunk] = []
    sections = _sections(text)
    for section, body in sections.items():
        body = body.strip()
        if not body:
            continue
        if section == "EXPERIENCE":
            starts = [m.start() for m in _ROLE_RE.finditer(body)] or [0]
            for i, s in enumerate(starts):
                piece = body[s: starts[i + 1] if i + 1 < len(starts) else len(body)].strip()
                chunks.append(Chunk(f"{cid}#exp{i}", cid, name, "experience", piece))
        else:
            chunks.append(Chunk(f"{cid}#{section.lower().replace(' ', '_')}", cid, name, section.lower(), body))
    return chunks


class ResumeIndex:
    """BM25 index over resume chunks + the parsed candidate profiles."""

    k1 = 1.4
    b = 0.6

    def __init__(self, chunks: list[Chunk], profiles: dict[str, CandidateProfile], directory: str):
        self.chunks = chunks
        self.profiles = profiles
        self.directory = directory
        self._tokens = [tokenize(c.text + " " + c.section) for c in chunks]
        self._tf = [Counter(t) for t in self._tokens]
        self._len = [len(t) for t in self._tokens]
        self._avg = (sum(self._len) / len(self._len)) if self._len else 1.0
        df: Counter[str] = Counter()
        for tf in self._tf:
            df.update(tf.keys())
        n = len(chunks)
        self._idf = {t: math.log(1 + (n - d + 0.5) / (d + 0.5)) for t, d in df.items()}

    # ------------------------------------------------------------------ build
    @classmethod
    def build(cls, directory: str = "resumes", use_cache: bool = True) -> "ResumeIndex":
        files = list_files(directory)
        signature = [[f["path"], f["size_bytes"], f["modified"]] for f in files]
        cache = get_root() / ".cache" / f"index_{re.sub(r'[^a-z0-9]+', '_', directory.lower())}.json"
        if use_cache and cache.exists():
            try:
                data = json.loads(cache.read_text(encoding="utf-8"))
                if data.get("version") == CACHE_VERSION and data.get("signature") == signature:
                    profiles = {k: CandidateProfile(**v) for k, v in data["profiles"].items()}
                    return cls([Chunk(**c) for c in data["chunks"]], profiles, directory)
            except (ValueError, TypeError, KeyError):
                pass  # stale or corrupt cache -> rebuild

        chunks: list[Chunk] = []
        profiles: dict[str, CandidateProfile] = {}
        for f in files:
            result = read_file(f["path"])
            if not result.get("success"):
                continue  # unreadable file: skip, it simply isn't searchable
            cid = Path(f["path"]).stem
            profile = parse_resume(result["content"], cid, f["path"])
            profiles[cid] = profile
            chunks.extend(chunk_resume(result["content"], profile))

        if use_cache:
            cache.parent.mkdir(exist_ok=True)
            cache.write_text(json.dumps({
                "version": CACHE_VERSION, "signature": signature,
                "profiles": {k: p.to_dict() for k, p in profiles.items()},
                "chunks": [asdict(c) for c in chunks],
            }), encoding="utf-8")
        return cls(chunks, profiles, directory)

    # ------------------------------------------------------------------ query
    def _score(self, i: int, q_terms: Iterable[str]) -> float:
        tf, length = self._tf[i], self._len[i]
        score = 0.0
        for t in q_terms:
            f = tf.get(t)
            if f:
                score += self._idf.get(t, 0.0) * f * (self.k1 + 1) / (f + self.k1 * (1 - self.b + self.b * length / self._avg))
        return score

    def search(self, query: str, top_k: int = 5, candidate_ids: Iterable[str] | None = None,
               sections: Iterable[str] | None = None) -> list[dict[str, Any]]:
        """Top chunks for ``query`` (optionally restricted to some candidates / sections)."""
        q_terms = list(dict.fromkeys(tokenize(query)))
        allowed = set(candidate_ids) if candidate_ids is not None else None
        allowed_sections = set(sections) if sections is not None else None
        scored = []
        for i, c in enumerate(self.chunks):
            if allowed is not None and c.candidate_id not in allowed:
                continue
            if allowed_sections is not None and c.section not in allowed_sections:
                continue
            s = self._score(i, q_terms)
            if s > 0:
                scored.append((s, i))
        scored.sort(reverse=True)
        return [{"score": round(s, 3), **asdict(self.chunks[i])} for s, i in scored[:top_k]]

    def search_candidates(self, query: str, top_k: int = 10) -> list[dict[str, Any]]:
        """Candidates ranked by aggregated chunk relevance (max + 0.5 * sum of the rest)."""
        per: dict[str, list[float]] = defaultdict(list)
        q_terms = list(dict.fromkeys(tokenize(query)))
        for i, c in enumerate(self.chunks):
            s = self._score(i, q_terms)
            if s > 0:
                per[c.candidate_id].append(s)
        ranked = []
        for cid, scores in per.items():
            scores.sort(reverse=True)
            ranked.append((scores[0] + 0.5 * sum(scores[1:]), cid))
        ranked.sort(reverse=True)
        return [{"candidate_id": cid, "name": self.profiles[cid].name, "score": round(s, 3)}
                for s, cid in ranked[:top_k]]

    def evidence(self, candidate_id: str, skill: str, top_k: int = 2) -> list[str]:
        """Short quotes from a candidate's resume that support ``skill``."""
        hits = self.search(skill, top_k=top_k, candidate_ids=[candidate_id], sections=["experience"])
        quotes = []
        for h in hits:
            for line in h["text"].splitlines():
                if skill in find_skills(line):
                    quotes.append(line.strip(" *-•"))
                    break
        return quotes

    def find_candidate(self, name_or_id: str, prefer: Iterable[str] = ()) -> str | None:
        """Resolve 'john', 'John Carter' or 'resume_john_carter' to a candidate id.

        ``prefer`` (e.g. the current shortlist) wins ties, so "John" means the shortlisted John.
        """
        q = name_or_id.strip().lower().replace("_", " ")
        if not q:
            return None
        if name_or_id in self.profiles:
            return name_or_id
        prefer = list(prefer)
        exact = [cid for cid, p in self.profiles.items() if p.name.lower() == q]
        if exact:
            return exact[0]
        partial = [cid for cid, p in self.profiles.items()
                   if q in p.name.lower().split() or p.name.lower().startswith(q) or q in cid.replace("_", " ")]
        for cid in prefer:
            if cid in partial:
                return cid
        return partial[0] if partial else None


_INDEX: ResumeIndex | None = None


def get_index(directory: str = "resumes", rebuild: bool = False) -> ResumeIndex:
    """Process-wide index (built once)."""
    global _INDEX
    if _INDEX is None or rebuild or _INDEX.directory != directory:
        _INDEX = ResumeIndex.build(directory)
    return _INDEX


def rag_search(query: str, top_k: int = 5) -> dict[str, Any]:
    """Tool entry point: semantic-ish search over resume chunks, returns grounded snippets."""
    if not isinstance(query, str) or not query.strip():
        return {"success": False, "error": {"type": "invalid_argument", "message": "query must be a non-empty string"}}
    top_k = max(1, min(int(top_k), 20))
    hits = get_index().search(query, top_k=top_k)
    return {"success": True, "query": query, "count": len(hits),
            "results": [{k: h[k] for k in ("candidate_id", "name", "section", "score", "text")} for h in hits]}
