"""Step 4-5: lexical (BM25) and dense retrieval over the chunks, rank fusion and reranking.

Everything here is pure numpy: the dense vectors and reranker scores are computed once by
`scripts/run_models.py` (which needs the models) and cached, so retrieval can be evaluated anywhere.
"""
from __future__ import annotations

import math
import re
import unicodedata
from collections import Counter
from functools import lru_cache

import numpy as np

_TOKEN = re.compile(r"\w+")


def tok_syllable(text: str) -> list[str]:
    """Whitespace/punctuation split = Vietnamese syllables ('học', 'bổng')."""
    return _TOKEN.findall(unicodedata.normalize("NFC", text).lower())


@lru_cache(maxsize=50_000)
def _segment(text: str) -> str:
    from pyvi import ViTokenizer  # optional dependency, only for word-level BM25

    return ViTokenizer.tokenize(text)


def tok_word(text: str) -> list[str]:
    """Word segmentation with pyvi: 'học bổng' -> 'học_bổng' (\\w keeps the underscore)."""
    text = unicodedata.normalize("NFC", text)
    return [t for line in text.split("\n") for t in _TOKEN.findall(_segment(line).lower())]


TOKENIZERS = {"syllable": tok_syllable, "word": tok_word}


class BM25:
    """Okapi BM25 (k1=1.5, b=0.75). Small corpus -> a dense doc-term matrix is fine."""

    def __init__(self, docs: list[list[str]], k1: float = 1.5, b: float = 0.75):
        self.k1, self.b = k1, b
        self.vocab = {t: i for i, t in enumerate(sorted({t for d in docs for t in d}))}
        tf = np.zeros((len(docs), len(self.vocab)), dtype=np.float32)
        for i, d in enumerate(docs):
            for t, n in Counter(d).items():
                tf[i, self.vocab[t]] = n
        dl = tf.sum(1, keepdims=True)
        df = (tf > 0).sum(0)
        self.idf = np.log(1 + (len(docs) - df + 0.5) / (df + 0.5)).astype(np.float32)
        self.w = tf * (k1 + 1) / (tf + k1 * (1 - b + b * dl / dl.mean()))   # saturated tf, length-normalised

    def scores(self, query: list[str]) -> np.ndarray:
        cols = [self.vocab[t] for t in set(query) if t in self.vocab]
        if not cols:
            return np.zeros(self.w.shape[0], dtype=np.float32)
        return self.w[:, cols] @ self.idf[cols]


def top(ids: list[str], scores: np.ndarray, k: int = 50) -> list[tuple[str, float]]:
    order = np.argsort(-scores, kind="stable")[:k]
    return [(ids[i], float(scores[i])) for i in order]


def dense_scores(chunk_vecs: np.ndarray, query_vec: np.ndarray) -> np.ndarray:
    """Cosine similarity; vectors are stored L2-normalised."""
    return chunk_vecs @ query_vec


def rrf(rankings: list[list[str]], k: int = 60, depth: int = 50) -> list[tuple[str, float]]:
    """Reciprocal rank fusion: score = sum 1/(k + rank). Uses ranks only, so BM25 scores and
    cosine similarities need no calibration against each other."""
    score: dict[str, float] = {}
    for r in rankings:
        for rank, cid in enumerate(r[:depth], 1):
            score[cid] = score.get(cid, 0.0) + 1.0 / (k + rank)
    return sorted(score.items(), key=lambda x: -x[1])


def rerank(candidates: list[str], pair_scores: dict[str, float]) -> list[tuple[str, float]]:
    """Order candidates by cross-encoder score. A candidate without a cached score keeps its place
    after the scored ones (it should not happen: run_models.py scores a superset)."""
    scored = [(c, pair_scores[c]) for c in candidates if c in pair_scores]
    rest = [(c, -math.inf) for c in candidates if c not in pair_scores]
    return sorted(scored, key=lambda x: -x[1]) + rest
