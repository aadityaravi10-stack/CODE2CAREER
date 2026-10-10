from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


Phase = Literal["setup", "opening", "active_discussion", "closing_round", "ended", "report_ready"]


class Topic(BaseModel):
    id: str
    title: str


class CreateSessionRequest(BaseModel):
    topic_id: str | None = None
    custom_topic: str | None = None
    panel_size: int = Field(default=3, ge=3, le=3)
    difficulty: Literal["supportive", "balanced", "challenging"] = "balanced"
    language: str = Field(default="en-IN", min_length=2, max_length=16)
    duration_minutes: int = Field(default=8, ge=2, le=30)
    practice_mode: bool = True


class StudentTurnRequest(BaseModel):
    text: str


class TranscriptMessage(BaseModel):
    id: int
    session_id: str
    speaker: str
    source: str
    text: str
    timestamp: datetime


class SessionResponse(BaseModel):
    id: str
    topic: str
    phase: Phase
    created_at: datetime
    demo_mode: bool
    difficulty: str = "balanced"
    language: str = "en-IN"
    duration_minutes: int = 8
    practice_mode: bool = True
    transcript: list[TranscriptMessage]


class AiTurnResponse(BaseModel):
    session: SessionResponse
    message: TranscriptMessage
    next_speaker: str | None = None


class ReportSection(BaseModel):
    score: str
    explanation: str
    quote: str | None
    suggestion: str


class FeedbackReport(BaseModel):
    session_id: str
    topic: str
    overall_summary: str
    overall_score: int = Field(ge=1, le=10)
    rating: Literal["Weak", "Average", "Strong", "Elite"]
    sections: dict[str, ReportSection]
    top_3_strengths: list[str]
    top_3_improvements: list[str]
    generated_at: datetime


class ErrorResponse(BaseModel):
    detail: str
    hint: str | None = None
    extra: dict[str, Any] | None = None
