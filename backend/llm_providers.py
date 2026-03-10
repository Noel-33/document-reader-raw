from typing import List
import os
import requests
from openai import OpenAI

OPENAI_MODELS = ["gpt-4o-mini", "gpt-4.1-mini", "gpt-4o"]
OLLAMA_MODELS = ["llama3.1", "mistral", "qwen2.5"]

def safe_str(x) -> str:
    try:
        return str(x)
    except Exception:
        return repr(x)

def safe_err_msg(e: Exception) -> str:
    msg = safe_str(e)
    return msg.encode("utf-8", "replace").decode("utf-8")

def available_models() -> List[str]:
    models = []
    models += [f"ollama:{m}" for m in OLLAMA_MODELS]
    models += [f"openai:{m}" for m in OPENAI_MODELS]
    return models

def call_llm(model: str, system: str, user: str) -> str:
    provider, name = model.split(":", 1)

    if provider == "ollama":
        r = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": name, "prompt": f"{system}\n\n{user}", "stream": False},
            timeout=180,
        )
        r.raise_for_status()
        return r.json()["response"]

    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY not set. Choose an ollama:* model or set OPENAI_API_KEY.")
        client = OpenAI(api_key=api_key)
        resp = client.chat.completions.create(
            model=name,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            temperature=0.2,
        )
        return resp.choices[0].message.content

    raise ValueError(f"Unknown provider: {provider}")
