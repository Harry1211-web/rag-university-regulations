"""Retrieval ablation (step 5): which way of finding chunks puts the evidence in the top k?

    python scripts/eval_retrieval.py                  # dev split (default)
    python scripts/eval_retrieval.py --fake-dense     # also a hashed bag-of-words "dense" model (plumbing check)
    python scripts/eval_retrieval.py --split test --final   # once, at the very end

Needs only numpy (+ pyvi for word-level BM25). Dense and reranker methods appear when their cache
from scripts/run_models.py exists in data/index/.
Writes reports/retrieval_<split>.md and .json.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.rag import config  # noqa: E402
from src.rag.baseline import fixed_size_chunks, map_gold  # noqa: E402
from src.rag.dataset import embed_text, load_chunks, load_gold_chunks, load_golden  # noqa: E402
from src.rag.embed import EMBEDDERS, RERANKERS, HashEmbedder, load_vectors, texts_sha  # noqa: E402
from src.rag.metrics import evaluate, first_hit, refusal_auc  # noqa: E402
from src.rag.retrieve import BM25, TOKENIZERS, dense_scores, rerank, rrf, top  # noqa: E402

INDEX_DIR = config.ROOT / "data" / "index"
DEPTH = 50


class Run:
    """Ranked chunk ids (and the top-1 score) for every question, for one method."""

    def __init__(self, name, corpus, group):
        self.name, self.corpus, self.group = name, corpus, group
        self.ranked: dict[str, list[str]] = {}
        self.top1: dict[str, float] = {}

    def add(self, qid, scored):
        self.ranked[qid] = [c for c, _ in scored]
        self.top1[qid] = scored[0][1] if scored else 0.0


def lexical_runs(corpus, ids, texts, rows):
    runs = []
    for name, tok in TOKENIZERS.items():
        bm = BM25([tok(t) for t in texts])
        run = Run(f"BM25 ({name})", corpus, "lexical")
        for r in rows:
            run.add(r["id"], top(ids, bm.scores(tok(r["question"])), DEPTH))
        runs.append(run)
    return runs


def dense_runs(corpus, ids, vecs, qvec, key, rows, lex):
    d = Run(f"Dense {key}", corpus, "dense")
    h = Run(f"Hybrid BM25 + {key}", corpus, "hybrid")
    for r in rows:
        d.add(r["id"], top(ids, dense_scores(vecs, qvec[r["id"]]), DEPTH))
        h.add(r["id"], rrf([lex.ranked[r["id"]], d.ranked[r["id"]]])[:DEPTH])
    return [d, h]


def load_dense(key, chunks, windows, rows):
    path = INDEX_DIR / f"{key}.npz"
    if not path.exists():
        return None
    z = load_vectors(path)
    if str(z["chunk_sha"]) != texts_sha([embed_text(c) for c in chunks]):
        print(f"! {path.name} is stale (chunks changed since it was computed): re-run scripts/run_models.py")
        return None
    q = dict(zip(z["q_ids"].tolist(), z["q_vecs"], strict=True))
    missing = [r["id"] for r in rows if r["id"] not in q]
    if missing:
        print(f"! {path.name} lacks {len(missing)} questions: re-run scripts/run_models.py")
        return None
    base_ok = str(z["base_sha"]) == texts_sha([w["text"] for w in windows])
    return z, q, base_ok


def fmt(x):
    return "–" if x is None else f"{x:.2f}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="dev", choices=["dev", "test", "all"])
    ap.add_argument("--final", action="store_true", help="required for --split test")
    ap.add_argument("--fake-dense", action="store_true")
    args = ap.parse_args()
    if args.split == "test" and not args.final:
        sys.exit("The test split is scored once, with every setting frozen. Add --final if that is now.")

    chunks = load_chunks()
    rows = load_golden(args.split)
    gold = load_gold_chunks()
    windows = fixed_size_chunks(chunks)
    gold_win = map_gold(load_golden(), gold, chunks, windows)

    ids, texts = [c["id"] for c in chunks], [embed_text(c) for c in chunks]
    wids, wtexts = [w["id"] for w in windows], [w["text"] for w in windows]
    runs = lexical_runs("structure", ids, texts, rows)
    base_runs = lexical_runs("fixed-300", wids, wtexts, rows)
    # hybrid uses syllable BM25: it beat word-segmented BM25 on dev (MRR 0.77 vs 0.68), fixed from here on
    lex, base_lex = runs[0], base_runs[0]

    dense_keys = []
    if args.fake_dense:
        h = HashEmbedder()
        qv = dict(zip([r["id"] for r in rows], h.encode([r["question"] for r in rows]), strict=True))
        runs += dense_runs("structure", ids, h.encode(texts), qv, "hash (fake)", rows, lex)
    for key in EMBEDDERS:
        got = load_dense(key, chunks, windows, rows)
        if not got:
            continue
        z, qv, base_ok = got
        dense_keys.append(key)
        runs += dense_runs("structure", ids, z["chunk_vecs"], qv, key, rows, lex)
        if base_ok:
            base_runs += dense_runs("fixed-300", wids, z["base_vecs"], qv, key, rows, base_lex)
    for name in RERANKERS:
        path = INDEX_DIR / f"rerank_{name}.json"
        if not path.exists():
            continue
        scores = json.loads(path.read_text(encoding="utf-8"))
        for hyb in [r for r in runs if r.group == "hybrid" and "fake" not in r.name]:
            rr = Run(f"{hyb.name} + {name}", "structure", "rerank")
            for r in rows:
                head = rerank(hyb.ranked[r["id"]][:20], scores.get(r["id"], {}))
                rr.add(r["id"], head + [(c, 0.0) for c in hyb.ranked[r["id"]][20:]])
            runs.append(rr)

    answerable = {r["id"]: r["expected_behavior"] == "answer" for r in rows}
    res = []
    for run in runs + base_runs:
        g = gold if run.corpus == "structure" else gold_win
        m = evaluate({q: v for q, v in run.ranked.items() if answerable[q]}, g)
        m["refusal_AUC"] = refusal_auc(run.top1, answerable)
        res.append((run, m))

    n_ans = sum(answerable.values())
    md = [f"# Retrieval — {args.split} split", "",
          f"{n_ans} answerable questions (with gold chunks), {len(rows) - n_ans} that must be refused.",
          "",
          "- **R@k**: the evidence for at least one citation is in the top k.",
          "- **Full@5**: the evidence for every citation is in the top 5 (only differs for multi-document questions).",
          "- **MRR@10**: mean of 1/rank of the first hit.",
          "- **refusal AUC**: how well the top-1 score alone separates answerable from unanswerable questions"
          " (0.5 = no signal).",
          "", "| Chunks | Method | R@1 | R@3 | R@5 | R@10 | Full@5 | MRR@10 | refusal AUC |",
          "|---|---|---:|---:|---:|---:|---:|---:|---:|"]
    for run, m in res:
        md.append(f"| {run.corpus} | {run.name} | {fmt(m.get('R@1'))} | {fmt(m.get('R@3'))} | {fmt(m.get('R@5'))} | "
                  f"{fmt(m.get('R@10'))} | {fmt(m.get('Full@5'))} | {fmt(m.get('MRR@10'))} | {fmt(m['refusal_AUC'])} |")

    best_run, _ = max(((r, m) for r, m in res if r.corpus == "structure"), key=lambda x: x[1].get("MRR@10", 0))
    md += ["", f"## Breakdown for the best method: {best_run.name}", "",
           "| Group | n | R@1 | R@5 | MRR@10 |", "|---|---:|---:|---:|---:|"]
    for field in ("type", "source", "multi_doc"):
        groups = defaultdict(list)
        for r in rows:
            if answerable[r["id"]]:
                groups[f"{field}={r[field]}"].append(r["id"])
        for gname, qids in sorted(groups.items()):
            m = evaluate({q: best_run.ranked[q] for q in qids}, gold)
            md.append(f"| {gname} | {m['n']} | {fmt(m.get('R@1'))} | {fmt(m.get('R@5'))} | {fmt(m.get('MRR@10'))} |")

    loc = {c["id"]: f"{c['doc_id']} · {c['loc']}" for c in chunks}
    misses = [r for r in rows if answerable[r["id"]] and (first_hit(best_run.ranked[r["id"]], gold[r["id"]]) or 99) > 5]
    md += ["", f"## Misses of the best method (evidence not in top 5): {len(misses)}", ""]
    for r in misses:
        want = "; ".join(loc[g[0]] for g in gold[r["id"]])
        got = ", ".join(loc[c] for c in best_run.ranked[r["id"]][:3])
        md.append(f"- `{r['id']}` {r['question']}  \n  gold: {want}  \n  top 3: {got}")

    if dense_keys:
        md += ["", "## Chunk length in model tokens", "",
               "| Model | max tokens read | median | max | truncated chunks |", "|---|---:|---:|---:|---:|"]
        for key in dense_keys:
            z = load_vectors(INDEX_DIR / f"{key}.npz")
            t, lim = z["chunk_tokens"], int(z["max_len"]) if "max_len" in z else 512
            md.append(f"| {key} | {lim} | {int(np.median(t))} | {int(t.max())} | {int((t > lim).sum())} |")

    config.REPORTS_DIR.mkdir(exist_ok=True)
    (config.REPORTS_DIR / f"retrieval_{args.split}.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    (config.REPORTS_DIR / f"retrieval_{args.split}.json").write_text(
        json.dumps([{"corpus": r.corpus, "method": r.name, **m} for r, m in res], indent=1), encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
