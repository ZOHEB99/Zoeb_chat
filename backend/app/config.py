from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    gemini_api_key: str = ""
    openrouter_api_key: str = ""

    gemini_model: str = "gemini-flash-latest"
    openrouter_model: str = "openai/gpt-4o"

    cors_origins: str = "http://localhost:3000"

    app_host: str = "0.0.0.0"
    app_port: int = 8000

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
