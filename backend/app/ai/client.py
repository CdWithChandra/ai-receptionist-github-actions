from openai import OpenAI
from app.config import settings
def get_openai_client() -> OpenAI:
    """
    Create and return an OpenAI client instance using the API key from settings.
    
    Returns:
        OpenAI: An instance of the OpenAI client.
    """
    if not settings.OPENAI_API_KEY:
        raise ValueError(
            "OPENAI_API_KEY is missing. Please set it in backend/.env."
        )
    return OpenAI(api_key=settings.OPENAI_API_KEY)

