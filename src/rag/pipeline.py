"""Step 6: the frozen retrieval pipeline, prompt building and answer parsing.

Retrieval is the configuration chosen on dev (docs/retrieval.md):
    BM25 (syllables) + Vietnamese_Embedding -> RRF top 20 -> bge-reranker-v2-m3 -> top 5.
For the evaluation questions the dense vectors and reranker scores come from the cache written by
scripts/run_models.py, so generation needs no model runtime for retrieval.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass

from . import config
from .dataset import embed_text
from .embed import load_vectors
from .llm import REFUSAL
from .retrieve import BM25, dense_scores, rerank, rrf, tok_syllable, top

EMBEDDER = "vn-embedding"
RERANKER = "bge-reranker-v2-m3"
FUSE_DEPTH, RERANK_DEPTH, TOP_K = 50, 20, 5
INDEX_DIR = config.ROOT / "data" / "index"
PROMPTS = config.ROOT / "prompts"


class CachedRetriever:
    """Frozen pipeline over cached vectors / reranker scores (evaluation questions only)."""

    def __init__(self, chunks: list[dict], embedder: str = EMBEDDER, reranker: str | None = RERANKER):
        self.chunks = {c["id"]: c for c in chunks}
        self.ids = [c["id"] for c in chunks]
        self.bm25 = BM25([tok_syllable(embed_text(c)) for c in chunks])
        z = load_vectors(INDEX_DIR / f"{embedder}.npz")
        self.vecs = z["chunk_vecs"]
        self.qvec = dict(zip(z["q_ids"].tolist(), z["q_vecs"], strict=True)) if "q_ids" in z else {}
        path = INDEX_DIR / f"rerank_{reranker}.json"
        self.scores = json.loads(path.read_text(encoding="utf-8")) if reranker else None

    def retrieve(self, qid: str, question: str, k: int = TOP_K) -> list[dict]:
        lex = [c for c, _ in top(self.ids, self.bm25.scores(tok_syllable(question)), FUSE_DEPTH)]
        den = [c for c, _ in top(self.ids, dense_scores(self.vecs, self.qvec[qid]), FUSE_DEPTH)]
        fused = [c for c, _ in rrf([lex, den])]
        if self.scores is not None:
            fused = [c for c, _ in rerank(fused[:RERANK_DEPTH], self.scores.get(qid, {}))] + fused[RERANK_DEPTH:]
        return [self.chunks[c] for c in fused[:k]]


def _prompt(name: str) -> str:
    return (PROMPTS / f"{name}.txt").read_text(encoding="utf-8").strip()


def format_question(row: dict) -> str:
    q = f"Câu hỏi: {row['question']}"
    if row.get("options"):
        q += "\nCác lựa chọn:\n" + "\n".join(f"{k}. {v}" for k, v in row["options"].items())
    return q


def build_messages(row: dict, chunks: list[dict] | None) -> list[dict]:
    """chunks=None -> closed book (no retrieval)."""
    if chunks is None:
        return [{"role": "system", "content": _prompt("closed_system")},
                {"role": "user", "content": format_question(row)}]
    blocks = []
    for i, c in enumerate(chunks, 1):
        head = " | ".join(line.split(": ", 1)[-1] for line in c["context"].splitlines())
        blocks.append(f"[{i}] ({head})\n{c['text']}")
    user = "Các đoạn trích:\n\n" + "\n\n".join(blocks) + "\n\n" + format_question(row)
    return [{"role": "system", "content": _prompt("rag_system")}, {"role": "user", "content": user}]


@dataclass
class Parsed:
    refused: bool
    option: str | None          # chosen letter for multiple-choice questions
    cited: list[int]            # 1-based excerpt numbers that exist
    invalid_cites: list[int]    # numbers outside the excerpt list (a hallucinated source)


_REFUSALS = [REFUSAL.rstrip(".").lower(), "không tìm thấy trong các văn bản", "không có thông tin"]


def parse_answer(text: str, n_ctx: int = 0) -> Parsed:
    low = " ".join(text.lower().split())
    # a refusal: the answer opens with the refusal sentence (it may explain afterwards), or is a short answer
    # containing it. A long answer that only mentions a gap somewhere is a (partial) answer, not a refusal.
    refused = low.startswith(_REFUSALS[0]) or (any(r in low for r in _REFUSALS) and len(low) < 200)
    m = re.search(r"đáp án\s*[:：]?\s*\(?([a-e])\b", low)
    nums = [int(n) for n in re.findall(r"\[(\d+)\]", text)]
    nums += [int(n) for grp in re.findall(r"\[(\d+(?:\s*[,;]\s*\d+)+)\]", text) for n in re.split(r"[,;]", grp)]
    cited = sorted({n for n in nums if 1 <= n <= n_ctx})
    invalid = sorted({n for n in nums if not 1 <= n <= n_ctx})
    return Parsed(refused, m.group(1) if m else None, cited, invalid)


def judge_messages(row: dict, answer: str, chunks: list[dict] | None) -> list[dict]:
    parts = [f"Question:\n{row['question']}", f"Reference answer:\n{row['answer']}", f"Assistant's answer:\n{answer}"]
    if chunks:
        parts.append("Excerpts given to the assistant:\n" + "\n\n".join(
            f"[{i}] {c['text']}" for i, c in enumerate(chunks, 1)))
    else:
        parts.append("Excerpts given to the assistant: none (closed book)")
    return [{"role": "system", "content": _prompt("judge_system")}, {"role": "user", "content": "\n\n".join(parts)}]


def parse_judge(text: str) -> dict:
    m = re.search(r"\{.*\}", text, re.S)
    try:
        d = json.loads(m.group(0)) if m else {}
    except json.JSONDecodeError:
        d = {}
    c = str(d.get("correctness", "")).lower()
    g = str(d.get("grounded", "na")).lower()
    return {"correctness": c if c in {"correct", "partial", "incorrect", "refused"} else "invalid",
            "grounded": g if g in {"yes", "no", "na"} else "na", "reason": str(d.get("reason", ""))[:300]}


class LiveRetriever(CachedRetriever):
    """Same frozen pipeline for a NEW question: the query is embedded and the candidates reranked on the fly
    (needs torch + sentence-transformers and the models in the Hugging Face cache; chunk vectors come from the
    cache written by scripts/run_models.py)."""

    def __init__(self, chunks: list[dict], device: str | None = None):
        super().__init__(chunks, reranker=None)
        from sentence_transformers import CrossEncoder

        from .embed import RERANKERS, SentenceTransformerEmbedder

        self.embedder = SentenceTransformerEmbedder(EMBEDDER, device=device)
        self.cross = CrossEncoder(RERANKERS[RERANKER], max_length=1024, device=device)

    def retrieve(self, qid: str | None, question: str, k: int = TOP_K) -> list[dict]:
        qv = self.embedder.encode([question], "query")[0]
        lex = [c for c, _ in top(self.ids, self.bm25.scores(tok_syllable(question)), FUSE_DEPTH)]
        den = [c for c, _ in top(self.ids, dense_scores(self.vecs, qv), FUSE_DEPTH)]
        cands = [c for c, _ in rrf([lex, den])][:RERANK_DEPTH]
        scores = self.cross.predict([(question, embed_text(self.chunks[c])) for c in cands], show_progress_bar=False)
        ranked = [c for c, _ in sorted(zip(cands, scores, strict=True), key=lambda x: -x[1])]
        return [self.chunks[c] for c in ranked[:k]]


def ask(question: str, retriever, llm, options: dict | None = None) -> dict:
    """Answer one question with citations resolved to their source: {answer, refused, sources, chunks}."""
    row = {"question": question, "options": options}
    chunks = retriever.retrieve(None, question)
    answer = llm.chat(build_messages(row, chunks))
    p = parse_answer(answer, len(chunks))
    sources = {n: f"{chunks[n - 1]['doc_title']} · {chunks[n - 1]['loc']}" for n in p.cited}
    return {"answer": answer, "refused": p.refused, "sources": sources, "chunks": chunks}
