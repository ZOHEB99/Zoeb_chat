import logging
from typing import Any

import httpx

from app.config import settings
from app.prompts import HEALTH_FITNESS_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class LLMServiceError(Exception):
    pass


class LLMService:
    def __init__(self) -> None:
        self._client = httpx.AsyncClient(timeout=60.0)

    async def close(self) -> None:
        await self._client.aclose()

    async def chat(self, messages: list[dict[str, str]]) -> dict[str, Any]:
        if settings.gemini_api_key:
            try:
                text = await self._chat_gemini(messages)
                return {"reply": text, "provider": "gemini"}
            except Exception as exc:
                logger.warning("Gemini request failed, trying OpenRouter fallback: %s", exc)

        if settings.openrouter_api_key:
            try:
                text = await self._chat_openrouter(messages)
                return {"reply": text, "provider": "openrouter"}
            except Exception as exc:
                logger.error("OpenRouter request failed: %s", exc)
                raise LLMServiceError("All AI providers failed. Check API keys and try again.") from exc

        raise LLMServiceError(
            "No AI provider configured. Set GEMINI_API_KEY or OPENROUTER_API_KEY."
        )

    async def _chat_gemini(self, messages: list[dict[str, str]]) -> str:
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{settings.gemini_model}:generateContent"
        )
        payload = {
            "systemInstruction": {"parts": [{"text": HEALTH_FITNESS_SYSTEM_PROMPT}]},
            "contents": self._to_gemini_contents(messages),
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 1024,
            },
        }
        response = await self._client.post(
            url,
            headers={
                "Content-Type": "application/json",
                "X-goog-api-key": settings.gemini_api_key,
            },
            json=payload,
        )
        response.raise_for_status()
        data = response.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]

    async def _chat_openrouter(self, messages: list[dict[str, str]]) -> str:
        url = "https://openrouter.ai/api/v1/chat/completions"
        payload = {
            "model": settings.openrouter_model,
            "messages": [{"role": "system", "content": HEALTH_FITNESS_SYSTEM_PROMPT}, *messages],
            "temperature": 0.7,
            "max_tokens": 1024,
        }
        response = await self._client.post(
            url,
            headers={
                "Authorization": f"Bearer {settings.openrouter_api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:3000",
                "X-Title": "FitCoach Health Chatbot",
            },
            json=payload,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    @staticmethod
    def _to_gemini_contents(messages: list[dict[str, str]]) -> list[dict[str, Any]]:
        role_map = {"user": "user", "assistant": "model"}
        contents: list[dict[str, Any]] = []
        for message in messages:
            role = role_map.get(message["role"])
            if not role:
                continue
            contents.append({"role": role, "parts": [{"text": message["content"]}]})
        return contents
