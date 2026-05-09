import logging

from config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, OPENROUTER_DEFAULT_MODEL, OPENROUTER_REASONING_MODEL

logger = logging.getLogger(__name__)

FREE_MODELS = {
    "nemotron-super": "nvidia/nemotron-3-super-120b-a12b:free",
    "gpt-oss": "openai/gpt-oss-120b:free",
    "laguna": "poolside/laguna-m.1:free",
    "owl-alpha": "openrouter/owl-alpha",
    "glm-air": "z-ai/glm-4.5-air:free",
    "minimax": "minimax/minimax-m2.5:free",
    "nemotron-reasoning": "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
    "gemma": "google/gemma-4-31b-it:free",
}

MODELS_BY_TASK = {
    "analysis": FREE_MODELS["nemotron-super"],
    "reasoning": FREE_MODELS["nemotron-reasoning"],
    "programming": FREE_MODELS["laguna"],
    "general": FREE_MODELS["gpt-oss"],
    "research": FREE_MODELS["owl-alpha"],
    "seo": FREE_MODELS["glm-air"],
}


def ask_openrouter(prompt: str, model: str | None = None, system: str = "") -> str:
    from openai import OpenAI

    if not OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY not set")

    model = model or OPENROUTER_DEFAULT_MODEL
    client = OpenAI(base_url=OPENROUTER_BASE_URL, api_key=OPENROUTER_API_KEY)
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    resp = client.chat.completions.create(model=model, messages=messages)
    return resp.choices[0].message.content.strip()


def ask_with_reasoning(prompt: str, system: str = "") -> str:
    return ask_openrouter(prompt, model=OPENROUTER_REASONING_MODEL, system=system)


def batch_describe_images(image_paths: list[str], prompt: str | None = None) -> list[str]:
    import ollama
    from config import OLLAMA_BASE_URL, VISION_MODEL

    client = ollama.Client(host=OLLAMA_BASE_URL)
    results = []

    for path in image_paths:
        try:
            resp = client.chat(
                model=VISION_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": prompt or "Describe this image in detail, focusing on any unusual phenomena.",
                        "images": [path],
                    }
                ],
            )
            results.append(resp["message"]["content"].strip())
        except Exception as e:
            logger.error(f"Vision error for {path}: {e}")
            results.append("")

    return results


def list_models() -> list[dict]:
    return [
        {"key": k, "model": v, "task": t}
        for t, v in MODELS_BY_TASK.items()
        for k, mv in FREE_MODELS.items()
        if mv == v
    ] or [{"key": k, "model": v, "task": ""} for k, v in FREE_MODELS.items()]
