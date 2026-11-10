"""Run the neural models once and cache their outputs (the only step that needs torch + Hugging Face).

    pip install -r requirements-models.txt
    python scripts/run_models.py                          # all embedders + reranker
    python scripts/run_models.py --models e5-small --no-rerank
    python scripts/run_models.py --only-rerank --rerankers vn-reranker

Writes, for each embedder, data/index/<key>.npz with:
    chunk vectors + token counts, fixed-size baseline vectors, question vectors
and data/index/rerank_<name>.json: cross-encoder scores for the candidate (question, chunk) pairs.
CPU is enough (337 chunks, 156 questions): about 1-5 min per embedder, 10-20 min per reranker.
Set HF_HOME to a drive with ~10 GB free: the models are cached there (default: C:\\Users\\<you>\\.cache).
"""
from __future__ import annotations

import argparse
import gc
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.rag import config  # noqa: E402
from src.rag.baseline import fixed_size_chunks  # noqa: E402
from src.rag.dataset import embed_text, load_chunks, load_golden  # noqa: E402
from src.rag.embed import (  # noqa: E402
    DEFAULT_EMBEDDERS,
    EMBEDDERS,
    RERANKERS,
    SentenceTransformerEmbedder,
    load_vectors,
    save_vectors,
    texts_sha,
)
from src.rag.retrieve import BM25, TOKENIZERS, dense_scores, rrf, top  # noqa: E402

INDEX_DIR = config.ROOT / "data" / "index"


def embed_all(keys, chunks, windows, golden, device, batch):
    texts = [embed_text(c) for c in chunks]
    base = [w["text"] for w in windows]
    qs = [r["question"] for r in golden]
    for key in keys:
        t0 = time.time()
        print(f"\n=== {key} ({EMBEDDERS[key][0]})")
        emb = SentenceTransformerEmbedder(key, device=device)
        ntok = emb.n_tokens(texts)
        save_vectors(
            INDEX_DIR / f"{key}.npz",
            chunk_ids=np.array([c["id"] for c in chunks]), chunk_vecs=emb.encode(texts, "passage", batch),
            chunk_sha=np.array(texts_sha(texts)), chunk_tokens=np.array(ntok), max_len=np.array(emb.max_len),
            base_ids=np.array([w["id"] for w in windows]), base_vecs=emb.encode(base, "passage", batch),
            base_sha=np.array(texts_sha(base)),
            q_ids=np.array([r["id"] for r in golden]), q_vecs=emb.encode(qs, "query", batch),
            q_sha=np.array(texts_sha(qs)),
        )
        over = sum(n > emb.max_len for n in ntok)
        print(f"tokens per chunk: median {int(np.median(ntok))}, max {max(ntok)}, truncated (> {emb.max_len}): {over}  "
              f"({time.time() - t0:.0f}s)")
        del emb
        gc.collect()


def candidates(chunks, golden, keys, depth):
    """Union of the top `depth` of every first-stage method, so any later fusion can be reranked."""
    ids = [c["id"] for c in chunks]
    texts = [embed_text(c) for c in chunks]
    bm25 = {name: (BM25([tok(t) for t in texts]), tok) for name, tok in TOKENIZERS.items()}
    dense = {k: load_vectors(INDEX_DIR / f"{k}.npz") for k in keys if (INDEX_DIR / f"{k}.npz").exists()}
    out = {}
    for i, r in enumerate(golden):
        # fuse lists as deep as eval_retrieval.py does (50), otherwise its hybrid top 20 has unscored chunks
        lexes = [[c for c, _ in top(ids, bm.scores(tok(r["question"])), 50)] for bm, tok in bm25.values()]
        lex = lexes[0]                                   # syllable BM25: the one the hybrid uses
        cand = {c for x in lexes for c in x[:depth]}
        for z in dense.values():
            d = [c for c, _ in top(ids, dense_scores(z["chunk_vecs"], z["q_vecs"][i]), 50)]
            cand |= set(d[:depth]) | {c for c, _ in rrf([lex, d])[:depth]}
        out[r["id"]] = sorted(cand)
    return out


def rerank_all(name, chunks, golden, cands, device, batch):
    from sentence_transformers import CrossEncoder

    t0 = time.time()
    text = {c["id"]: embed_text(c) for c in chunks}
    model = CrossEncoder(RERANKERS[name], max_length=1024, device=device)
    print(f"device: {model.model.device}")
    pairs = [(r["id"], cid) for r in golden for cid in cands[r["id"]]]
    pairs.sort(key=lambda p: len(text[p[1]]))       # similar lengths per batch -> far less padding
    q = {r["id"]: r["question"] for r in golden}
    print(f"\n=== reranker {name}: {len(pairs)} pairs")
    scores = model.predict([(q[a], text[b]) for a, b in pairs], batch_size=batch, show_progress_bar=True)
    out: dict[str, dict[str, float]] = {}
    for (qid, cid), s in zip(pairs, scores, strict=True):
        out.setdefault(qid, {})[cid] = float(s)
    (INDEX_DIR / f"rerank_{name}.json").write_text(json.dumps(out), encoding="utf-8")
    print(f"done ({time.time() - t0:.0f}s)")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="+", default=DEFAULT_EMBEDDERS, choices=list(EMBEDDERS))
    ap.add_argument("--rerankers", nargs="+", default=list(RERANKERS), choices=list(RERANKERS))
    ap.add_argument("--no-rerank", action="store_true")
    ap.add_argument("--only-rerank", action="store_true", help="reuse the cached vectors, run the rerankers only")
    ap.add_argument("--rerank-depth", type=int, default=20)
    ap.add_argument("--device", default=None, help="cpu / cuda (default: auto)")
    ap.add_argument("--batch", type=int, default=16)
    args = ap.parse_args()

    chunks = load_chunks()
    golden = load_golden()            # all splits: vectors are inputs, not results; test is only *scored* at the end
    windows = fixed_size_chunks(chunks)
    if not args.only_rerank:
        embed_all(args.models, chunks, windows, golden, args.device, args.batch)
    if not args.no_rerank:
        cands = candidates(chunks, golden, list(EMBEDDERS), args.rerank_depth)
        for name in args.rerankers:
            try:
                rerank_all(name, chunks, golden, cands, args.device, args.batch)
            except (ValueError, OSError, ImportError) as e:   # one broken model must not lose the others' results
                print(f"\n! reranker {name} failed: {e}")
                print("  (a 'processing class' error usually means: pip install sentencepiece protobuf)")
    print(f"\ncache written to {INDEX_DIR}. Next: python scripts/eval_retrieval.py")


if __name__ == "__main__":
    main()
