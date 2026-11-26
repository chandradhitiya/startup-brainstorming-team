"""
OpenAI Chat Completions universal compatibility helpers.

This module provides an adaptive, resilient wrapper around any OpenAI-compatible provider:
- Adapts parameters for GPT-4, GPT-5, o1/o3, DeepSeek, Groq, NVIDIA NIM, Ollama, and local vLLM.
- Gracefully handles parameter rejections (temperature, max_completion_tokens, response_format, extra_body).
- Automatically manages transient rate limits (HTTP 429) and adaptive pacing.
"""

from __future__ import annotations

import logging
import os
import re
import time
from typing import Any, Dict, List, Optional

logger = logging.getLogger("mirofish.llm_compat")


def is_gpt5_family(model: Optional[str]) -> bool:
    """Return True when model belongs to GPT-5 family aliases/snapshots."""
    if not model:
        return False
    return model.strip().lower().startswith("gpt-5")


def is_reasoning_model(model: Optional[str]) -> bool:
    """Return True when model is known to reject temperature or require max_completion_tokens."""
    if not model:
        return False
    lower = model.strip().lower()
    return (
        is_gpt5_family(model)
        or lower.startswith("o1")
        or lower.startswith("o3")
        or "deepseek-reasoner" in lower
    )


def create_chat_completion(
    client: Any,
    *,
    model: str,
    messages: List[Dict[str, Any]],
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    response_format: Optional[Dict[str, Any]] = None,
) -> Any:
    """
    Create a chat completion with dynamic model-specific parameter adaptation and auto-retry.
    """
    # Ensure no message has empty or whitespace-only content, which causes HTTP 400 Bad Request on many providers
    cleaned_messages = []
    for msg in messages:
        c = msg.get("content")
        if c is None or (isinstance(c, str) and not c.strip()):
            cleaned_messages.append({**msg, "content": "..."})
        else:
            cleaned_messages.append(msg)

    kwargs: Dict[str, Any] = {
        "model": model,
        "messages": cleaned_messages,
    }

    if response_format is not None:
        kwargs["response_format"] = response_format

    reasoning_model = is_reasoning_model(model)
    base_url_str = str(getattr(client, "base_url", ""))
    is_groq = "groq.com" in base_url_str

    if is_groq:
        kwargs["extra_body"] = {"reasoning_format": "hidden"}

    if temperature is not None and not reasoning_model:
        kwargs["temperature"] = temperature

    # Token cap assignment:
    # reasoning_model and groq prefer max_completion_tokens; generic/local endpoints prefer max_tokens
    if max_tokens is not None:
        if reasoning_model or is_groq:
            kwargs["max_completion_tokens"] = max_tokens
        else:
            kwargs["max_tokens"] = max_tokens
    elif is_groq:
        kwargs["max_completion_tokens"] = 4096

    # Optional pacing delay to prevent rate limit spikes on low-tier providers
    pacing_delay = float(os.environ.get("LLM_REQUEST_DELAY_SEC", "0"))
    if pacing_delay > 0:
        time.sleep(pacing_delay)

    max_retries = int(os.environ.get("LLM_MAX_RETRIES", "5"))
    max_wait_allowed = float(os.environ.get("LLM_MAX_RETRY_WAIT_SEC", "120.0"))

    for attempt in range(max_retries):
        try:
            return client.chat.completions.create(**kwargs)
        except Exception as e:
            err_str = str(e).lower()

            # 1. Rate Limit (HTTP 429) adaptive backoff
            is_rate_limit = "429" in err_str or "rate_limit" in err_str or "rate limit" in err_str
            if is_rate_limit and attempt < max_retries - 1:
                match = re.search(r"try again in ([0-9.]+)s", str(e), re.IGNORECASE)
                wait_time = float(match.group(1)) + 1.5 if match else min(5.0 * (2 ** attempt), 45.0)
                if wait_time <= max_wait_allowed:
                    logger.warning(
                        f"LLM rate limit encountered (attempt {attempt + 1}/{max_retries}). "
                        f"Waiting {wait_time:.1f}s before retrying..."
                    )
                    time.sleep(wait_time)
                    continue

            # 2. Transient network / timeout connection errors
            is_transient_conn = any(
                term in err_str for term in ("connection error", "timeout", "timed out", "econnreset", "502", "503", "504")
            )
            if is_transient_conn and attempt < max_retries - 1:
                backoff = min(3.0 * (attempt + 1), 20.0)
                logger.warning(
                    f"Transient network/server error ({type(e).__name__}). "
                    f"Waiting {backoff:.1f}s before retry {attempt + 1}/{max_retries}..."
                )
                time.sleep(backoff)
                continue

            raise


def extract_chat_completion_text(response: Any) -> str:
    """Extract plain text from chat completion response across SDK content shapes."""
    choices = getattr(response, "choices", None) or []
    if not choices:
        return ""

    message = getattr(choices[0], "message", None)
    if message is None:
        return ""

    content = getattr(message, "content", "")

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        chunks: List[str] = []
        for item in content:
            if isinstance(item, dict):
                text_obj = item.get("text")
                if isinstance(text_obj, dict):
                    text_obj = text_obj.get("value")
                if isinstance(text_obj, str):
                    chunks.append(text_obj)
                elif isinstance(item.get("content"), str):
                    chunks.append(item["content"])
                continue

            text_obj = getattr(item, "text", None)
            if isinstance(text_obj, dict):
                text_obj = text_obj.get("value")
            if isinstance(text_obj, str):
                chunks.append(text_obj)
                continue

            content_obj = getattr(item, "content", None)
            if isinstance(content_obj, str):
                chunks.append(content_obj)

        return "".join(chunks).strip()

    return str(content or "")
