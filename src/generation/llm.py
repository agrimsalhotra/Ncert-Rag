import os

from config.settings import (
    GEMINI_MODEL,
    GROQ_MODEL,
    LLM_MAX_RETRIES,
    LLM_PROVIDERS,
    LLM_TEMPERATURE,
    OPENROUTER_BASE_URL,
    OPENROUTER_MODEL,
)

# Which environment variable holds each provider's API key
KEY_NAMES = {
    "groq": "GROQ_API_KEY",
    "gemini": "GOOGLE_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
}


def build_single_llm(provider):
    """Build one chat model. Only the chosen provider's package is imported."""
    if provider not in KEY_NAMES:
        raise ValueError(f"Unknown provider {provider!r}. Use: groq, gemini, openrouter")

    key_name = KEY_NAMES[provider]
    if not os.getenv(key_name):
        raise ValueError(f"{key_name} is missing. Add it to your .env file.")

    if provider == "groq":
        from langchain_groq import ChatGroq

        return ChatGroq(
            model=GROQ_MODEL,
            temperature=LLM_TEMPERATURE,
            max_retries=LLM_MAX_RETRIES,
        )

    if provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(
            model=GEMINI_MODEL,
            temperature=LLM_TEMPERATURE,
            max_retries=LLM_MAX_RETRIES,
        )

    # provider == "openrouter": OpenAI-compatible API on a different URL
    from langchain_openai import ChatOpenAI

    return ChatOpenAI(
        model=OPENROUTER_MODEL,
        base_url=OPENROUTER_BASE_URL,
        api_key=os.getenv("OPENROUTER_API_KEY"),
        temperature=LLM_TEMPERATURE,
        max_retries=LLM_MAX_RETRIES,
    )


def build_llm():
    """First provider in LLM_PROVIDERS is primary. The rest are used if it fails."""
    if len(LLM_PROVIDERS) == 0:
        raise ValueError("LLM_PROVIDERS is empty. Set it in your .env file.")

    models = [build_single_llm(provider) for provider in LLM_PROVIDERS]
    primary = models[0]
    fallbacks = models[1:]

    if len(fallbacks) > 0:
        return primary.with_fallbacks(fallbacks)
    return primary