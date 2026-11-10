"""Chat-model factory (LangChain) with the same provider rules as Milestone 1.

Selection: ``--provider`` / ``LLM_PROVIDER`` > first provider with a key set
(anthropic, openai, gemini, openrouter, ollama). ``LLM_PROVIDER=none`` (or no provider
configured) runs the agent in **offline mode**: every node still works, using the deterministic
parsers in ``matching_tools.py``; only the free-form prose and open questions lose the LLM.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse

try:  # .env support is optional
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # pragma: no cover
    pass


@dataclass(frozen=True)
class ProviderSpec:
    name: str
    kind: str                       # "anthropic" | "openai_compat"
    key_envs: tuple[str, ...]
    model_env: str
    default_model: str
    base_url_env: str | None = None
    default_base_url: str | None = None
    keyed_base_url: str | None = None
    key_required: bool = True
    placeholder_key: str = ""


PROVIDERS: dict[str, ProviderSpec] = {s.name: s for s in (
    ProviderSpec("anthropic", "anthropic", ("ANTHROPIC_API_KEY",), "ANTHROPIC_MODEL", "claude-sonnet-5-5"),
    ProviderSpec("openai", "openai_compat", ("OPENAI_API_KEY",), "OPENAI_MODEL", "gpt-4o-mini",
                 base_url_env="OPENAI_BASE_URL"),
    ProviderSpec("gemini", "openai_compat", ("GEMINI_API_KEY", "GOOGLE_API_KEY"), "GEMINI_MODEL", "gemini-3.8-flash",
                 base_url_env="GEMINI_BASE_URL",
                 default_base_url="https://generativelanguage.googleapis.com/v1beta/openai/"),
    ProviderSpec("openrouter", "openai_compat", ("OPENROUTER_API_KEY",), "OPENROUTER_MODEL", "openai/gpt-4o-mini",
                 base_url_env="OPENROUTER_BASE_URL", default_base_url="https://openrouter.ai/api/v1"),
    ProviderSpec("ollama", "openai_compat", ("OLLAMA_API_KEY",), "OLLAMA_MODEL", "llama3.1:8b",
                 base_url_env="OLLAMA_BASE_URL", default_base_url="http://localhost:11434/v1",
                 keyed_base_url="https://ollama.com/v1", key_required=False, placeholder_key="ollama"),
)}


def _env(*names: str) -> str | None:
    for n in names:
        v = (os.environ.get(n) or "").strip()
        if v:
            return v
    return None


def resolve_provider(explicit: str | None = None) -> str | None:
    """Provider name, or ``None`` for offline mode."""
    name = (explicit or os.environ.get("LLM_PROVIDER") or "").strip().lower()
    if name in ("none", "offline", "off"):
        return None
    if name:
        if name not in PROVIDERS:
            raise ValueError(f"Unknown provider '{name}'. Choose one of: {', '.join(PROVIDERS)}, none.")
        return name
    for n, spec in PROVIDERS.items():
        if _env(*spec.key_envs) or (not spec.key_required and spec.base_url_env and _env(spec.base_url_env)):
            return n
    return None


def create_chat_model(provider: str | None = None, model: str | None = None, temperature: float = 0.1) -> Any | None:
    """A LangChain chat model, or ``None`` when running offline."""
    name = resolve_provider(provider)
    if name is None:
        return None
    spec = PROVIDERS[name]
    key = _env(*spec.key_envs)
    if spec.key_required and not key:
        raise ValueError(f"{' or '.join(spec.key_envs)} is not set (needed for provider '{name}').")
    chosen = model or _env(spec.model_env) or spec.default_model
    if spec.kind == "anthropic":
        from langchain_anthropic import ChatAnthropic

        return ChatAnthropic(model=chosen, temperature=temperature, max_tokens=4096)
    if name == "ollama" and not key:
        # Local Ollama: use the native API so we can raise the context window (the OpenAI-compatible
        # endpoint is stuck at the model default, often 4k tokens - too small for tool results).
        try:
            from langchain_ollama import ChatOllama

            base = (_env(spec.base_url_env) or "http://localhost:11434").removesuffix("/v1").rstrip("/")
            return ChatOllama(model=chosen, base_url=base, temperature=temperature,
                              num_ctx=int(_env("OLLAMA_NUM_CTX") or 16384))
        except ImportError:
            pass
    from langchain_openai import ChatOpenAI

    url = (_env(spec.base_url_env) if spec.base_url_env else None) or (
        spec.keyed_base_url if (key and spec.keyed_base_url) else spec.default_base_url)
    if name == "ollama" and url and urlparse(url).path in ("", "/"):
        url = url.rstrip("/") + "/v1"
    return ChatOpenAI(model=chosen, api_key=key or spec.placeholder_key, base_url=url,
                      temperature=temperature, timeout=120, max_retries=1)


def describe(model: Any | None) -> str:
    if model is None:
        return "offline (deterministic reasoning, no LLM)"
    name = getattr(model, "model_name", None) or getattr(model, "model", None) or type(model).__name__
    return f"{type(model).__name__}:{name}"
