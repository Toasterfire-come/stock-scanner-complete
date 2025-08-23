#!/usr/bin/env python3

import argparse
import json
import os
import re
import sys
from typing import Any, Dict, List, Optional


SYSTEM_PROMPT = (
    "You are a content generator. Produce exactly ten Quora-style question-and-answer pairs "
    "about a given topic. Return ONLY valid JSON without code fences or extra text. "
    "Use this exact structure: {\"results\": [ {\"question\": string, \"answer\": string} x10 ] }. "
    "Keep each answer helpful, specific, and 120-200 words. Avoid repetition."
)


def extract_json_object(text: str) -> Optional[Dict[str, Any]]:
    if not isinstance(text, str):
        return None
    # Try direct parse
    try:
        return json.loads(text)
    except Exception:
        pass
    # Strip fences if present
    fenced = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
    if fenced:
        inner = fenced.group(1)
        try:
            return json.loads(inner)
        except Exception:
            pass
    # Fallback: first JSON object in text
    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        candidate = match.group(0)
        try:
            return json.loads(candidate)
        except Exception:
            pass
    return None


def build_messages(topic: str) -> List[Dict[str, str]]:
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                "Generate 10 Quora-style Q&A pairs on the topic: "
                f"{topic}. Output only JSON with key \"results\" "
                "(array of 10 objects with \"question\" and \"answer\")."
            ),
        },
    ]


def call_chat_completions(
    *,
    api_base: str,
    model: str,
    messages: List[Dict[str, str]],
    temperature: float,
    max_tokens: int,
    api_key: Optional[str] = None,
    timeout_seconds: int = 120,
) -> str:
    # Import here so --help works without deps installed
    import requests  # type: ignore

    url = api_base.rstrip("/") + "/v1/chat/completions"
    headers: Dict[str, str] = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=timeout_seconds)
    try:
        resp.raise_for_status()
    except Exception as e:
        sys.stderr.write(f"Request failed: {e}\nBody: {resp.text[:2000]}\n")
        raise SystemExit(1)

    data = resp.json()
    try:
        return data["choices"][0]["message"]["content"]
    except Exception:
        sys.stderr.write("Unexpected response format.\n")
        sys.stderr.write(json.dumps(data, indent=2) + "\n")
        raise SystemExit(2)


def parse_results(content: str) -> List[Dict[str, str]]:
    obj = extract_json_object(content) or {}
    results = []
    if isinstance(obj, dict):
        if isinstance(obj.get("results"), list):
            results = obj.get("results", [])
        elif isinstance(obj.get("items"), list):
            results = obj.get("items", [])

    cleaned: List[Dict[str, str]] = []
    for idx, r in enumerate(results[:10], start=1):
        question = str((r or {}).get("question", "")).strip()
        answer = str((r or {}).get("answer", "")).strip()
        if question and answer:
            cleaned.append({"index": idx, "question": question, "answer": answer})
    return cleaned


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate 10 Quora-style Q&A via Ollama or any OpenAI-compatible API"
    )
    parser.add_argument(
        "topic",
        nargs="?",
        default=None,
        help="Topic/prompt to generate Q&A about (if omitted, read from --topic or STDIN)",
    )
    parser.add_argument(
        "--topic",
        dest="topic_opt",
        help="Topic to use (alternative to positional)",
    )
    parser.add_argument(
        "--api-base",
        default=os.getenv("LLM_API_BASE", "http://127.0.0.1:11434"),
        help="Base URL for OpenAI-compatible API (default: http://127.0.0.1:11434)",
    )
    parser.add_argument(
        "--api-key",
        default=os.getenv("OPENAI_API_KEY", None),
        help="API key for services that require it (Ollama usually doesn't)",
    )
    parser.add_argument(
        "--model",
        default=os.getenv("LLM_MODEL", "llama3.1:8b-instruct"),
        help="Model name (default: llama3.1:8b-instruct)",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.8,
        help="Sampling temperature (default: 0.8)",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=2048,
        help="Max tokens for the response (default: 2048)",
    )
    parser.add_argument(
        "--out",
        help="Path to write JSON output (default: print to stdout)",
    )

    args = parser.parse_args()

    topic = args.topic or args.topic_opt
    if not topic:
        if not sys.stdin.isatty():
            topic = sys.stdin.read().strip()
    if not topic:
        parser.error("No topic provided. Pass positional 'topic', --topic, or pipe via STDIN.")

    messages = build_messages(topic)
    content = call_chat_completions(
        api_base=args.api_base,
        model=args.model,
        messages=messages,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        api_key=args.api_key,
    )
    results = parse_results(content)

    if not results:
        sys.stderr.write("Model did not return parseable results.\n")
        # Show a short excerpt of the raw content to help debug
        sys.stderr.write((content or "")[0:1000] + "\n")
        raise SystemExit(3)

    output = json.dumps(results, ensure_ascii=False, indent=2)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Wrote {len(results)} items to {args.out}")
    else:
        print(output)


if __name__ == "__main__":
    main()