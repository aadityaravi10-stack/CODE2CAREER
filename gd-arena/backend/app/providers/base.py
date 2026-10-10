from abc import ABC, abstractmethod

from app.models.schemas import FeedbackReport, TranscriptMessage


class LLMProvider(ABC):
    @abstractmethod
    def participant_turn(
        self,
        participant: dict[str, str],
        topic: str,
        transcript: list[TranscriptMessage],
        phase: str,
        language: str = "en-IN",
    ) -> str:
        raise NotImplementedError

    @abstractmethod
    def moderator_message(self, topic: str, phase: str, transcript: list[TranscriptMessage], language: str = "en-IN") -> str:
        raise NotImplementedError

    @abstractmethod
    def feedback_report(self, session_id: str, topic: str, transcript: list[TranscriptMessage]) -> FeedbackReport:
        raise NotImplementedError


class SpeechToTextProvider(ABC):
    @abstractmethod
    def transcribe(self, audio_bytes: bytes) -> str:
        raise NotImplementedError


class TextToSpeechProvider(ABC):
    @abstractmethod
    def synthesize(self, text: str) -> bytes:
        raise NotImplementedError
