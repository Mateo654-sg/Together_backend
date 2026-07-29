"""
OpenAI provider for AI service.

Uses OpenAI's chat completions API for generating responses
and text-embedding-ada-002 for embeddings.
"""

from openai import AsyncOpenAI

from app.services.ai.base import AIProvider


class OpenAIProvider(AIProvider):
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self._client = AsyncOpenAI(api_key=api_key)
        self._model = model

    @property
    def name(self) -> str:
        return "openai"

    @property
    def model(self) -> str:
        return self._model

    async def generate(self, prompt: str, context: str = "") -> dict:
        system_prompt = (
            "Eres un asistente financiero personal experto en finanzas personales y de pareja. "
            "Responde en español de forma clara, concisa y útil. "
            "Usa la información de contexto del usuario para personalizar tu respuesta."
        )
        messages = [{"role": "system", "content": system_prompt}]
        if context:
            messages.append({"role": "user", "content": f"Contexto financiero del usuario:\n{context}"})
        messages.append({"role": "user", "content": prompt})

        response = await self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            temperature=0.7,
            max_tokens=1024,
        )

        answer = response.choices[0].message.content or ""
        usage = response.usage

        return {
            "answer": answer,
            "tokens_input": usage.prompt_tokens if usage else 0,
            "tokens_output": usage.completion_tokens if usage else 0,
        }

    async def embeddings(self, text: str) -> list[float]:
        response = await self._client.embeddings.create(
            model="text-embedding-ada-002",
            input=text,
        )
        return response.data[0].embedding
