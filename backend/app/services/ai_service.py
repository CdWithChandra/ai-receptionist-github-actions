from openai import OpenAIError

from app.ai.client import get_openai_client
from app.schemas.chat import ChatResponse
from app.prompts.receptionist_prompt import SYSTEM_PROMPT

class AIService:
    """
    Service responsible for AI-generated responses.
    """

    @staticmethod
    def get_ai_response(message: str) -> ChatResponse:
        """
        Generate an AI response using OpenAI.

        Args:
            message (str): User message.

        Returns:
            ChatResponse: AI reply.
        """
        try:
            client = get_openai_client()

            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT,
                    },
                    {
                        "role": "user",
                        "content": message,
                    },
                ],
                max_tokens=150,
            )

            reply = response.choices[0].message.content

            return ChatResponse(
                reply=reply
            )

        except ValueError:
            return ChatResponse(
                reply=(
                    "OpenAI API key is not configured. "
                    "Please add OPENAI_API_KEY to your .env file."
                )
            )

        except OpenAIError as e:
            return ChatResponse(
                reply=f"OpenAI error: {str(e)}"
            )

        except Exception as e:
            return ChatResponse(
                reply=f"Unexpected error: {str(e)}"
            )