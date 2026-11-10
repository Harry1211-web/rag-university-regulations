# rag-university-regulations

A retrieval-augmented assistant for students' questions about **Ton Duc Thang University (TDTU) academic
regulations**. It answers in Vietnamese with citations (`Điều 25 khoản 2`), and refuses when the documents do
not contain the answer.

It is a notebook and script pipeline with no UI. The point is to **measure** what each part contributes
against a closed-book baseline, with a dev/test protocol.

## Results (test split, run once after freezing every setting on dev)

| | Overall | Free-text answers | Refuses when the answer is not in the documents | Answers grounded in the excerpts |
|---|---:|---:|---:|---:|
| gpt-6-luna, closed book | 41% | 37% | 2 / 9 | – |
| **gpt-6-luna + RAG** | **93%** | **99%** | **7 / 9** (9 / 9 counting explicit "not stated" answers) | **99%** |
| qwen3.5:4b local, closed book | 20% | 17% | 0 / 9 | – |
| qwen3.5:4b local + RAG | 73% | 76% | 3 / 9 | 52% |

- **Retrieval puts the evidence in the top 5 for 98% of questions** (MRR@10 0.92, versus 0.71 for BM25 alone).
- **Retrieval more than doubles the accuracy of a strong API model**, and makes it cite the right chunk 96% of the time.
- **A local 4B model gains even more** (×3.6), but it follows the "only from the excerpts" rule much less reliably:
  52% of its answers are grounded.
- **Structure-aware chunking beats fixed 300-word windows for every retrieval method.** It matters most for the best
  embedder: MRR 0.86 vs 0.74.
- **A Vietnamese fine-tune helps the embedder but not the reranker.** On this data, bge-reranker-v2-m3 beats
  Vietnamese_Reranker on both dev and test, the opposite of the result its authors report on legal QA.

Full results, error analysis, dev tuning history and incident log: **[docs/results.md](docs/results.md)**.

## Pipeline

```
18 .docx regulations ─► ingest (paragraphs + tables, NFC) ─► structure-aware chunks (337)
                                                                  │
question ─► BM25 (syllables) ┐                                    │
         ─► Vietnamese_Embedding ┴► rank fusion, top 20 ─► bge-reranker-v2-m3 ─► top 5 excerpts
                                                                  │
                                       LLM: answer only from the excerpts, cite [n], or refuse
```

| Step | Design doc |
|---|---|
| Chunking at Điều / khoản level, tables as self-describing rows, context headers | [docs/chunking.md](docs/chunking.md) |
| Retrieval ablation: 2 lexical, 4 dense, fusion, 2 rerankers, fixed-window control | [docs/retrieval.md](docs/retrieval.md) |
| Generation: prompts with citation and refusal rules, closed-book baseline, two LLM judges | [docs/results.md](docs/results.md), [prompts/](prompts) |
| Evaluation set: 156 questions, dev/test split, gold chunks | [eval/README.md](eval/README.md) |

## Corpus and evaluation data

- **Corpus:** 18 Vietnamese documents (training regulation 1830/QĐ-TĐT, conduct, scholarships, exam rules, …), listed
  in [`sources.yaml`](sources.yaml).
  - Most come from the university's **private student portal**, so **the documents are not in this repository**.
  - Point `RAG_DATA_DIR` at your copy.
  - A few public facts were removed on purpose to create refusal tests.
- **Evaluation:** [`eval/golden.jsonl`](eval/golden.jsonl) has 156 questions. 141 must be answered and 15 must be
  refused (mostly near misses: the topic is in the corpus, the asked fact is not).
  - 30 questions come from the official orientation-week quiz.
  - 126 were written for the project and checked by the author against the documents.
  - Split: dev 62 for tuning, test 94 run once.

## Reproduce

```bash
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env                                   # RAG_DATA_DIR, LLM endpoint, Ollama model
python scripts/build_chunks.py                         # chunks + gold chunk mapping
pytest                                                 # no corpus or model needed (synthetic fixtures, FakeLLM)

pip install -r requirements-models.txt                 # torch + sentence-transformers (a 4 GB GPU or CPU is enough)
python scripts/run_models.py                           # embeddings and reranker scores, cached in data/index/
python scripts/eval_retrieval.py                       # retrieval ablation   -> reports/retrieval_dev.md

python scripts/run_generation.py                       # 4 configs x 2 judges, resumable -> data/runs/
python scripts/eval_generation.py                      # scores               -> reports/generation_dev.md
python scripts/run_generation.py --split test --final  # once, at the end
```

Notebooks:
- `01_ingest_and_chunk` shows the chunks.
- `02_index_and_retrieval` compares the search methods.
- `03_ask` answers a new question with citations.

Hardware used: Intel i5-12450H, GTX 1650 (4 GB), 16 GB RAM.

## Layout

```
sources.yaml     document manifest
src/rag/         ingest, chunk, retrieve, embed, baseline, pipeline (retrieval + prompts + parsing), llm, metrics, report
scripts/         build_chunks, run_models, eval_retrieval, run_generation, eval_generation
prompts/         rag_system, closed_system, judge_system
eval/            golden.jsonl (dev/test), gold_chunks.json
reports/         generated results (chunk stats, retrieval, generation per split, dev runs v1-v3)
notebooks/       01 ingest and chunk, 02 index and retrieval, 03 ask
tests/           pytest with synthetic .docx fixtures and a fake LLM
```

## Limitations

- Small test set (94 questions, only 9 that must be refused).
- Mostly synthetic questions.
- An LLM judge validated only against a second LLM judge.
- Retrieval misses that would need query rewriting are not fixed.
- Details: [docs/results.md § Limitations](docs/results.md#6-limitations).
