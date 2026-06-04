import httpx
from openai import OpenAI
from src.config import get_settings

class GrokAPIError(Exception):
    """Custom exception raised when xAI Grok API call fails."""
    pass

def call_grok_api(system_prompt: str, user_prompt: str) -> str:
    """
    Call the configured LLM API (Groq, Gemini, xAI, etc.) with OpenAI SDK.
    Returns the string completion (expecting JSON shape).
    """
    settings = get_settings()
    api_key = settings.active_llm_key
    base_url = settings.active_llm_base
    model = settings.active_llm_model

    if not api_key:
        raise GrokAPIError("LLM API Key is missing. Fallback engine triggered.")

    try:
        # Construct client pointing to resolved LLM base
        client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=10.0,  # 10s timeout
        )

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.2,  # Lower temperature for recommendation deterministic outputs
        )

        content = response.choices[0].message.content
        if not content:
            raise GrokAPIError("Received empty response from Grok API.")
        return content

    except httpx.HTTPError as http_err:
        raise GrokAPIError(f"HTTP connection error to xAI: {str(http_err)}")
    except Exception as err:
        raise GrokAPIError(f"Unexpected error calling Grok API: {str(err)}")
