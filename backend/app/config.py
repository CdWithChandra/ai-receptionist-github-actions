from dotenv import load_dotenv
import os

# # Load environment variables from backend/.env
# load_dotenv() #Reads the .env file and loads the values into the environment.

# class Settings:
#     """Application configuration loaded from environment variables."""
#     OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
#     APP_NAME = os.getenv("APP_NAME","AI Receptionist API")
#     APP_VERSION = os.getenv("APP_VERSION","1.0.0")
#     HOST = os.getenv("HOST","127.0.0.1")
#     PORT = int(os.getenv("PORT","8000"))

# #Creates a single configuration object that the rest of the application can import.
# settings = Settings()

import os

from dotenv import load_dotenv


# Load environment variables from backend/.env
load_dotenv()


class Settings:
    """Application configuration loaded from environment variables."""

    APP_NAME = os.getenv(
        "APP_NAME",
        "AI Receptionist API",
    )

    APP_VERSION = os.getenv(
        "APP_VERSION",
        "1.0.0",
    )

    HOST = os.getenv(
        "HOST",
        "127.0.0.1",
    )

    PORT = int(
        os.getenv(
            "PORT",
            "8000",
        )
    )

    OPENAI_API_KEY = os.getenv(
        "OPENAI_API_KEY"
    )


# Create a single configuration object
# that the application can import.
settings = Settings()
