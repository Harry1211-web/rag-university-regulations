"""Retrieval metrics against eval/gold_chunks.json (one list of chunk ids per citation)."""
from __future__ import annotations

import numpy as np


def first_hit(ranked: list[str], groups: list[list[str]]) -> int | None:
    """1-based rank of the first retrieved chunk that covers ANY citation."""
    gold = {c for g in groups for c in g}
    return next((i for i, c in enumerate(ranked, 1) if c in gold), None)


def covers_all(ranked: list[str], groups: list[list[str]], k: int) -> bool:
    """Every citation has at least one of its chunks in the top k (matters for multi-document questions)."""
    top = set(ranked[:k])
    return all(top & set(g) for g in groups)


def evaluate(rankings: dict[str, list[str]], gold: dict[str, list[list[str]]], ks=(1, 3, 5, 10)) -> dict:
    """Recall@k (any citation covered), Full@k (all citations covered), MRR@10.

    Only questions that have gold chunks count; questions that must be refused have none and are
    evaluated separately (see refusal_auc)."""
    qids = [q for q in rankings if gold.get(q)]
    if not qids:
        return {"n": 0}
    ranks = [first_hit(rankings[q], gold[q]) for q in qids]
    res = {"n": len(qids)}
    for k in ks:
        res[f"R@{k}"] = float(np.mean([r is not None and r <= k for r in ranks]))
    res["Full@5"] = float(np.mean([covers_all(rankings[q], gold[q], 5) for q in qids]))
    res["MRR@10"] = float(np.mean([1 / r if r and r <= 10 else 0.0 for r in ranks]))
    return res


def refusal_auc(top_score: dict[str, float], answerable: dict[str, bool]) -> float | None:
    """How well the best retrieval score alone separates answerable from unanswerable questions
    (AUC: 1.0 = a threshold separates them perfectly, 0.5 = no signal)."""
    pos = [s for q, s in top_score.items() if answerable.get(q)]
    neg = [s for q, s in top_score.items() if answerable.get(q) is False]
    if not pos or not neg:
        return None
    wins = sum((p > n) + 0.5 * (p == n) for p in pos for n in neg)
    return wins / (len(pos) * len(neg))
