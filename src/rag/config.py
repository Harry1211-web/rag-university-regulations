"""Paths and chunking settings. Everything can be overridden with environment variables (.env)."""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _load_dotenv(path: Path = ROOT / ".env") -> None:
    """Tiny .env reader (KEY=VALUE lines) so we do not need python-dotenv for two variables."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8-sig").splitlines():   # -sig: Notepad may add a BOM
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"'))


_load_dotenv()

# The corpus is NOT in the repo (portal documents). Default: sibling folder of the repo.
DATA_DIR = Path(os.environ.get("RAG_DATA_DIR", ROOT.parent / "DA03_data" / "data" / "text"))
MANIFEST = ROOT / "sources.yaml"
PROCESSED_DIR = ROOT / "data" / "processed"
REPORTS_DIR = ROOT / "reports"
EVAL_DIR = ROOT / "eval"

# Chunk size is counted in whitespace tokens (= Vietnamese syllables). Measured: ~1.4 model tokens per
# syllable, so 300 syllables + header is a median 306 and a max 680 tokens; the BGE-M3 family reads 1024,
# E5 truncates 16 chunks at 512 (docs/retrieval.md).
MAX_WORDS = int(os.environ.get("RAG_MAX_WORDS", 300))
MIN_WORDS = int(os.environ.get("RAG_MIN_WORDS", 50))
