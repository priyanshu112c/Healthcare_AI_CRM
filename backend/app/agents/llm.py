from langchain_groq import ChatGroq
from app.config import settings


def get_llm(temperature: float | None = None):
    return ChatGroq(
        api_key=settings.groq_api_key,
        model=settings.model,
        temperature=temperature if temperature is not None else settings.temperature,
        max_tokens=settings.max_tokens,
    )


def get_fallback_llm():
    return ChatGroq(
        api_key=settings.groq_api_key,
        model=settings.model_fallback,
        temperature=settings.temperature,
        max_tokens=settings.max_tokens,
    )
