"""Control condition for the chunking choice: fixed-size windows.

The windows are cut from the SAME rendered text as the structure-aware chunks (same table
rendering, same cleaning), concatenated per document, with no context header. So the comparison
isolates exactly what docs/chunking.md claims to add: boundaries at Điều/khoản and the header.
"""
from __future__ import annotations

import unicodedata


def fixed_size_chunks(chunks: list[dict], size: int = 300, overlap: int = 50) -> list[dict]:
    by_doc: dict[str, list[dict]] = {}
    for c in chunks:                                   # chunks.jsonl is in document order
        by_doc.setdefault(c["doc_id"], []).append(c)
    out = []
    step = size - overlap
    for doc_id, cs in by_doc.items():
        words = "\n".join(c["text"] for c in cs).split()
        starts = range(0, max(1, len(words) - overlap), step)
        for i, s in enumerate(starts):
            out.append({"id": f"{doc_id}~{i + 1:03d}", "doc_id": doc_id, "text": " ".join(words[s:s + size])})
    return out


def _squash(s: str) -> str:
    return " ".join(unicodedata.normalize("NFC", s).lower().split())


def _trigrams(s: str) -> set[tuple[str, ...]]:
    w = _squash(s).split()
    return {tuple(w[i:i + 3]) for i in range(len(w) - 2)}


def map_gold(golden: list[dict], gold_groups: dict[str, list[list[str]]], chunks: list[dict],
             windows: list[dict], min_overlap: float = 0.5) -> dict[str, list[list[str]]]:
    """Translate gold chunk ids into window ids, citation by citation.

    - citation with a quote: the windows that contain the quote;
    - otherwise (or if the quote was cut in two by a window boundary): the windows whose word
      trigrams overlap a gold chunk by >= min_overlap of the smaller of the two.
    """
    text = {c["id"]: c["text"] for c in chunks}
    win_tri = [(w["id"], w["doc_id"], _trigrams(w["text"]), _squash(w["text"])) for w in windows]
    out: dict[str, list[list[str]]] = {}
    for r in golden:
        groups = gold_groups.get(r["id"])
        if not groups:
            continue
        mapped = []
        for cit, group in zip(r["citations"], groups, strict=False):   # unresolved citations have no group
            hits = []
            for c in [cit, *(cit.get("alternatives") or [])]:          # alternatives may sit in another document
                if c.get("quote"):
                    q = _squash(c["quote"])
                    hits += [wid for wid, d, _, s in win_tri if d == c["doc_id"] and q in s]
            if not hits:
                for cid in group:
                    g, doc = _trigrams(text[cid]), cid.split("#")[0]
                    for wid, d, t, _ in win_tri:
                        if d == doc and g and t and len(g & t) / min(len(g), len(t)) >= min_overlap:
                            hits.append(wid)
            mapped.append(sorted(set(hits)))
        out[r["id"]] = mapped
    return out
