"""LLM clients (step 6): an OpenAI-compatible API, a local Ollama model, and a fake for tests.

Only the standard library is used (urllib), so nothing extra has to be installed.
Settings come from .env (never commit it):
    RAG_LLM_BASE_URL=https://api.openai.com/v1
    RAG_LLM_MODEL=gpt-6-luna
    RAG_LLM_API_KEY=sk-...
    RAG_OLLAMA_URL=http://localhost:11434        (optional)
    RAG_OLLAMA_MODEL=qwen3.5:4b                  (optional)
"""
from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Protocol

from . import config  # noqa: F401  (loads .env)

REFUSAL = "Không tìm thấy trong các văn bản hiện có."
_THINK = re.compile(r"<think>.*?</think>", re.S)


class LLM(Protocol):
    name: str

    def chat(self, messages: list[dict], json_mode: bool = False) -> str: ...


def _post(url: str, body: dict, headers: dict, timeout: int = 300, retries: int = 5) -> dict:
    data = json.dumps(body).encode()
    for attempt in range(retries):
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json", **headers})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            msg = e.read().decode(errors="replace")[:500]
            deterministic = "repeat limit" in msg      # Ollama stopped a repetition loop: same input, same loop
            if e.code in (429, 500, 502, 503, 504) and attempt < retries - 1 and not deterministic:
                time.sleep(min(60, 2 ** attempt * 3))          # rate limit / server hiccup: back off
                continue
            raise RuntimeError(f"HTTP {e.code} from {url}: {msg}") from None
        except (urllib.error.URLError, TimeoutError) as e:
            if attempt < retries - 1:
                time.sleep(min(60, 2 ** attempt * 3))
                continue
            raise RuntimeError(f"cannot reach {url}: {e}") from None
    raise RuntimeError("unreachable")


@dataclass
class OpenAICompatLLM:
    """Any /v1/chat/completions endpoint (OpenAI, Groq, vLLM, ...)."""

    model: str
    base_url: str
    api_key: str
    name: str = ""
    _no_temperature: bool = False         # some reasoning models reject temperature

    def __post_init__(self):
        self.name = self.name or self.model

    def chat(self, messages: list[dict], json_mode: bool = False) -> str:
        body: dict = {"model": self.model, "messages": messages}
        if not self._no_temperature:
            body["temperature"] = 0
        if json_mode:
            body["response_format"] = {"type": "json_object"}
        url = self.base_url.rstrip("/") + "/chat/completions"
        auth = {"Authorization": f"Bearer {self.api_key}"}
        try:
            r = _post(url, body, auth)
        except RuntimeError as e:
            if "temperature" in str(e) and not self._no_temperature:
                self._no_temperature = True
                return self.chat(messages, json_mode)
            raise
        return _THINK.sub("", r["choices"][0]["message"]["content"] or "").strip()


@dataclass
class OllamaLLM:
    """Local model through Ollama's native API (lets us turn thinking off and set the context size;
    the default 2-4k context would silently cut the retrieved chunks)."""

    model: str = "qwen3.5:4b"
    url: str = "http://localhost:11434"
    num_ctx: int = 8192
    name: str = ""

    def __post_init__(self):
        self.name = self.name or self.model

    num_predict: int = 1024               # cap on the answer length: a stuck model cannot run forever

    def chat(self, messages: list[dict], json_mode: bool = False) -> str:
        body = {"model": self.model, "messages": messages, "stream": False, "think": False,
                "options": {"temperature": 0, "num_ctx": self.num_ctx, "num_predict": self.num_predict}}
        if json_mode:
            body["format"] = "json"
        url = self.url.rstrip("/") + "/api/chat"
        try:
            r = _post(url, body, {}, timeout=600)
        except RuntimeError as e:
            # With temperature 0 (and JSON mode) a small model can loop on one token; Ollama aborts it with
            # "token repeat limit reached". Retrying the same request loops again, so retry ONCE with a
            # little randomness and a repetition penalty.
            if "repeat limit" not in str(e):
                raise
            body["options"].update(temperature=0.3, repeat_penalty=1.15)
            r = _post(url, body, {}, timeout=600)
        return _THINK.sub("", r["message"]["content"] or "").strip()


def from_env(kind: str) -> LLM:
    """kind = 'api' (RAG_LLM_*) or 'local' (RAG_OLLAMA_*)."""
    if kind == "api":
        missing = [k for k in ("RAG_LLM_BASE_URL", "RAG_LLM_MODEL", "RAG_LLM_API_KEY") if not os.environ.get(k)]
        if missing:
            raise SystemExit(f"set {', '.join(missing)} in .env")
        return OpenAICompatLLM(os.environ["RAG_LLM_MODEL"], os.environ["RAG_LLM_BASE_URL"], os.environ["RAG_LLM_API_KEY"])
    if kind == "local":
        return OllamaLLM(os.environ.get("RAG_OLLAMA_MODEL", "qwen3.5:4b"),
                         os.environ.get("RAG_OLLAMA_URL", "http://localhost:11434"))
    raise ValueError(kind)


@dataclass
class FakeLLM:
    """Answers from the context it is given: the first numbered block that shares a word with the
    question, cited, or the refusal sentence. Enough to test prompts, parsing and metrics for free."""

    name: str = "fake"
    calls: list[list[dict]] = field(default_factory=list)

    def chat(self, messages: list[dict], json_mode: bool = False) -> str:
        self.calls.append(messages)
        user = messages[-1]["content"]
        if json_mode:                                   # acting as a judge
            return json.dumps({"correctness": "correct", "grounded": "yes", "reason": "fake"})
        q = re.search(r"Câu hỏi:\s*(.+)", user)
        words = {w.lower() for w in re.findall(r"\w{3,}", q.group(1))} if q else set()
        context = user.split("Câu hỏi:")[0]
        for num, body in re.findall(r"\[(\d+)\]\s*(.+?)(?=\n\[\d+\]|\Z)", context, re.S):
            text = body.split("\n", 1)[-1] if body.startswith("(") else body   # skip the "(document | section)" header
            if words & {w.lower() for w in re.findall(r"\w{3,}", text)}:
                return f"{' '.join(text.split())[:200]} [{num}]"
        return REFUSAL
