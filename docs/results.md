# Results

All numbers on this page are from the **test split** (94 questions: 85 must be answered, 9 must be refused). The test
split was run **once**, after every setting had been frozen on dev. Per-question detail:
[`reports/generation_test.md`](../reports/generation_test.md) and [`reports/retrieval_test.md`](../reports/retrieval_test.md).

## 1. Closed book vs RAG

| Config | Overall | Multiple choice (14) | Free text (71, judge) | False refusal | Refusal recall (9) |
|---|---:|---:|---:|---:|---:|
| gpt-6-luna, closed book | 41% | 71% | 37% | 31% | 22% |
| **gpt-6-luna + RAG** | **93%** | 71% | **99%** | 5% | 78% |
| qwen3.5:4b (local), closed book | 20% | 50% | 17% | 1% | 0% |
| qwen3.5:4b (local) + RAG | 73% | 86% | 76% | 1% | 33% |

Metrics:
- **Overall**: answerable questions score correct = 1, partial = 0.5; must-refuse questions score 1 if refused.
- **Free text**: graded by gpt-6-luna as judge against the human reference answer.
- **Refusal recall**: must-refuse questions that the model declined.

Findings:
- **Retrieval more than doubles accuracy.** gpt-6-luna goes from 41% to 93% overall and from 37% to 99% on free-text
  questions. The small local model goes from 20% to 73% (×3.6).
- **Without the documents, the API model mostly refuses or guesses:**
  - it refuses 31% of the answerable questions;
  - it answers 7 of the 9 questions whose answer is not in the documents.
- **With RAG, the API model's answers are grounded and cited:**
  - the judge finds 99% of them supported by the excerpts;
  - 96% cite a gold chunk;
  - citation precision is 86%;
  - no answer cites an excerpt number that does not exist.
- **The local 4B model benefits from the documents but does not follow the rules well.** Only 52% of its answers are
  grounded, citation precision is 68%, and it answers 6 of the 9 must-refuse questions. For a deployment that must not
  invent rules, model size matters as much as retrieval.
- **Multiple choice is the one place RAG does not help gpt-6-luna (71% in both columns).** The options themselves give
  the closed-book model strong hints. The RAG prompt (v3, below) only picks an option whose key content is in the
  excerpts. On 4 questions the evidence was retrieved but only partly matched the option, and the model refused
  rather than guessed. This is the price of 100% refusal on dev.

### Manual check of the API model's 7 errors

| Question | Scored as | What happened |
|---|---|---|
| shcd13, shcd16, shcd19, shcd29 | over-refusal | Multiple choice. The evidence was in the context but did not state the option's key content verbatim, so the model refused (rule 7) |
| q122 *dormitory price* | hallucination | Gave the Khánh Hòa campus price, **labelled as such**, and said the main campus price is not in the documents. Arguably correct |
| q124 *conduct score for party admission* | hallucination | Said the score is a criterion but **the documents give no threshold**. Correct behaviour, but it did not use the exact refusal sentence |
| q069 | partial | The two judges disagree (API: partial, local: correct). The answer omits the list of other excluded courses |

The refusal metric is deliberately strict: only the fixed refusal sentence counts. Counting the two explicit "the
documents do not say" answers as refusals would give gpt-6-luna + RAG a refusal recall of 9/9.

## 2. Retrieval (test, 85 answerable questions)

| Method | R@1 | R@5 | MRR@10 |
|---|---:|---:|---:|
| BM25, syllables | 0.61 | 0.84 | 0.71 |
| Dense Vietnamese_Embedding | 0.79 | 0.95 | 0.86 |
| Hybrid BM25 + Vietnamese_Embedding | 0.75 | 0.93 | 0.82 |
| **Hybrid + bge-reranker-v2-m3 (frozen pipeline)** | **0.87** | **0.98** | **0.92** |
| Hybrid + Vietnamese_Reranker | 0.80 | 0.95 | 0.87 |
| *Fixed 300-word windows:* BM25 / dense / hybrid | 0.56 / 0.61 / 0.65 | 0.87 / 0.92 / 0.94 | 0.68 / 0.74 / 0.77 |

- **Dev results held on test.** The frozen pipeline scores MRR 0.92 on both (dev R@1 0.88, test 0.87).
- **The reranker is the largest single gain**, and bge-reranker-v2-m3 again beats the Vietnamese fine-tuned reranker.
- **One dev conclusion did not hold on test:** fusion with BM25 *hurt* the dense model (0.86 → 0.82 MRR), while on dev
  it helped (0.83 → 0.88). After reranking the difference disappears. It is still reported as a dev/test discrepancy.
- **Structure-aware chunks beat fixed windows for every method** (for example dense MRR 0.86 vs 0.74), confirming the
  dev result.

## 3. How the prompt and grading were tuned (dev only)

Three runs on dev (62 questions), each change made after reading the errors, then frozen:

| Run | Change | gpt-6-luna + RAG overall | Multiple choice | Refusal recall |
|---|---|---:|---:|---:|
| v1 | — | 76% | 60% | 100% |
| v2 | Judge rubric: grade what the *question* asks, not every detail of the reference. RAG prompt: complete answers (conditions, exceptions); multiple choice: pick the best-supported option | 91% | 89% | 50% |
| v3 | Multiple choice: pick an option only if its **key content** is in the excerpts; same topic is not enough | 92% | 67% | 100% |

- **v1 → v2** mixes two effects:
  - the new judge rubric. The closed-book answers did not change at all and still gained 3 points;
  - the new prompt.
- **v2 relaxed the multiple-choice rule too far.** Every question has *some* excerpt on the same topic, so the model
  stopped refusing.
- **v3 restores refusal.** The cost is multiple-choice recall, which is the trade-off seen on test.
- v1 and v2 were scored with an earlier refusal parser (see incident 8 below). Their reports are kept as
  `reports/generation_dev_v1.md` and `reports/generation_dev_v2.md`.

## 4. Judges

Free-text answers were graded by gpt-6-luna and, independently, by qwen3.5:4b.

| Answers graded | Same label | Cohen's κ |
|---|---:|---:|
| closed book, API model | 77% | 0.70 |
| closed book, local model | 75% | 0.53 |
| RAG, API model | 79% | −0.03 |
| RAG, local model | 59% | 0.17 |

The judges agree well where answers vary in quality (closed book). On the RAG answers of the API model almost every
label is "correct", so κ collapses even at 79% raw agreement (the kappa prevalence paradox). The disagreements there are
correct vs partial. The headline numbers use the API judge.

No human grading was done beyond the author's review of the reference answers. A human-graded sample is the next step
to validate the judge.

## 5. Cost and latency

Median seconds per answer (generation only; retrieval is cached):

| | closed book | RAG |
|---|---:|---:|
| gpt-6-luna (API) | 3.1 s | 1.9 s |
| qwen3.5:4b (GTX 1650, 4 GB) | 11 s | 31 s |

Adding ~2.5k tokens of excerpts did not slow the API model down (its RAG answers are longer, median 138 vs 79
characters, but returned sooner; the API's latency is not under our control). The local model is slow because 5 excerpts
and a long answer stretch a 4B model on 4 GB of VRAM.

## 6. Limitations

- **Small evaluation set:** 94 test questions, of which only 9 must be refused. One question is worth 1.1 points of
  "overall" and 11 points of "refusal recall".
- **The set is mostly synthetic:** 126 of the 156 questions were written for this project, by the same process that
  built the corpus. The 30 official orientation-quiz questions are the independent part.
- **One LLM judge, validated only against another LLM.**
- **Retrieval misses that need query rewriting are not fixed.** Example: a grade calculation question with no regulation
  keyword in it. Rewriting would require re-running the reranker on new queries.
- **No page-level citations:** the corpus was rebuilt from scans, so citations point to Điều / khoản / mục.
- **The corpus is a snapshot of the private student portal** (Nov 2026) and is not redistributed.

## 7. Incident log

| # | What went wrong | Effect | Fix |
|---|---|---|---|
| 1 | Assumed 300 syllables < 512 tokens; measured median 306, max 678 | 16 chunks truncated by 512-token models | Read 1024 tokens with the BGE-M3 family; E5 keeps its hard 512 limit, reported per model |
| 2 | Files copied from the build environment to the laptop were silently not updated | A run used an old embedder list | Verify an MD5 hash after every write |
| 3 | Vietnamese_Reranker has no `tokenizer.json` | Failed to load | Install `sentencepiece`; one failing model no longer stops the others |
| 4 | Reranker candidates were fused 20 deep, evaluation fuses 50 deep | ~1 of 20 candidates unscored per question (equal for both rerankers) | Fuse 50 deep in `run_models.py` |
| 5 | Gold set: q022 missed an alternative source; shcd06/17 were labelled answerable but have no answer in the corpus | Wrong scores | `alternatives` field; relabelled to refuse |
| 6 | v1 judge rubric penalised details the question did not ask for | RAG answers under-scored | Rubric v2, applied to every config |
| 7 | v2 multiple-choice rule ("best supported option") was too permissive | Refusal recall 100% → 50% | Rule v3: key content must be in the excerpts |
| 8 | Refusal parser required answers < 200 characters | Long refusals by the local model counted as hallucinations | An answer that opens with the refusal sentence is a refusal. Found on test, fixed in the scorer only, re-scored for every config |
| 9 | Local judge entered a repetition loop on one answer | 1 missing local grade (test q083) | None needed: the API grade is the headline |
