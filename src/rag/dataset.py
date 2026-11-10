"""Load the generated chunk file and the evaluation set."""
from __future__ import annotations

import json

from . import config


def _jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def load_chunks(path=None) -> list[dict]:
    path = path or config.PROCESSED_DIR / "chunks.jsonl"
    if not path.exists():
        raise FileNotFoundError(f"{path} not found: run `python scripts/build_chunks.py` first")
    return _jsonl(path)


def embed_text(c: dict) -> str:
    """What is indexed: context header + body (see docs/chunking.md)."""
    return f"{c['context']}\n\n{c['text']}" if c.get("context") else c["text"]


def load_golden(split: str | None = None) -> list[dict]:
    rows = _jsonl(config.EVAL_DIR / "golden.jsonl")
    return [r for r in rows if split in (None, "all") or r["split"] == split]


def load_gold_chunks() -> dict[str, list[list[str]]]:
    with open(config.EVAL_DIR / "gold_chunks.json", encoding="utf-8") as f:
        return json.load(f)
