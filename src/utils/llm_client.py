"""LLM client: Local Ollama with Groq fallback."""

import os
from langchain_core.messages import HumanMessage, SystemMessage

OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "qwen2.5-coder:3b-instruct-q4_K_M"


def get_llm():
    try:
        from langchain_ollama import OllamaLLM
        return OllamaLLM(base_url=OLLAMA_BASE_URL, model=OLLAMA_MODEL)
    except Exception:
        pass

    api_key = os.environ.get("GROQ_API_KEY", "")
    if api_key:
        from langchain_groq import ChatGroq
        return ChatGroq(
            groq_api_key=api_key,
            model_name="openai/gpt-oss-20b",
            temperature=0.3,
            max_tokens=2048,
        )

    raise RuntimeError(
        "No LLM available. Start Ollama or set GROQ_API_KEY."
    )


def invoke_llm(system_prompt: str, user_prompt: str) -> str:
    llm = get_llm()
    messages = [SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)]
    resp = llm.invoke(messages)
    return resp.content if hasattr(resp, "content") else str(resp)
