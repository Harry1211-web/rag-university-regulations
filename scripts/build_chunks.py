"""Build the chunk file from the corpus and check it against the golden sets.

    python scripts/build_chunks.py                 # uses RAG_DATA_DIR or ../DA03_data/data/text
    python scripts/build_chunks.py --max-words 250

Outputs
    data/processed/chunks.jsonl    one chunk per line (git-ignored: it contains the documents)
    reports/chunk_stats.md         size statistics + golden-set coverage (committed)
    eval/gold_chunks.json          question id -> one list of chunk ids per citation (committed)
    (reads eval/golden.jsonl)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.rag import config  # noqa: E402
from src.rag.chunk import chunk_corpus  # noqa: E402
from src.rag.ingest import load_corpus, load_manifest  # noqa: E402
from src.rag.report import chunk_stats, golden_coverage, stats_markdown  # noqa: E402

GOLDEN = "golden.jsonl"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default=str(config.DATA_DIR))
    ap.add_argument("--max-words", type=int, default=config.MAX_WORDS)
    ap.add_argument("--min-words", type=int, default=config.MIN_WORDS)
    args = ap.parse_args()

    manifest = load_manifest(config.MANIFEST)
    docs = load_corpus(args.data_dir, config.MANIFEST)
    chunks = chunk_corpus(docs, manifest, max_words=args.max_words, min_words=args.min_words)

    config.PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    out = config.PROCESSED_DIR / "chunks.jsonl"
    with open(out, "w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(c.to_dict(), ensure_ascii=False) + "\n")

    md = stats_markdown(chunk_stats(chunks), args.max_words, args.min_words)
    md += "\n## Golden-set coverage\n\nEvery citation in `eval/golden.jsonl` is mapped to the chunk(s) that contain it.\n\n"
    md += "| Source | Split | Questions | Must answer | Resolved to chunks | Must refuse |\n|---|---|---:|---:|---:|---:|\n"
    rows = [json.loads(line) for line in open(config.EVAL_DIR / GOLDEN, encoding="utf-8")]
    cov = golden_coverage(rows, chunks, manifest)
    gold = {m["id"]: m["groups"] for m in cov["mapping"]}
    for src in sorted({r["source"] for r in rows}):
        for split in ("dev", "test"):
            sub = [r for r in rows if r["source"] == src and r["split"] == split]
            ans = [r for r in sub if r["expected_behavior"] == "answer"]
            md += (f"| {src} | {split} | {len(sub)} | {len(ans)} | {sum(r['id'] in gold for r in ans)} | "
                   f"{len(sub) - len(ans)} |\n")
    missing = [r["id"] for r in rows if r["expected_behavior"] == "answer" and r["id"] not in gold]
    md += f"\nAnswerable questions without a gold chunk: {missing or 'none'}\n"
    for u in cov["unresolved"]:
        md += f"\n- unresolved citation: `{u['id']}` {u['citation']}"
    md += "\n"
    config.REPORTS_DIR.mkdir(exist_ok=True)
    (config.REPORTS_DIR / "chunk_stats.md").write_text(md, encoding="utf-8")
    (config.EVAL_DIR / "gold_chunks.json").write_text(json.dumps(gold, ensure_ascii=False, indent=1), encoding="utf-8")
    print(md)
    print(f"wrote {out} ({len(chunks)} chunks)")


if __name__ == "__main__":
    main()
