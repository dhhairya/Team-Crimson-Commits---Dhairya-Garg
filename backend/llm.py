"""Thin OpenRouter wrapper. One function used by both the vision and agent stages."""

import json
import os
import re
import time

import requests
from dotenv import load_dotenv

import net  # noqa: F401  - patches urllib3 to skip the blackholed IPv6 route

load_dotenv()

API_URL = "https://openrouter.ai/api/v1/chat/completions"
VISION_MODEL = os.getenv("VISION_MODEL", "google/gemini-3.5-flash")
AGENT_MODEL = os.getenv("AGENT_MODEL", "google/gemini-3.5-flash")


def chat(messages, model, tools=None, temperature=0.2, timeout=90):
    """Call OpenRouter and return the raw assistant message dict."""
    key = os.getenv("OPENROUTER_API_KEY")
    if not key:
        raise RuntimeError("OPENROUTER_API_KEY is not set (put it in backend/.env)")

    payload = {"model": model, "messages": messages, "temperature": temperature}
    if tools:
        payload["tools"] = tools

    started = time.time()
    print(f"  -> {model} ...", flush=True)
    resp = requests.post(
        API_URL,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json=payload,
        timeout=timeout,
    )
    if resp.status_code >= 400:
        raise RuntimeError(f"OpenRouter {resp.status_code}: {resp.text[:300]}")

    body = resp.json()
    if "choices" not in body:  # OpenRouter reports some errors with a 200
        raise RuntimeError(f"OpenRouter returned no choices: {str(body)[:300]}")

    print(f"  <- {model} replied in {time.time() - started:.1f}s", flush=True)
    return body["choices"][0]["message"]


def parse_json(text):
    """Pull a JSON object out of a model reply. Returns None if there isn't one."""
    if not text:
        return None
    text = re.sub(r"```(?:json)?|```", "", text).strip()
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None
