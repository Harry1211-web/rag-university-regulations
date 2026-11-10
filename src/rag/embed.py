"""Embedding models and the vector cache.

The models run once, in `scripts/run_models.py`, on a machine that can download them from
Hugging Face. The vectors are cached in `data/index/<model>.npz`, so evaluation needs only numpy.
"""
from __future__ import annotations

import hashlib
import zlib
from pathlib import Path

import numpy as np

from .retrieve import tok_syllable

EMBEDDERS = {
    # key: (hugging face id, query prefix, passage prefix, max tokens). E5 was trained with these prefixes and loses
    # accuracy without them; BGE-M3 uses none. E5 cannot read past 512 tokens (position embeddings); the BGE-M3
    # family reads up to 8192, so 1024 covers every chunk (max 680 tokens measured).
    "e5-small": ("intfloat/multilingual-e5-small", "query: ", "passage: ", 512),      # small multilingual baseline
    "bge-m3": ("BAAI/bge-m3", "", "", 1024),                                         # strong multilingual
    "vn-embedding": ("AITeamVN/Vietnamese_Embedding", "", "", 1024),                 # BGE-M3 fine-tuned on Vietnamese
    "e5-base": ("intfloat/multilingual-e5-base", "query: ", "passage: ", 512),      # optional (not in the default run)
}
DEFAULT_EMBEDDERS = ["e5-small", "bge-m3", "vn-embedding"]
RERANKERS = {
    "bge-reranker-v2-m3": "BAAI/bge-reranker-v2-m3",
    "vn-reranker": "AITeamVN/Vietnamese_Reranker",
}


def texts_sha(texts: list[str]) -> str:
    """Fingerprint of the texts, so a stale cache (chunks rebuilt) is detected, not silently used."""
    return hashlib.sha1("\x00".join(texts).encode()).hexdigest()[:12]


def save_vectors(path: Path, **arrays) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(path, **arrays)


def load_vectors(path: Path) -> dict[str, np.ndarray]:
    with np.load(path, allow_pickle=False) as z:
        return {k: z[k] for k in z.files}


class SentenceTransformerEmbedder:
    def __init__(self, key: str, device: str | None = None):
        from sentence_transformers import SentenceTransformer

        self.key = key
        self.hf_id, self.q_prefix, self.p_prefix, self.max_len = EMBEDDERS[key]
        self.model = SentenceTransformer(self.hf_id, device=device)
        self.model.max_seq_length = self.max_len
        print(f"device: {self.model.device}, max tokens: {self.max_len}")
        self.tokenizer = self.model.tokenizer

    def encode(self, texts: list[str], kind: str, batch_size: int = 16) -> np.ndarray:
        prefix = self.q_prefix if kind == "query" else self.p_prefix
        v = self.model.encode([prefix + t for t in texts], batch_size=batch_size, normalize_embeddings=True,
                              show_progress_bar=True, convert_to_numpy=True)
        return v.astype(np.float32)

    def n_tokens(self, texts: list[str], kind: str = "passage") -> list[int]:
        prefix = self.q_prefix if kind == "query" else self.p_prefix
        return [len(self.tokenizer(prefix + t, verbose=False)["input_ids"]) for t in texts]


class HashEmbedder:
    """Stand-in for tests and CI: hashed bag of syllables and syllable bigrams. It has no idea of
    meaning (synonyms score 0), so it only checks the plumbing, never the quality."""

    key = "hash"

    def __init__(self, dim: int = 512):
        self.dim = dim

    def encode(self, texts: list[str], kind: str = "passage", batch_size: int = 0) -> np.ndarray:
        out = np.zeros((len(texts), self.dim), dtype=np.float32)
        for i, t in enumerate(texts):
            toks = tok_syllable(t)
            for g in toks + [f"{a} {b}" for a, b in zip(toks, toks[1:], strict=False)]:
                out[i, zlib.crc32(g.encode()) % self.dim] += 1.0
        n = np.linalg.norm(out, axis=1, keepdims=True)
        return out / np.maximum(n, 1e-9)

    def n_tokens(self, texts: list[str], kind: str = "passage") -> list[int]:
        return [len(tok_syllable(t)) for t in texts]
