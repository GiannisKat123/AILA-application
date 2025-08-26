from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Application configuration settings loaded from environment variables
    or a `.env` file. Provides strongly typed access to environment values.
    """

    OLLAMA_SERVER_URL: str
    """URL of the Ollama server for model inference."""

    FRONTEND_URL: str
    """Base URL of the frontend client application."""

    DB_USERNAME: str
    """Database username credential."""

    DB_PASSWORD: str
    """Database password credential."""

    DB_HOST: str
    """Hostname or IP address of the database server."""

    DB_DATABASE_NAME: str
    """Name of the application’s database."""

    DB_DRIVER_NAME: str
    """Database driver (e.g., `postgresql`, `mysql`, `sqlite`)."""

    ACCESS_TOKEN_EXPIRE_MINUTES: int
    """Duration (in minutes) before access tokens expire."""

    API_KEY: str
    """Generic API key for application-level integrations."""

    SECRET_KEY: str
    """Secret key used for signing tokens and securing sensitive operations."""

    ALGORITHM: str
    """Cryptographic algorithm used for JWT or token signing (e.g., `HS256`)."""

    VITE_API_URL: str
    """API base URL injected into the frontend (e.g., Vite builds)."""

    APP_PASSWORD: str
    """Application-specific password (e.g., for email sending)."""

    SENDER_EMAIL: str
    """Default email address used for sending application emails."""

    COHERE_API_KEY: str
    """API key for accessing Cohere’s services."""

    COHERE_MODEL_ID: str
    """Identifier of the Cohere model to use."""

    INIT_MODE: str
    """Initialization mode (e.g., `dev`, `prod`, `test`)."""

    OPEN_AI_MODEL: str
    """OpenAI model name (e.g., `gpt-4o-mini`)."""

    TAVILY_API_KEY: str
    """API key for Tavily API integration."""

    class Config:
        """
        Configuration for Pydantic settings.
        Loads values from `.env` file by default.
        """
        env_file = ".env"


# Singleton instance of Settings, ready to be imported across the app
settings = Settings()
