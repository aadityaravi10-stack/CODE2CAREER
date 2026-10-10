import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.providers.mock import MockLLMProvider


class ProviderRegistry:
    """Selects Gemini first, then Groq and OpenRouter, with mock mode for demos."""

    def __init__(self):
        self.mode = os.getenv("AI_MODE", "auto").lower()
        self.mock = MockLLMProvider()
        self._provider = self._select_provider()

    def selected_name(self) -> str:
        return self._provider.name

    def llm(self):
        return self._provider

    def _select_provider(self):
        choices = {
            "gemini": ("GEMINI_API_KEY", "Google Gemini Flash Lite"),
            "groq": ("GROQ_API_KEY", "Groq Llama 3.3 70B"),
            "openrouter": ("OPENROUTER_API_KEY", "OpenRouter"),
        }
        order = [self.mode] if self.mode in choices else ["gemini", "groq", "openrouter"]
        for provider_id in order:
            env_name, name = choices[provider_id]
            key = os.getenv(env_name)
            if key:
                return RemoteLLMProvider(provider_id, name, key, self.mock)
        return NamedMockProvider(self.mock)


class NamedMockProvider(MockLLMProvider):
    name = "mock"

    def __init__(self, mock: MockLLMProvider):
        self.__dict__.update(mock.__dict__)


class RemoteLLMProvider(MockLLMProvider):
    """Minimal HTTPS clients for the three configured LLM providers."""

    def __init__(self, provider_id: str, name: str, api_key: str, fallback: MockLLMProvider):
        self.provider_id = provider_id
        self.name = name
        self.api_key = api_key
        self.fallback = fallback

    def participant_turn(self, participant, topic, transcript, phase, language="en-IN"):
        prompt = (
            f"You are {participant['name']}, a {participant['label']} in a group discussion. "
            f"Your style is {participant['style']}. Topic: {topic}. Phase: {phase}. "
            f"Respond only in the locale {language}, in 2 concise sentences. Build on the student where possible, do not mention being an AI.\n"
            f"Recent transcript:\n{self._transcript_text(transcript)}"
        )
        return self._complete(prompt) or self.fallback.participant_turn(participant, topic, transcript, phase, language)

    def moderator_message(self, topic, phase, transcript, language="en-IN"):
        prompt = (
            f"Act as a concise group discussion moderator. Topic: {topic}. Phase: {phase}. "
            f"Write one supportive instruction of at most 35 words, only in locale {language}.\n"
            f"Recent transcript:\n{self._transcript_text(transcript)}"
        )
        return self._complete(prompt) or self.fallback.moderator_message(topic, phase, transcript, language)

    def _complete(self, prompt: str) -> str:
        try:
            if self.provider_id == "gemini":
                url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-lite:generateContent?key=" + self.api_key
                payload = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"temperature": 0.7, "maxOutputTokens": 180}}
                response = _post_json(url, payload)
                return response["candidates"][0]["content"]["parts"][0]["text"].strip()
            url = "https://api.groq.com/openai/v1/chat/completions" if self.provider_id == "groq" else "https://openrouter.ai/api/v1/chat/completions"
            model = "llama-3.3-70b-versatile" if self.provider_id == "groq" else os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.3-70b-instruct")
            response = _post_json(url, {"model": model, "messages": [{"role": "user", "content": prompt}], "temperature": 0.7, "max_tokens": 180}, {"Authorization": f"Bearer {self.api_key}"})
            return response["choices"][0]["message"]["content"].strip()
        except (HTTPError, URLError, KeyError, IndexError, json.JSONDecodeError):
            return ""

    @staticmethod
    def _transcript_text(transcript) -> str:
        return "\n".join(f"{message.speaker}: {message.text}" for message in transcript[-6:]) or "No prior turns."


def _post_json(url: str, payload: dict, headers: dict | None = None) -> dict:
    request = Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json", **(headers or {})}, method="POST")
    with urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))
