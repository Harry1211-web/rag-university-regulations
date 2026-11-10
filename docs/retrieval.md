# Retrieval design

Code:
- [`src/rag/retrieve.py`](../src/rag/retrieve.py): BM25, dense, fusion and reranking;
- [`src/rag/metrics.py`](../src/rag/metrics.py): the metrics;
- [`src/rag/baseline.py`](../src/rag/baseline.py): the control condition;
- [`scripts/run_models.py`](../scripts/run_models.py) and [`scripts/eval_retrieval.py`](../scripts/eval_retrieval.py).

Results: [`reports/retrieval_dev.md`](../reports/retrieval_dev.md).

## Methods compared

| Method | What it matches | Expected strength / weakness |
|---|---|---|
| BM25, syllables | Shared syllables, weighted by rarity | Exact codes and numbers (*điểm H*, *Điều 25*, *IELTS*); fails on paraphrase (*qua môn* vs *đạt*) |
| BM25, words (pyvi) | Shared segmented words (*học_bổng*) | More specific terms; segmentation errors can make a query and a chunk disagree |
| Dense: multilingual-e5-small, BGE-M3, Vietnamese_Embedding | Cosine similarity of embeddings | Paraphrase and synonyms; can confuse near-identical codes. BGE-M3 vs its Vietnamese fine-tune isolates the effect of language-specific training |
| Hybrid | Reciprocal rank fusion of BM25 (syllables) + one dense model | Ranks only, so no score calibration needed |
| Hybrid + reranker (bge-reranker-v2-m3, Vietnamese_Reranker) | A cross-encoder reads question and chunk together, on the hybrid top 20 | Most precise; too slow to run on all chunks |

All methods index `context header + body` (see [chunking.md](chunking.md)).
- **Control condition:** the same methods run on **fixed 300-word windows** with a 50-word overlap and no header, cut from the same rendered text. This isolates the effect of the chunking.

## Why the models run separately
Only `run_models.py` needs torch and Hugging Face. It caches:
- chunk, window and question vectors;
- token counts;
- cross-encoder scores for a superset of the candidates.

These go in `data/index/`, with a fingerprint of the texts so a stale cache is detected. Evaluation is then pure numpy and runs in CI.
`HashEmbedder` (hashed bag of syllables) stands in for a model in tests. It checks the plumbing only.

## Metrics
Gold chunks come from `eval/gold_chunks.json`: one list of chunk ids per citation; alternatives count as the same citation.

| Metric | Definition |
|---|---|
| R@k | At least one citation's evidence is in the top k |
| Full@5 | Every citation's evidence is in the top 5 (only differs for multi-document questions) |
| MRR@10 | Mean of 1/rank of the first hit (0 if not in the top 10) |
| refusal AUC | How well the top-1 retrieval score alone separates answerable from unanswerable questions |

The dev split has only 5 refusal questions, so the refusal AUC is indicative only.

## Protocol
- Every choice (tokenizer for the hybrid, top-k, the reranker depth) is made on **dev**.
  - Already decided: the hybrid uses syllable BM25, which beat word BM25 on dev (MRR 0.77 vs 0.68).
- `--split test --final` is run once at the end.

## Results on dev (57 answerable questions)

Full table: [`reports/retrieval_dev.md`](../reports/retrieval_dev.md). With 57 questions, one question is worth
0.018, so differences under ~0.04 are within noise.

| Method (structure-aware chunks) | R@1 | R@5 | MRR@10 |
|---|---:|---:|---:|
| BM25, syllables | 0.63 | 0.93 | 0.77 |
| Dense e5-small / bge-m3 / Vietnamese_Embedding | 0.65 / 0.70 / 0.72 | 0.93 / 0.95 / 0.98 | 0.76 / 0.79 / 0.83 |
| Hybrid BM25 + Vietnamese_Embedding | 0.79 | 0.96 | 0.88 |
| Hybrid + bge-reranker-v2-m3 (any embedder) | **0.88** | 0.96 | **0.92** |
| Hybrid + Vietnamese_Reranker (any embedder) | 0.77 | 0.96 | 0.86 |

Findings:
1. **Fusion beats either method alone.** Lexical and dense search miss different questions: codes and
   numbers on one side, paraphrase on the other.
2. **The reranker decides the final order.** Once reranked, the first-stage embedder no longer matters
   (identical rows for all four), so the cheapest one (e5-small) is enough in practice.
3. **The Vietnamese fine-tune helps the embedder** (+0.04 MRR over BGE-M3) **but not the reranker.**
   Vietnamese_Reranker is 0.06 MRR below bge-reranker-v2-m3 here, although its authors report the opposite on
   legal QA (Zalo 2021). Questions written by students about university rules are a different distribution.
4. **Chunking and model quality interact.** On fixed 300-word windows, Vietnamese_Embedding is the *worst*
   embedder (MRR 0.60 vs 0.83 on structure-aware chunks). Every method loses on fixed windows: syllable BM25
   0.77 → 0.68, best hybrid 0.88 → 0.77.
5. **Token lengths.** 300 syllables is not < 512 tokens: median 306, max 678, so 16 chunks were truncated at 512.
   Reading 1024 tokens (BGE-M3 family) changed bge-m3's MRR by < 0.01: the evidence sits early in those chunks.
   E5 cannot read past 512 tokens.
6. **The top-1 score is a weak refusal signal** (AUC 0.78 for the chosen pipeline, on only 5 unanswerable dev
   questions). Refusal has to be decided by the generator, from the content of the retrieved chunks.
7. **Remaining misses (2):**
   - `shcd11` is a calculation with no regulation keyword in it (only course names and numbers), so retrieval
     lands on scholarships;
   - `shcd28` hits the right section but the wrong half (contacts instead of the psychologist's role).

   Both are candidates for query rewriting in step 6.

**Test results** (run once, after freezing): the frozen pipeline scores R@1 0.87, R@5 0.98, MRR@10 0.92 on 85 test
questions, the same as on dev. See [results.md](results.md#2-retrieval-test-85-answerable-questions).

**Frozen for step 6 and the test run:** BM25 (syllables) + Vietnamese_Embedding → RRF top 20 →
bge-reranker-v2-m3 → top 5 to the generator.

Known caveat: the reranker cache was computed with fused lists 20 deep, while evaluation fuses lists 50 deep. That
left ~1 of the 20 candidates per question unscored, kept below the scored ones. This applies equally to both
rerankers. `run_models.py` now fuses 50 deep; it matters only if the caches are rebuilt.
