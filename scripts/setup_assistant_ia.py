#!/usr/bin/env python3
"""Assistant IA local setup helper.

Creates `secrets/assistant_ia.local.txt`, optionally tests the configured endpoint,
and can pull an Ollama model when explicitly requested.
"""

from __future__ import annotations

import argparse
import subprocess
import os
import time
from pathlib import Path

import requests


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "secrets" / "assistant_ia.local.txt"
OLLAMA_MODELS_DIR = ROOT / "models" / "llm" / "ollama"


DEFAULT_ENDPOINTS = {
    "Ollama": "http://localhost:11434/api/chat",
    "Ollama Cloud": "https://ollama.com/api/chat",
    "Jan.ai": "http://127.0.0.1:1337/v1/chat/completions",
    "LM Studio": "http://localhost:1234/v1/chat/completions",
    "Endpoint compatible": "https://proxy.example.com/v1/chat/completions",
}


def normalize_models_url(provider: str, base_url: str) -> str:
    clean = base_url.rstrip("/")
    if provider in {"Ollama", "Ollama Cloud"} and "/v1/" not in clean:
        for suffix in ["/api/chat", "/api/generate", "/api/tags"]:
            if clean.endswith(suffix):
                return clean[: -len(suffix)] + "/api/tags"
        if clean.endswith("/api"):
            return clean + "/tags"
        return clean + "/api/tags"
    if clean.endswith("/chat/completions"):
        return clean[: -len("/chat/completions")] + "/models"
    if clean.endswith("/v1"):
        return clean + "/models"
    return clean + "/v1/models"


def write_config(args: argparse.Namespace) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Configuration locale Assistant IA - ignorée par Git",
        "AI_PROVIDER=" + args.provider,
        "AI_BASE_URL=" + args.base_url,
        "AI_MODEL=" + args.model,
        "AI_API_KEY=" + (args.api_key or ""),
        "AI_TIMEOUT=" + str(args.timeout),
        "AI_TEMPERATURE=" + str(args.temperature),
        "AI_PASSWORD=" + (args.password or ""),
    ]
    CONFIG_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Configuration écrite: {CONFIG_PATH}")


def test_endpoint(args: argparse.Namespace) -> None:
    url = normalize_models_url(args.provider, args.base_url)
    headers = {}
    if args.api_key:
        headers["Authorization"] = f"Bearer {args.api_key}"
    response = requests.get(url, headers=headers, timeout=min(args.timeout, 15))
    response.raise_for_status()
    body = response.json()
    if args.provider == "Ollama" and "/api/" in url:
        models = [item.get("name") or item.get("model") for item in body.get("models", [])]
    else:
        models = [item.get("id") for item in body.get("data", [])]
    models = [m for m in models if m]
    print(f"Endpoint OK: {url}")
    print("Modèles détectés:", ", ".join(models[:20]) if models else "aucun modèle retourné")


def pull_ollama_model(model: str) -> None:
    OLLAMA_MODELS_DIR.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["OLLAMA_MODELS"] = str(OLLAMA_MODELS_DIR)
    subprocess.run(["ollama", "pull", model], check=True, env=env)


def start_ollama_server() -> None:
    OLLAMA_MODELS_DIR.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["OLLAMA_MODELS"] = str(OLLAMA_MODELS_DIR)
    subprocess.Popen(
        ["ollama", "serve"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL,
        start_new_session=True,
        env=env,
    )
    print(f"Ollama lancé avec OLLAMA_MODELS={OLLAMA_MODELS_DIR}")
    time.sleep(2)


def main() -> None:
    parser = argparse.ArgumentParser(description="Configure l'Assistant IA local du portfolio.")
    parser.add_argument("--provider", choices=list(DEFAULT_ENDPOINTS), default="Ollama")
    parser.add_argument("--base-url", default=None)
    parser.add_argument("--model", default="llama3.2")
    parser.add_argument("--api-key", default="")
    parser.add_argument("--password", default="")
    parser.add_argument("--timeout", type=int, default=40)
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--test", action="store_true", help="Teste la découverte des modèles après écriture.")
    parser.add_argument("--start", action="store_true", help="Démarre Ollama avec stockage des modèles dans le projet.")
    parser.add_argument("--pull-ollama", action="store_true", help="Lance `ollama pull MODEL` avant le test.")
    args = parser.parse_args()
    if not args.base_url:
        args.base_url = DEFAULT_ENDPOINTS[args.provider]
    if args.start:
        if args.provider != "Ollama":
            raise SystemExit("--start est réservé au provider Ollama local.")
        start_ollama_server()
    if args.pull_ollama:
        if args.provider != "Ollama":
            raise SystemExit("--pull-ollama est réservé au provider Ollama local.")
        pull_ollama_model(args.model)
    write_config(args)
    if args.test:
        test_endpoint(args)


if __name__ == "__main__":
    main()
