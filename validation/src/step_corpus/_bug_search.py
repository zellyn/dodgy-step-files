"""Bug-report search over STEP_PROBLEM_CATALOG.json.

Acceptance criterion for the catalog: someone who hits a defective STEP file
in the wild and writes a good-faith bug report (in *their* words, not OCCT
API names) should be able to find a matching catalog entry.

This module turns that criterion into mechanical regression: a small BM25
index over the title / description / reproducer / expected_kernel_behavior /
notes fields, exposed as a Python API and a CLI.

CLI
---

    uv run python -m step_corpus._bug_search "non-watertight shell with tiny gap between faces"

Library
-------

    from step_corpus._bug_search import BugIndex
    idx = BugIndex.load()
    for score, entry in idx.search("torus with negative major radius", k=5):
        print(f"{score:6.2f}  {entry['id']}  {entry['title']}")

The implementation is intentionally pure-Python and dependency-free so the
test suite does not pull in scikit-learn / nltk just to gate searchability.
"""
from __future__ import annotations

import math
import re
import sys
from collections import Counter
from collections.abc import Iterable, Sequence
from typing import Any

from step_corpus import catalog

# Fields concatenated into the per-entry document, with weights applied via
# repetition. The title is the most diagnostic field (humans phrase reports
# similarly to titles) so we weight it heaviest. Sources / fixture_path are
# excluded: they're file paths and OCCT-API tokens, exactly the
# license-leaky vocabulary we *don't* want driving searchability.
FIELD_WEIGHTS: dict[str, int] = {
    "title": 4,
    "category": 2,
    "description": 2,
    "reproducer": 1,
    "expected_kernel_behavior": 1,
    "notes": 1,
}

# Tokens with no diagnostic value across CAD-defect documents. Hand-curated
# from a TF inspection of the catalog; expand if it improves the test
# results, never to mask a regression.
_STOPWORDS = frozenset(
    """
    a an and are as at be but by do does for from has have in into is it
    its of on or that the their these this to via with without when where
    if then than not no yes also too can may might should would will be
    been being one two three four five six seven eight nine ten step part
    file files entry entries entity entities catalog kernel reader writer
    occt see also note notes status pending merged
    """.split()
)

_TOKEN_RE = re.compile(r"[A-Za-z0-9_]+")


def _tokenize(text: str) -> list[str]:
    """Lowercase + alphanumeric tokenization with stopword removal.

    We keep digits: fixture names like ``ap242`` and ``r2025x`` carry real
    information. We split on every non-alphanumeric / non-underscore so
    ``ManifoldSolidBrep.outer`` tokenizes as ``manifoldsolidbrep`` +
    ``outer`` (good; that's how a bug reporter would search).
    """
    return [t for t in (m.group(0).lower() for m in _TOKEN_RE.finditer(text)) if t not in _STOPWORDS]


def _build_doc(entry: dict[str, Any]) -> list[str]:
    """Concatenate weighted fields into one bag-of-tokens document."""
    tokens: list[str] = []
    for field, weight in FIELD_WEIGHTS.items():
        value = entry.get(field) or ""
        if isinstance(value, list):
            value = " ".join(str(v) for v in value)
        for _ in range(weight):
            tokens.extend(_tokenize(str(value)))
    return tokens


class BugIndex:
    """Pure-Python BM25 index over the catalog.

    BM25 is the standard IR ranker for short structured documents; with
    k1=1.5 / b=0.75 (defaults below) it consistently outperforms TF-IDF on
    the bug-report queries we care about.
    """

    K1 = 1.5
    B = 0.75

    def __init__(self, entries: Sequence[dict[str, Any]]) -> None:
        self.entries: list[dict[str, Any]] = list(entries)
        self.docs: list[list[str]] = [_build_doc(e) for e in self.entries]
        self.doc_lens: list[int] = [len(d) for d in self.docs]
        self.avgdl: float = (sum(self.doc_lens) / len(self.doc_lens)) if self.doc_lens else 0.0
        self.tf: list[Counter[str]] = [Counter(d) for d in self.docs]
        df: Counter[str] = Counter()
        for tokens in self.docs:
            for term in set(tokens):
                df[term] += 1
        n = len(self.docs)
        self.idf: dict[str, float] = {
            term: math.log(1 + (n - freq + 0.5) / (freq + 0.5)) for term, freq in df.items()
        }

    @classmethod
    def load(cls, path: str | None = None) -> "BugIndex":
        return cls(catalog.load_catalog(path))

    def _score(self, query_tokens: Iterable[str], doc_idx: int) -> float:
        tf = self.tf[doc_idx]
        dl = self.doc_lens[doc_idx]
        if dl == 0:
            return 0.0
        norm = 1 - self.B + self.B * (dl / self.avgdl) if self.avgdl else 1.0
        score = 0.0
        for term in query_tokens:
            f = tf.get(term, 0)
            if not f:
                continue
            idf = self.idf.get(term, 0.0)
            score += idf * (f * (self.K1 + 1)) / (f + self.K1 * norm)
        return score

    def search(self, query: str, k: int = 10) -> list[tuple[float, dict[str, Any]]]:
        """Return the top-k entries scored against ``query``.

        Ties are broken by catalog order (stable). Entries with score 0 are
        omitted.
        """
        q = _tokenize(query)
        if not q:
            return []
        scored: list[tuple[float, int]] = []
        for i in range(len(self.docs)):
            s = self._score(q, i)
            if s > 0:
                scored.append((s, i))
        scored.sort(key=lambda t: (-t[0], t[1]))
        return [(s, self.entries[i]) for s, i in scored[:k]]

    def rank_of(self, query: str, entry_id: str, k: int = 50) -> int | None:
        """Return the 1-based rank of ``entry_id`` in results for ``query``.

        Returns ``None`` if the target is not in the top-k. Used by the
        regression test.
        """
        for rank, (_score, entry) in enumerate(self.search(query, k=k), start=1):
            if entry["id"] == entry_id:
                return rank
        return None


def _format_hit(rank: int, score: float, entry: dict[str, Any]) -> str:
    title = entry["title"]
    if len(title) > 90:
        title = title[:87] + "..."
    return f"{rank:>3}. [{score:6.2f}] {entry['id']:<8} {title}"


def main(argv: Sequence[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args or args[0] in {"-h", "--help"}:
        print(__doc__.split("\n\n")[0])
        print("\nUsage: python -m step_corpus._bug_search [-k N] <query...>")
        return 0
    k = 10
    if args[0] == "-k":
        if len(args) < 3:
            print("error: -k requires a value and a query", file=sys.stderr)
            return 2
        k = int(args[1])
        args = args[2:]
    query = " ".join(args)
    idx = BugIndex.load()
    hits = idx.search(query, k=k)
    if not hits:
        print(f"No matches for: {query!r}")
        return 1
    print(f"Top {len(hits)} of {k} for: {query!r}\n")
    for rank, (score, entry) in enumerate(hits, start=1):
        print(_format_hit(rank, score, entry))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
