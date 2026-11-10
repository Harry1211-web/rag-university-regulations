"""Steps 6-7: answer the evaluation questions (closed book vs RAG, API model vs local model) and grade
the free-text answers with two LLM judges. Run it where the API and Ollama are reachable.

    python scripts/run_generation.py --limit 3          # smoke test: 3 questions, every config
    python scripts/run_generation.py                    # dev split, 4 configs, 2 judges
    python scripts/run_generation.py --split test --final
    python scripts/run_generation.py --fake             # no API calls (plumbing check)

Every answer and every grade is saved as one JSON file under data/runs/, so an interrupted run
resumes where it stopped and nothing is paid for twice. Scoring: scripts/eval_generation.py.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.rag import config  # noqa: E402
from src.rag.dataset import load_chunks, load_golden  # noqa: E402
from src.rag.llm import FakeLLM, from_env  # noqa: E402
from src.rag.pipeline import CachedRetriever, build_messages, judge_messages, parse_judge  # noqa: E402

RUNS = config.ROOT / "data" / "runs"
CONFIGS = {  # name -> (which LLM, retrieval?)
    "closed-api": ("api", False), "rag-api": ("api", True),
    "closed-local": ("local", False), "rag-local": ("local", True),
}


def ollama_up(llm) -> bool:
    try:
        urllib.request.urlopen(llm.url.rstrip("/") + "/api/tags", timeout=5)
        return True
    except OSError:
        return False


def sha(messages) -> str:
    return hashlib.sha1(json.dumps(messages, ensure_ascii=False).encode()).hexdigest()[:12]


def run_one(path: Path, fn, record: dict) -> dict | None:
    """Call fn() unless the result is cached FOR THE SAME PROMPT; save it. Returns the record or None on failure.
    A cached file made with another prompt (prompt_sha differs) is recomputed, so editing a prompt re-runs
    exactly the answers or grades it affects."""
    if path.exists():
        old = json.loads(path.read_text(encoding="utf-8"))
        if old.get("prompt_sha") == record["prompt_sha"]:
            return old
    t0 = time.time()
    try:
        out = fn()
    except RuntimeError as e:
        print(f"    ! {path.parent.name}/{path.stem}: {e}")
        return None
    record.update(out, seconds=round(time.time() - t0, 1))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, ensure_ascii=False, indent=1), encoding="utf-8")
    return record


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="dev", choices=["dev", "test"])
    ap.add_argument("--final", action="store_true", help="required for --split test")
    ap.add_argument("--configs", nargs="+", default=list(CONFIGS), choices=list(CONFIGS))
    ap.add_argument("--judges", nargs="*", default=["api", "local"], choices=["api", "local"])
    ap.add_argument("--limit", type=int, default=0, help="first N questions only (smoke test)")
    ap.add_argument("--fake", action="store_true", help="FakeLLM everywhere, writes to data/runs_fake/")
    args = ap.parse_args()
    if args.split == "test" and not args.final:
        sys.exit("The test split is run once, with every setting frozen. Add --final if that is now.")

    runs = RUNS.with_name("runs_fake") if args.fake else RUNS
    rows = load_golden(args.split)[: args.limit or None]
    chunks = load_chunks()
    retriever = CachedRetriever(chunks)

    llms = {}
    for kind in {CONFIGS[c][0] for c in args.configs} | set(args.judges):
        llms[kind] = FakeLLM(name=f"fake-{kind}") if args.fake else from_env(kind)
    if "local" in llms and not args.fake and not ollama_up(llms["local"]):
        print("! Ollama is not running: start the Ollama app (or `ollama serve`), then re-run. Skipping local model.")
        args.configs = [c for c in args.configs if CONFIGS[c][0] != "local"]
        args.judges = [j for j in args.judges if j != "local"]
        llms.pop("local")
    print(f"{len(rows)} questions ({args.split}), configs: {args.configs}, judges: {args.judges}")
    print("models:", {k: v.name for k, v in llms.items()})

    failures = 0
    for name in args.configs:
        kind, use_rag = CONFIGS[name]
        llm = llms[kind]
        print(f"\n=== {name} ({llm.name})")
        for i, r in enumerate(rows, 1):
            ctx = retriever.retrieve(r["id"], r["question"]) if use_rag else None
            msgs = build_messages(r, ctx)
            rec = run_one(runs / args.split / name / f"{r['id']}.json",
                          lambda llm=llm, msgs=msgs: {"answer": llm.chat(msgs)},
                          {"id": r["id"], "config": name, "model": llm.name, "prompt_sha": sha(msgs),
                           "retrieved": [c["id"] for c in ctx] if ctx else []})
            if rec is None:
                failures += 1
                if failures >= 5:
                    sys.exit("5 failures: stopping (check the key, the model name, or the network).")
                continue
            print(f"  [{i}/{len(rows)}] {r['id']}: {rec['answer'][:70]!r}".replace("\\n", " "))

            # grade free-text answers to answerable questions; multiple choice and refusals are scored exactly
            if r["expected_behavior"] != "answer" or r.get("options"):
                continue
            for j in args.judges:
                jm = judge_messages(r, rec["answer"], ctx)
                run_one(runs / args.split / f"judge-{j}" / name / f"{r['id']}.json",
                        lambda j=j, jm=jm: parse_judge(llms[j].chat(jm, json_mode=True)),
                        {"id": r["id"], "config": name, "judge": llms[j].name, "prompt_sha": sha(jm)})
    print(f"\ndone; results in {runs / args.split}. Next: python scripts/eval_generation.py --split {args.split}")


if __name__ == "__main__":
    main()
