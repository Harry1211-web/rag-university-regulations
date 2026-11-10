"""Chunk statistics and a golden-set coverage check.

The coverage check answers: "for every question in the golden set, can we name the chunk(s)
that contain the answer?" If not, Recall@k is undefined for that question - better to find
out now than after building the index.
"""
from __future__ import annotations

import re
import statistics as st
import unicodedata
from collections import Counter, defaultdict

from .chunk import Chunk


def chunk_stats(chunks: list[Chunk]) -> dict:
    w = sorted(c.n_words for c in chunks)
    q = lambda p: w[min(len(w) - 1, int(p * len(w)))]  # noqa: E731
    per_doc = Counter(c.doc_id for c in chunks)
    return {
        "n_chunks": len(chunks),
        "n_docs": len(per_doc),
        "words": {"min": w[0], "p10": q(0.1), "median": st.median(w), "p90": q(0.9), "max": w[-1],
                  "total": sum(w)},
        "with_table": sum(c.has_table for c in chunks),
        "split_sections": sum(1 for c in chunks if c.part[1] > 1),
        "per_doc": dict(per_doc.most_common()),
    }


def stats_markdown(s: dict, max_words: int, min_words: int) -> str:
    w = s["words"]
    lines = [
        "# Chunk statistics",
        "",
        f"Settings: max_words={max_words}, min_words={min_words} (words = whitespace tokens, i.e. Vietnamese syllables)",
        "",
        f"- Documents: {s['n_docs']}",
        f"- Chunks: {s['n_chunks']} ({s['with_table']} contain table rows; "
        f"{s['split_sections']} come from sections that had to be split)",
        f"- Words per chunk (body, without the context header): min {w['min']}, p10 {w['p10']}, "
        f"median {w['median']}, p90 {w['p90']}, max {w['max']}; total {w['total']}",
        "",
        "| Document | Chunks |",
        "|---|---:|",
        *[f"| {d} | {n} |" for d, n in s["per_doc"].items()],
    ]
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------- golden coverage
_ARTICLE = re.compile(r"Điều\s+(\d+)", re.I)
_KHOAN = re.compile(r"khoản\s+(\d+)", re.I)


def _nfc(s: str) -> str:
    return unicodedata.normalize("NFC", s or "").strip()


def _squash(s: str) -> str:
    return " ".join(_nfc(s).lower().split())


def doc_id_from(citation: dict, manifest: list[dict]) -> str | None:
    """Citations use either a manifest id ('doc_id') or the file name stem ('doc')."""
    if citation.get("doc_id"):
        return citation["doc_id"]
    stem = _nfc(citation.get("doc", "")).upper()
    for m in manifest:
        if _nfc(m["file"]).rsplit(".", 1)[0].upper() == stem:
            return m["id"]
    return None


def _line_starts(c: Chunk, label: str) -> bool:
    return re.search(rf"(^|\n)(\[[^\]]*\]\s*)?{re.escape(label)}[\s.:)]", c.text) is not None


def _path_has(c: Chunk, label: str) -> bool:
    return any(re.match(rf"{re.escape(label)}[\s.:)]", h, re.I) for h in c.path)


def resolve(citation: dict, chunks_by_doc: dict[str, list[Chunk]], manifest: list[dict]) -> list[str]:
    """Return the ids of the chunks a citation points to (empty if it cannot be resolved).

    Constraints are applied one by one and only kept when they leave at least one chunk:
    article -> khoản -> điểm for legal texts; phụ lục / section numbers / keywords otherwise."""
    doc = doc_id_from(citation, manifest)
    hits = list(chunks_by_doc.get(doc or "", []))
    if not hits:
        return []
    if citation.get("quote"):          # verbatim evidence: exact, and a typo is reported, not guessed
        q = _squash(citation["quote"])
        return [c.id for c in hits if q in _squash(c.text)]
    loc = _nfc(citation.get("loc") or "")

    def narrow(pred):
        nonlocal hits
        kept = [c for c in hits if pred(c)]
        if kept:
            hits = kept
        return bool(kept)

    art = int(m.group(1)) if (m := _ARTICLE.search(loc)) else None
    if art is not None:
        if not narrow(lambda c: c.article == int(art)):
            return []
        k = m.group(1) if (m := _KHOAN.search(loc)) else None
        if k is not None:
            k = re.match(r"\d+", str(k)).group(0)
            narrow(lambda c: k in c.khoan or c.part[1] == 1)
        if m := re.search(r"điểm\s+([a-zđ])\b", loc, re.I):
            narrow(lambda c: _line_starts(c, m.group(1)))
        return [c.id for c in hits]

    if re.search(r"tiêu đề|\d\s*[–-]\s*\d", loc, re.I):      # whole document / a range of items
        return [c.id for c in hits]
    if m := re.search(r"phụ lục\s*(\d+)", loc, re.I):
        if not narrow(lambda c: _path_has(c, f"PHỤ LỤC {m.group(1)}")):
            return []
    if m := re.search(r"\b([IVX]+)\.(\d+)\b", loc):          # "II.6" = section II, item 6
        narrow(lambda c: _path_has(c, f"{m.group(1)}."))
        narrow(lambda c: _path_has(c, f"{m.group(2)}.") or _line_starts(c, f"{m.group(2)}."))
    elif m := re.search(r"\b(\d+(?:\.\d+)+)\b", loc):        # "5.2"
        if not narrow(lambda c: _path_has(c, m.group(1)) or _line_starts(c, m.group(1))):
            return []
    elif m := re.search(r"mục\s+(\d+)\b", loc, re.I):          # "mục 8"
        narrow(lambda c: _path_has(c, f"{m.group(1)}."))
    if m := re.search(r"điểm\s+([a-zđ])\b", loc, re.I):
        narrow(lambda c: _line_starts(c, f"{m.group(1)})") or _line_starts(c, m.group(1)))
    if m := re.search(r"[–-]\s*([^\d].+)$", loc):               # "mục 2 – Tầm nhìn"
        narrow(lambda c: m.group(1).lower() in c.text.lower())
    return [c.id for c in hits]


def golden_coverage(rows: list[dict], chunks: list[Chunk], manifest: list[dict]) -> dict:
    by_doc: dict[str, list[Chunk]] = defaultdict(list)
    for c in chunks:
        by_doc[c.doc_id].append(c)
    resolved, unresolved, n_cit = [], [], 0
    for r in rows:
        groups = []
        for cit in r.get("citations") or []:
            n_cit += 1
            got = resolve(cit, by_doc, manifest)
            for alt in cit.get("alternatives") or []:      # other documents that state the same thing
                got = got + [i for i in resolve(alt, by_doc, manifest) if i not in got]
            if got:
                groups.append(got)
            else:
                unresolved.append({"id": r["id"], "citation": cit})
        if groups:
            # one group per citation: any chunk of a group covers that citation; a multi-document
            # question is fully retrieved only when every group is covered
            resolved.append({"id": r["id"], "gold_chunks": sorted({i for g in groups for i in g}), "groups": groups})
    with_cit = sum(1 for r in rows if r.get("citations"))
    return {"questions": len(rows), "with_citations": with_cit, "resolved": len(resolved),
            "citations": n_cit, "unresolved": unresolved, "mapping": resolved}
