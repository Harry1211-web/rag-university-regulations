"""Score the saved answers (step 7): closed book vs RAG, API vs local model. Needs no model or network.

    python scripts/eval_generation.py                 # dev
    python scripts/eval_generation.py --split test
    python scripts/eval_generation.py --fake          # score data/runs_fake/ (plumbing check)

Exact checks: multiple-choice letter, refusal, citations. LLM-judge checks: free-text correctness and
groundedness, from two judges whose agreement is reported.
Writes reports/generation_<split>.md and .json.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.rag import config  # noqa: E402
from src.rag.dataset import load_chunks, load_gold_chunks, load_golden  # noqa: E402
from src.rag.pipeline import parse_answer  # noqa: E402

SCORE = {"correct": 1.0, "partial": 0.5}
CONFIG_ORDER = ["closed-api", "rag-api", "closed-local", "rag-local"]


def load_dir(d: Path) -> dict[str, dict]:
    return {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in sorted(d.glob("*.json"))} if d.exists() else {}


def kappa(a: list[str], b: list[str]) -> float | None:
    """Cohen's kappa: agreement corrected for chance (1 = perfect, 0 = chance level)."""
    if not a:
        return None
    po = sum(x == y for x, y in zip(a, b, strict=True)) / len(a)
    ca, cb = Counter(a), Counter(b)
    pe = sum(ca[k] * cb[k] for k in set(a) | set(b)) / len(a) ** 2
    return None if pe == 1 else (po - pe) / (1 - pe)


def pct(x):
    return "–" if x is None else f"{100 * x:.0f}%"


def mean(xs):
    xs = list(xs)
    return sum(xs) / len(xs) if xs else None


def score_config(name, rows, answers, judges, gold):
    """Per-question outcome + aggregate metrics for one configuration."""
    out, per_q = {}, []
    for r in rows:
        a = answers.get(r["id"])
        if a is None:
            continue
        n_ctx = len(a.get("retrieved") or [])
        p = parse_answer(a["answer"], n_ctx)
        q = {"id": r["id"], "expected": r["expected_behavior"], "type": r["type"], "refused": p.refused,
             "mcq": bool(r.get("options")), "answer": a["answer"]}
        if r["expected_behavior"] == "refuse":
            q["score"] = 1.0 if p.refused else 0.0
        elif q["mcq"]:
            q["score"] = 1.0 if (p.option == r["gold_option"] and not p.refused) else 0.0
        else:
            grades = {j: g[r["id"]]["correctness"] for j, g in judges.items() if r["id"] in g}
            q["grades"] = grades
            q["grounded"] = {j: g[r["id"]]["grounded"] for j, g in judges.items() if r["id"] in g}
            main = grades.get("api") or grades.get("local")
            q["score"] = 0.0 if p.refused else (SCORE.get(main, 0.0) if main else None)
        if n_ctx:
            ret = a["retrieved"]
            groups = gold.get(r["id"], [])
            g_all = {c for g in groups for c in g}
            q["gold_in_context"] = bool(g_all & set(ret)) if groups else None
            cited_ids = [ret[i - 1] for i in p.cited]
            q["cited"] = cited_ids
            q["cites_gold"] = bool(g_all & set(cited_ids)) if groups else None
            q["cite_precision"] = (sum(c in g_all for c in cited_ids) / len(cited_ids)) if (cited_ids and groups) else None
            q["invalid_cites"] = p.invalid_cites
        per_q.append(q)

    ans = [q for q in per_q if q["expected"] == "answer"]
    ref = [q for q in per_q if q["expected"] == "refuse"]
    scored = [q for q in per_q if q["score"] is not None]
    out["n"] = len(per_q)
    out["overall"] = mean(q["score"] for q in scored)
    out["mcq_acc"] = mean(q["score"] for q in ans if q["mcq"])
    out["free_acc"] = mean(q["score"] for q in ans if not q["mcq"] and q["score"] is not None)
    out["false_refusal"] = mean(q["refused"] for q in ans)
    out["refusal_recall"] = mean(q["refused"] for q in ref)
    answered = [q for q in ans if not q["refused"] and "cited" in q]
    if answered:
        out["cites_any"] = mean(bool(q["cited"]) for q in answered)
        out["cites_gold"] = mean(q["cites_gold"] for q in answered if q["cites_gold"] is not None)
        out["cite_precision"] = mean(q["cite_precision"] for q in answered if q["cite_precision"] is not None)
        out["invalid_cites"] = sum(bool(q["invalid_cites"]) for q in answered)
        g = [q["grounded"].get("api") for q in answered if q.get("grounded")]
        g = [x for x in g if x in ("yes", "no")]
        out["grounded"] = mean(x == "yes" for x in g)
        out["gold_in_context"] = mean(q["gold_in_context"] for q in ans if q.get("gold_in_context") is not None)
    return out, per_q


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="dev", choices=["dev", "test"])
    ap.add_argument("--fake", action="store_true")
    args = ap.parse_args()
    base = config.ROOT / "data" / ("runs_fake" if args.fake else "runs") / args.split
    rows = load_golden(args.split)
    gold = load_gold_chunks()
    loc = {c["id"]: f"{c['doc_id']} · {c['loc']}" for c in load_chunks()}
    configs = [c for c in CONFIG_ORDER if (base / c).exists()]
    if not configs:
        sys.exit(f"no answers in {base}: run scripts/run_generation.py first")

    results, per_qs, agree = {}, {}, {}
    for name in configs:
        answers = load_dir(base / name)
        judges = {j: load_dir(base / f"judge-{j}" / name) for j in ("api", "local")}
        judges = {j: g for j, g in judges.items() if g}
        results[name], per_qs[name] = score_config(name, rows, answers, judges, gold)
        if len(judges) == 2:
            both = sorted(set(judges["api"]) & set(judges["local"]))
            a = [judges["api"][q]["correctness"] for q in both]
            b = [judges["local"][q]["correctness"] for q in both]
            agree[name] = (len(both), mean(x == y for x, y in zip(a, b, strict=True)), kappa(a, b))

    n_ans = sum(r["expected_behavior"] == "answer" for r in rows)
    md = [f"# Generation — {args.split} split", "",
          f"{len(rows)} questions: {n_ans} must be answered, {len(rows) - n_ans} must be refused. "
          "Retrieval for RAG is frozen (docs/retrieval.md): top 5 chunks.", "",
          "| Config | Overall | Multiple choice | Free text (judge) | False refusal | Refusal recall |",
          "|---|---:|---:|---:|---:|---:|"]
    for name in configs:
        m = results[name]
        md.append(f"| {name} | {pct(m['overall'])} | {pct(m['mcq_acc'])} | {pct(m['free_acc'])} | "
                  f"{pct(m['false_refusal'])} | {pct(m['refusal_recall'])} |")
    md += ["", "- **Overall**: mean score over all questions (answerable: correct = 1, partial = 0.5; must-refuse: 1 if"
           " refused).", "- **Free text**: graded by the API judge (the local judge where the API one is missing).",
           "- **False refusal**: answerable questions the model declined. **Refusal recall**: must-refuse questions it"
           " declined.", ""]

    rag = [c for c in configs if c.startswith("rag")]
    if rag:
        md += ["## Citations and grounding (RAG)", "",
               "| Config | Evidence in context | Cites something | Cites gold chunk | Citation precision | Invalid cite"
               " numbers | Grounded (judge) |", "|---|---:|---:|---:|---:|---:|---:|"]
        for name in rag:
            m = results[name]
            md.append(f"| {name} | {pct(m.get('gold_in_context'))} | {pct(m.get('cites_any'))} | {pct(m.get('cites_gold'))}"
                      f" | {pct(m.get('cite_precision'))} | {m.get('invalid_cites', 0)} | {pct(m.get('grounded'))} |")
        md.append("")
    if agree:
        md += ["## Judge agreement (API judge vs local judge, same answers)", "",
               "| Config | n | Same label | Cohen's kappa |", "|---|---:|---:|---:|"]
        for name, (n, same, k) in agree.items():
            md.append(f"| {name} | {n} | {pct(same)} | {'–' if k is None else f'{k:.2f}'} |")
        md.append("")

    for name in rag:
        bad = [q for q in per_qs[name] if q["score"] is not None and q["score"] < 1]
        md += [f"## Errors of {name}: {len(bad)}", "",
               "Cause: **retrieval** = the evidence was not in the 5 chunks; **generation** = it was, but the answer is"
               " wrong; **over-refusal** / **hallucination** = refused an answerable question / answered a must-refuse"
               " one.", ""]
        cause = Counter()
        for q in bad:
            if q["expected"] == "refuse":
                c = "hallucination"
            elif q["refused"]:
                c = "over-refusal" + (" (evidence missing)" if q.get("gold_in_context") is False else "")
            elif q.get("gold_in_context") is False:
                c = "retrieval"
            else:
                c = "generation"
            cause[c] += 1
            row = next(r for r in rows if r["id"] == q["id"])
            grade = ", ".join(f"{j}: {g}" for j, g in (q.get("grades") or {}).items())
            expected = row["answer"] or f"(option {row.get('gold_option')})"
            md.append(f"- `{q['id']}` **{c}** {('(' + grade + ')') if grade else ''} — {row['question']}  \n"
                      f"  expected: {expected[:200]}  \n  got: {' '.join(q['answer'].split())[:250]}  \n"
                      f"  cited: {', '.join(loc.get(c, c) for c in q.get('cited', [])) or '—'}")
        md += ["", "Causes: " + ", ".join(f"{k} {v}" for k, v in cause.most_common()), ""]

    out = config.REPORTS_DIR / f"generation_{args.split}{'_fake' if args.fake else ''}"
    out.with_suffix(".md").write_text("\n".join(md) + "\n", encoding="utf-8")
    out.with_suffix(".json").write_text(json.dumps({"metrics": results, "judge_agreement": agree,
                                                    "per_question": per_qs}, ensure_ascii=False, indent=1),
                                        encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
